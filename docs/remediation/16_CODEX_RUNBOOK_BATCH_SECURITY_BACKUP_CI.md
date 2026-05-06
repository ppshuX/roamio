# Codex 批量执行说明：安全脱敏 + SQLite 备份恢复 + CI/最小验证补强

面向 **Codex（或同级自动化助手）**：按本文档顺序完成下列工作，一次性合并为一个 PR。**不要**重写 Git 历史、**不要**在仓库中写入任何真实生产密钥。

**前置阅读：** [05_SECURITY_CLEANUP.md](05_SECURITY_CLEANUP.md)、[production-sqlite-summary.md](../production-sqlite-summary.md)

---

## 与当前仓库对齐的备注（阅后即执行）

- API 挂载：根路由为 `path('api/v1/', include('backend.api.urls'))`（见 `roamio/urls.py`），Smoke 请以 **`/api/v1/...`** 为准。
- 后端测试入口：CI 使用 **`python manage.py test backend.tests`**，在本仓库对应 **`backend/tests.py`**（单文件模块，**不是** `backend/tests/` 目录）。Codex **新增至多 2～3** 个测试方法即可，勿与现有 `AuthAccessTests`、`AuthCookieFlowTests`、`TripApiSmokeTests` 等重复断言同一路径的同一场景。
- 环境示例：`05_SECURITY_CLEANUP.md` 曾写「只保留根 `.env.example`」为目标；实操上可同时维护 **`env.prod.example`**（生产占位 + `ROAMIO_USE_SQLITE`）— 两套模板均需仅占位符，不得含真密钥。
- **`docs/production-sqlite-summary.md`** 尚未包含「备份与恢复」小节时，任务块 **B3** 为必做增补。

---

## 总目标（本次 PR 收口标准）

| 序号 | 目标 | 验收方式 |
|------|------|-----------|
| G1 | 降低仓库明文秘密与误提交风险 | 根目录有可运行的轻量扫描脚本（或 Makefile 目标）；模板文件仅占位符 |
| G2 | 生产 SQLite 可备份与可恢复（运维可跟文档操作） | `scripts/` 下备份/还原脚本存在且带用法注释；汇总文档更新 |
| G3 | CI 与本地能对「根本没挂」有更稳信号 | 保留或增强现有 `manage.py check` + `backend.tests`；可选增加极少量 smoke |

---

## 任务块 A — 秘密与模板（对齐 M1 / 阶段 1）

### A1 盘点环境模板文件

1. 检查仓库内所有环境示例文件，至少包含：
   - 根目录 **`.env.example`**
   - **`env.prod.example`**
   - **`frontend/web/.env.example`**（若存在）
2. 确保：
   - 所有取值均为明显占位符（如 `replace-with-*`、`your-*`、`xxxxxxxx`）。
   - 变量名与实际 `roamio/settings` 用到的键对齐（可对照 `prod.py`、`dev.py`、`base.py`）。
3. **`env.prod.example`** 必须与当前生产说明一致：**`ROAMIO_SETTINGS`、`ROAMIO_USE_SQLITE`**、占位 `SECRET_KEY`、示例 `ALLOWED_HOSTS` / CSRF / CORS 等。（参考 `production-sqlite-summary.md`。）

### A2 全库敏感信息扫描（只读盘点 + 可安全修复）

1. 用 `rg`（或等价）扫描以下模式（**排除** `.git`、`node_modules`、静态构建产物、`db.sqlite3`、锁文件）；对**疑似真实**内容进行脱敏替换或删除整段可复制秘密的说明：
   - 长随机串看起来像 `SECRET_KEY=` 后的真实值
   - `password=`、`PASSWORD=`、`passwd`（非占位符上下文）
   - `sk-`、`AKIA`、`SecretId`、`SecretKey`、`api_key`、`APP_KEY`、`client_secret`
   - 内网/云托管特征：`*.tencentcdb.com`、`sql.tencent`、`mysql://`、`redis://:密码@`
   - 邮箱授权码明文（QQ/163 SMTP 常见）
2. **优先处理 `docs/**/*.md`、`*.example`、`README*`**；若在业务代码注释中发现真密钥——改为「从环境变量读取」或删除该行。
3. **禁止**：把任何人的**真实生产** `.env` 内容写入仓库。
4. 产出：**`scripts/scan_repo_secrets.sh`**（bash，推荐 `chmod +x`）、或 **`Makefile` target `scan-secrets`**，内部调用 **`rg` 优先**（Ubuntu CI 可先 `sudo apt-get install ripgrep` 或使用 `grep -R`）；并维护很小的 **`scripts/secret_scan_allowlist.txt`**：**每行可写 `-g '*.lock'`、`!path/to/file` 等备注**，或由脚本按需 `grep -vFf` 该文件跳过「已知占位行」——格式在脚本注释中写清即可，不必强行与 `rg --glob` 一一等同。

### A3 PR 附带「轮换提示」节选

以下二选一即可，**不要求重复两份**：（1）本文件文末「轮换提示」已满足运维提醒时，仅在 PR 中引用本文档链接；（2）或新建简短 **`docs/remediation/17_ROTATION_REMINDER_STUB.md`**，内容与 **`05_SECURITY_CLEANUP.md`** 中「Credentials To Rotate」条目对齐（仅类目，不写值）。

---

