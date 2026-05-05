# 生产环境改用本地 SQLite 说明（腾讯云 MySQL 停用后）

本文档记录：**在保持 `ROAMIO_SETTINGS=prod`（HTTPS、密钥等生产项）的前提下，将数据库从 MySQL 切到项目根目录 SQLite** 的原因、代码变更与运维操作。  
相关提交：**`cfcf850b`** — `feat(settings): prod SQLite via ROAMIO_USE_SQLITE; load .env before settings selection`

---

## 背景

- 原生产库为腾讯云 MySQL（例如内网域名 `*.sql.tencentcdb.com`），**库已过期或不可达**。
- 希望继续用 **prod 配置**（`DEBUG=False`、安全 Cookie、密钥等），但**数据落在单文件 SQLite**：`{项目根}/db.sqlite3`。

---

## 曾出现的问题

1. **`.env` 生效顺序错误**  
   旧逻辑在 `roamio/settings/__init__.py` 里先根据环境变量选择 `prod` / `dev`，再在其他模块里 `load_dotenv()`，导致 `.env` 中的 `ROAMIO_SETTINGS`、`ROAMIO_USE_SQLITE` 在**选择配置时并未读入**，仍会使用 `prod` 下的 MySQL `DB_HOST`，出现 `Unknown MySQL server host`、登录/迁移失败等。

2. **代码未推送到远端**  
   若修复只在本机未 `git push`，服务器 `git pull` 显示 «Already up to date» 但仍是旧代码，`export ROAMIO_USE_SQLITE=1` 也会无效。

---

## 代码改动摘要

| 文件 | 说明 |
|------|------|
| `roamio/settings/__init__.py` | 在读取 `ROAMIO_SETTINGS` **之前**加载项目根 `.env`，若存在 `.env.prod` 则再加载并**覆盖**同名键，保证环境变量先就绪。 |
| `roamio/settings/prod.py` | 当 `ROAMIO_USE_SQLITE` 为真（`1` / `true` / `yes` / `on`）时，`DATABASES` 指向 `BASE_DIR / 'db.sqlite3'`；否则仍使用 MySQL `DB_*`。 |
| `scripts/deploy_uwsgi.sh` | 从 `.env` / `.env.prod` 探测 `ROAMIO_USE_SQLITE`；`manage.py check` 与 uWSGI 子进程传递该变量；uWSGI 启动时附加 `--env`。 |
| `env.prod.example` | 增加 `ROAMIO_USE_SQLITE` 的示例与注释。 |

---

## 服务器配置（`.env` 示例）

在项目根 `~/roamio/.env`（或单独使用 `.env.prod`）中至少包含：

```bash
ROAMIO_SETTINGS=prod
ROAMIO_USE_SQLITE=1

SECRET_KEY=你的生产密钥
ALLOWED_HOSTS=roamio.cn,www.roamio.cn

# CSRF / CORS 按域名填写
CSRF_TRUSTED_ORIGINS=https://roamio.cn,https://www.roamio.cn
CORS_ALLOWED_ORIGINS=https://roamio.cn,https://www.roamio.cn
```

在 **`ROAMIO_USE_SQLITE=1`** 时，可不再依赖有效的 `DB_*`；旧 MySQL 变量可保留或删除，Django 不会使用它们连接 MySQL。

---

## 部署命令（参考）

```bash
cd ~/roamio
git pull origin master

# 若 .env 尚未写入，可临时导出后执行迁移
export ROAMIO_SETTINGS=prod
export ROAMIO_USE_SQLITE=1
python3 manage.py migrate

bash scripts/deploy_uwsgi.sh
```

`.env` 配置完整后，多数情况下只需 `git pull`、`migrate`、`deploy`，不必每次手动 `export`。

---

## 验证

- `python3 manage.py migrate` 应在**无 MySQL 报错**下完成（通常显示 `No migrations to apply` 或正常应用迁移）。
- 确认代码版本：  
  `grep -n ROAMIO_USE_SQLITE roamio/settings/prod.py`  
  应能看到 `if _env_truthy('ROAMIO_USE_SQLITE'):` 分支。
- 浏览器访问站点，检查登录与主要 API 是否正常。

---

## 回退到 MySQL（将来若恢复云库）

1. 去掉或置空 `ROAMIO_USE_SQLITE`（设为 `0` 或删除该行）。  
2. 在 `.env` 中补齐有效 `DB_NAME`、`DB_USER`、`DB_PASSWORD`、`DB_HOST` 等。  
3. `python3 manage.py migrate` 后重启 uWSGI。

---

## 备忘

- SQLite 适合单机、中小流量；多进程写放大、备份与并发策略与 MySQL 不同，若日后规模上升需再评估是否迁回 RDS/自建 MySQL。
- 项目根 `db.sqlite3` 需纳入备份策略（拷贝文件或定期导出）。
