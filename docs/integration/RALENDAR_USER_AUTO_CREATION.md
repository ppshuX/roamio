# Ralendar 用户自动创建机制

> **集成对接**：Roamio ↔ Ralendar 用户自动创建与绑定

---

## 📋 场景说明

### 场景：Roamio 邮箱注册，Ralendar 无账号

**用户行为**：
1. 用户在 Roamio 用邮箱注册：`user@example.com`
2. Ralendar 中没有该用户的账号
3. 用户点击"同步到 Ralendar"

**问题**：
- 如果 Ralendar 中不存在该邮箱的用户，如何创建事件？

---

## 🎯 解决方案

### 方案 A：Ralendar 自动创建用户（推荐）

**逻辑**：
1. Roamio 发送同步请求：`{ email: "user@example.com", events: [...] }`
2. Ralendar 检查用户是否存在：
   - 如果存在：直接创建事件
   - 如果不存在：自动创建用户（使用邮箱作为标识符）
3. 创建事件并返回成功

**优点**：
- ✅ 用户体验好，无需额外操作
- ✅ 自动关联邮箱和事件
- ✅ 用户后续可以通过 QQ 登录绑定账号

**缺点**：
- ⚠️ 需要 Ralendar 支持自动创建用户
- ⚠️ 用户需要通过 QQ 登录来绑定账号（否则无法登录 Ralendar）

---

### 方案 B：提示用户先绑定 QQ（兜底）

**逻辑**：
1. Roamio 在同步前检查用户是否存在（通过 `check_email_exists` API）
2. 如果用户不存在且没有 QQ 绑定：
   - 提示用户："请先绑定 QQ 账号，或登录 Ralendar 后再同步"
   - 提供绑定 QQ 的入口
3. 如果用户有 QQ 绑定：
   - 直接同步（Ralendar 会通过 unionid 自动创建或匹配用户）

**优点**：
- ✅ 确保用户可以通过 QQ 登录 Ralendar
- ✅ 明确的用户引导

**缺点**：
- ❌ 需要用户额外操作
- ❌ 打断用户体验

---

## 🔄 完整流程

### 场景 1：Roamio 邮箱注册 + 无 QQ 绑定

```
1. 用户在 Roamio 用邮箱注册：user@example.com
2. 用户点击"同步到 Ralendar"
3. Roamio 检查：
   - 用户是否有 QQ 绑定？❌ 没有
   - Ralendar 中是否有该邮箱？❓ 未知
4. Roamio 调用 check_email_exists("user@example.com")
5. Ralendar 返回：{ "exists": false }
6. Roamio 提示用户：
   - "请先绑定 QQ 账号，或登录 Ralendar 后再同步"
   - 提供绑定 QQ 的入口
```

### 场景 2：Roamio 邮箱注册 + 有 QQ 绑定

```
1. 用户在 Roamio 用邮箱注册：user@example.com
2. 用户绑定 QQ（unionid: UID_123）
3. 用户点击"同步到 Ralendar"
4. Roamio 检查：
   - 用户是否有 QQ 绑定？✅ 有（unionid: UID_123）
5. Roamio 调用 batch_create_events：
   {
     "unionid": "UID_123",
     "email": "user@example.com",
     "events": [...]
   }
6. Ralendar 检查用户：
   - 通过 unionid 查找：找到用户 ✅
   - 或通过 unionid 创建：创建用户 ✅
7. 创建事件并返回成功
```

### 场景 3：Ralendar 已有账号 + Roamio 邮箱注册

```
1. 用户在 Ralendar 用 QQ 登录，绑定了邮箱：user@example.com
2. 用户在 Roamio 用邮箱注册：user@example.com
3. 用户点击"同步到 Ralendar"
4. Roamio 检查：
   - 用户是否有 QQ 绑定？❌ 没有
5. Roamio 调用 check_email_exists("user@example.com")
6. Ralendar 返回：
   {
     "exists": true,
     "owner": {
       "email": "user@example.com",
       "unionid": "UID_123",
       "provider": "qq"
     }
   }
7. Roamio 提示用户：
   - "检测到该邮箱已在 Ralendar 注册，请绑定相同的 QQ 账号"
   - 提供绑定 QQ 的入口
8. 用户绑定 QQ 后，再次同步：
   - 通过 unionid 匹配到 Ralendar 用户 ✅
   - 创建事件并返回成功
```

