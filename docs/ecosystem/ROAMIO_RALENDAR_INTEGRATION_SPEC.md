# 🤝 Roamio × Ralendar 集成对接文档

> **版本**: v1.0  
> **日期**: 2025-11-08  
> **目标**: 实现 Roamio 旅行事件与 Ralendar 日历系统的深度融合

---

## 📋 目录

- [1. 项目背景](#1-项目背景)
- [2. 集成目标](#2-集成目标)
- [3. 职责划分](#3-职责划分)
- [4. 数据流设计](#4-数据流设计)
- [5. API 接口规范](#5-api-接口规范)
- [6. 数据模型](#6-数据模型)
- [7. 认证方案](#7-认证方案)
- [8. 实施计划](#8-实施计划)
- [9. 测试用例](#9-测试用例)

---

## 1. 项目背景

### 1.1 Roamio 简介

**Roamio** 是一个旅行规划和分享平台，用户可以：
- 创建旅行计划
- 分享旅行故事
- 添加旅行事件（景点、餐厅、活动等）

### 1.2 Ralendar 简介

**Ralendar** 是一个智能日历和提醒系统，提供：
- 日历展示
- 地图导航（百度地图集成）
- 邮件/系统提醒
- 事件管理

### 1.3 集成需求

用户在 **Roamio** 中添加旅行事件时，如果设置了时间、地点或提醒，应该自动同步到 **Ralendar**，由 Ralendar 负责：
- 日历展示
- 地图导航
- 提醒任务调度
- 发送邮件/系统通知

---

## 2. 集成目标

### 2.1 用户体验目标

```
用户在 Roamio 添加事件
    ↓
填写：标题 + 地点 + 时间 + 提醒
    ↓
点击"保存"
    ↓
自动同步到 Ralendar
    ↓
Ralendar 自动：
  ✅ 生成地图链接
  ✅ 设置提醒任务
  ✅ 到时间后发送邮件/通知
    ↓
用户在 Roamio 点击"查看日历"或"导航"
    ↓
跳转到 Ralendar
    ↓
Ralendar 展示日历/打开地图
```

### 2.2 技术目标

- ✅ **数据互通**：Roamio 事件自动同步到 Ralendar
- ✅ **账号统一**：使用统一的用户体系（QQ UnionID 或内部 UID）
- ✅ **职责清晰**：Roamio 负责记录，Ralendar 负责提醒和地图
- ✅ **松耦合**：通过 RESTful API 通信，独立部署
- ✅ **高可用**：同步失败不影响 Roamio 主流程

---

## 3. 职责划分

### 3.1 Roamio 的职责

| 功能 | 说明 |
|------|------|
| **旅行内容管理** | 创建、编辑、删除旅行计划 |
| **事件信息记录** | 记录事件的标题、描述、时间、地点、提醒 |
| **用户界面展示** | 在旅行详情页显示事件列表 |
| **调用 Ralendar API** | 将事件数据同步到 Ralendar |
| **保存 ralendar_event_id** | 记录 Ralendar 返回的事件 ID，用于后续更新/删除 |
| **提供跳转链接** | "查看日历"、"导航" 按钮跳转到 Ralendar |

### 3.2 Ralendar 的职责

| 功能 | 说明 |
|------|------|
| **接收事件数据** | 提供 API 接收来自 Roamio 的事件数据 |
| **日历展示** | 在日历界面显示来自 Roamio 的事件 |
| **地图功能** | 集成百度地图，生成导航链接 |
| **提醒任务调度** | 使用 Celery + Redis 设置定时任务 |
| **发送邮件提醒** | 到时间后自动发送邮件 |
| **系统通知** | 推送浏览器通知或 App 通知 |
| **地图导航** | 提供地图页面，支持导航功能 |

---

## 4. 数据流设计

### 4.1 创建事件流程

```
┌─────────────────────────────────────────────────────────────┐
│  用户在 Roamio 添加事件                                      │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Roamio 后端                                                 │
├─────────────────────────────────────────────────────────────┤
│  1. 保存到 Roamio 数据库（trips_event 表）                  │
│  2. 如果有时间/地点/提醒 → 调用 Ralendar API               │
│     POST /api/v1/events/                                    │
│     Body: {                                                 │
│       title, description, start_time,                       │
│       location: { name, address, lat, lng },                │
│       reminder: { enabled, time, method },                  │
│       source_app: 'roamio',                                 │
│       source_id: '123',                                     │
│       roamio_trip_id: 456                                   │
│     }                                                       │
│  3. 保存 Ralendar 返回的 event_id                           │
└─────────────────────────────────────────────────────────────┘
    ↓
    📡 HTTP POST
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Ralendar 后端                                               │
├─────────────────────────────────────────────────────────────┤
│  1. 接收事件数据                                             │
│  2. 保存到 Ralendar 数据库（ralendar_event 表）             │
│  3. 如果有地点 → 生成百度地图链接                           │
│     baidu_map_url = generate_map_url(lat, lng)              │
│  4. 如果有提醒 → 设置 Celery 定时任务                       │
│     schedule_reminder(event_id, reminder_time)              │
│  5. 返回响应：                                               │
│     {                                                       │
│       id: 789,                                              │
│       baidu_map_url: 'https://...',                         │
│       reminder_scheduled: true                              │
│     }                                                       │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Ralendar 定时任务（到提醒时间时）                           │
├─────────────────────────────────────────────────────────────┤
│  Celery Task: send_event_reminder(event_id)                │
│  1. 查询事件信息                                             │
│  2. 如果 reminder_method == 'email'                         │
│     → 发送邮件到用户邮箱                                     │
│  3. 如果 reminder_method == 'system'                        │
│     → 推送系统通知                                           │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 更新事件流程

```
Roamio 更新事件
    ↓
PUT /api/v1/events/{ralendar_event_id}/
    ↓
Ralendar 更新数据库
    ↓
如果提醒时间变化 → 更新定时任务
```

### 4.3 删除事件流程

```
Roamio 删除事件
    ↓
DELETE /api/v1/events/{ralendar_event_id}/
    ↓
Ralendar 删除数据库记录
    ↓
取消定时任务
```

---

## 5. API 接口规范

### 5.1 认证方式

**推荐方案：API Key + JWT Token**

```http
Authorization: Bearer {JWT_TOKEN}
X-API-Key: {ROAMIO_API_KEY}
```

- `JWT_TOKEN`: 用户身份认证（共享 SECRET_KEY）
- `API_KEY`: 应用身份认证（Roamio 专用密钥）

### 5.2 创建事件

**请求**

```http
POST /api/v1/events/
Content-Type: application/json
Authorization: Bearer {JWT_TOKEN}
X-API-Key: {ROAMIO_API_KEY}

{
  "title": "参观故宫",
  "description": "上午参观故宫博物院，了解历史文化",
  "start_time": "2025-12-01T09:00:00+08:00",
  "end_time": "2025-12-01T12:00:00+08:00",
  "location": {
    "name": "故宫博物院",
    "address": "北京市东城区景山前街4号",
    "lat": 39.916527,
    "lng": 116.397026
  },
  "reminder": {
    "enabled": true,
    "time": "2025-12-01T08:30:00+08:00",
    "method": "email"
  },
  "source_app": "roamio",
  "source_id": "123",
  "roamio_trip_id": 456,
  "roamio_user_id": 789
}
```

**响应**

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": 999,
  "title": "参观故宫",
  "start_time": "2025-12-01T09:00:00+08:00",
  "location": {
    "name": "故宫博物院",
    "address": "北京市东城区景山前街4号",
    "lat": 39.916527,
    "lng": 116.397026
  },
  "baidu_map_url": "https://api.map.baidu.com/marker?location=39.916527,116.397026&title=故宫博物院&content=北京市东城区景山前街4号&output=html",
  "reminder": {
    "enabled": true,
    "time": "2025-12-01T08:30:00+08:00",
    "method": "email",
    "scheduled": true
  },
  "source_app": "roamio",
  "source_id": "123",
  "created_at": "2025-11-08T10:00:00+08:00"
}
```

### 5.3 更新事件

**请求**

```http
PUT /api/v1/events/{id}/
Content-Type: application/json
Authorization: Bearer {JWT_TOKEN}
X-API-Key: {ROAMIO_API_KEY}

{
  "title": "参观故宫（更新）",
  "start_time": "2025-12-01T10:00:00+08:00",
  "reminder": {
    "enabled": true,
    "time": "2025-12-01T09:30:00+08:00",
    "method": "email"
  }
}
```

**响应**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 999,
  "title": "参观故宫（更新）",
  "start_time": "2025-12-01T10:00:00+08:00",
  "reminder": {
    "enabled": true,
    "time": "2025-12-01T09:30:00+08:00",
    "method": "email",
    "scheduled": true
  },
  "updated_at": "2025-11-08T11:00:00+08:00"
}
```

### 5.4 删除事件

**请求**

```http
DELETE /api/v1/events/{id}/
Authorization: Bearer {JWT_TOKEN}
X-API-Key: {ROAMIO_API_KEY}
```

**响应**

```http
HTTP/1.1 204 No Content
```

### 5.5 查询事件（可选）

**请求**

```http
GET /api/v1/events/?source_app=roamio&source_id=123
Authorization: Bearer {JWT_TOKEN}
```

**响应**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "count": 1,
  "results": [
    {
      "id": 999,
      "title": "参观故宫",
      "start_time": "2025-12-01T09:00:00+08:00",
      "baidu_map_url": "https://...",
      "reminder": {
        "enabled": true,
        "scheduled": true
      }
    }
  ]
}
```

---

## 6. 数据模型

### 6.1 Roamio 数据模型

```python
# backend/models/event.py

class TripEvent(models.Model):
    """旅行事件模型"""
    
    # 基础字段
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # 时间字段
    event_time = models.DateTimeField(null=True, blank=True)
    
    # 地点字段
    location_name = models.CharField(max_length=200, blank=True)
    location_address = models.CharField(max_length=500, blank=True)
    location_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    # 提醒字段
    reminder_enabled = models.BooleanField(default=False)
    reminder_time = models.DateTimeField(null=True, blank=True)
    reminder_method = models.CharField(max_length=20, choices=[('email', '邮件'), ('system', '系统通知')])
    
    # Ralendar 同步
    synced_to_ralendar = models.BooleanField(default=False)
    ralendar_event_id = models.IntegerField(null=True, blank=True)  # 关键字段
    
    # 来源标记
    source_app = models.CharField(max_length=50, default='roamio')
```

### 6.2 Ralendar 数据模型（需要实现）

```python
# ralendar/models/event.py

class Event(models.Model):
    """日历事件模型"""
    
    # 基础字段
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # 时间字段
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    
    # 地点字段
    location_name = models.CharField(max_length=200, blank=True)
    location_address = models.CharField(max_length=500, blank=True)
    location_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    baidu_map_url = models.URLField(blank=True)  # Ralendar 生成
    
    # 提醒字段
    reminder_enabled = models.BooleanField(default=False)
    reminder_time = models.DateTimeField(null=True, blank=True)
    reminder_method = models.CharField(max_length=20, choices=[('email', '邮件'), ('system', '系统通知')])
    reminder_scheduled = models.BooleanField(default=False)  # 是否已设置定时任务
    
    # 来源标记（重要）
    source_app = models.CharField(max_length=50, default='ralendar')  # 'roamio', 'ralendar', 'rote'
    source_id = models.CharField(max_length=100, blank=True)  # Roamio 中的事件 ID
    roamio_trip_id = models.IntegerField(null=True, blank=True)  # 关联的旅行 ID
    roamio_user_id = models.IntegerField(null=True, blank=True)  # Roamio 用户 ID
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

---

## 7. 认证方案

### 7.1 统一账号体系

**方案：内部 UID 绑定**

```python
# backend/models/user_profile.py

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # 统一 UID（生态系统内部唯一标识）
    ecosystem_uid = models.CharField(max_length=100, unique=True)
    
    # QQ 登录信息
    qq_openid = models.CharField(max_length=100, blank=True, unique=True)
    qq_unionid = models.CharField(max_length=100, blank=True)
```

**登录流程**：

```
用户在 Roamio 用 QQ 登录
    ↓
Roamio 生成 ecosystem_uid = f'roamio_{user.id}_{timestamp}'
    ↓
生成 JWT Token（包含 ecosystem_uid）
    ↓
用户在 Ralendar 用 QQ 登录
    ↓
Ralendar 根据 QQ openid 查找 ecosystem_uid
    ↓
如果找不到 → 调用 Roamio API 查询
    ↓
绑定 ecosystem_uid
    ↓
生成 JWT Token（相同的 ecosystem_uid）
```

### 7.2 JWT Token 共享

**关键配置**：

```python
# roamio/settings.py 和 ralendar/settings.py

# 统一的密钥（必须相同）
SECRET_KEY = os.getenv('ECOSYSTEM_SECRET_KEY', 'roamio-ecosystem-unified-2025')

# JWT 配置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'SIGNING_KEY': SECRET_KEY,  # 使用统一密钥
    'ALGORITHM': 'HS256',
}
```

### 7.3 API Key 配置

**Roamio 配置**：

```python
# roamio/settings.py

RALENDAR_API_URL = os.getenv('RALENDAR_API_URL', 'https://ralendar.com/api/v1')
RALENDAR_API_KEY = os.getenv('RALENDAR_API_KEY', 'roamio-api-key-2025')
```

**Ralendar 配置**：

```python
# ralendar/settings.py

# 允许的 API Key（可以支持多个应用）
ALLOWED_API_KEYS = {
    'roamio-api-key-2025': 'Roamio',
    'rote-api-key-2025': 'Rote',
}

# 中间件验证
class APIKeyMiddleware:
    def __call__(self, request):
        api_key = request.headers.get('X-API-Key')
        if api_key not in ALLOWED_API_KEYS:
            return JsonResponse({'error': 'Invalid API Key'}, status=403)
```

---

## 8. 实施计划

### 8.1 Phase 1: Ralendar 基础 API（1-2 周）

**任务**：

- [ ] 创建 `Event` 模型（包含 `source_app`, `source_id` 等字段）
- [ ] 实现 `EventViewSet`（CRUD API）
- [ ] 实现 API Key 认证中间件
- [ ] 实现 JWT Token 验证（共享 SECRET_KEY）
- [ ] 编写 API 文档

**验收标准**：

- ✅ 可以通过 API 创建、更新、删除事件
- ✅ API Key 认证正常
- ✅ JWT Token 验证正常

### 8.2 Phase 2: 地图功能（1 周）

**任务**：

- [ ] 申请百度地图 AK
- [ ] 实现 `generate_baidu_map_url()` 方法
- [ ] 创建地图页面 `/map?event_id={id}`
- [ ] 支持移动端跳转百度地图 App

**验收标准**：

- ✅ 创建事件时自动生成 `baidu_map_url`
- ✅ 地图页面可以正常显示
- ✅ 移动端可以跳转到百度地图 App

### 8.3 Phase 3: 提醒功能（1-2 周）

**任务**：

- [ ] 配置 Celery + Redis
- [ ] 实现 `schedule_reminder()` 方法
- [ ] 实现 `send_event_reminder` Celery 任务
- [ ] 配置邮件服务（腾讯云 SES 或 SendGrid）
- [ ] 实现系统通知（可选）

**验收标准**：

- ✅ 创建事件时自动设置定时任务
- ✅ 到时间后自动发送邮件
- ✅ 邮件内容包含事件详情和跳转链接

### 8.4 Phase 4: 日历展示（1 周）

**任务**：

- [ ] 创建日历页面 `/calendar`
- [ ] 支持按月/周/日查看
- [ ] 显示来自 Roamio 的事件（标记来源）
- [ ] 支持点击事件查看详情

**验收标准**：

- ✅ 日历页面可以正常显示
- ✅ 来自 Roamio 的事件有特殊标记
- ✅ 点击事件可以跳转到 Roamio 旅行详情

### 8.5 Phase 5: 统一账号（1 周）

**任务**：

- [ ] 修改 `UserProfile` 模型，添加 `ecosystem_uid`
- [ ] 修改 QQ 登录逻辑，生成/查询 `ecosystem_uid`
- [ ] 实现跨项目用户查询 API
- [ ] 测试账号互通

**验收标准**：

- ✅ 用户在 Roamio 和 Ralendar 登录后是同一个账号
- ✅ JWT Token 可以在两个项目间互通

---

## 9. 测试用例

### 9.1 创建事件测试

**测试场景 1：完整事件（有时间、地点、提醒）**

```bash
curl -X POST https://ralendar.com/api/v1/events/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {JWT_TOKEN}" \
  -H "X-API-Key: roamio-api-key-2025" \
  -d '{
    "title": "参观故宫",
    "start_time": "2025-12-01T09:00:00+08:00",
    "location": {
      "name": "故宫博物院",
      "lat": 39.916527,
      "lng": 116.397026
    },
    "reminder": {
      "enabled": true,
      "time": "2025-12-01T08:30:00+08:00",
      "method": "email"
    },
    "source_app": "roamio",
    "source_id": "123"
  }'
```

**预期结果**：

- ✅ 返回 201 Created
- ✅ 响应包含 `id`, `baidu_map_url`, `reminder.scheduled: true`
- ✅ 数据库中创建了事件记录
- ✅ Celery 中创建了定时任务

**测试场景 2：仅标题（无时间、地点、提醒）**

```bash
curl -X POST https://ralendar.com/api/v1/events/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {JWT_TOKEN}" \
  -H "X-API-Key: roamio-api-key-2025" \
  -d '{
    "title": "购买纪念品",
    "source_app": "roamio",
    "source_id": "124"
  }'
```

**预期结果**：

- ✅ 返回 201 Created
- ✅ `baidu_map_url` 为空
- ✅ `reminder.scheduled: false`

### 9.2 更新事件测试

**测试场景：修改提醒时间**

```bash
curl -X PUT https://ralendar.com/api/v1/events/999/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {JWT_TOKEN}" \
  -H "X-API-Key: roamio-api-key-2025" \
  -d '{
    "reminder": {
      "enabled": true,
      "time": "2025-12-01T09:00:00+08:00",
      "method": "email"
    }
  }'
```

**预期结果**：

- ✅ 返回 200 OK
- ✅ 数据库中更新了提醒时间
- ✅ Celery 定时任务已更新

### 9.3 删除事件测试

```bash
curl -X DELETE https://ralendar.com/api/v1/events/999/ \
  -H "Authorization: Bearer {JWT_TOKEN}" \
  -H "X-API-Key: roamio-api-key-2025"
```

**预期结果**：

- ✅ 返回 204 No Content
- ✅ 数据库中删除了事件记录
- ✅ Celery 定时任务已取消

### 9.4 提醒发送测试

**测试场景：到达提醒时间**

1. 创建事件，提醒时间设为 1 分钟后
2. 等待 1 分钟
3. 检查邮箱

**预期结果**：

- ✅ 收到邮件
- ✅ 邮件标题：`旅行提醒：参观故宫`
- ✅ 邮件内容包含事件详情和跳转链接

---

## 10. 错误处理

### 10.1 同步失败处理

**场景**：Ralendar API 调用失败

**Roamio 处理**：

```python
try:
    result = service.create_event(event)
    if result:
        event.synced_to_ralendar = True
        event.ralendar_event_id = result['id']
        event.save()
except Exception as e:
    # 记录日志，但不影响主流程
    logger.error(f'同步到 Ralendar 失败: {e}')
    # 用户仍然可以在 Roamio 中看到事件
    # 只是没有日历和提醒功能
```

### 10.2 提醒发送失败处理

**场景**：邮件发送失败

**Ralendar 处理**：

```python
@shared_task(bind=True, max_retries=3)
def send_event_reminder(self, event_id):
    try:
        event = Event.objects.get(id=event_id)
        send_mail(...)
    except Exception as e:
        # 重试 3 次
        raise self.retry(exc=e, countdown=60)  # 1 分钟后重试
```

---

## 11. 安全考虑

### 11.1 API Key 保护

- ✅ API Key 存储在环境变量中，不提交到 Git
- ✅ 使用 HTTPS 加密传输
- ✅ 定期更换 API Key

### 11.2 用户数据保护

- ✅ JWT Token 验证用户身份
- ✅ 只能操作自己的事件
- ✅ 敏感信息（邮箱）不在 API 响应中暴露

### 11.3 限流

- ✅ 每个 API Key 每分钟最多 60 次请求
- ✅ 超过限制返回 429 Too Many Requests

---

## 12. 监控与日志

### 12.1 监控指标

- ✅ API 调用成功率
- ✅ 同步失败次数
- ✅ 提醒发送成功率
- ✅ API 响应时间

### 12.2 日志记录

```python
# Roamio
logger.info(f'同步事件到 Ralendar: event_id={event.id}')
logger.error(f'同步失败: {e}')

# Ralendar
logger.info(f'接收到来自 Roamio 的事件: source_id={data["source_id"]}')
logger.info(f'提醒已发送: event_id={event.id}, user={event.user.email}')
```

---

## 13. 联系方式

### Roamio 团队

- **项目负责人**: [您的名字]
- **技术负责人**: [技术负责人]
- **邮箱**: dev@roamio.com
- **文档**: https://roamio.com/docs/api

### Ralendar 团队

- **项目负责人**: [待填写]
- **技术负责人**: [待填写]
- **邮箱**: [待填写]
- **文档**: [待填写]

---

## 14. 附录

### 14.1 完整的数据流图

```
┌─────────────────────────────────────────────────────────────┐
│                        Roamio 前端                           │
│  用户添加事件 → 填写表单 → 点击保存                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                        Roamio 后端                           │
│  1. 保存到数据库                                             │
│  2. 调用 Ralendar API                                       │
└─────────────────────────────────────────────────────────────┘
                          ↓ HTTP POST
┌─────────────────────────────────────────────────────────────┐
│                       Ralendar 后端                          │
│  1. 验证 API Key + JWT Token                                │
│  2. 保存到数据库                                             │
│  3. 生成地图链接                                             │
│  4. 设置提醒任务                                             │
│  5. 返回响应                                                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                      Celery 定时任务                         │
│  到提醒时间 → 发送邮件/系统通知                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                          用户                                │
│  收到邮件 → 点击链接 → 跳转到 Ralendar/Roamio              │
└─────────────────────────────────────────────────────────────┘
```

### 14.2 环境变量配置示例

**Roamio `.env`**:

```bash
# Ralendar 集成
RALENDAR_API_URL=https://ralendar.com/api/v1
RALENDAR_API_KEY=roamio-api-key-2025

# 统一密钥
ECOSYSTEM_SECRET_KEY=roamio-ecosystem-unified-2025
```

**Ralendar `.env`**:

```bash
# 统一密钥（必须与 Roamio 相同）
ECOSYSTEM_SECRET_KEY=roamio-ecosystem-unified-2025

# 百度地图
BAIDU_MAP_AK=your-baidu-map-ak

# 邮件服务
EMAIL_HOST=smtp.qq.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@ralendar.com
EMAIL_HOST_PASSWORD=your-password

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

---

**文档版本**: v1.0  
**最后更新**: 2025-11-08  
**维护者**: Roamio 开发团队

---

**祝 Roamio × Ralendar 集成顺利！** 🚀✨


