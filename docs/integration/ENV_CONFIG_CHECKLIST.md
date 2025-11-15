# Ralendar OAuth 环境变量配置清单

> **状态**：⏳ 等待 Ralendar 团队提供凭证  
> **更新时间**：2025-11-14

---

## 📋 需要配置的环境变量

### 开发环境 (`cloud_settings/.env.development`)

```bash
# ==================== Ralendar OAuth 配置 ====================

# OAuth 客户端 ID（待 Ralendar 提供）
RALENDAR_OAUTH_CLIENT_ID=

# OAuth 客户端密钥（待 Ralendar 提供）
RALENDAR_OAUTH_CLIENT_SECRET=

# OAuth 授权 URL
RALENDAR_OAUTH_AUTHORIZE_URL=https://app7626.acapp.acwing.com.cn/oauth/authorize

# OAuth Token URL
RALENDAR_OAUTH_TOKEN_URL=https://app7626.acapp.acwing.com.cn/api/oauth/token

# OAuth UserInfo URL
RALENDAR_OAUTH_USERINFO_URL=https://app7626.acapp.acwing.com.cn/api/oauth/userinfo

# OAuth 回调地址（开发环境）
RALENDAR_OAUTH_REDIRECT_URI=http://localhost:8080/auth/ralendar/callback
```

### 生产环境 (`cloud_settings/.env`)

```bash
# ==================== Ralendar OAuth 配置 ====================

# OAuth 客户端 ID（待 Ralendar 提供）
RALENDAR_OAUTH_CLIENT_ID=

# OAuth 客户端密钥（待 Ralendar 提供）
RALENDAR_OAUTH_CLIENT_SECRET=

# OAuth 授权 URL（生产环境待定）
RALENDAR_OAUTH_AUTHORIZE_URL=https://ralendar.com/oauth/authorize

# OAuth Token URL（生产环境待定）
RALENDAR_OAUTH_TOKEN_URL=https://ralendar.com/api/oauth/token

# OAuth UserInfo URL（生产环境待定）
RALENDAR_OAUTH_USERINFO_URL=https://ralendar.com/api/oauth/userinfo

# OAuth 回调地址（生产环境）
RALENDAR_OAUTH_REDIRECT_URI=https://roamio.cn/auth/ralendar/callback
```

---

## ✅ 配置检查清单

### 收到凭证后

- [ ] 填入 `RALENDAR_OAUTH_CLIENT_ID`
- [ ] 填入 `RALENDAR_OAUTH_CLIENT_SECRET`
- [ ] 确认 URL 是否正确（测试环境 vs 生产环境）
- [ ] 确认回调地址与提供给 Ralendar 的一致
- [ ] 重启 Django 服务使配置生效

### 验证配置

```python
# 在 Django shell 中验证
python manage.py shell

from django.conf import settings

print("Client ID:", settings.RALENDAR_OAUTH_CLIENT_ID)
print("Redirect URI:", settings.RALENDAR_OAUTH_REDIRECT_URI)
print("Authorize URL:", settings.RALENDAR_OAUTH_AUTHORIZE_URL)

# 不要打印 CLIENT_SECRET！
```

---

## 🔐 安全注意事项

### ⚠️ 绝对不要

- ❌ 将 `CLIENT_SECRET` 提交到 Git
- ❌ 在日志中打印 `CLIENT_SECRET`
- ❌ 在前端暴露 `CLIENT_SECRET`
- ❌ 在错误信息中泄露 `CLIENT_SECRET`

### ✅ 应该做

- ✅ 仅在服务器端使用
- ✅ 使用环境变量存储
- ✅ 定期轮换（建议每季度）
- ✅ 使用不同的凭证给测试/生产环境

---

## 📞 待 Ralendar 团队回复

### 需要确认

1. **client_id** 和 **client_secret**
2. 测试环境 URL 是否为 `https://app7626.acapp.acwing.com.cn`
3. 生产环境 URL（待定）
4. 回调地址白名单是否已添加：
   - `https://roamio.cn/auth/ralendar/callback`
   - `http://localhost:8080/auth/ralendar/callback`

---

**下一步**：收到凭证后 5 分钟内完成配置 ✨

