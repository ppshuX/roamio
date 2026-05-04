# 目录重构、Vite 迁移与未来整改指南

> 文档性质：未来工程整改的执行指南。  
> 更新时间：2026-05-04  
> 适用范围：仓库布局、前端构建链、Django 静态资源消费方式、PR 切分和 Codex 执行边界。  
> 不替代：[01_PROBLEM_INVENTORY.md](01_PROBLEM_INVENTORY.md)、[02_REMEDIATION_PLAN.md](02_REMEDIATION_PLAN.md)、[03_ROADMAP.md](03_ROADMAP.md)。安全与 settings 细节见 [05_SECURITY_CLEANUP.md](05_SECURITY_CLEANUP.md)、[07_SETTINGS_SPLIT.md](07_SETTINGS_SPLIT.md)。

## 0. 当前基线

在开始本指南的目录/Vite 改造前，必须先确认当前瘦身基线已经可审查、可回滚。

当前已完成或进行中的前置工作：

- 敏感文档与冗余历史文档已做两轮清理。
- Django settings 已从单文件拆为 `roamio/settings/{base,dev,prod}.py`。
- 默认本地运行使用 dev settings，`python manage.py check` 已通过。
- 前端仍是 Vue CLI，当前源码目录为 `frontend/web/`。
- 当前仓库仍提交根目录 `web/dist` 构建产物；是否继续提交构建产物尚未最终确认。
- PR-A 已采用过渡策略：`frontend/web` 构建时仍输出到根目录 `web/dist`，让 Django 现有静态入口继续可用。
- Django 业务 app 当前仍叫 `backend`，不得在目录迁移中顺手改名。

开始后续整改前，建议先把当前瘦身结果作为一个独立检查点保存。继续叠加目录迁移和 Vite 会显著增加 diff 审查成本。

## 1. 结论

目标方向合理，但必须分阶段做。

| 事项 | 判断 |
| --- | --- |
| 顶层拆成 `backend/` + `frontend/` | 合理，职责更清楚。 |
| Vue CLI 迁移到 Vite | 合理，Vue 3 项目继续维护时值得做。 |
| 前端构建输出到 `backend/web_dist/` | 合理，但必须和 Django、Nginx、部署策略一致。 |
| Django 项目包改为 `config/` | 合理，但应放在后期独立阶段。 |
| Django 业务 app `backend` 改名为 `api` 或 `core` | 第一阶段禁止做，风险最高。 |

## 2. 总目标

最终结构建议如下：

```text
<repo-root>/
  README.md
  .env.example
  docs/
    remediation/

  frontend/
    web/
      index.html
      vite.config.js
      package.json
      public/
      src/

  backend/
    manage.py
    config/
      settings/
        __init__.py
        base.py
        dev.py
        prod.py
      urls.py
      wsgi.py
      asgi.py
      api_docs_config.py

    backend/              # 业务 Django app，第一阶段仍保留当前 app 名
      migrations/
      models/
      api/
      views/
      utils/

    static/
    web_dist/
    media/

  templates/
  scripts/
```

说明：

- `backend/backend/` 这个路径虽然名字重复，但它保留了 Django app 名，避免触发迁移表、ContentType、权限和外键字符串风险。
- 如果后续强烈希望把业务 app 改名为 `api` 或 `core`，必须作为独立里程碑处理，不能和本指南的目录/Vite 迁移混在一起。

## 3. 非目标

本指南不要求一次完成以下事项：

- 不重写业务逻辑。
- 不微服务化。
- 不顺手重构认证、Trip、评论、AI、Ralendar 等业务边界。
- 不在未确认部署链路前删除或忽略构建产物。
- 不在目录/Vite 改造中混入密钥轮换、脱敏、安全大扫。
- 不执行 Django app rename。

## 4. 阶段路线

严格按以下顺序执行。每一阶段都应能单独审查、单独回滚。

### PR-A：只移动前端目录（已完成）

目标：`web/` -> `frontend/web/`，仍然使用 Vue CLI。

允许改动：