---

## 📡 API 需求

### 1. Ralendar 支持自动创建用户

**接口**：`POST /api/fusion/events/batch/`

**请求**：
```json
{
  "email": "user@example.com",
  "events": [...]
}
```

**逻辑**：
1. 如果用户不存在（通过 email 查找）：
   - 自动创建用户（使用邮箱作为标识符）
   - 创建事件
   - 返回成功
2. 如果用户存在：
   - 直接创建事件
   - 返回成功

**响应**：
```json
{
  "success": true,
  "created_count": 1,
  "failed_count": 0,
  "details": {
    "created": [...],
    "failed": []
  },
  "user_created": true,  // 🌟 新增：是否创建了用户
  "user_id": 123
}
```

---

### 2. Roamio 同步前检查用户（可选）

**接口**：`POST /api/fusion/users/check-email/`

**请求**：
```json
{
  "email": "user@example.com"
}
```

**响应**：
```json
{
  "exists": false
}
```

**逻辑**：
1. 如果用户不存在且没有 QQ 绑定：
   - 提示用户绑定 QQ 或登录 Ralendar
2. 如果用户存在：
   - 直接同步

---

## 🔧 实现建议

### Roamio 端

1. **同步前检查**：
   ```python
   # 如果用户没有 QQ 绑定，检查 Ralendar 中是否存在
   if not unionid and not openid:
       if user_email:
           # 检查 Ralendar 中是否存在该邮箱
           result = ralendar_client.check_email_exists(user_email)
           if not result.get('exists'):
               # 提示用户绑定 QQ 或登录 Ralendar
               return Response({
                   'error': '请先绑定 QQ 账号，或登录 Ralendar 后再同步',
                   'code': 'RALENDAR_USER_NOT_FOUND',
                   'suggestion': '绑定 QQ 账号'
               }, status=400)
   ```

2. **同步时传递用户信息**：
   ```python
   # 优先级：unionid > openid > email
   result = client.batch_create_events(
       user_token,
       events,
       trip.slug,
       unionid=unionid,
       openid=openid,
       email=user_email
   )
   ```

---

### Ralendar 端

1. **自动创建用户**：
   ```python
   # 在 batch_create_events 中
   if email:
       user = User.objects.filter(email=email).first()
       if not user:
           # 自动创建用户（使用邮箱作为标识符）
           user = User.objects.create(
               email=email,
               username=email.split('@')[0],
               is_active=True
           )
           logger.info(f"自动创建用户：{email}")
   ```

2. **返回用户创建信息**：
   ```python
   return {
       "success": True,
       "created_count": len(created_events),
       "failed_count": len(failed_events),
       "details": {
           "created": created_events,
           "failed": failed_events
       },
       "user_created": user_created,  # 🌟 新增
       "user_id": user.id if user else None
   }
   ```

---

## ✅ 推荐方案

**采用方案 A（Ralendar 自动创建用户）+ 方案 B（Roamio 同步前检查）的组合**：

1. **Roamio 同步前检查**：
   - 如果用户没有 QQ 绑定，检查 Ralendar 中是否存在
   - 如果不存在，提示用户绑定 QQ（更好的用户体验）

2. **Ralendar 自动创建用户**：
   - 如果用户不存在，自动创建用户
   - 用户后续可以通过 QQ 登录绑定账号

3. **用户体验优化**：
   - 如果用户有 QQ 绑定：直接同步（无需检查）
   - 如果用户没有 QQ 绑定：提示绑定 QQ（明确引导）

---

## 📞 联系方式

如有技术问题，请联系：

- **Ralendar Team**: dev@ralendar.example.com
- **Roamio Team**: dev@roamio.cn

**最后更新**：2025-11-14

