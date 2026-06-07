# Roamio 前端主题规范（Bootstrap 5.3）

> **状态**：生效（自合入起，Codex / 人类实现须遵守）  
> **目标**：去掉「默认 AI 紫」视觉（`#667eea` / `#764ba2` 及同类渐变），统一到**克制、偏自然/旅行向**的调色；**不改**交互、路由、接口与业务逻辑。  
> **栈约束**：运行时 UI 以 **Bootstrap 5.3** 为主（`main.js` 已全量引入）；**不得**在本任务中把页面改写为 Tailwind 原子类或 DaisyUI 组件范式（仓库内若存在未接入的 tailwind/daisy 依赖，视为无关，禁止借机双栈混写）。

---

## 1. 设计原则（Must）

1. **主色单一来源**：所有「品牌主色、链色、主按钮、原先紫系边框/字色」必须能追溯到 **`roamio-theme.css` 中 §2 定义的 token（及 §2 中与 Bootstrap 对齐的变量覆盖）**，禁止在组件内继续手写新的紫/靛青品牌色。
2. **禁止标志性紫蓝渐变条**：全站 **不得** 再使用 `linear-gradient(135deg, #667eea … #764ba2 …)` 或视觉等价的紫→紫渐变作为主顶栏/侧栏/大块背景。
3. **渐变少用、且低调**：若保留渐变，仅允许 **同色系、低对比**（例如主色到略深主色，透明度或明度差 ≤ 15%）；**禁止**高饱和双色对角渐变作为大面积背景。
4. **语义色保留**：成功/警告/危险/信息（绿、黄、红、蓝灰）若已用于**具体语义**（预算、等级、状态），可不调或仅做对比度微调；**不要把语义块强制改成主色绿**。
5. **对比度**：正文与背景 WCAG 粗略目标 **≥ 4.5:1**；主按钮文字与按钮底色的对比须清晰可读。

---

## 2. Token（规范色值）

下列为 **Roamio Theme v1** 推荐值；实现时写入 **`frontend/web/src/styles/roamio-theme.css`**（新建）的 `:root`，并供全站引用。

| Token | 含义 | Hex | 说明 |
|-------|------|-----|------|
| `--roamio-primary` | 主色 | `#0f766e` | 深青绿，旅行/自然向，替代原紫主色 |
| `--roamio-primary-hover` | 主色悬停 | `#0d9488` | 可略亮于主色用于 hover |
| `--roamio-primary-active` | 主色按下 | `#115e59` | 略深 |
| `--roamio-primary-muted` | 弱背景 | `#ecfdf5` | 极浅绿底，替代 `#e0e7ff` 类冷紫浅底 |
| `--roamio-accent` | 点缀（少用） | `#b45309` | 琥珀强调，仅小面积标签/提醒，**不可替代主色铺满** |

**与 Bootstrap 对齐（Must）**：在同一文件内覆盖 Bootstrap 5.3 变量，使 `btn-primary`、`text-primary`、链接默认色跟主色走，例如：

```css
:root {
  --bs-primary: #0f766e;
  --bs-primary-rgb: 15, 118, 110;
  --bs-link-color: #0f766e;
  --bs-link-hover-color: #115e59;
}
```

（若需 `btn-outline-primary`、focus ring 一致，可顺带设置 `--bs-focus-ring-color` 等与主色协调的变量。）

---

## 3. 工程落地（Must）

1. **新建** `frontend/web/src/styles/roamio-theme.css`，内容包含 §2 变量 + Bootstrap 覆盖。
2. **入口**：在 `frontend/web/src/main.js` 中，于 `bootstrap.min.css` **之后** 增加一行：  
   `import './styles/roamio-theme.css'`
3. **组件改造**：将各 `.vue` / 内联样式中的  
   - `#667eea`、`#764ba2`、`#5568d3`、`#6a3f91`  
   - `rgba(102, 126, 234, …)`、`rgba(118, 75, 162, …)`  
   替换为 **`var(--roamio-primary)`** 等语义 token，或直接使用 Bootstrap 工具类（如 `bg-primary`、`text-primary`、`btn-primary`）若场景匹配。
4. **`linear-gradient(135deg, #667eea … #764ba2 …)`**：一律删除或改为 **纯色** `background: var(--roamio-primary)`；侧栏/顶栏若需层次，可用 **极浅** `--roamio-primary-muted` 铺底 + 顶区纯色条，勿恢复紫渐变。
5. **`frontend/web/src/config/api.js` 中 `DEFAULT_AVATAR_SVG`**：占位圆填充色中的 `%23667eea` 须改为与主色等价的 URL 编码 hex（如 `#0f766e` → `%230f766e`）。
6. **不计入「品牌紫」的渐变**（默认保留，除非对比度明显问题）：如 TripProgress 绿条、TripHighlights/TripTips 米色暖块、UserProfileCard 等与**等级/语义**绑定的多色条——仅当与新技术债冲突时再个案处理。

