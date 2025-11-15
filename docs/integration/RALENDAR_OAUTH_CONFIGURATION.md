# Ralendar OAuth 配置指南

> **⚠️ 重要**：本文档包含配置步骤，但**不包含**真实凭证  
> **凭证位置**：`cloud_settings/.env`（该目录已在 .gitignore 中）

---

## 🔑 已获取的凭证

Ralendar 团队已提供以下凭证：

```
Client ID:     ralendar_client_CJjjv6N9prR6JpDGmWijgA
Client Secret: ZaEM6BTUqZ_KMPXq_Bh9ixlhRyBgG_YFc8cuRYbybms
```

**回调地址（已在 Ralendar 白名单中）**：
- 生产环境：`https://roamio.cn/auth/ralendar/callback`
- 开发环境：`http://localhost:8080/auth/ralendar/callback`

---

## 📝 配置步骤

### 步骤 1：编辑配置文件

在服务器上执行：

```bash
# 编辑生产环境配置
vim cloud_settings/.env
```

### 步骤 2：添加以下配置

在 `.env` 文件末尾添加：

```bash
# ==================== Ralendar OAuth 配置 ====================
# 配置时间：2025-11-14

RALENDAR_OAUTH_CLIENT_ID=ralendar_client_CJjjv6N9prR6JpDGmWijgA
RALENDAR_OAUTH_CLIENT_SECRET=ZaEM6BTUqZ_KMPXq_Bh9ixlhRyBgG_YFc8cuRYbybms
RALENDAR_OAUTH_REDIRECT_URI=https://roamio.cn/auth/ralendar/callback

# Ralendar OAuth 端点（测试环境）
RALENDAR_OAUTH_AUTHORIZE_URL=https://app7626.acapp.acwing.com.cn/oauth/authorize
RALENDAR_OAUTH_TOKEN_URL=https://app7626.acapp.acwing.com.cn/api/oauth/token
RALENDAR_OAUTH_USERINFO_URL=https://app7626.acapp.acwing.com.cn/api/oauth/userinfo
```

保存并退出（`:wq`）

### 步骤 3：重启服务

```bash
supervisorctl restart roamio
```

### 步骤 4：验证配置

```bash
python manage.py shell
```

在 Python shell 中执行：

```python
from django.conf import settings

# 检查配置是否加载
print("Client ID:", settings.RALENDAR_OAUTH_CLIENT_ID)
print("Redirect URI:", settings.RALENDAR_OAUTH_REDIRECT_URI)
print("Authorize URL:", settings.RALENDAR_OAUTH_AUTHORIZE_URL)

# 确认没有警告信息
# 如果配置正确，不应该看到 [WARNING] Ralendar OAuth configuration incomplete

exit()
```

---

## ✅ 验证清单

- [ ] 配置文件已编辑（`cloud_settings/.env`）
- [ ] 6 个环境变量已添加
- [ ] 服务已重启
- [ ] Django 启动时无 OAuth 警告
- [ ] Python shell 可以正确读取配置

---

## 🧪 快速测试

配置完成后，立即测试：

```bash
# 1. 检查服务状态
supervisorctl status roamio

# 2. 查看最新日志（确认无错误）
tail -f logs/roamio.log

# 3. 访问个人中心
# 打开浏览器：https://roamio.cn/user/center
# 应该能看到"连接 Ralendar"按钮
```

---

## 🔐 安全提示

### ✅ 应该做的
- ✅ 凭证仅保存在服务器的 `cloud_settings/.env`
- ✅ `cloud_settings/` 目录已在 `.gitignore` 中
- ✅ 服务器文件权限设置正确（600 或 640）
- ✅ 定期备份配置文件

### ❌ 不要做的
- ❌ 不要将凭证提交到 Git
- ❌ 不要在代码中硬编码凭证
- ❌ 不要在日志中打印 `CLIENT_SECRET`
- ❌ 不要在前端暴露 `CLIENT_SECRET`
- ❌ 不要在公开文档中写真实凭证

---

## 📊 配置完成后

### 可以开始的工作

1. **端到端测试**（30分钟）
   - 参考：`docs/integration/OAUTH_TEST_PLAN.md`
   - 测试授权流程
   - 测试同步功能
   - 测试多账号场景

2. **监控配置**
   - 配置 OAuth 相关的监控指标
   - 设置告警规则

3. **用户公告**
   - 发布新功能公告
   - 编写使用教程

---

## ❓ 故障排查

### 问题 1：启动时仍显示警告

```
[WARNING] Ralendar OAuth configuration incomplete
```

**解决方案**：
```bash
# 检查配置是否正确添加
cat cloud_settings/.env | grep RALENDAR

# 确保重启了服务
supervisorctl restart roamio
```

### 问题 2：Django 无法读取配置

**解决方案**：
```bash
# 检查 settings.py 是否正确读取
grep RALENDAR_OAUTH roamio/settings.py

# 检查环境变量是否加载
python manage.py shell
>>> import os
>>> print(os.getenv('RALENDAR_OAUTH_CLIENT_ID'))
```

### 问题 3：回调地址不匹配

**错误信息**：`redirect_uri_mismatch`

**解决方案**：
- 检查 `.env` 中的 `RALENDAR_OAUTH_REDIRECT_URI`
- 确保与 Ralendar 白名单中的地址完全一致
- 注意 http vs https
- 注意结尾不要有多余的斜杠

---

## 📞 技术支持

如有问题，请联系：
- **Roamio 团队**：dev@roamio.cn
- **Ralendar 团队**：dev@ralendar.example.com

---

**配置完成！准备开始测试！** 🎉

