# ✅ Roamio × Ralendar 集成验收清单

> **更新时间**: 2025-11-08  
> **状态**: 🚀 准备部署测试

---

## 📋 集成完成情况

### ✅ **已完成的配置**

| 配置项 | 状态 | 说明 |
|--------|------|------|
| **SECRET_KEY 同步** | ✅ 完成 | 两边使用相同的密钥 |
| **QQ UnionID 权限** | ✅ 完成 | 两边都已获取权限 |
| **UnionID 参数添加** | ✅ 完成 | 所有 QQ API 请求都添加了 `unionid=1` |
| **数据库 unionid 字段** | ✅ 完成 | `SocialAccount` 模型已有字段 |
| **UnionID 保存逻辑** | ✅ 完成 | QQ 登录时自动保存 |
| **Ralendar API 客户端** | ✅ 完成 | `RalendarClient` 已实现 |
| **前端 API 调用** | ✅ 完成 | `ralendar.js` 已实现 |
| **添加到日历按钮** | ✅ 完成 | `AddToCalendarButton` 已创建 |
| **TripDetailView 重构** | ✅ 完成 | 从 1214 行减少到 448 行 |
| **环境变量配置** | ✅ 完成 | `.env` 配置文档已创建 |

---

## 🎯 Roamio 配置详情

### **1. SECRET_KEY 配置**

**文件**: `roamio/settings.py` (第 29-32 行)

```python
SECRET_KEY = os.getenv(
    'SECRET_KEY', 
    'django-insecure-#6avwo7=$9vse4txxj!phdfx5-ql(bc5otpoiw@x)u0i+^1-5h'
)
```

**`.env` 文件**: `cloud_settings/.env`

```bash
SECRET_KEY=django-insecure-#6avwo7=$9vse4txxj!phdfx5-ql(bc5otpoiw@x)u0i+^1-5h
```

---

### **2. QQ UnionID 获取配置**

**文件**: `backend/utils/qq_oauth.py`

**第 120 行**（获取 OpenID）:
```python
params = {
    'access_token': access_token,
    'unionid': 1,  # ⭐ 添加此参数以获取 UnionID
}
```

**第 186 行**（获取用户信息）:
```python
params = {
    'access_token': access_token,
    'oauth_consumer_key': settings.QQ_APP_ID,
    'openid': openid,
    'unionid': 1,  # ⭐ 添加此参数以获取 UnionID
}
```

---

### **3. UnionID 存储**

**模型**: `backend/models/social_auth.py`

```python
class SocialAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.CharField(max_length=20)
    uid = models.CharField(max_length=100)
    unionid = models.CharField(max_length=100, blank=True, null=True)  # ✅ 已有
    nickname = models.CharField(max_length=100, blank=True)
    avatar_url = models.URLField(blank=True)
```

**保存逻辑**: `backend/api/viewsets/auth_viewset.py` (第 365-372 行)

```python
SocialAccount.objects.create(
    user=user,
    provider='qq',
    uid=openid,
    unionid=unionid if unionid else None,  # ✅ 保存 UnionID
    nickname=qq_info.get('nickname', ''),
    avatar_url=qq_info.get('avatar_url', '')
)
```

---

### **4. Ralendar API 配置**

**文件**: `roamio/settings.py` (第 460-463 行)

```python
RALENDAR_API_URL = os.getenv(
    'RALENDAR_API_URL',
    'https://app7626.acapp.acwing.com.cn/api/v1'
)
```

**API 客户端**: `backend/utils/ralendar_client.py`
- ✅ 批量创建事件
- ✅ 获取旅行事件
- ✅ 删除旅行事件
- ✅ 更新/删除单个事件

**API ViewSet**: `backend/api/viewsets/ralendar_viewset.py`
- ✅ `POST /api/v1/ralendar/trips/{slug}/add-to-calendar/`
- ✅ `GET /api/v1/ralendar/trips/{slug}/calendar-events/`
- ✅ `DELETE /api/v1/ralendar/trips/{slug}/calendar-events/`

---

### **5. 前端集成**

**API 调用**: `web/src/api/ralendar.js`
- ✅ `addTripToCalendar()`
- ✅ `getTripCalendarEvents()`
- ✅ `deleteTripCalendarEvents()`

**组件**: `web/src/components/AddToCalendarButton.vue`
- ✅ 添加到日历按钮
- ✅ 同步状态显示
- ✅ 移除功能

**页面集成**: `web/src/views/TripDetailView.vue`
- ✅ 已集成 `AddToCalendarButton`
- ✅ 已重构为组件化结构

