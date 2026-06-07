# Codex Execution Guardrails (Backend Relocation)

> 状态：生效（用于约束 Codex 执行大重构）  
> 适用任务：`13_BACKEND_RELOCATION_MASTER_PLAN.md`

## 1. 执行模式（先计划，后改动）

Codex 必须按以下流程执行：

1. **Step A - 只读分析**：先阅读代码与文档，输出本批计划，不改文件
2. **Step B - 等待批准**：只有收到“批准本批”才允许修改文件
3. **Step C - 实施与验证**：按批准范围修改并运行质量门
4. **Step D - 报告结果**：汇报改动、验证结果、风险、回滚点

## 2. 本次任务允许改动路径

- `backend/**`
- `roamio/**`（仅当与 Django 启动配置直接相关）
- `.github/workflows/**`
- `docs/remediation/**`
- 根目录 `manage.py`（仅用于过渡兼容）

## 3. 禁止改动（硬禁止）

- 禁止改动业务逻辑（auth/trip/ai/ralendar 功能语义）
- 禁止改动数据库模型与迁移文件
- 禁止改动前端业务代码（`frontend/web/src/**`）
- 禁止改动 `.env` 或任何密钥配置值
- 禁止做全仓库大范围替换
- 禁止未经批准删除文件

## 4. 批次大小限制

- 每批最多修改 **8 个文件**
- 每批只完成 **1 个明确目标**
- 如果超范围，必须拆成下一批并先征求批准

## 5. 强制质量门

每批改完必须执行并汇报：

1. `python manage.py check`
2. `python manage.py test backend.tests`
3. `cd frontend/web && npm run build`

如果该批引入 `backend/` 命令入口，还必须追加：

4. `cd backend && python manage.py check`
5. `cd backend && python manage.py test backend.tests`

## 6. Git 行为限制

- 未经明确指令：**不得 commit**
- 未经明确指令：**不得 push**
- 禁止使用破坏性 git 命令（`reset --hard`、`checkout --`、force push）

## 7. 输出模板（每批结束必须按此格式）

### 批次目标

- （一句话说明本批目标）

### 修改文件

- `path/a`
- `path/b`

### 实际改动

- （3-6 条关键变更）

### 质量门结果

- `python manage.py check`: PASS/FAIL
- `python manage.py test backend.tests`: PASS/FAIL
- `frontend build`: PASS/FAIL
- `backend/check`: PASS/FAIL（如适用）
- `backend/test`: PASS/FAIL（如适用）

### 风险与回滚

- 风险：
- 回滚步骤：

## 8. 失败停止条件

出现以下任一情况，必须停止并请求人工确认：

- 需要改动未授权路径
- 质量门失败且原因不明确
- 出现与当前批次无关的大量连锁修改
- 需要改动生产部署关键配置但无明确确认

## 9. 可直接给 Codex 的最小指令

```text
执行 backend 下沉重构，但必须严格遵循 docs/remediation/13_BACKEND_RELOCATION_MASTER_PLAN.md 与 docs/remediation/14_CODEX_EXECUTION_GUARDRAILS.md。
先做只读分析并输出“本批计划+修改文件列表+风险”，不要改文件。
只有我回复“批准本批”后，才允许实施。
每批最多改 8 个文件、只做 1 个目标。
每批必须跑并汇报 check/test/build，未经我明确允许不得 commit 或 push。
```