- 移动 `web/` 到 `frontend/web/`。
- 修正 README、脚本、文档中的前端路径。
- 保持 `package.json` 和 Vue CLI。
- 过渡期让 Vue CLI 输出到根目录 `web/dist`，避免本阶段修改 Django 静态资源读取逻辑。

禁止改动：

- 不迁 Vite。
- 不改 Django settings。
- 不改 `STATICFILES_DIRS`。
- 不改构建产物提交策略。

验收：

```powershell
cd frontend/web
npm run build
```

```powershell
cd <repo-root>
python manage.py check
```

### PR-B：Vue CLI 迁移到 Vite

目标：`frontend/web/` 使用 Vite，构建输出到约定目录。

允许改动：

- 新增 `vite.config.js`。
- 将 `index.html` 放到 `frontend/web/` 根目录。
- 使用 `@vitejs/plugin-vue`。
- 保留 `@` -> `src` alias。
- 检查并迁移 `process.env` / `VUE_APP_*` 到 `import.meta.env.VITE_*`。
- 配置 dev proxy，使本地 API 调用行为与当前开发方式一致。
- 配置 `build.outDir`。推荐最终目标是 `../../backend/web_dist`。

禁止改动：

- 不移动 `manage.py`。
- 不移动 `roamio/` 项目包。
- 不改业务 API 行为。
- 不删除旧 `web/dist` 兼容策略，除非部署链路已经确认。

验收：

```powershell
cd frontend/web
npm run dev
```

```powershell
cd frontend/web
npm run build
```

构建后应能看到：

```text
backend/web_dist/index.html
```

### PR-C：Django 消费 `web_dist`

目标：Django 的静态文件和 SPA fallback 消费 Vite 构建产物。

允许改动：

- 更新 `STATICFILES_DIRS`，加入 `backend/web_dist`。
- 更新 SPA 入口视图，使 `/` 和 history fallback 指向 `web_dist/index.html`。
- 过渡期可保留旧 `web/dist` fallback，直到部署策略确认。
- 更新部署文档中的静态资源路径。

禁止改动：

- 不移动 Django 项目根。
- 不改 app 名。
- 不删除旧 dist 提交策略，除非已确认部署方式。

验收：

```powershell
python manage.py check
python manage.py runserver
```

本地打开：

```text
http://localhost:8000/
```

应能加载 SPA。

### PR-D：移动 Django 根目录与项目配置包

目标：将 Django 运行根迁到 `backend/`，项目配置包迁到 `backend/config/`。

允许改动：

- `manage.py` 移到 `backend/manage.py`。
- `roamio/` 项目包迁到 `backend/config/`，或团队明确决定保留 `backend/roamio/`。
- 更新 `DJANGO_SETTINGS_MODULE`。
- 更新 `ROOT_URLCONF`、`WSGI_APPLICATION`、`ASGI_APPLICATION`。
- 更新 `api_docs_config` import。
- 更新 README、脚本、部署文档中的工作目录。

禁止改动：

- 不改业务 app 名。
- 不改数据库迁移语义。
- 不混入 Vite 迁移之外的新业务重构。

验收：

```powershell
cd backend
python manage.py check
python manage.py test
python manage.py runserver
```

### PR-E：可选的 Django 业务 app rename

默认不做。

只有满足以下条件时才允许启动：

- 已有 staging 数据库。
- 已有数据库备份。
- 已输出迁移影响分析。
- 已覆盖 `django_migrations`、`django_content_type`、权限表、外键字符串、`AUTH_USER_MODEL`、历史 migration import。
- staging 全量 migrate 和核心冒烟通过。

## 5. 三处路径必须一致

一旦选择 Vite 构建输出目录，以下三处必须一致：

1. Vite：`build.outDir`。
2. Django：`STATICFILES_DIRS` 或 SPA 入口视图读取目录。
3. Nginx/部署：静态目录和 `index.html` 所在目录。

推荐目标：

```text
frontend/web -> build.outDir -> ../../backend/web_dist
Django -> backend/web_dist
Nginx -> backend/web_dist
```

## 6. `web_dist` 是否提交 Git

必须先确认部署方式。

方案 1：不提交构建产物。

