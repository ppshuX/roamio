# M4 Frontend `<script setup>` Standard

> 状态：生效（从本文件合入后开始执行）  
> 目标：统一前端代码风格到 Vue 3 Composition API + `<script setup>`，降低后续重构与协作成本。

## 1. 适用范围

- 目录：`frontend/web/src/**`
- 新增 `.vue` 文件：必须使用 `<script setup>`
- 迁移中的旧文件：允许短期共存，但不得新增 Options API 代码

## 2. 强制规范（Must）

1. 组件脚本统一使用 `<script setup>`
2. 状态统一走 Pinia setup store（`defineStore(id, () => {})`）
3. 网络请求统一走 `src/api/api.js` 或 `src/api/streamApi.js`
4. 认证状态统一走 `useUserStore()`：
   - `accessToken` 在 Pinia 内存
   - `refreshToken` 仅 HttpOnly Cookie
5. 禁止在组件内直接操作认证 token 存储（`localStorage access_token/refresh_token`）
6. 禁止在组件内直接 `fetch('/api/...')`（特殊场景需在 PR 说明并评审）

## 3. 推荐规范（Should）

- 组合函数提取到 `src/composables/*`，避免超大组件继续膨胀
- 业务 API 分层：
  - `src/api/*.js`：请求封装
  - `views/components`：仅处理展示和交互
- 对外暴露统一命名：
  - 布尔状态：`isXxx` / `hasXxx`
  - 动作函数：`handleXxx` / `loadXxx` / `submitXxx`

## 4. 文件结构约定（组件内）

`<script setup>` 建议顺序：

1. imports
2. props / emits（`defineProps` / `defineEmits`）
3. store / router / route
4. refs / reactives
5. computed
6. watch / watchEffect
7. methods（业务动作）
8. lifecycle（`onMounted` 等）

## 5. 迁移策略（分批）

### Batch A（优先）
- `stores/*`
- `api/*`
- `router/*`

### Batch B（中优先）
- `views/auth/*`
- `views/user-center/*`

### Batch C（最后）
- 大型复杂组件（如 `components/events/GlobalSidebar.vue`）
- 已完成：`components/events/GlobalSidebar.vue` 已提取 composables 并迁移到 `<script setup>`
- 原则：先拆子组件，再迁 `<script setup>`

## 6. 提交门槛（每个迁移 PR 必须满足）

1. `python manage.py check` 通过
2. `python manage.py test backend.tests` 通过
3. `cd frontend/web && npm run build` 通过
4. PR 描述包含：
   - 本次迁移文件列表
   - 是否引入行为变化（默认不允许）
   - 回滚方式（恢复到迁移前 commit）

## 7. 禁止项（Do Not）

- 不做“全量一次性迁移”
- 不在同一个 PR 混入 UI 大改、接口改协议、样式体系切换（Tailwind/DaisyUI）等主题
- 不在迁移 `<script setup>` 时顺手重写业务逻辑

## 8. Definition of Done

前端完成标准化的判定条件：

1. 活跃模块（auth、trip、user-center、events）均完成 `<script setup>` 迁移
2. 新增组件 100% 使用 `<script setup>`
3. 认证链路无 localStorage token 依赖
4. API 调用收敛到 `src/api/*`
