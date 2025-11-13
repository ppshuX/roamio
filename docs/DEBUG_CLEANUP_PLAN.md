# 🧹 调试信息清理计划

**目标**：清理不必要的调试代码，保留有用的错误处理和日志

**状态**：待执行（进入稳定期后逐步清理）

---

## 📊 调试信息统计

### 前端（web/src）
- **console.log**：79 处（24 个文件）
- **console.error**：部分保留（错误处理）
- **console.warn**：部分保留（警告信息）

### 后端（backend）
- **print()**：6 处（3 个文件）
- **logger.debug**：部分保留
- **临时注释**：待清理

---

## 🎯 清理策略

### 应该删除的
- ❌ 调试用的 `console.log('变量值：', xxx)`
- ❌ 临时的 `console.log('到这里了')`
- ❌ 开发时的 `debugger` 语句
- ❌ 已废弃的注释代码

### 应该保留的
- ✅ 错误处理：`console.error('API 请求失败:', error)`
- ✅ 关键警告：`console.warn('天气API限流')`
- ✅ 后端日志：`logger.info()`, `logger.error()`
- ✅ 重要注释和文档

---

## 📋 待清理文件列表

### 高优先级（频繁访问的页面）
1. `web/src/views/TripDetailView.vue`（10 处）
2. `web/src/views/TripEditorView.vue`（6 处）
3. `web/src/views/MyTripsView.vue`（5 处）
4. `web/src/views/user-center/UserCenterView.vue`（10 处）

### 中优先级（工具组件）
5. `web/src/utils/localEventStorage.js`（13 处）
6. `web/src/components/ai/TripGenerator.vue`（2 处）
7. `web/src/components/events/GlobalSidebar.vue`（3 处）

### 低优先级（其他组件）
8. 其他组件的零散 console.log

---

## 🔧 清理步骤

### 阶段 1：保留有用日志，删除调试信息
```javascript
// 删除这种
console.log('trip data:', trip)

// 保留这种
console.error('加载旅行失败:', error)

// 改为这种
if (import.meta.env.MODE === 'development') {
  console.log('Debug:', data)
}
```

### 阶段 2：统一日志格式
```javascript
// 统一前缀
console.error('[TripDetail] 加载失败:', error)
console.warn('[API] 请求超时')
```

### 阶段 3：后端日志优化
```python
# 删除 print()
print('用户登录:', user)

# 改为 logger
logger.info(f'用户登录: {user.username}')
```

---

## 📝 执行时间表

### 本周（2025-11-13 - 2025-11-17）
- [ ] 清理核心页面的调试信息
- [ ] 统一错误日志格式

### 下周（2025-11-18 - 2025-11-24）
- [ ] 清理组件的调试信息
- [ ] 添加开发模式条件判断

### 月底前（2025-11-30）
- [ ] 完成所有调试信息清理
- [ ] 代码审查和优化

---

## ✅ 验收标准

### 清理完成标准
1. 生产环境浏览器控制台无无用 log
2. 保留所有必要的错误处理
3. 后端日志使用 logging 模块
4. 代码通过 ESLint 检查

---

## 🔍 检测命令

### 前端调试信息检测
```bash
# 查找所有 console.log
grep -r "console\.log" web/src --include="*.vue" --include="*.js"

# 查找所有 debugger
grep -r "debugger" web/src --include="*.vue" --include="*.js"
```

### 后端调试信息检测
```bash
# 查找所有 print()
grep -r "print(" backend --include="*.py"
```

---

**此清理计划将在稳定期逐步执行，确保代码质量和可维护性。**

