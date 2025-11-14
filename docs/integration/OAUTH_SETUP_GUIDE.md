# Ralendar OAuth 集成设置指南

> **状态**：✅ 核心功能已完成  
> **需要**：Ralendar 团队提供 client_id 和 client_secret

---

## 📋 前置要求

### 从 Ralendar 团队获取配置

联系 Ralendar 团队，让他们运行以下命令为 Roamio 创建 OAuth 客户端：

```bash
cd ralendar/backend
python manage.py init_oauth_client \
    --client-name "Roamio" \
    --redirect-uris "https://roamio.cn/auth/ralendar/callback,http://localhost:8080/auth/ralendar/callback"
```

他们会提供：
- `Client ID` （例如：ralendar_client_xxx）
- `Client Secret` （例如：yyy）

---

## 🔧 Roamio 配置

### 步骤1：环境变量配置

在 `cloud_settings/.env` 文件中添加：

```bash
# Ralendar OAuth 配置
RALENDAR_OAUTH_CLIENT_ID=ralendar_client_xxx
RALENDAR_OAUTH_CLIENT_SECRET=yyy
RALENDAR_OAUTH_REDIRECT_URI=https://roamio.cn/auth/ralendar/callback

# 开发环境
# RALENDAR_OAUTH_REDIRECT_URI=http://localhost:8080/auth/ralendar/callback
```

### 步骤2：数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

这会创建 `RalendarAccount` 表。

---

## 🎯 使用流程

### 1. 用户绑定 Ralendar 账号

**前端流程**：

```javascript
import { getRalendarAuthorizeUrl } from '@/api/ralendarOAuth'

// 点击"连接 Ralendar"按钮
async function connectRalendar() {
  try {
    // 1. 获取授权 URL
    const response = await getRalendarAuthorizeUrl()
    const { authorize_url, state } = response
    
    // 2. 保存来源页面（用于授权后跳回）
    sessionStorage.setItem('ralendar_auth_origin', window.location.pathname)
    
    // 3. 跳转到 Ralendar 授权页面
    window.location.href = authorize_url
    
  } catch (error) {
    console.error('获取授权URL失败:', error)
    alert('连接失败，请重试')
  }
}
```

**用户操作**：
1. 跳转到 Ralendar
2. 登录（QQ/AcWing/邮箱）
3. 点击"授权"
4. 自动跳回 Roamio
5. 显示"连接成功"

---

### 2. 查看已绑定账号

```vue
<template>
  <RalendarAccountManager 
    @connect="connectRalendar"
    @update="refreshData"
  />
</template>

<script>
import RalendarAccountManager from '@/components/ralendar/RalendarAccountManager.vue'

export default {
  components: {
    RalendarAccountManager
  },
  methods: {
    connectRalendar() {
      // 跳转授权
    },
    refreshData() {
      // 刷新页面数据
    }
  }
}
</script>
```

---

### 3. 同步到 Ralendar

**后端 API**：

```http
POST /api/v1/ralendar/trips/{slug}/sync-ai-trip/
Authorization: Bearer {roamio_jwt_token}
Content-Type: application/json

{
  "ralendar_account_id": 1,  // 可选，不传则使用默认账号
  "events": [
    {
      "title": "北京五日游 - Day 1",
      "description": "抵达北京",
      "start_time": "2025-11-15T09:00:00+08:00",
      "end_time": "2025-11-15T11:00:00+08:00",
      "location": "北京首都国际机场",
      "latitude": 40.0799,
      "longitude": 116.6031
    }
  ]
}
```

**前端调用**：

```javascript
import { syncTripToCalendar } from '@/api/ralendar'

async function syncToRalendar(tripSlug, events, ralendarAccountId) {
  try {
    const response = await syncTripToCalendar(tripSlug, {
      ralendar_account_id: ralendarAccountId,  // 可选
      events: events
    })
    
    if (response.code === 200) {
      const { synced_count, ralendar_account } = response.data
      alert(`成功同步 ${synced_count} 个事件到 ${ralendar_account}`)
    }
  } catch (error) {
    if (error.response?.data?.code === 'NO_RALENDAR_ACCOUNT') {
      alert('请先绑定 Ralendar 账号')
      // 跳转到个人中心
      router.push('/user/center')
    } else {
      alert('同步失败：' + error.response?.data?.error)
    }
  }
}
```

---

## 🔄 关键变化

### 旧逻辑（已移除）

