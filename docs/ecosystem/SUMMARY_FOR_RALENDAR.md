# 📨 Roamio × Ralendar 集成需求（给 Ralendar 团队）

> **发送日期**: 2025-11-08  
> **发送方**: Roamio 开发团队  
> **接收方**: Ralendar 开发团队

---

## 👋 Hi Ralendar 团队！

我们是 **Roamio**（旅行规划平台）开发团队。我们计划与 **Ralendar**（日历提醒系统）深度融合，打造一个完整的旅行生态系统！🌍✨

---

## 🎯 我们想实现什么？

### 用户体验

```
用户在 Roamio 添加旅行事件
    ↓
填写：标题 + 地点 + 时间 + 提醒
    ↓
点击"保存"
    ↓
自动同步到 Ralendar
    ↓
Ralendar 自动：
  ✅ 在日历中显示
  ✅ 生成地图导航链接
  ✅ 到时间后发送邮件/通知
    ↓
用户在 Roamio 点击"查看日历"或"导航"
    ↓
跳转到 Ralendar
```

---

## 🤝 职责划分

### Roamio 负责

- ✅ 旅行内容管理
- ✅ 事件信息记录
- ✅ 调用 Ralendar API
- ✅ 提供用户界面

### Ralendar 负责（需要你们实现）

- ✅ 接收事件数据（API）
- ✅ 日历展示
- ✅ 地图导航（百度地图）
- ✅ 提醒任务调度（Celery）
- ✅ 发送邮件/系统通知

---

## 📋 需要 Ralendar 实现的功能

### 1. 事件 API（最重要）⭐⭐⭐

**创建事件**

```http
POST /api/v1/events/
Content-Type: application/json
Authorization: Bearer {JWT_TOKEN}
X-API-Key: roamio-api-key-2025

{
  "title": "参观故宫",
  "start_time": "2025-12-01T09:00:00+08:00",
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
  "source_id": "123"
}
```

**响应**

```json
{
  "id": 999,
  "baidu_map_url": "https://api.map.baidu.com/...",
  "reminder_scheduled": true
}
```

**其他接口**

- `PUT /api/v1/events/{id}/` - 更新事件
- `DELETE /api/v1/events/{id}/` - 删除事件

### 2. 地图功能 ⭐⭐

- 接收地点信息（名称、地址、坐标）
- 生成百度地图链接
- 提供地图页面 `/map?event_id={id}`

### 3. 提醒功能 ⭐⭐⭐

- 接收提醒设置（时间、方式）
- 使用 Celery + Redis 设置定时任务
- 到时间后发送邮件或系统通知

### 4. 日历展示 ⭐

- 在日历中显示来自 Roamio 的事件
- 标记来源（显示 "来自 Roamio"）
- 支持点击跳转到 Roamio

---

## 🔑 认证方案

### 统一账号

**使用统一的 SECRET_KEY 生成 JWT Token**

```python
# roamio/settings.py 和 ralendar/settings.py
SECRET_KEY = 'roamio-ecosystem-unified-2025'  # 必须相同
```

### API Key

**Roamio 调用 Ralendar API 时使用**

```http
X-API-Key: roamio-api-key-2025
```

---

## 📊 数据模型

### Ralendar 需要的 Event 模型

```python
class Event(models.Model):
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
    reminder_method = models.CharField(max_length=20)  # 'email' 或 'system'
    reminder_scheduled = models.BooleanField(default=False)
    
    # 来源标记（重要！）
    source_app = models.CharField(max_length=50, default='ralendar')
    source_id = models.CharField(max_length=100, blank=True)
    roamio_trip_id = models.IntegerField(null=True, blank=True)
```

---

## ⏱️ 实施时间表

### Phase 1: 基础 API（1-2 周）⭐⭐⭐

- [ ] 创建 Event 模型
- [ ] 实现 CRUD API
- [ ] API Key 认证
- [ ] JWT Token 验证

### Phase 2: 地图功能（1 周）⭐⭐

- [ ] 申请百度地图 AK
- [ ] 生成地图链接
- [ ] 创建地图页面

### Phase 3: 提醒功能（1-2 周）⭐⭐⭐

- [ ] 配置 Celery + Redis
- [ ] 实现提醒任务调度
- [ ] 发送邮件提醒

### Phase 4: 日历展示（1 周）⭐

- [ ] 在日历中显示来自 Roamio 的事件
- [ ] 标记来源

---

## 📚 详细文档

我们已经准备了完整的技术文档：

📄 **`ROAMIO_RALENDAR_INTEGRATION_SPEC.md`**

包含：
- ✅ 完整的 API 接口规范
- ✅ 数据模型设计
- ✅ 认证方案
- ✅ 数据流设计
- ✅ 测试用例
- ✅ 错误处理
- ✅ 安全考虑

**请查看这个文档获取所有技术细节！** 📖

---

## 🧪 测试用例

### 测试场景 1：创建事件

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
- ✅ 响应包含 `id`, `baidu_map_url`, `reminder_scheduled: true`
- ✅ 到提醒时间后发送邮件

---

## 🤔 常见问题

### Q1: 为什么不由 Roamio 自己实现地图和提醒？

**A**: 职责分离！
- Roamio 专注于旅行内容
- Ralendar 专注于日历和提醒
- 这样更灵活，可以独立升级

### Q2: 如果 Ralendar API 调用失败怎么办？

**A**: 不影响 Roamio 主流程！
- 用户仍然可以在 Roamio 中看到事件
- 只是没有日历和提醒功能
- Roamio 会记录日志，后续可以重试

### Q3: 用户数据安全吗？

**A**: 完全安全！
- 使用 HTTPS 加密传输
- JWT Token 验证用户身份
- API Key 验证应用身份
- 只能操作自己的事件

---

## 📞 联系方式

### Roamio 团队

- **项目负责人**: [您的名字]
- **技术负责人**: [技术负责人]
- **邮箱**: dev@roamio.com
- **GitHub**: https://github.com/roamio/roamio
- **文档**: https://roamio.com/docs

### 需要讨论？

我们随时欢迎沟通！可以通过以下方式联系我们：
- 📧 邮件：dev@roamio.com
- 💬 微信：[微信号]
- 📱 电话：[电话号码]

---

## 🎉 期待合作！

**Roamio × Ralendar = 完整的旅行生态系统！** 🌍✨

我们相信这个集成会给用户带来极佳的体验！

**有任何问题，请随时联系我们！** 😊

---

**附件**：
- 📄 `ROAMIO_RALENDAR_INTEGRATION_SPEC.md` - 完整技术文档
- 📄 `ROAMIO_V2_TECHNICAL_PLAN.md` - Roamio v2.0 技术方案
- 📄 `API_STANDARDS.md` - API 规范

---

**Roamio 开发团队**  
2025-11-08