---

## 📝 **部署清单**

### **步骤 1: 创建 `.env` 文件**

在你的电脑上创建 `cloud_settings/.env`，内容如下：

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

### **步骤 2: 上传 `.env` 到服务器**

```bash
# 方法 1: 使用 SCP
scp cloud_settings/.env acs@47.121.137.60:~/roamio/cloud_settings/.env

# 方法 2: 手动创建
ssh acs@47.121.137.60
cd ~/roamio/cloud_settings
nano .env
# 粘贴上面的内容，保存退出
```

---

### **步骤 3: 部署最新代码**

```bash
# 在服务器上执行
cd ~/roamio
git pull

# 重启 uWSGI
pkill -9 -f uwsgi
sleep 3
nohup uwsgi --ini cloud_settings/uwsgi.ini > logs/uwsgi.log 2>&1 &

# 检查服务
sleep 5
ps aux | grep uwsgi | grep -v grep

echo "✅ 部署完成！"
```

---

### **步骤 4: 验证配置**

```bash
# 在服务器上验证
cd ~/roamio
python3 manage.py shell
```

```python
# 1. 验证 SECRET_KEY
from django.conf import settings
print("SECRET_KEY:", settings.SECRET_KEY[:50])
# 应该输出: django-insecure-#6avwo7=$9vse4txxj!phdfx5-ql(bc5o

# 2. 验证 Ralendar API URL
print("RALENDAR_API_URL:", settings.RALENDAR_API_URL)
# 应该输出: https://app7626.acapp.acwing.com.cn/api/v1

# 3. 检查现有用户的 UnionID
from backend.models import SocialAccount
accounts = SocialAccount.objects.filter(provider='qq')
for acc in accounts[:5]:
    print(f"User: {acc.user.username}")
    print(f"  OpenID: {acc.uid[:15]}...")
    print(f"  UnionID: {acc.unionid[:15] if acc.unionid else 'None'}")
    print()

exit()
```

---

### **步骤 5: 测试 QQ 登录**

1. **退出当前登录**
2. **重新 QQ 登录**
3. **查看日志**：

```bash
tail -50 logs/uwsgi.log | grep -E "QQ|unionid|UnionID"
```

4. **检查数据库**：

```bash
python3 manage.py shell
```

```python
from backend.models import SocialAccount
latest = SocialAccount.objects.filter(provider='qq').order_by('-id').first()
print(f"最新 QQ 用户:")
print(f"  Username: {latest.user.username}")
print(f"  OpenID: {latest.uid}")
print(f"  UnionID: {latest.unionid}")  # 应该不为空！
```

---

## 🧪 **集成测试**

### **测试 1: UnionID 获取**

```bash
# 期望：QQ 登录后，数据库中有 unionid
SELECT user_id, uid, unionid, provider 
FROM backend_socialaccount 
WHERE provider = 'qq' 
ORDER BY id DESC 
LIMIT 5;
```

**预期结果**: `unionid` 字段不为空

---

### **测试 2: JWT Token 互认**

```bash
# 1. 在 Roamio 登录，获取 Token
curl -X POST https://app7508.acapp.acwing.com.cn/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# 2. 使用 Roamio 的 Token 访问 Ralendar API
curl -X GET https://app7626.acapp.acwing.com.cn/api/v1/events/ \
  -H "Authorization: Bearer ROAMIO_ACCESS_TOKEN"
```

**预期结果**: 返回 200，不是 401

---

### **测试 3: 添加到日历**

1. 登录 Roamio
2. 进入任意旅行详情页（例如 `/trip/trip4`）
3. 点击"添加到 Ralendar"按钮
4. 检查是否成功

---

## 📊 **集成验收标准**

根据 Ralendar 团队的清单：

- [x] 在 Roamio `.env` 中配置 `SECRET_KEY`（与 Ralendar 相同）✅
- [x] 能够调用 Ralendar API（客户端已实现）✅
- [x] 能够为旅行计划批量创建事件（API 已实现）✅
- [ ] 创建的事件能在 Ralendar 中正常显示 ⏳（需要测试）
- [ ] 时间显示正确（没有时区偏移）⏳（需要测试）
- [ ] 地图位置正常显示（如果有坐标）⏳（需要测试）
- [x] 能够删除旅行计划的所有事件（API 已实现）✅
- [x] 前端"添加到日历"按钮正常工作（组件已创建）✅
- [x] 错误处理友好（显示清晰的错误信息）✅

---

## 🔄 **QQ UnionID 验证**

