# M5.5 Gunicorn Migration Remediation

> **Codex 执行入口（人机分工 + Prompt）**：[18_CODEX_RUNBOOK_GUNICORN_MIGRATION.md](18_CODEX_RUNBOOK_GUNICORN_MIGRATION.md)
>
> 状态：Draft（建议在当前线上稳定 24-48h 后执行）  
> 目标：将当前 `Nginx + uWSGI` 运行链路平滑迁移为 `Nginx + Gunicorn`，降低维护复杂度，保留可回滚能力。  
> 范围：仅部署链路与运行脚本；不改业务逻辑、不改数据库语义。

## 1. 为什么要迁移

当前项目可以稳定运行在 uWSGI 上，但已暴露出以下维护成本：

- 进程管理和参数漂移（重复拉起、端口占用）排查成本高
- 多进程 + 本地缓存在 OAuth state 校验场景下容易踩坑
- 团队后续运维经验和生态文档更偏向 Gunicorn

迁移到 Gunicorn 的收益：

- 启动参数更直观、错误日志更易读
- 与 systemd / Docker / CI 部署链路更通用
- 更容易标准化发布和回滚脚本

## 2. 非目标（本次不做）

- 不改 Django app 结构
- 不改前端构建方案
- 不改数据库引擎和数据迁移策略
- 不改业务 API 协议与鉴权语义

## 3. 迁移总策略

采用“三步迁移”：

1. **并行准备**：新增 Gunicorn 启动脚本与健康检查，不切流量  
2. **灰度切换**：Nginx 上游从 uWSGI 切到 Gunicorn（保留 uWSGI 脚本）  
3. **稳定观察**：验证通过后再下线 uWSGI 常规入口

任何一步失败，立即按回滚步骤恢复 `uWSGI`。

## 4. 前置条件（必须满足）

- HTTPS 已恢复正常（`http -> https` 重定向、证书有效）
- `HOME` 与核心 API 可返回 200（或鉴权预期状态）
- 当前运行环境变量可复现（至少 `ROAMIO_SETTINGS`、QQ OAuth、数据库配置）
- 已有可用数据库备份点（SQLite 或 MySQL）

## 5. 目标运行形态

- Nginx: 对 `/api` 与 SPA 请求反向代理到 Gunicorn
- Gunicorn: 监听 `127.0.0.1:8000`（或新端口如 8001）
- Django: 保持 `roamio.wsgi:application`
- 前端构建输出仍为 `backend/web_dist/`

## 6. 执行批次（给 Codex）

## Batch A：脚本与依赖准备（不切流量）

允许改动：

- `requirements-prod.txt`（若未包含 `gunicorn`）
- `scripts/start_gunicorn.sh`（新增）
- `scripts/stop_gunicorn.sh`（新增）
- `scripts/healthcheck.sh`（新增或更新）
- 文档文件

禁止改动：

- Nginx 生产流量入口
- 业务代码、模型、迁移

验收：

- `gunicorn --version` 可执行
- 启动脚本可在本机拉起进程并监听端口

## Batch B：Nginx 上游切换（可回滚）

允许改动：

- Nginx 对应站点配置中 upstream / pass 方式

建议：

- 先用独立 upstream 名称（如 `roamio_gunicorn`）
- 保留旧 uWSGI 配置块（注释而非删除）

验收：

- `nginx -t` 通过
- `nginx -s reload` 成功
- `HOME`、`/api/v1/trips/`、QQ 登录 URL 接口正常

## Batch C：观察与收口

观察窗口：建议 24-48h

检查项：

- 错误日志是否有显著新增 5xx
- QQ OAuth 回调是否稳定
- API 性能无明显退化

收口：

- 稳定后将 uWSGI 启动脚本标注为“兼容回滚入口”
- 更新 README / 运维文档默认入口为 Gunicorn

## 7. 推荐脚本模板（最小）

`scripts/start_gunicorn.sh` 示例：

```bash
#!/usr/bin/env bash
set -euo pipefail

cd /home/acs/roamio
export ROAMIO_SETTINGS="${ROAMIO_SETTINGS:-dev}"

pkill -f "gunicorn.*roamio.wsgi:application" || true

gunicorn roamio.wsgi:application \
  --bind 127.0.0.1:8000 \
  --workers 2 \
  --threads 2 \
  --timeout 60 \
  --access-logfile /tmp/gunicorn.access.log \
  --error-logfile /tmp/gunicorn.error.log \
  --daemon
```

## 8. 质量门（每批必跑）

本地/服务器至少执行：

1. `python manage.py check`（或 `cd backend && python manage.py check`）
2. `python manage.py test backend.tests`
3. `cd frontend/web && npm run build`
4. `curl -I https://roamio.cn/`
5. `curl -I https://roamio.cn/api/v1/trips/`
6. `curl -sS https://roamio.cn/api/v1/auth/qq_login_url/`

## 9. 回滚方案（必须可一键执行）

触发条件：

- 连续 5xx 明显上升
- OAuth 回调稳定失败
- Gunicorn 进程频繁退出

回滚步骤：

1. 停 Gunicorn
2. Nginx 上游恢复到 uWSGI
3. 启动 uWSGI
4. 重新执行健康检查

## 10. 风险与注意事项

- `dev + LocMem` 多进程对 OAuth state 不友好，建议 dev 也接 Redis 缓存
- 迁移期不要同时改数据库和部署链路
- 严禁在同一批次混入前端样式/业务重构

## 11. Codex 执行指令（可直接复制）

```text
严格按 docs/remediation/15_GUNICORN_MIGRATION_REMEDIATION.md 执行，分 Batch A/B/C 串行推进。
每批先输出修改计划和风险，等我批准后再改文件。
禁止改业务逻辑、模型、迁移、.env 真值。
每批结束必须给出 check/test/build 与线上 curl 结果。
未经我明确允许不得 commit、不得 push。
```