## 任务块 B — SQLite 备份与恢复（对齐 M6 子集）

### B1 脚本：`scripts/backup_sqlite.sh`

- 假定默认数据库路径为 **项目根** `db.sqlite3`（与 Django `BASE_DIR / 'db.sqlite3'` 一致）。
- 行为建议：
  - 支持环境变量 **`ROAMIO_DB_PATH`** 覆盖数据库文件路径。
  - 备份到 **`BACKUP_DIR`**：默认 `./backups/sqlite/`（项目根下）；若希望与数据分区分离可改为 `./var/backups/sqlite/`（二选一写入脚本注释默认值即可）。
  - 文件名带时间戳：`db-YYYYMMDD-HHMMSS.sqlite3`。
  - 使用 **`sqlite3 "$DB" ".backup '$OUT'"`** 若在 PATH 中存在 `sqlite3`；否则回退 **`cp`** 并在注释中说明 WAL 一致性风险。
  - 保留最近 **`KEEP`** 份（可选，默认例如 14），删旧备份。
  - **`set -euo pipefail`**，缺文件时清晰报错退出。

### B2 脚本：`scripts/restore_sqlite.sh`

- 参数：备份文件路径；可选 `--dry-run` 仅打印将执行的操作。
- 行为：停机说明写在注释（**必须由人工停 uWSGI**）；恢复到项目根默认 `db.sqlite3`（可 `ROAMIO_DB_PATH` 覆盖）；建议先对已存在库做 **`db.sqlite3.pre-restore-<timestamp>`** 重命名备份。
- 禁止在脚本内写死服务器路径口令；一切皆环境变量或可传参。

### B3 文档

在 **`docs/production-sqlite-summary.md`** 增加一节 **「备份与恢复」**，链接上述两脚本、cron 示例一行（注释形式即可）、以及与 **`deploy_uwsgi.sh`** 的配合顺序简述。

---

## 任务块 C — CI / 最小验证补强（对齐 M3）

### C1 后端测试

1. 阅读 **`.github/workflows/ci.yml`**。默认 **`manage.py check`** 不强制 `export ROAMIO_SETTINGS`（与本地 dev 对齐即可）；若在 CI 中要显式强调，可加 **`ROAMIO_SETTINGS=dev`**，但不得以 `prod` 跑 CI（缺密钥会挂）。
2. 在 **`backend/tests.py`** 中按需增加 **≤3** 条极薄 smoke（新 `TestCase` 或挂在现有 Case 内均可），例如：**匿名 GET `/api/v1/auth/me/` → 401**（路径以路由为准）。
3. **避免重复**：`/api/v1/trips/`、`/api/v1/auth/login/`、`trip-plans` 等已由现有用例覆盖，勿再抄一份。
4. 不得引入需外网或可下载大模型的集成测试。

### C2 （可选加分）CI 中运行密钥扫描脚本

在工作流中加一步：**`bash scripts/scan_repo_secrets.sh`**（若脚本非致命误报较多，可先 `continue-on-error: true`，但须在脚本头注释写明「零容忍项」并逐步收紧）。

---

## 硬约束（违反则视为失败）

1. **不**提交真实 `SECRET_KEY`、数据库密码、OAuth Secret、COS 密钥、SMTP 口令。
2. **不**执行 `git filter-repo` / 历史重写（仅可在文档中提示由人工决策）。
3. **不**大规模重构业务视图/序列化器；本篇范围限于安全模板、脚本、文档、测试与 CI 小改。
4. **不**删除未在本文档列出的、`05_SECURITY_CLEANUP.md` 已声明删除路径以外的生产关键代码。

---

## 提交与 PR 要求

1. 一个 PR、逻辑可拆为多 commit 但合并前建议 **`squash` 或由维护者自定**。
2. PR 描述需包含：**变更摘要**、**如何本地运行 `backup_sqlite.sh`/`scan_repo_secrets.sh`**、**已知限制**；新增的 `scripts/*.sh` 需在 PR 说明中写明是否需 `chmod +x`。
3. 若 CI 不可用（ fork 无私密），仍需保证脚本在 Ubuntu / bash 下可跑。

---

## 完成自检清单（Codex / 人手均可勾）

- [ ] `env.prod.example` 与 `.env.example`（及前端示例）占位符齐全且无明显真实秘密
- [ ] `scripts/scan_repo_secrets.sh`（或等价）存在且根 `README.md` 或 `docs/remediation/README.md` 索引中可加一行指向（任选一处）
- [ ] `backup_sqlite.sh` / `restore_sqlite.sh` 存在，`production-sqlite-summary.md` 已更新备份章节
- [ ] 新增或补强测试，`python manage.py test backend.tests` 本地通过
- [ ] （可选）CI 已调用扫描脚本
- [ ] 新建 **`docs/remediation/17_ROTATION_REMINDER_STUB.md`**（或与 A3 一样仅用本文档末节 + PR 说明二选一）

---

## 轮换提示（仅占位，不写真实值）

合并本 PR 后，若历史中曾出现过真实凭据，维护者须在对应云控制台逐项轮换：**Django SECRET_KEY、数据库、Redis、SMTP、QQ OAuth、COS、Qwen、地图 Key、Ralendar OAuth** 等。详见 [05_SECURITY_CLEANUP.md](05_SECURITY_CLEANUP.md)。
