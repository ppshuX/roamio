# 🚀 Roamio v2.0 下一步计划

> **日期**: 2025-11-08  
> **当前状态**: Phase 1 完成，等待 Ralendar 团队响应

---

## 📊 当前进度

```
✅ Phase 1: 后端基础（100%）
   ├─ ✅ 数据库模型设计
   ├─ ✅ API 接口实现
   ├─ ✅ 序列化器实现
   └─ ✅ 管理后台配置

⏸️  等待 Ralendar 团队完成 API

⏳ Phase 2: 前端组件（0%）
   ├─ ⏳ 本地存储工具类
   ├─ ⏳ 事件表单组件
   ├─ ⏳ 事项列表组件
   └─ ⏳ 集成到旅行详情页
```

---

## 🎯 两条并行路线

### **路线 A：独立开发（推荐）** ⭐

**不等待 Ralendar，先完成 Roamio 前端**

#### 优势
- ✅ Roamio 可以独立运行
- ✅ 用户可以先使用基础功能
- ✅ 后续对接 Ralendar 更灵活

#### 任务清单

**Week 1: 前端基础组件**

- [ ] **Day 1-2**: 本地存储工具类 + 事件表单（基础版）
  ```
  创建文件：
  - web/src/utils/localEventStorage.js
  - web/src/components/events/EventForm.vue
  - web/src/api/events.js
  ```

- [ ] **Day 3-4**: 事件表单（完整版）+ 事项列表
  ```
  创建文件：
  - web/src/components/events/EventFormEnhanced.vue（3步骤）
  - web/src/components/events/EventsSidebar.vue
  - web/src/components/events/EventItem.vue
  ```

- [ ] **Day 5-6**: 集成到旅行详情页
  ```
  修改文件：
  - web/src/views/TripDetailView.vue
  ```

- [ ] **Day 7**: 测试 + 优化
  ```
  - 功能测试
  - 移动端适配
  - 性能优化
  ```

**里程碑**：
- ✅ 用户可以在旅行详情页添加事件
- ✅ 游客可以添加本地事项（localStorage）
- ✅ 登录用户可以添加云端事项（API）
- ✅ 双轨制界面展示

**预览效果**：

```
┌─────────────────────────────────────────────────────────┐
│  旅行详情页                                              │
├──────────────────────┬──────────────────────────────────┤
│                      │  📋 事项管理                     │
│  旅行内容            │  ┌────────────────────────────┐ │
│                      │  │  ➕ 添加事件               │ │
│  • 描述              │  └────────────────────────────┘ │
│  • 照片              │                                  │
│  • 故事              │  📍 参观故宫                     │
│                      │  ⏰ 12月1日 09:00                │
│                      │  🔔 已设置提醒                   │
│                      │  [编辑] [删除]                   │
│                      │  （同步到 Ralendar 后显示导航）  │
└──────────────────────┴──────────────────────────────────┘
```

---

### **路线 B：等待 Ralendar（不推荐）** ⏸️

**等待 Ralendar 完成 API 后再开发前端**

#### 劣势
- ❌ Roamio 进度被阻塞
- ❌ 用户看不到进展
- ❌ 时间浪费

#### 时间成本
- Ralendar 开发时间：2-4 周
- Roamio 等待时间：2-4 周
- **总损失**：2-4 周

---

## 📋 详细任务拆解（路线 A）

### Task 1: 本地存储工具类（4 小时）

**文件**: `web/src/utils/localEventStorage.js`

```javascript
export class LocalEventStorage {
  static KEY = 'roamio_local_events'
  
  // 获取所有本地事项
  static getAll() { ... }
  
  // 获取指定旅行的事项
  static getByTripId(tripId) { ... }
  
  // 添加事项
  static add(event) { ... }
  
  // 更新事项
  static update(eventId, updates) { ... }
  
  // 删除事项
  static delete(eventId) { ... }
  
  // 批量转移到云端后清理
  static deleteByIds(eventIds) { ... }
}
```

**验收标准**：
- ✅ 可以保存/读取/更新/删除本地事项
- ✅ 数据格式统一
- ✅ 错误处理完善

---

### Task 2: API 封装（2 小时）

**文件**: `web/src/api/events.js`