---

## 4. 分阶段范围（建议 PR 切分）

### Batch A — 壳层与用户第一印象（优先）

- `src/components/NavBar.vue`
- `src/components/Footer.vue`
- `src/components/events/GlobalSidebar.vue`
- `src/App.vue`（若有全局背景色）
- `src/views/auth/LoginView.vue`、`RegisterView.vue`、`ForgotPasswordView.vue`、`QQCallbackView.vue`、`RalendarCallback.vue`

### Batch B — 编辑器与行程主路径

- `TripEditorView.vue`、`TripListView.vue`、`MyTripsView.vue`
- `components/editor/*`、`components/trip/TripActionButtons.vue`、`TripItinerary.vue`、`TripBasicInfo.vue`
- `components/ai/TripGenerator.vue`、`TripGeneratorSimple.vue`
- `components/map/MapPicker.vue`

### Batch C — 其余紫系残留

- 对其余 `rg` 命中文件扫尾（评论、日历、天气、用户中心等与 §5 清单一致）。

Codex 可实现为 **单 PR（推荐一次收干净）** 或 **A → B → C 三个 PR**；每批须独立通过验收。

---

## 5. 已知紫系命中清单（扫尾用）

以下路径在基线中曾出现 `#667eea` / `#764ba2` 或同色渐变（实现后应清零或仅剩 §6 例外）：

- `components/NavBar.vue`、`Footer.vue`
- `components/events/GlobalSidebar.vue`、`components/editor/EditorSidebar.vue`、`ContentEditor.vue`、`BasicInfoEditor.vue`、`ModuleSelector.vue`
- `views/auth/*`（登录注册忘记密码与 OAuth 回调）
- `views/TripEditorView.vue`、`TripListView.vue`、`MyTripsView.vue`、`user-center/UserCenterView.vue` 等
- `components/calendar/*`、`components/comments/*`、`components/map/MapPicker.vue`、`components/ai/*`、`components/WeatherWidget.vue`、`components/UserProfilePopover.vue`、`components/ralendar/RalendarAccountManager.vue`
- `config/api.js`

（以合入前 `rg "667eea|764ba2"` 在 `frontend/web/src` 结果为检。）

---

## 6. 例外与禁止

**例外**：

- 第三方品牌色（如 QQ 图标固有配色）保持原样。
- 明确 **错误/成功** 语义红绿色块不做「统一刷成主色」。

**禁止**：

- 引入 Tailwind 类名替代 Bootstrap 布局/组件作为本任务主手段。
- 修改任何 `props` / `emit` / `vue-router` / Pinia / `src/api` 调用契约。
- 不得刻意引入新字体 CDN 依赖（可继续使用系统字体栈）。

---

## 7. 验收（Must）

1. `cd frontend/web && npm run build` 成功。
2. `cd frontend/web && npm run lint` 若项目已配置且无既有债务扩大；**不得**为压 lint 关闭规则掩盖错误。
3. **主题扫除**（在 `frontend/web/src` 下）：  
   `667eea` / `764ba2` / `5568d3` / `6a3f91` **零命中**（§6 例外除外；`api.js` SVG 已更新）。  
   允许保留 **非品牌** 渐变（如灰阶、绿进度条、米色提示块）只要不含上述 hex。
4. **人工抽检**：顶栏、登录页、行程列表/编辑入口、GlobalSidebar 打开态无紫蓝对角渐变主条。

---

## 8. 提交说明建议

- `style(frontend): roamio bootstrap theme v1 (replace legacy purple brand)`  
或分批：`style(frontend): theme shell (navbar, auth, sidebar)`

---

## 9. Codex 执行摘要（复制块）

1. 新建 `roamio-theme.css`，定义 §2 token + §3 Bootstrap 覆盖；`main.js` 在 bootstrap 后 import。  
2. 按 §5 全局替换旧紫与紫渐变；顶栏/侧栏/主 CTA 优先。  
3. 更新 `DEFAULT_AVATAR_SVG` 填充色。  
4. 跑 §7 验收；PR 描述附 `rg` 前后说明或截图一句。

---

**修订**：主题重大变更时递增版本号于本文标题下（如 v2）并保留上一版 token 表于 git 历史即可。
