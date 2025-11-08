# 🔐 环境变量配置文档

> **更新时间**: 2025-11-08  
> **用途**: 生产环境 `.env` 文件配置

---

## 📋 完整的 `.env` 文件内容

将以下内容保存为 `cloud_settings/.env`（服务器上）：

```bash
# ==================== Django 核心配置 ====================
# ⚠️ 重要：与 Ralendar 共享相同的 SECRET_KEY 以实现 JWT Token 互认
SECRET_KEY=django-insecure-#6avwo7=$9vse4txxj!phdfx5-ql(bc5otpoiw@x)u0i+^1-5h

# 调试模式（生产环境设为 False）
DEBUG=False

# ==================== AcWing 配置 ====================
ACWING_APPID=7626
ACWING_SECRET=7030aff130bd41c9876413211fe406af

# ==================== QQ 互联配置 ====================
QQ_APPID=102818448
QQ_APPKEY=sZ0B7nDQP8Bzb1JP

# ==================== 邮件配置 (QQ邮箱) ====================
EMAIL_HOST=smtp.qq.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=2064747320@qq.com
EMAIL_HOST_PASSWORD=zwcqgzukwkfyeaja
DEFAULT_FROM_EMAIL=2064747320@qq.com

# ==================== Celery/Redis 配置 ====================
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# ==================== 提醒设置 ====================
REMINDER_ADVANCE_MINUTES=15

# ==================== Ralendar 集成配置 ====================
RALENDAR_API_URL=https://app7626.acapp.acwing.com.cn/api/v1
```

---

## 🔄 与旧配置的对比

### **改进点**

1. ✅ **添加了 `SECRET_KEY`**（与 Ralendar 共享）
2. ✅ **去除了重复的配置**（旧文件中 ACWING 和 QQ 配置重复了）
3. ✅ **添加了 `RALENDAR_API_URL`**（Ralendar 集成）
4. ✅ **添加了清晰的分类注释**

### **删除的重复项**

旧配置中这些行是重复的（已删除）：
```bash
# 第 1-6 行与第 10-14 行重复
ACWING_APPID=7626
ACWING_SECRET=7030aff130bd41c9876413211fe406af
QQ_APPID=102818448
QQ_APPKEY=sZ0B7nDQP8Bzb1JP
DEBUG=False
```

---

## 🚀 部署步骤

### **方法 1: 直接在服务器上编辑**

```bash
# SSH 登录服务器
ssh acs@47.121.137.60

# 编辑 .env 文件
cd ~/roamio/cloud_settings
nano .env

# 粘贴上面的完整配置
# 保存：Ctrl+O, 回车
# 退出：Ctrl+X

# 重启服务
cd ~/roamio
pkill -9 -f uwsgi
nohup uwsgi --ini cloud_settings/uwsgi.ini > logs/uwsgi.log 2>&1 &
```

---

### **方法 2: 从本地上传**

```bash
# 在本地创建 .env 文件
# 文件路径：cloud_settings/.env
# 内容：见上面的完整配置

# 上传到服务器
scp cloud_settings/.env acs@47.121.137.60:~/roamio/cloud_settings/.env

# SSH 登录服务器并重启
ssh acs@47.121.137.60
cd ~/roamio
pkill -9 -f uwsgi
nohup uwsgi --ini cloud_settings/uwsgi.ini > logs/uwsgi.log 2>&1 &
```

---

## 🔍 验证配置

### **1. 检查 SECRET_KEY 是否生效**

```bash
# 在服务器上
cd ~/roamio
python3 manage.py shell

# 在 Python shell 中
>>> from django.conf import settings
>>> print(settings.SECRET_KEY)
# 应该输出：django-insecure-#6avwo7=$9vse4txxj!phdfx5-ql(bc5otpoiw@x)u0i+^1-5h
```

### **2. 检查 Ralendar API URL**

```bash
>>> print(settings.RALENDAR_API_URL)
# 应该输出：https://app7626.acapp.acwing.com.cn/api/v1
```

### **3. 测试 JWT Token**

```bash
# 登录 Roamio 获取 Token
curl -X POST https://app7508.acapp.acwing.com.cn/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# 使用 Token 访问 Ralendar API
curl -X GET https://app7626.acapp.acwing.com.cn/api/v1/events/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 如果返回 200 而不是 401，说明 SECRET_KEY 配置成功！
```

---

## ⚠️ 安全提醒

### **1. 不要提交 `.env` 到 Git**

确保 `.gitignore` 包含：
```
.env
cloud_settings/.env
*.env
```

### **2. 定期更换密钥**

生产环境建议：
- 每 3-6 个月更换一次 SECRET_KEY
- 更换后需要所有用户重新登录

### **3. 备份配置**

```bash
# 在服务器上备份
cp cloud_settings/.env cloud_settings/.env.backup.$(date +%Y%m%d)
```

---

## 📊 配置项说明

| 配置项 | 用途 | 是否必需 |
|--------|------|----------|
| `SECRET_KEY` | JWT Token 签名 | ✅ 必需 |
| `DEBUG` | 调试模式 | ✅ 必需 |
| `ACWING_APPID` | AcWing 登录 | 可选 |
| `QQ_APPID` | QQ 登录 | ✅ 必需 |
| `EMAIL_HOST_USER` | 邮件发送 | ✅ 必需 |
| `CELERY_BROKER_URL` | 异步任务 | 可选 |
| `RALENDAR_API_URL` | Ralendar 集成 | ✅ 必需 |

---

## 🆘 常见问题

### **Q1: 修改 SECRET_KEY 后用户无法登录？**

**A**: 这是正常的。修改 SECRET_KEY 后，旧的 Token 会失效。用户需要重新登录。

---

### **Q2: 如何在 settings.py 中读取 .env？**

**A**: 已配置好，使用 `python-dotenv`：

```python
# roamio/settings.py
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-key')
```

---

### **Q3: .env 文件位置？**

**A**: 
- **开发环境**: `roamio/.env`（项目根目录）
- **生产环境**: `roamio/cloud_settings/.env`（服务器配置目录）

---

## 📞 技术支持

如有问题，请联系：
- **开发者**: ppshuX
- **QQ**: 2064747320

---

**最后更新**: 2025-11-08  
**文档版本**: v1.0

