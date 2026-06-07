# M5 Backend Relocation Master Plan (`backend/` 下沉工程)

> 状态：Draft（待你确认后生效）  
> 目标：将后端工程从“仓库根目录驱动”迁移为“`backend/` 目录驱动”，并保证全链路可回滚、可验证、可持续开发。

## 1. 工程目标（Done 的定义）

满足以下条件才算完成：

1. 后端命令入口统一为：`cd backend && python manage.py ...`
2. Django 配置入口、ASGI/WSGI、测试、CI、部署脚本均基于 `backend/`
3. 本地开发、CI、生产部署三环境均可运行
4. 文档、脚本、命令示例不再依赖根目录 `manage.py`
5. 迁移过程全程分批，每批可独立回滚

## 2. 非目标（本轮明确不做）

- 不做 Django app 业务拆分（`backend` app 名保持不变）
- 不做数据库结构重构（不新增迁移、不改模型语义）
- 不做前端样式体系切换（Tailwind/DaisyUI 属于独立主题）
- 不做功能性新需求开发

## 3. 风险与控制

- **风险：路径级破坏**（导入路径、脚本路径、部署路径）
  - 控制：每批小步改动 + 固定质量门 + 快速回滚
- **风险：运行入口混乱**（新旧命令并存）
  - 控制：过渡期允许兼容，但文档必须明确“主入口”
- **风险：CI/部署断链**
  - 控制：先补测试命令，再切 CI，最后切部署

## 4. 分阶段执行（必须按顺序）

## Phase 0 - Baseline 冻结（只读）

目标：建立重构前基线，禁止改代码。

- 输出当前目录树（后端相关）
- 输出当前命令入口矩阵（本地/CI/部署）
- 输出风险清单与迁移批次计划

验收：

- 无文件改动
- 基线命令记录齐全

## Phase 1 - 入口最小迁移（小改）

目标：建立 `backend/manage.py` 主入口，同时保留根目录兼容入口（过渡期）。

建议改动：

- 新增 `backend/manage.py`
- 根目录 `manage.py` 改为兼容 shim（仅转发）
- 核对 `asgi.py` / `wsgi.py` / settings 导入路径

验收命令：

- `python manage.py check`
- `python manage.py test backend.tests`
- `cd frontend/web && npm run build`
- `cd backend && python manage.py check`
- `cd backend && python manage.py test backend.tests`

回滚：

- 恢复 `manage.py`
- 删除 `backend/manage.py`

## Phase 2 - CI 与脚本切换

目标：把自动化链路切到 `backend/` 入口。

建议改动：

- `.github/workflows/ci.yml` 后端步骤切换 `working-directory: backend`
- 文档中的后端命令改为 `cd backend && ...`
- 本地辅助脚本（如有）同步更新

验收命令：

- 本地完整质量门通过
- CI green（至少 1 次）

回滚：

- 恢复 CI 到根目录命令入口

## Phase 3 - 部署链路切换

目标：生产环境命令全部切到 `backend/` 入口。

建议改动：

- uWSGI/Gunicorn 启动命令与工作目录更新
- 发布脚本中 `manage.py` 命令路径更新
- Nginx/静态收集命令文档同步

验收命令（生产或预发）：

- `python manage.py check`（在 `backend/` 下）
- 应用健康检查通过（API 200、静态资源正常）

回滚：

- 一键回到上一个可用发布版本

## Phase 4 - 兼容层下线（可选，最后做）

目标：移除根目录 `manage.py` 兼容层（仅在全链路稳定后）。

前置条件：

- 连续 2-3 次发布未出现路径相关问题
- 文档、CI、部署、人工习惯已完全迁移

## 5. 每批通用质量门（强制）

每一个批次都必须跑：

1. `python manage.py check`
2. `python manage.py test backend.tests`
3. `cd frontend/web && npm run build`

如果切换到 `backend/` 入口后，再额外跑：

4. `cd backend && python manage.py check`
5. `cd backend && python manage.py test backend.tests`

## 6. 提交策略（强制）

- 每批只做一个子目标
- 每批单独 commit，message 必须写清“why”
- 不允许“混改”：路径迁移 PR 不得夹带业务逻辑改动
- 未通过质量门，不得进入下一批

## 7. 人工回归最小清单

- 登录 / 登出
- Trip 列表 / 详情
- AI 生成与保存
- Ralendar 关键路径
- 管理后台可访问（如启用）

## 8. Codex 执行要求（引用文档）

执行时必须同时遵循：

- `14_CODEX_EXECUTION_GUARDRAILS.md`

