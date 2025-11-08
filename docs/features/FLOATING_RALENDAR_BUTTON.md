# 🎯 悬浮 Ralendar 按钮功能说明

> **移动端专属** - 让旅行事项管理更便捷

---

## 📱 功能概述

在移动端旅行编辑页面，我们提供了一个**可拖拽的悬浮圆形按钮**，让用户随时随地管理旅行事项，无需滚动到页面底部。

### 设计灵感
- 🎵 酷狗音乐悬浮窗
- 💬 微信悬浮球
- 📱 iOS AssistiveTouch

---

## ✨ 核心功能

### 1. **悬浮按钮**
- 圆形设计，使用 Ralendar 官方 logo
- 渐变紫色背景 (`#667eea` → `#764ba2`)
- 默认位置：右下角
- 事项数量徽章（红色，显示待办事项数）

### 2. **自由拖拽**
- 👆 触摸/鼠标拖拽
- 🧲 自动吸附到屏幕左右边缘
- 💾 位置自动保存到 `localStorage`
- 🔄 下次打开恢复上次位置

### 3. **拖到垃圾桶隐藏**
- 拖拽时底部中央出现垃圾桶区域
- 接近垃圾桶时按钮变红并抖动
- 松手后按钮消失
- 隐藏状态保存到 `localStorage`

### 4. **点击展开面板**
- 点击按钮弹出底部面板（Bottom Sheet）
- 显示完整的事项管理界面
- 支持添加、编辑、删除事项
- 本地事项 + 云端事项双轨管理

### 5. **响应式设计**
- 📱 **移动端**（≤768px）：显示悬浮按钮
- 💻 **桌面端**（>768px）：显示右侧边栏（原设计）

---

## 🎨 视觉效果

### 按钮状态

| 状态 | 效果 |
|------|------|
| **默认** | 渐变紫色，轻微阴影 |
| **悬停** | 放大 1.1 倍，阴影加深 |
| **拖拽中** | 放大 1.15 倍，透明度 0.8 |
| **接近垃圾桶** | 变红色，抖动动画 |

### 事项徽章
```
事项数量 > 0  → 显示红色徽章
事项数量 > 99 → 显示 "99+"
事项数量 = 0  → 不显示徽章
```

### 垃圾桶区域
- 拖拽时从底部淡入
- 红色圆角矩形
- 垃圾桶图标 + "拖到这里隐藏"文字
- 接近时放大 1.2 倍

---

## 🔧 技术实现

### 组件结构
```
FloatingRalendarButton.vue
├── 悬浮按钮 (floating-btn)
│   ├── Ralendar Logo
│   └── 事项数量徽章
├── 垃圾桶区域 (trash-zone)
└── 事项面板 (events-panel)
    ├── 面板头部
    └── EventsSidebar 组件
```

### 核心逻辑

#### 1. 拖拽处理
```javascript
// 触摸事件（移动端）
handleTouchStart → 记录起始位置
handleTouchMove → 更新按钮位置，检测垃圾桶
handleTouchEnd → 吸附边缘或隐藏

// 鼠标事件（桌面端测试）
handleMouseDown → 添加全局监听
mousemove → 更新位置
mouseup → 清理监听
```

#### 2. 位置吸附
```javascript
snapToEdge() {
  // 限制在屏幕范围内
  // 判断左右半屏
  // 吸附到最近的边缘
  // 保存到 localStorage
}
```

#### 3. 垃圾桶检测
```javascript
checkNearTrash(x, y) {
  // 定义垃圾桶区域（底部中央）
  // 判断触摸点是否在区域内
  // 更新 isNearTrash 状态
}
```

#### 4. 状态持久化
```javascript
// 保存
localStorage.setItem('ralendar_button_position', JSON.stringify(position))
localStorage.setItem('ralendar_button_visible', 'true/false')

// 恢复
onMounted(() => {
  const savedPosition = localStorage.getItem('ralendar_button_position')
  const savedVisible = localStorage.getItem('ralendar_button_visible')
  // ...
})
```

---

## 📐 尺寸规范

| 元素 | 尺寸 |
|------|------|
| 悬浮按钮 | 60×60 px |
| Ralendar Logo | 40×40 px |
| 事项徽章 | 最小 20px 宽，高度自适应 |
| 垃圾桶区域 | 120×120 px |
| 屏幕边距 | 20 px |

---

## 🎯 用户交互流程

### 场景 1：首次使用
```
1. 进入旅行编辑页面
2. 看到右下角悬浮按钮（带 Ralendar logo）
3. 点击按钮 → 弹出事项面板
4. 添加/查看事项
5. 关闭面板
```

### 场景 2：调整位置
```
1. 长按按钮开始拖拽
2. 移动到舒适位置
3. 松手 → 自动吸附到边缘
4. 位置自动保存
```

### 场景 3：隐藏按钮
```
1. 长按按钮开始拖拽
2. 底部出现垃圾桶
3. 拖到垃圾桶区域 → 按钮变红抖动
4. 松手 → 按钮消失
5. 隐藏状态保存
```

### 场景 4：重新显示（未来功能）
```
1. 导航栏点击"召唤 Ralendar"
2. 按钮从右下角淡入
3. 可见状态保存
```

---

## 🔄 与桌面端的区别

| 特性 | 移动端 | 桌面端 |
|------|--------|--------|
| **显示方式** | 悬浮按钮 | 右侧边栏 |
| **位置** | 可拖拽 | 固定 |
| **展开方式** | 底部面板 | 直接显示 |
| **隐藏方式** | 拖到垃圾桶 | 不支持 |
| **持久化** | localStorage | 无需 |

---

## 📊 性能优化

### 1. 条件渲染
```vue
<!-- 仅移动端渲染 -->
<div v-if="isVisible && isMobile" class="floating-ralendar">
```

### 2. 事件节流
- 拖拽过程中不触发点击事件
- 使用 CSS `transition` 而非 JS 动画

### 3. 懒加载
- `EventsSidebar` 仅在面板打开时渲染
- 使用 `v-if` 而非 `v-show`

---

## 🐛 已知限制

1. **导航栏召唤功能**：暂未实现（需要全局状态管理）
2. **横屏适配**：需要调整垃圾桶位置
3. **iPad 适配**：需要根据实际尺寸优化

---

## 🚀 未来计划

- [ ] 导航栏"召唤 Ralendar"按钮
- [ ] 长按显示快捷菜单（快速添加事项）
- [ ] 双击快速打开最近事项
- [ ] 自定义按钮样式（主题色）
- [ ] 震动反馈（拖到垃圾桶时）
- [ ] 手势支持（上滑展开面板）

---

## 📝 代码位置

```
web/src/components/events/
├── FloatingRalendarButton.vue  # 悬浮按钮组件
├── EventsSidebar.vue           # 事项侧边栏
├── EventForm.vue               # 事项表单
└── EventItem.vue               # 事项列表项

web/src/views/
└── TripEditorView.vue          # 旅行编辑页面（集成）
```

---

## 🎨 设计资源

- **Ralendar Logo**: `/static/images/ralendar_logo_final.png`
- **颜色方案**:
  - 主色：`#667eea` → `#764ba2` (渐变)
  - 危险色：`#ff6b6b` → `#ee5a6f` (垃圾桶)
  - 徽章色：`#ff4757`

---

**最后更新**: 2025-11-08  
**版本**: 1.0  
**状态**: ✅ 已实现并部署

