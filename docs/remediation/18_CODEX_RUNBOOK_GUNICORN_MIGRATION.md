# Codex 主路径：**Gunicorn 迁移**（相对 uWSGI）

> **排期**：在「站点已可从 Nginx+uWSGI 稳定对外」前提下，本条是**部署向优先于**「数据库/SQLite 应急、模板扫描类整改」（见 [`16`](16_CODEX_RUNBOOK_BATCH_SECURITY_BACKUP_CI.md)）的主线之一。SQLite 改过的是**数据在哪**；Gunicorn 改的是**应用进程谁来扛**——两码事。

## 真理来源（规格与批次）

全文以 **`docs/remediation/15_GUNICORN_MIGRATION_REMEDIATION.md`** 为准：三段式 **Batch A → B → C**、验收、回滚、质量门。**本文只做 Codex「能干什么 / 不能干什么」的补充与可复制 Prompt**。

---

## 人机分工

| Codex / PR 能做的 | **必须人肉**做的 |
|-------------------|----------------|
| **`Batch A`**：补齐/对齐 **`requirements-prod.txt`**、`start_gunicorn.sh`、`stop_gunicorn.sh`、`healthcheck.sh`（若有）、新增与 **`deploy_uwsgi.sh` 对称的 `deploy_gunicorn.sh`**（建前端、`manage.py check`、按 `PORT`/`APP_ROOT`/环境变量拉起 Gunicorn、健康检查脚本调用）；文档与 **Nginx 配置示例片段**（放 `docs/`，不写死生产密钥）。 | **`Batch B`**：在 VPS 上改**真实 Nginx**、`nginx -t`、`reload`。 |
| CI 可加「仅校验脚本 bash -n」或文档链接；**不得在 CI 绑你私有机密**。 | **`Batch C`**：24–48h 观察、`curl`/日志判断是否收口；决定是否注释 uWSGI 常规入口。 |
| 产出回滚说明书（重申 15 §9）。 | **回滚**：停 Gunicorn、Nginx 指回 upstream、再起 uWSGI。 |

Codex **不能** SSH、不能替你 `nginx -s reload`、不能假设已切流量。

---

## Batch A 建议 PR 内容（与 15 §6 对齐并略扩展）

1. **`scripts/deploy_gunicorn.sh`**（新建）：行为尽量与 **`deploy_uwsgi.sh`** 平行——`git pull`、可选 `AUTO_STASH`、Python 解析 `.env`（prod 时）、`npm run build`、`manage.py check`、**停旧 Gunicorn**（用 `stop_gunicorn.sh` 或 pidfile）、**起新 Gunicorn**（`start_gunicorn.sh`，**默认端口需与 Nginx 即将指向的一致**：若生产 uWSGI 为 `8000`，Gunicorn 灰度可先用 `8001` 并在文档写清「Nginx upstream 改指向」）。  
2. **`scripts/start_gunicorn.sh` / `stop_gunicorn.sh`**：与 `15` 中质量门一致；避免无差别 `pkill -f` 误杀 **`deploy_gunicorn.sh`**（可参考 uWSGI 使用 **`pgrep -x`/pidfile** 的思路）。  
3. **`scripts/healthcheck.sh`**（若尚无）：对 `HEALTHCHECK_BASE_URL` 做与 `deploy_uwsgi.sh` 同级的检查。  
4. **`docs/guides/`** 下增加 **Nginx `proxy_pass` Gunicorn 示例**（`http://127.0.0.1:PORT`，保留原 `uwsgi_pass` **注释块**便于回滚）。  
5. **README**：标明「默认生产仍为 uWSGI；Gunicorn 为迁移路径」，链到本文与 `15`。

**禁止**：改业务视图/模型/迁移；与本迁移同批次改数据库引擎或大改 settings 语义。

---

## 质量门（每批）

照 **`15`** §8：**check**、**test**、**build**、以及对**已切换的环境**执行 `curl`（Batch A 若在 CI/沙盒无公网域名，写明「生产 curl 由维护者在切流量后执行」）。

---

## 附录：给 Codex 的 Prompt（复制用）

```text
【主任务】部署栈迁移——Gunicorn 替代 uWSGI，只做仓库内交付与文档；不负责登录我的服务器改 Nginx。

【必读规格】严格执行：
docs/remediation/15_GUNICORN_MIGRATION_REMEDIATION.md
辅以人机边界说明：
docs/remediation/18_CODEX_RUNBOOK_GUNICORN_MIGRATION.md

【只做 Batch A 除非我明确书面让你写 Nginx「示例」以外的内容】：
- 实现或补强 scripts/deploy_gunicorn.sh（与 deploy_uwsgi.sh 行为对称：pull、前端构建、Django check、停/起 Gunicorn、healthcheck）。
- 校准 start_gunicorn.sh、stop_gunicorn.sh（pidfile、端口、PYTHONPATH、`--chdir` 与 `roamio.wsgi` 一致）。
- requirements-prod.txt 已有 gunicorn 则对齐版本说明；增补 healthcheck.sh 若无。
- docs/guides 下给出 Nginx proxy 到 Gunicorn 的示例片段，保留 uwsgi_pass 注释回滚路径。
- 更新 README：默认仍为 uWSGI，Gunicorn 为迁移步骤；链接 15 与 18。
禁止：业务代码/模型迁移、改写 Git 历史、提交真实密钥、在同一 PR 混入 SQLite/大安全配置（除非我可单独批准）。

结束前：manage.py check、manage.py test backend.tests、frontend build；bash -n 新脚本。
PR 写明：运维在 Batch B 需要改的 Nginx 指令级清单与我应执行的 curl 序列（引用 §8）。
```

---

## 与你之前的疑问对齐

- **「放着 Gunicorn 大迁移不做」**：同意——**那才是部署向「大活儿」**；SQLite/`.env` 顺序修的是当时线上连不上库的**止血**。  
- **后续**：优先按 **Batch A PR → 人肉 Batch B/C** 走完 `15`，再排到 `16` 那种扫模板/密钥的细水长流。
