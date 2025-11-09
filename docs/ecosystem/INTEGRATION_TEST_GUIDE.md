# 🧪 Roamio × Ralendar 集成测试指南

> **测试时间**: 2025-11-09 10:00 开始  
> **状态**: ⏳ 等待 Ralendar 团队部署

---

## ⚠️ **重要提醒**

### **当前状态**：

| 系统 | 部署状态 | 说明 |
|------|---------|------|
| **Roamio** | ✅ 已完成 | 所有代码已推送并部署 |
| **Ralendar** | ⏳ 等待中 | 计划 11-09 上午 09:00 部署 |

### **为什么现在测试会失败？**

```
错误: 401 Unauthorized

原因:
1. Ralendar 服务器还没有部署最新代码
2. Ralendar 的 SECRET_KEY 可能还没有更新
3. Ralendar 的 UnionID 功能还没有上线
4. Ralendar 的数据库迁移还没有执行

结论: 等 Ralendar 团队明天上午部署后再测试！
```

---

## 📋 **测试前检查清单**

### **Roamio 侧**（已完成 ✅）

- [x] SECRET_KEY 配置为与 Ralendar 相同
- [x] QQ OAuth 添加 `unionid=1` 参数（3 个位置）
- [x] UnionID 字段已添加到数据库
- [x] Ralendar API 客户端已实现
- [x] 前端"添加到 Ralendar"按钮已集成
- [x] 侧边栏"添加待办"功能已实现
- [x] 代码已推送到 GitHub
- [x] 服务器已部署最新代码

### **Ralendar 侧**（等待中 ⏳）

- [ ] 部署最新代码（包含 UnionID 支持）
- [ ] 执行数据库迁移（添加 unionid 字段）
- [ ] 配置 SECRET_KEY（与 Roamio 相同）
- [ ] 重启服务
- [ ] 验证 API 端点可用

---

## 🧪 **测试场景**

### **场景 1: Token 互认测试**

**目标**: 验证 Roamio 的 Token 可以访问 Ralendar API

**步骤**:
```bash
# 1. 在 Roamio 登录
# 2. 打开浏览器控制台（F12）
localStorage.getItem('access_token')

# 3. 复制 Token，然后测试 Ralendar API
curl -X GET https://app7626.acapp.acwing.com.cn/api/v1/events/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 预期结果:
# ✅ 返回 200（不是 401）
# ✅ 返回 JSON 数据（可能是空列表）
```

**如果失败**:
- 检查 SECRET_KEY 是否完全一致
- 检查 Ralendar 是否已重启服务

---

### **场景 2: 侧边栏创建事件**

**目标**: 在 Roamio 侧边栏中创建事件，同步到 Ralendar

**步骤**:
```
1. 登录 Roamio
2. 点击导航栏 "Ralendar"
3. 右侧滑出侧边栏
4. 点击 "添加待办"
5. 填写表单:
   - 标题: 测试事件
   - 描述: 这是一个测试
   - 时间: 2025-11-20 10:00
6. 点击 "创建"
7. 预期: 显示"创建成功！"
```

**验证**:
```bash
# 在 Ralendar 数据库中查询
SELECT id, title, start_time, source_app 
FROM api_event 
WHERE source_app='roamio' 
ORDER BY id DESC 
LIMIT 1;

# 预期: 看到刚才创建的事件
```

---

### **场景 3: 旅行计划批量同步**

**目标**: 将旅行计划的多个行程同步到 Ralendar

**步骤**:
```
1. 登录 Roamio
2. 打开一个旅行详情页（例如: /trip/xiamen-trip/）
3. 点击 "添加到 Ralendar" 按钮
4. 确认对话框
5. 预期: 显示"成功添加 N 个事件到日历"
```

**验证**:
```bash
# 在 Ralendar 数据库中查询
SELECT id, title, start_time, source_app, related_trip_slug 
FROM api_event 
WHERE related_trip_slug='xiamen-trip' 
ORDER BY id;

# 预期: 看到该旅行的所有行程事件
```

---

### **场景 4: UnionID 用户识别**

**目标**: 确认同一个 QQ 用户在两边被识别为同一用户

