# Roamio × Ralendar OAuth 集成技术规范

> **文档类型**：技术需求文档  
> **目标受众**：Ralendar 开发团队  
> **版本**：v1.0  
> **日期**：2025-11-14

---

## 📋 目录

1. [背景与目标](#背景与目标)
2. [方案概述](#方案概述)
3. [技术规范](#技术规范)
4. [API 详细设计](#api-详细设计)
5. [数据模型](#数据模型)
6. [安全规范](#安全规范)
7. [用户体验优化](#用户体验优化)
8. [测试场景](#测试场景)
9. [实施计划](#实施计划)
10. [FAQ](#faq)

---

## 📖 背景与目标

### 当前问题

Roamio 和 Ralendar 的集成面临以下挑战：

1. **用户匹配复杂**：通过邮箱/unionid 匹配存在冲突风险
2. **账号耦合度高**：需要强制绑定 QQ 或邮箱
3. **数据安全隐患**：自动创建用户可能导致数据混乱
4. **扩展性差**：无法支持一个 Roamio 账号绑定多个 Ralendar 账号

### 解决方案

采用标准的 **OAuth 2.0 授权码流程**，实现：

- ✅ Roamio 和 Ralendar 完全解耦
- ✅ 用户自主选择绑定账号，无歧义
- ✅ 支持多账号绑定
- ✅ 符合行业标准，安全可靠

### 参考案例

- GitHub OAuth（允许第三方应用访问仓库）
- Google OAuth（允许第三方应用访问 Calendar）
- 微信开放平台（允许第三方应用获取用户信息）

---

## 🎯 方案概述

### 用户流程

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 用户在 Roamio 点击 "连接 Ralendar"                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. 跳转到 Ralendar 授权页面                                 │
│    - 如果未登录：引导登录（QQ/AcWing/邮箱）                 │
│    - 如果已登录：直接显示授权确认页面                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. 用户点击 "授权" 或 "拒绝"                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. 跳回 Roamio（携带授权码 code）                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Roamio 后端用 code 换取 access_token                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. 保存 token，完成绑定                                      │
│    之后使用 token 调用 Ralendar API 同步日历                │
└─────────────────────────────────────────────────────────────┘
```

### 技术架构

```
Roamio                          Ralendar
  │                                │
  │  1. 请求授权 URL                │
  ├────────────────────────────────>│
  │  GET /oauth/authorize           │
  │                                │
  │  2. 返回授权页面                │
  │<────────────────────────────────┤
  │                                │
  │  3. 用户授权                    │
  │────────────────────────────────>│
  │                                │
  │  4. 回调（带 code）             │
  │<────────────────────────────────┤
  │                                │
  │  5. 用 code 换 token            │
  ├────────────────────────────────>│
  │  POST /oauth/token              │
  │                                │
  │  6. 返回 access_token           │
  │<────────────────────────────────┤
  │                                │
  │  7. 调用 API                    │
  ├────────────────────────────────>│
  │  Authorization: Bearer token    │
  │                                │
```

---

## 🔧 技术规范

### OAuth 2.0 授权码流程

Ralendar 需要实现标准的 OAuth 2.0 Authorization Code Flow，包括：

1. **授权端点**（Authorization Endpoint）
2. **Token 端点**（Token Endpoint）
3. **用户信息端点**（UserInfo Endpoint）
4. **Token 刷新机制**（Token Refresh）

---

## 📡 API 详细设计

### 1. 获取授权 URL（Roamio 客户端调用）

**端点**：无需 API，由 Roamio 直接构造

**URL 格式**：
```
GET https://ralendar.com/oauth/authorize?
    client_id={client_id}&
    redirect_uri={redirect_uri}&
    response_type=code&
    state={state}&
    scope={scope}
```

**参数说明**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `client_id` | string | ✅ | Roamio 的应用 ID（由 Ralendar 分配） |
| `redirect_uri` | string | ✅ | 授权回调地址（需预先注册）<br>例：`https://roamio.cn/auth/ralendar/callback` |
| `response_type` | string | ✅ | 固定值：`code` |
| `state` | string | ✅ | 防 CSRF 攻击的随机字符串（Roamio 生成） |
| `scope` | string | ⚠️ | 请求的权限范围，例：`calendar:read calendar:write` |

**示例**：
```
https://ralendar.com/oauth/authorize?
    client_id=roamio_app_20251114&
    redirect_uri=https://roamio.cn/auth/ralendar/callback&
    response_type=code&
    state=abc123xyz789&
    scope=calendar:read calendar:write
```

---

### 2. 授权页面（Ralendar 实现）

**功能**：

1. 检查用户登录状态
   - 未登录 → 显示登录页面（QQ/AcWing/邮箱）
   - 已登录 → 显示授权确认页面

2. 显示授权信息
   ```
   ┌─────────────────────────────────────────┐
   │  Roamio 请求访问您的日历                │
   │                                         │
   │  该应用将获得以下权限：                  │
   │  ✓ 查看您的日历事件                     │
   │  ✓ 创建和编辑日历事件                   │
   │                                         │
   │  授权后，Roamio 可以将您的旅行计划      │
   │  自动同步到 Ralendar 日历               │
   │                                         │
   │  [ 拒绝 ]           [ 授权 ]           │
   └─────────────────────────────────────────┘
   ```

3. 用户点击"授权"后
   - 生成授权码（code，10分钟有效）
   - 重定向到 `redirect_uri?code={code}&state={state}`

4. 用户点击"拒绝"后
   - 重定向到 `redirect_uri?error=access_denied&state={state}`

**回调示例（授权成功）**：
```
https://roamio.cn/auth/ralendar/callback?
    code=AUTHORIZATION_CODE_123456&
    state=abc123xyz789
```

**回调示例（用户拒绝）**：
```
https://roamio.cn/auth/ralendar/callback?
    error=access_denied&
    state=abc123xyz789
```

---

### 3. 换取 Access Token（Token Endpoint）

**端点**：`POST /api/oauth/token`

**请求头**：
```http
Content-Type: application/json
```

**请求体**：
```json
{
  "grant_type": "authorization_code",
  "code": "AUTHORIZATION_CODE_123456",
  "client_id": "roamio_app_20251114",
  "client_secret": "SECRET_KEY_xyz789",
  "redirect_uri": "https://roamio.cn/auth/ralendar/callback"
}
```

**参数说明**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `grant_type` | string | ✅ | 固定值：`authorization_code` |
| `code` | string | ✅ | 授权码（10分钟有效，一次性使用） |
| `client_id` | string | ✅ | Roamio 的应用 ID |
| `client_secret` | string | ✅ | Roamio 的应用密钥（需保密） |
| `redirect_uri` | string | ✅ | 必须与授权时的 `redirect_uri` 一致 |

**响应（成功）**：

HTTP 200 OK
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 7200,
  "refresh_token": "REFRESH_TOKEN_abc123",
  "scope": "calendar:read calendar:write"
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `access_token` | string | 访问令牌（JWT 格式）<br>用于调用 Ralendar API |
| `token_type` | string | 固定值：`Bearer` |
| `expires_in` | integer | Token 有效期（秒）<br>建议：7200（2小时） |
| `refresh_token` | string | 刷新令牌（可选）<br>用于获取新的 access_token |
| `scope` | string | 实际授予的权限范围 |

**响应（失败）**：

HTTP 400 Bad Request
```json
{
  "error": "invalid_grant",
  "error_description": "授权码无效或已过期"
}
```

**错误码**：

| 错误码 | 说明 |
|--------|------|
| `invalid_request` | 请求参数缺失或格式错误 |
| `invalid_client` | client_id 或 client_secret 错误 |
| `invalid_grant` | 授权码无效、过期或已使用 |
| `unauthorized_client` | 客户端无权使用此授权类型 |

---

### 4. 获取用户信息（UserInfo Endpoint）

**端点**：`GET /api/oauth/userinfo`

**请求头**：
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**响应（成功）**：

HTTP 200 OK
```json
{
  "user_id": 12345,
  "username": "张三",
  "email": "zhangsan@example.com",
  "avatar": "https://ralendar.com/media/avatars/user_12345.jpg",
  "provider": "qq",
  "created_at": "2025-01-01T12:00:00Z"
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `user_id` | integer | Ralendar 用户 ID |
| `username` | string | 用户名 |
| `email` | string | 邮箱（如有） |
| `avatar` | string | 头像 URL（如有） |
| `provider` | string | 登录方式：`qq` / `acwing` / `email` |
| `created_at` | string | 账号创建时间（ISO 8601 格式） |

**响应（失败）**：

HTTP 401 Unauthorized
```json
{
  "error": "invalid_token",
  "error_description": "Token 无效或已过期"
}
```

---

### 5. 刷新 Access Token（可选）

**端点**：`POST /api/oauth/token`

**请求体**：
```json
{
  "grant_type": "refresh_token",
  "refresh_token": "REFRESH_TOKEN_abc123",
  "client_id": "roamio_app_20251114",
  "client_secret": "SECRET_KEY_xyz789"
}
```

**响应（成功）**：

HTTP 200 OK
```json
{
  "access_token": "NEW_ACCESS_TOKEN...",
  "token_type": "Bearer",
  "expires_in": 7200,
  "refresh_token": "NEW_REFRESH_TOKEN...",
  "scope": "calendar:read calendar:write"
}
```

---

### 6. 撤销 Token（可选）

**端点**：`POST /api/oauth/revoke`

**请求头**：
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**响应（成功）**：

HTTP 200 OK
```json
{
  "success": true,
  "message": "Token 已撤销"
}
```

---

## 🗄️ 数据模型

### OAuth 客户端（OAuthClient）

Ralendar 需要管理接入的第三方应用（如 Roamio）。

```python
class OAuthClient(models.Model):
    """OAuth 客户端（第三方应用）"""
    client_id = models.CharField(max_length=100, unique=True)
    client_secret = models.CharField(max_length=255)
    client_name = models.CharField(max_length=100)  # 例：Roamio
    redirect_uris = models.JSONField()  # 允许的回调地址列表
    allowed_scopes = models.JSONField()  # 允许的权限范围
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**示例数据**：
```python
OAuthClient.objects.create(
    client_id='roamio_app_20251114',
    client_secret='SECRET_KEY_xyz789',
    client_name='Roamio',
    redirect_uris=[
        'https://roamio.cn/auth/ralendar/callback',
        'http://localhost:8080/auth/ralendar/callback'  # 开发环境
    ],
    allowed_scopes=['calendar:read', 'calendar:write']
)
```

---

### 授权码（AuthorizationCode）

临时存储授权码，用于换取 access_token。

```python
class AuthorizationCode(models.Model):
    """授权码（10分钟有效，一次性）"""
    code = models.CharField(max_length=100, unique=True)
    client = models.ForeignKey(OAuthClient, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    redirect_uri = models.CharField(max_length=500)
    scope = models.CharField(max_length=200)
    expires_at = models.DateTimeField()  # 10分钟后过期
    used = models.BooleanField(default=False)  # 是否已使用
    created_at = models.DateTimeField(auto_now_add=True)
```

---

### Access Token（AccessToken）

存储已颁发的 access_token。

```python
class AccessToken(models.Model):
    """访问令牌"""
    token = models.CharField(max_length=500, unique=True)  # JWT
    client = models.ForeignKey(OAuthClient, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    scope = models.CharField(max_length=200)
    expires_at = models.DateTimeField()  # 2小时后过期
    refresh_token = models.CharField(max_length=100, blank=True, null=True)
    is_revoked = models.BooleanField(default=False)  # 是否已撤销
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## 🔒 安全规范

### 1. Client Secret 管理

- ✅ **存储**：加密存储（使用 Django 的 `make_password`）
- ✅ **传输**：仅在后端通信，不暴露给前端
- ✅ **泄露应对**：支持重新生成 client_secret

### 2. State 参数（防 CSRF）

- ✅ Roamio 生成随机 state，缓存 10 分钟
- ✅ 回调时验证 state 是否匹配
- ✅ 验证后立即删除 state

### 3. 授权码（Code）安全

- ✅ 10 分钟有效期
- ✅ 一次性使用（使用后标记为 `used=True`）
- ✅ 绑定 client_id 和 redirect_uri

### 4. Access Token 安全

- ✅ 使用 JWT 格式，包含签名
- ✅ 2 小时有效期（可配置）
- ✅ 支持撤销（用户在 Ralendar 可撤销授权）

### 5. HTTPS 强制

- ✅ 生产环境强制使用 HTTPS
- ✅ 开发环境可使用 HTTP（仅限 localhost）

### 6. Redirect URI 白名单

- ✅ 严格校验 redirect_uri 必须在白名单内
- ✅ 不允许通配符（防止重定向攻击）

---

## 🎨 用户体验优化

### 1. 智能登录引导

**场景1：Roamio 用户使用 QQ 登录**

跳转到 Ralendar 授权页面时：
- 优先显示 QQ 登录按钮
- 如果用户已用该 QQ 登录过 Ralendar，自动识别

**场景2：Roamio 用户使用邮箱登录**

跳转到 Ralendar 授权页面时：
- 预填邮箱到登录表单
- 如果邮箱已注册，引导登录
- 如果邮箱未注册，引导快速注册

**实现方式**：

在授权 URL 中添加提示参数（可选）：
```
https://ralendar.com/oauth/authorize?
    client_id=roamio_app&
    redirect_uri=https://roamio.cn/callback&
    response_type=code&
    state=abc123&
    hint_email=user@example.com&      # 提示邮箱
    hint_provider=qq                  # 提示登录方式
```

---

### 2. 清晰的授权说明

授权页面文案示例：

```
┌─────────────────────────────────────────────────┐
│  🗓️ Roamio 请求访问您的 Ralendar 日历         │
│                                                 │
│  Roamio 将获得以下权限：                        │
│  ✓ 查看您的日历事件                            │
│  ✓ 创建和编辑日历事件                          │
│                                                 │
│  ⚠️ Roamio 不会：                              │
│  • 删除您的事件                                │
│  • 分享您的数据给第三方                        │
│  • 访问您的密码                                │
│                                                 │
│  您可以随时在设置中撤销此授权。                 │
│                                                 │
│  [ 取消 ]                    [ 授权 Roamio ]  │
└─────────────────────────────────────────────────┘
```

---

### 3. 授权管理页面

用户可以在 Ralendar 的设置页面查看和管理授权：

```
已授权的应用：

┌─────────────────────────────────────────┐
│ 🌍 Roamio                               │
│ 权限：读取日历、编辑日历                │
│ 授权时间：2025-11-14 10:30             │
│                                         │
│ [ 撤销授权 ]                           │
└─────────────────────────────────────────┘
```

---

## 🧪 测试场景

### 场景1：首次授权

1. Roamio 用户点击"连接 Ralendar"
2. 跳转到 Ralendar，使用 QQ 登录
3. 点击"授权"
4. 跳回 Roamio，显示"连接成功"
5. 同步日历，成功

**预期结果**：
- ✅ 授权流程顺畅
- ✅ Token 正确保存
- ✅ API 调用成功

---

### 场景2：用户拒绝授权

1. Roamio 用户点击"连接 Ralendar"
2. 跳转到 Ralendar
3. 点击"取消"
4. 跳回 Roamio，显示"授权已取消"

**预期结果**：
- ✅ 正确处理拒绝情况
- ✅ 不保存任何数据

---

### 场景3：Token 过期

1. 用户已绑定 Ralendar
2. Token 过期（2小时后）
3. 用户同步日历
4. Roamio 使用 refresh_token 获取新 token
5. 同步成功

**预期结果**：
- ✅ 自动刷新 token
- ✅ 用户无感知

---

### 场景4：撤销授权

1. 用户在 Ralendar 撤销 Roamio 的授权
2. 用户在 Roamio 同步日历
3. API 返回 401 错误
4. Roamio 提示"需要重新授权"

**预期结果**：
- ✅ 正确识别授权已撤销
- ✅ 引导用户重新授权

---

### 场景5：多账号绑定

1. Roamio 用户 A 绑定 Ralendar 账号 X
2. 用户 A 再次点击"连接 Ralendar"
3. 登录 Ralendar 账号 Y
4. 授权成功
5. Roamio 显示两个账号，可选择同步目标

**预期结果**：
- ✅ 支持绑定多个账号
- ✅ 可切换同步目标

---

## 📅 实施计划

### 阶段1：OAuth 服务器实现（Ralendar）

**时间**：1-2 周

**任务**：
- [ ] 数据库模型设计（OAuthClient, AuthorizationCode, AccessToken）
- [ ] 授权端点实现（/oauth/authorize）
- [ ] Token 端点实现（/oauth/token）
- [ ] UserInfo 端点实现（/oauth/userinfo）
- [ ] 授权页面 UI 开发
- [ ] 授权管理页面开发
- [ ] 单元测试

---

### 阶段2：OAuth 客户端实现（Roamio）

**时间**：3-5 天

**任务**：
- [ ] RalendarAccount 数据模型
- [ ] 授权流程后端 API
- [ ] 回调处理
- [ ] Token 刷新逻辑
- [ ] 前端"连接 Ralendar"按钮
- [ ] 前端授权状态显示
- [ ] 前端账号管理界面

---

### 阶段3：联调测试

**时间**：2-3 天

**任务**：
- [ ] 端到端测试
- [ ] 安全测试
- [ ] 性能测试
- [ ] 文档完善

---

### 阶段4：上线部署

**时间**：1 天

**任务**：
- [ ] 生产环境配置
- [ ] 监控告警配置
- [ ] 灰度发布
- [ ] 用户公告

---

## ❓ FAQ

### Q1: 为什么使用 OAuth 而不是直接共享用户？

**A**: OAuth 提供了标准的授权机制，具有以下优势：
- 用户匹配无歧义
- 支持多账号绑定
- 符合行业标准
- 安全可控

---

### Q2: Client Secret 如何管理？

**A**: 
- Ralendar 后台生成并分配给 Roamio
- Roamio 保存在服务器环境变量中（不提交到代码仓库）
- 仅在后端通信中使用，不暴露给前端

---

### Q3: Token 有效期多久合适？

**A**: 
- Access Token：2 小时（平衡安全性和用户体验）
- Refresh Token：30 天（可配置）
- Authorization Code：10 分钟（足够完成授权流程）

---

### Q4: 如果用户在 Ralendar 删除账号会怎样？

**A**: 
- Roamio 调用 API 时返回 404 或 401
- Roamio 自动清理该用户的 RalendarAccount 记录
- 提示用户"Ralendar 账号已不存在"

---

### Q5: 是否支持单点登录（SSO）？

**A**: 
- 当前方案不是 SSO，而是授权（OAuth）
- 用户需要分别登录 Roamio 和 Ralendar
- 但授权后，Roamio 可以无缝调用 Ralendar API

---

### Q6: Scope 如何设计？

**A**: 建议的权限范围：
- `calendar:read` - 读取日历事件
- `calendar:write` - 创建和编辑事件
- `calendar:delete` - 删除事件（暂不开放）
- `user:read` - 读取用户基本信息

Roamio 默认请求：`calendar:read calendar:write user:read`

---

## 📞 联系方式

### 技术对接

- **Roamio 技术负责人**：[联系方式]
- **Ralendar 技术负责人**：[联系方式]

### 文档维护

- **最后更新**：2025-11-14
- **版本**：v1.0
- **文档仓库**：[Git 仓库地址]

---

## 📎 附录

### A. 完整的授权流程时序图

```mermaid
sequenceDiagram
    participant U as 用户
    participant R as Roamio 前端
    participant RS as Roamio 后端
    participant RaS as Ralendar 服务器
    
    U->>R: 点击"连接 Ralendar"
    R->>RS: 请求授权 URL
    RS->>RS: 生成 state
    RS-->>R: 返回授权 URL
    R->>U: 跳转到 Ralendar
    
    U->>RaS: 访问授权页面
    RaS->>U: 显示登录/授权页面
    U->>RaS: 登录并点击"授权"
    
    RaS->>RaS: 生成授权码 code
    RaS->>U: 重定向到 Roamio (带 code)
    U->>R: 访问回调地址
    
    R->>RS: 提交 code 和 state
    RS->>RS: 验证 state
    RS->>RaS: 用 code 换取 token
    RaS->>RaS: 验证 code
    RaS-->>RS: 返回 access_token
    
    RS->>RaS: 获取用户信息
    RaS-->>RS: 返回用户信息
    
    RS->>RS: 保存 RalendarAccount
    RS-->>R: 返回成功
    R->>U: 显示"连接成功"
```

### B. 错误码速查表

| 错误码 | HTTP 状态 | 说明 | 处理建议 |
|--------|----------|------|---------|
| `invalid_request` | 400 | 请求参数错误 | 检查参数格式 |
| `invalid_client` | 401 | client_id/secret 错误 | 检查客户端配置 |
| `invalid_grant` | 400 | 授权码无效 | 重新发起授权 |
| `unauthorized_client` | 401 | 客户端未授权 | 联系管理员 |
| `unsupported_grant_type` | 400 | 不支持的授权类型 | 检查 grant_type |
| `invalid_scope` | 400 | 权限范围无效 | 检查 scope 参数 |
| `invalid_token` | 401 | Token 无效或过期 | 刷新 token |
| `insufficient_scope` | 403 | 权限不足 | 请求更高权限 |

### C. 参考资源

- [RFC 6749 - OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc6749)
- [OAuth 2.0 简化版指南](https://oauth.net/2/)
- [Django OAuth Toolkit](https://django-oauth-toolkit.readthedocs.io/)

---

**文档结束**

有任何问题请联系 Roamio 技术团队 📧