```javascript
import request from './request'

// 获取事件列表
export const getEvents = (tripId) => {
  return request.get(`/trip-plans/${tripId}/events/`)
}

// 创建事件
export const createEvent = (tripId, data) => {
  return request.post(`/trip-plans/${tripId}/events/`, data)
}

// 更新事件
export const updateEvent = (tripId, eventId, data) => {
  return request.put(`/trip-plans/${tripId}/events/${eventId}/`, data)
}

// 删除事件
export const deleteEvent = (tripId, eventId) => {
  return request.delete(`/trip-plans/${tripId}/events/${eventId}/`)
}

// 批量导入本地事项
export const batchCreateFromLocal = (tripId, events) => {
  return request.post(`/trip-plans/${tripId}/events/batch_create_from_local/`, {
    events
  })
}

// 切换完成状态
export const toggleComplete = (tripId, eventId) => {
  return request.post(`/trip-plans/${tripId}/events/${eventId}/toggle_complete/`)
}
```

---

### Task 3: 事件表单组件（基础版）（8 小时）

**文件**: `web/src/components/events/EventForm.vue`

**功能**：
- ✅ 标题输入（必填）
- ✅ 描述输入（选填）
- ✅ 时间选择（选填）
- ✅ 地点输入（选填，暂时文本输入）
- ✅ 保存到本地/云端按钮

**界面**：

```
┌─────────────────────────────────────┐
│  添加事件                            │
├─────────────────────────────────────┤
│  事件标题 *                          │
│  [                              ]   │
│                                     │
│  事件描述                            │
│  [                              ]   │
│  [                              ]   │
│                                     │
│  事件时间                            │
│  [2025-12-01  09:00            ]   │
│                                     │
│  地点（暂时文本输入）                │
│  [故宫博物院                    ]   │
│                                     │
│  [保存到本地] [保存到云端]          │
└─────────────────────────────────────┘
```

---

### Task 4: 事件表单组件（增强版）（12 小时）

**文件**: `web/src/components/events/EventFormEnhanced.vue`

**功能**：
- ✅ 3 步骤流程（基本信息 → 地点选择 → 时间提醒）
- ✅ 地图选点（预留接口，暂时文本输入）
- ✅ 提醒设置（提前时间、提醒方式）
- ✅ 智能提示（有时间 → 提示会同步到日历）

**界面**：

```
┌─────────────────────────────────────┐
│  添加事件                            │
├─────────────────────────────────────┤
│  ① 基本信息  ② 地点  ③ 时间提醒    │
│  ─────────   ─────   ─────────      │
│                                     │
│  步骤 1: 基本信息                    │
│                                     │
│  事件标题 *                          │
│  [参观故宫                      ]   │
│                                     │
│  事件描述                            │
│  [上午参观故宫博物院            ]   │
│                                     │
│  [下一步：选择地点]                 │
└─────────────────────────────────────┘
```

---

### Task 5: 事项列表组件（8 小时）

**文件**: 
- `web/src/components/events/EventsSidebar.vue`
- `web/src/components/events/EventItem.vue`

**功能**：
- ✅ 显示本地事项列表
- ✅ 显示云端事项列表（登录后）
- ✅ 支持编辑、删除操作
- ✅ 支持本地 ↔ 云端转移
- ✅ 空状态提示

**界面**：

```
┌─────────────────────────────────────┐
│  事项管理                   [+ 添加] │
├─────────────────────────────────────┤
│  💻 本地事项 (2)                     │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ 📍 参观故宫                   │ │
│  │ ⏰ 12月1日 09:00              │ │
│  │ [拉到云端] [编辑] [删除]     │ │
│  └───────────────────────────────┘ │
│                                     │
│  ☁️ 云端事项 (3)                     │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ 📍 品尝烤鸭                   │ │
│  │ ⏰ 12月1日 18:00              │ │
│  │ 🔔 已设置提醒                 │ │
│  │ [编辑] [删除]                 │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

### Task 6: 集成到旅行详情页（8 小时）

**文件**: `web/src/views/TripDetailView.vue`

**修改内容**：

```vue
<template>
  <div class="trip-detail-view">
    <div class="container">
      <div class="row">
        <!-- 左侧：旅行内容 -->
        <div class="col-lg-8">
          <TripHeader :trip="trip" />
          <TripContent :trip="trip" />
          <CommentSection :trip-id="tripId" />
        </div>
        
        <!-- 右侧：事项管理栏（新增） -->
        <div class="col-lg-4">
          <EventsSidebar :trip-id="tripId" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import EventsSidebar from '@/components/events/EventsSidebar.vue'