```python
# ❌ 旧：使用 Roamio JWT + unionid/openid/email 匹配
user_token = request.auth  # Roamio 的 JWT
result = client.batch_create_events(
    user_token,
    events,
    trip.slug,
    unionid=unionid,
    openid=openid,
    email=email
)
```

**问题**：
- 复杂的用户匹配逻辑
- 邮箱冲突
- 无法支持多账号

---

### 新逻辑（OAuth）

```python
# ✅ 新：使用 RalendarAccount 的 OAuth Token
ralendar_account = RalendarAccount.objects.get(user=request.user, is_default=True)
access_token = ralendar_account.access_token

result = client.batch_create_events(
    access_token,  # Ralendar OAuth Token
    events,
    trip.slug
)
```

**优点**：
- 简单明确
- 无用户匹配问题
- 支持多账号

---

## 🧪 测试

### 测试场景1：完整授权流程

1. 用户在 Roamio 登录
2. 点击"连接 Ralendar"
3. 跳转到 Ralendar
4. 使用 QQ 登录 Ralendar
5. 点击"授权"
6. 跳回 Roamio，显示"连接成功"
7. 在个人中心看到已绑定账号

**预期**：
- ✅ 授权流程顺畅
- ✅ Token 正确保存到数据库
- ✅ 账号信息完整（用户名、邮箱、头像）

---

### 测试场景2：同步日历

1. 用户已绑定 Ralendar 账号
2. 在旅行编辑器点击"同步到 Ralendar"
3. 选择默认账号
4. 点击确认

**预期**：
- ✅ 显示"同步成功"
- ✅ 在 Ralendar 中可以看到事件
- ✅ 事件信息完整（标题、时间、地点）

---

### 测试场景3：多账号切换

1. 用户绑定第一个 Ralendar 账号 A
2. 再次点击"添加账号"
3. 绑定第二个 Ralendar 账号 B
4. 在同步时选择账号 B
5. 确认同步

**预期**：
- ✅ 两个账号都显示在列表中
- ✅ 可以选择同步到账号 B
- ✅ 事件创建在账号 B 的日历中

---

### 测试场景4：Token 过期

1. 用户的 Token 已过期（2小时后）
2. 点击"同步到 Ralendar"

**预期**：
- ✅ 显示"Token 已过期，请重新授权"
- ✅ 提供重新授权按钮
- ✅ 点击后重新走授权流程
- ✅ 授权后 Token 更新，可以继续使用

---

## 📊 数据库表结构

### RalendarAccount

```sql
CREATE TABLE ralendar_accounts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    ralendar_user_id INTEGER NOT NULL,
    ralendar_username VARCHAR(100) NOT NULL,
    ralendar_email VARCHAR(254),
    ralendar_avatar TEXT,
    ralendar_provider VARCHAR(20),
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_type VARCHAR(20) DEFAULT 'Bearer',
    token_expires_at DATETIME,
    scope VARCHAR(200) DEFAULT 'calendar:read calendar:write',
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    last_synced_at DATETIME,
    UNIQUE (user_id, ralendar_user_id),
    FOREIGN KEY (user_id) REFERENCES auth_user(id)
);
```

---

## ❓ FAQ

### Q1: 如果用户没有绑定 Ralendar 怎么办？

A: 同步时会返回错误：

```json
{
  "error": "尚未绑定 Ralendar 账号",
  "code": "NO_RALENDAR_ACCOUNT"
}
```

前端应该引导用户去个人中心绑定。

---

### Q2: 如何支持多账号？

A: 用户可以绑定多个 Ralendar 账号：
- 第一个账号自动设为默认
- 后续可以手动设置默认账号
- 同步时可以选择使用哪个账号

---

### Q3: Token 过期怎么办？

A: 
- Token 默认 2 小时有效
- 过期后需要重新授权
- 未来可以实现 refresh_token 自动刷新

---

### Q4: 如何解绑账号？

A: 在个人中心的 Ralendar 账号管理中点击"解绑"。

---

### Q5: Ralendar 和 Roamio 的账号是同一个吗？

A: 不是！它们是独立的：
- Roamio 账号：用于登录 Roamio
- Ralendar 账号：用于登录 Ralendar
- 通过 OAuth 授权建立连接

---

## 📞 技术支持

- **Roamio 团队**: 
- **Ralendar 团队**: 

---

**最后更新**：2025-11-14  
**版本**：v1.0