- `backend/web_dist/` 加入 `.gitignore`。
- CI 或服务器部署时执行前端 build。
- 推荐长期方案，但需要部署链路支持。

方案 2：继续提交构建产物。

- 不 ignore `backend/web_dist/`。
- 接受每次前端 build 带来较大 diff。
- 如果当前服务器依赖 `git pull` 后直接获得静态文件，短期应选择此方案。

在确认前，不要删除旧 `web/dist` 相关策略。

## 7. Vite 迁移检查清单

工程：

- [ ] Node 版本写入 README，建议 18 或 20 LTS。
- [ ] 安装 `vite` 与 `@vitejs/plugin-vue`。
- [ ] `frontend/web/index.html` 包含 `<div id="app">`。
- [ ] `frontend/web/index.html` 使用 `<script type="module" src="/src/main.js">`。
- [ ] `vite.config.js` 配置 `@` alias。
- [ ] dev proxy 与当前 API 调用方式一致。
- [ ] `build.outDir` 指向约定目录。

环境变量：

- [ ] 搜索 `VUE_APP_`。
- [ ] 搜索 `process.env`。
- [ ] 迁移到 `import.meta.env.VITE_*`。
- [ ] 新增 `frontend/web/.env.example`，只放占位符。
- [ ] 确认真实 `.env` 被 `.gitignore`。

依赖与资源：

- [ ] Bootstrap CSS/JS 在 Vite 下可正常导入。
- [ ] 确认没有 jQuery 运行时依赖。
- [ ] 搜索 Webpack `require()`。
- [ ] 动态资源改为 `import` 或 `new URL(..., import.meta.url)`。
- [ ] 检查 `public/` 资源路径。

Django：

- [ ] `STATICFILES_DIRS` 包含 `web_dist`。
- [ ] SPA fallback 指向 Vite `index.html`。
- [ ] 本地 `runserver` 能加载 SPA。

## 8. 每阶段必须记录的结果

每个阶段完成后，在 PR 描述或整改文档中记录：

- 改了哪些目录。
- 改了哪些入口命令。
- `python manage.py check` 结果。
- `npm run build` 结果。
- 是否触碰构建产物提交策略。
- 是否触碰 settings、密钥、脱敏。
- 已知警告和未解决风险。

## 9. 停止条件

出现以下情况时，应停止继续叠加改动：

- `python manage.py check` 失败且不是明显依赖缺失。
- `npm run build` 失败且原因涉及资源路径或路由。
- SPA 在本地无法加载。
- 需要决定是否删除 `web/dist` 或 ignore `web_dist`，但部署方式未确认。
- 任何改动需要重命名 Django app。
- 任何改动需要触碰真实密钥、生产配置或服务器部署脚本。

## 10. 回滚策略

- PR-A 回滚：恢复 `web/` 目录位置和文档路径。
- PR-B 回滚：恢复 Vue CLI 的 `package.json`、`vue.config.js`、`public/index.html`、构建输出路径。
- PR-C 回滚：恢复 Django 对旧 `web/dist` 的读取逻辑。
- PR-D 回滚：恢复仓库根 `manage.py`、`roamio/` 项目包和 `DJANGO_SETTINGS_MODULE`。
- PR-E 回滚：必须依赖数据库备份和迁移回滚方案，不能只靠 Git revert。

## 11. Codex 执行边界

给 Codex 的执行指令应使用以下口径：

```text
严格按 docs/remediation/10_RESTRUCTURE_VITE_CODEX_SPEC.md 的阶段执行。
默认只做当前阶段，不提前做后续阶段。
默认不执行 Django app rename。
settings、密钥、脱敏、安全清理不得与目录/Vite 改造混在同一批改动。
每阶段必须给出 python manage.py check 与 npm run build 的结果。
```

## 12. 推荐下一步

PR-A 完成并验证通过后，下一步才进入 PR-B：

```text
Vue CLI -> Vite
构建输出从过渡的 web/dist 迁到 backend/web_dist
不改 Django
不改 dist 策略
```

PR-B 仍不得移动 `manage.py` 或重命名 Django app。