**步骤**:
```bash
# 1. 用 QQ 登录 Roamio
# 2. 查看 Roamio 数据库
SELECT user_id, uid, unionid 
FROM backend_socialaccount 
WHERE provider='qq' 
ORDER BY id DESC 
LIMIT 1;

# 3. 用同一个 QQ 登录 Ralendar
# 4. 查看 Ralendar 数据库
SELECT user_id, openid, unionid 
FROM api_qquser 
ORDER BY id DESC 
LIMIT 1;

# 5. 对比 unionid 值
# 预期: 完全相同 ✅
```

---

## 🐛 **常见问题排查**

### **问题 1: 401 Unauthorized**

**可能原因**:
- SECRET_KEY 不一致
- Token 格式错误
- Ralendar 服务未重启

**解决方案**:
```bash
# 1. 检查 Roamio 的 SECRET_KEY
cd ~/roamio
grep SECRET_KEY cloud_settings/.env

# 2. 检查 Ralendar 的 SECRET_KEY
cd ~/kotlin_calendar/backend
grep SECRET_KEY .env

# 3. 确保完全一致（逐字符对比）
# 4. 重启两边的服务
```

---

### **问题 2: 404 Not Found**

**可能原因**:
- API 端点路径错误
- Ralendar 的路由配置问题

**解决方案**:
```bash
# 检查 Ralendar 的 URL 配置
cd ~/kotlin_calendar/backend
python manage.py show_urls | grep events
```

---

### **问题 3: CORS 错误**

**可能原因**:
- 前端直接调用 Ralendar API（不应该）
- 应该通过 Roamio 后端代理

**解决方案**:
- 确保前端调用的是 `/api/v1/ralendar/...`（Roamio 后端）
- 不要直接调用 `https://app7626.acapp.acwing.com.cn/...`

---

## 📊 **测试数据示例**

### **创建单个事件**

```json
POST /api/v1/ralendar/trips/events/

{
  "title": "测试待办",
  "description": "这是一个测试事件",
  "start_time": "2025-11-20T10:00:00+08:00"
}

后端自动添加:
{
  "source_app": "roamio"
}
```

### **批量创建事件（旅行计划）**

```json
POST /api/v1/ralendar/trips/xiamen-trip/add-to-calendar/

{
  "events": [
    {
      "title": "厦门五日游 - Day 1: 抵达厦门",
      "description": "14:00 抵达厦门高崎国际机场，入住酒店",
      "start_time": "2025-11-15T14:00:00+08:00",
      "end_time": "2025-11-15T18:00:00+08:00",
      "location": "厦门高崎国际机场",
      "latitude": 24.5440,
      "longitude": 118.1278,
      "email_reminder": true
    },
    {
      "title": "厦门五日游 - Day 2: 鼓浪屿",
      "description": "09:00 游览鼓浪屿，参观日光岩、菽庄花园",
      "start_time": "2025-11-16T09:00:00+08:00",
      "end_time": "2025-11-16T17:00:00+08:00",
      "location": "鼓浪屿",
      "latitude": 24.4472,
      "longitude": 118.0656,
      "email_reminder": true
    }
  ]
}

后端自动添加:
{
  "source_app": "roamio",
  "related_trip_slug": "xiamen-trip"
}
```

---

## 🎯 **成功标准**

### **✅ Token 互认成功**:
- Roamio 的 Token 可以访问 Ralendar API
- 返回 200（不是 401）

### **✅ 事件创建成功**:
- 前端显示"创建成功"
- Ralendar 数据库中有对应记录
- `source_app = 'roamio'`

### **✅ UnionID 识别成功**:
- 同一个 QQ 用户在两边的 unionid 相同
- 事件归属到正确的用户

---

## 📞 **联系方式**

### **Ralendar 团队**:
- QQ: 2064747320
- 服务器: app7626.acapp.acwing.com.cn

### **测试时间**:
- 2025-11-09 10:00 - 12:00
- 2025-11-09 14:00 - 16:00

---

## 🚀 **准备就绪！**

**Roamio 侧所有代码已完成！**

等待 Ralendar 团队部署后，我们就可以开始联调测试了！

---

**Roamio 团队**  
**2025-11-09 10:30**