// ...
</script>
```

**响应式设计**：
- PC 端：左右分栏（8:4）
- 移动端：上下排列，事项栏可折叠

---

## 🎯 验收标准

### Phase 2 完成标准

- [ ] **功能完整性**
  - ✅ 用户可以在旅行详情页看到事项栏
  - ✅ 游客可以添加本地事项
  - ✅ 登录用户可以添加云端事项
  - ✅ 可以编辑、删除事项
  - ✅ 本地事项可以转移到云端

- [ ] **用户体验**
  - ✅ 界面美观，符合 Roamio 设计风格
  - ✅ 操作流畅，无明显卡顿
  - ✅ 移动端体验良好
  - ✅ 错误提示友好

- [ ] **代码质量**
  - ✅ 代码规范，通过 ESLint 检查
  - ✅ 组件拆分合理，单一职责
  - ✅ 关键功能有注释

---

## 🚀 Ralendar 集成时间表

### 等待 Ralendar 完成（预计 2-4 周）

**Ralendar 需要完成的任务**：

1. **Phase 1: 基础 API**（1-2 周）
   - [ ] 创建 Event 模型
   - [ ] 实现 CRUD API
   - [ ] API Key 认证
   - [ ] JWT Token 验证

2. **Phase 2: 地图功能**（1 周）
   - [ ] 申请百度地图 AK
   - [ ] 生成地图链接
   - [ ] 创建地图页面

3. **Phase 3: 提醒功能**（1-2 周）
   - [ ] 配置 Celery + Redis
   - [ ] 实现提醒任务调度
   - [ ] 发送邮件提醒

### Roamio 对接（1 周）

**Ralendar 完成后，Roamio 需要做的**：

- [ ] **Day 1-2**: 实现 Ralendar 同步服务
  ```
  创建文件：
  - backend/utils/ralendar_sync.py
  ```

- [ ] **Day 3-4**: 更新前端，显示同步状态
  ```
  修改文件：
  - web/src/components/events/EventItem.vue
  添加：
  - "查看日历" 按钮（跳转到 Ralendar）
  - "导航" 按钮（跳转到 Ralendar）
  ```

- [ ] **Day 5-6**: 测试数据互通
  ```
  测试场景：
  - 在 Roamio 创建事件 → Ralendar 收到
  - 在 Roamio 更新事件 → Ralendar 更新
  - 在 Roamio 删除事件 → Ralendar 删除
  - 提醒时间到 → 收到邮件
  ```

- [ ] **Day 7**: 上线

---

## 📚 文档清单

### 已完成的文档

- ✅ **技术方案**: `ROAMIO_V2_TECHNICAL_PLAN.md`
- ✅ **实施优先级**: `ROAMIO_V2_IMPLEMENTATION_PRIORITY.md`
- ✅ **进度报告**: `ROAMIO_V2_PROGRESS_REPORT.md`
- ✅ **集成对接文档**: `ROAMIO_RALENDAR_INTEGRATION_SPEC.md`（给 Ralendar 团队）
- ✅ **下一步计划**: `ROAMIO_V2_NEXT_STEPS.md`（本文档）

### 待创建的文档

- ⏳ **前端组件文档**: `FRONTEND_COMPONENTS_GUIDE.md`
- ⏳ **API 使用文档**: `API_USAGE_GUIDE.md`
- ⏳ **测试文档**: `TESTING_GUIDE.md`

---

## 💡 建议

### 给 Roamio 团队

**推荐：立即开始路线 A（独立开发）** ⭐

**理由**：
1. ✅ 不依赖 Ralendar，可以立即开始
2. ✅ 用户可以先使用基础功能
3. ✅ 后续对接更灵活
4. ✅ 节省 2-4 周等待时间

**时间安排**：
```
Week 1: 前端组件开发
Week 2: 测试 + 优化
Week 3-4: 等待 Ralendar（期间可以做其他功能）
Week 5: Ralendar 对接
Week 6: 上线
```

### 给 Ralendar 团队

**文档已发送**：`ROAMIO_RALENDAR_INTEGRATION_SPEC.md`

**关键信息**：
- ✅ API 接口规范
- ✅ 数据模型设计
- ✅ 认证方案
- ✅ 测试用例

**请优先完成**：
1. Phase 1: 基础 API（最重要）
2. Phase 3: 提醒功能（核心功能）
3. Phase 2: 地图功能（可以后续优化）

---

## 🎉 总结

**当前状态**：
- ✅ Roamio 后端 100% 完成
- ✅ 集成文档已发送给 Ralendar 团队
- ⏳ 等待 Ralendar 响应

**下一步**：
- 🚀 **立即开始前端组件开发**（推荐）
- ⏸️ 或等待 Ralendar 完成 API（不推荐）

**预计完成时间**：
- 前端组件：1 周
- Ralendar 对接：1 周（Ralendar 完成后）
- **总计**：2 周（不含 Ralendar 开发时间）

---

**Bro，准备好开始前端开发了吗？** 🚀😊

**我建议立即开始，不要等待！** 💪✨