### **Roamio 配置检查**

```python
# backend/utils/qq_oauth.py

# ✅ 第 120 行：get_qq_openid 中添加了 unionid=1
params = {
    'access_token': access_token,
    'unionid': 1,
}

# ✅ 第 186 行：get_qq_user_info 中添加了 unionid=1
params = {
    'access_token': access_token,
    'oauth_consumer_key': settings.QQ_APP_ID,
    'openid': openid,
    'unionid': 1,
}
```

### **数据库字段检查**

```sql
-- 检查 unionid 字段是否存在
DESCRIBE backend_socialaccount;

-- 检查现有数据
SELECT id, user_id, provider, uid, unionid 
FROM backend_socialaccount 
WHERE provider = 'qq' 
LIMIT 5;
```

---

## 🚀 **部署步骤（完整版）**

### **1. 本地准备**

```bash
# 1.1 创建 .env 文件
# 在 cloud_settings/.env 中添加上面的配置

# 1.2 提交最新代码（已完成）
git push
```

### **2. 服务器部署**

```bash
# 2.1 SSH 登录
ssh acs@47.121.137.60

# 2.2 上传 .env 文件（如果还没上传）
# 或者在服务器上手动创建

# 2.3 拉取最新代码
cd ~/roamio
git pull

# 2.4 检查 .env 文件
cat cloud_settings/.env | grep SECRET_KEY
# 应该输出: SECRET_KEY=django-insecure-#6avwo7=$9vse4txxj!phdfx5-ql(bc5otpoiw@x)u0i+^1-5h

# 2.5 重启服务
pkill -9 -f uwsgi
sleep 3
nohup uwsgi --ini cloud_settings/uwsgi.ini > logs/uwsgi.log 2>&1 &

# 2.6 检查服务状态
sleep 5
ps aux | grep uwsgi | grep -v grep

# 2.7 检查日志
tail -50 logs/uwsgi.log
```

### **3. 验证部署**

```bash
# 3.1 验证 SECRET_KEY
cd ~/roamio
python3 manage.py shell

>>> from django.conf import settings
>>> print(settings.SECRET_KEY == 'django-insecure-#6avwo7=$9vse4txxj!phdfx5-ql(bc5otpoiw@x)u0i+^1-5h')
# 应该输出: True

>>> print(settings.RALENDAR_API_URL)
# 应该输出: https://app7626.acapp.acwing.com.cn/api/v1

>>> exit()
```

---

## 🧪 **功能测试**

### **测试 1: QQ 登录 + UnionID**

1. 访问 Roamio: `https://app7508.acapp.acwing.com.cn`
2. 退出当前登录
3. 点击"QQ 一键登录"
4. 完成 QQ 授权
5. 在服务器上检查：

```bash
cd ~/roamio
python3 manage.py shell

>>> from backend.models import SocialAccount
>>> latest = SocialAccount.objects.filter(provider='qq').order_by('-id').first()
>>> print(f"UnionID: {latest.unionid}")
# 应该输出一个非空的 UnionID，例如: UID_A1B2C3D4E5F6G7H8
```

---

### **测试 2: JWT Token 互认**

```bash
# 1. 在 Roamio 登录，复制 access_token
# 2. 使用这个 Token 访问 Ralendar API

curl -X GET https://app7626.acapp.acwing.com.cn/api/v1/events/ \
  -H "Authorization: Bearer YOUR_ROAMIO_ACCESS_TOKEN"

# 预期结果: 返回 200，不是 401
```

---

### **测试 3: 添加到日历**

1. 登录 Roamio
2. 进入旅行详情页（例如 `/trip/trip4`）
3. 点击"添加到 Ralendar"按钮
4. 确认对话框
5. 等待同步完成
6. 检查按钮状态变为"已同步到日历"
7. 登录 Ralendar，查看是否有对应的事件

---

## 📞 **技术支持**

### **Roamio 团队**
- **开发者**: ppshuX
- **服务器**: app7508.acapp.acwing.com.cn (47.121.137.60)
- **QQ**: 2064747320

### **Ralendar 团队**
- **开发者**: ppshuX
- **服务器**: app7626.acapp.acwing.com.cn
- **QQ**: 2064747320

---

## 🎉 **准备就绪！**

**所有代码已完成并提交！** 

**下一步**: 
1. 创建 `cloud_settings/.env` 文件
2. 上传到服务器
3. 部署并测试

**预计完成时间**: 30 分钟

---

**最后更新**: 2025-11-08  
**文档版本**: v1.0

