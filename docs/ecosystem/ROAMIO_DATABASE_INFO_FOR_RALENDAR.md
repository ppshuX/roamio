# 🔑 Roamio 数据库信息 - 提供给 Ralendar 团队

> **文档版本**: v1.0  
> **更新日期**: 2025-11-08  
> **状态**: 待提供数据库信息

---

## ⚠️ **重要说明**

Roamio 当前使用 **SQLite 本地数据库**，需要先迁移到腾讯云 MySQL/PostgreSQL 才能与 Ralendar 共享数据库。

---

## 📊 **当前数据库状态**

### 数据库类型
```python
# roamio/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # 本地文件
    }
}
```

### SECRET_KEY
```python
SECRET_KEY = 'django-insecure-*il-h$$9=73a(2g5g_edot=!#$je=r@ey7(ov0s1uyitc@@o9m'
```

---

## ✅ **已完成的准备工作**

### 1. QQ UnionID 权限
- ✅ 已在 QQ 互联平台获取 UnionID 权限
- ✅ 代码已添加 `unionid=1` 参数
- ✅ 数据库模型已有 `unionid` 字段
- ✅ 登录逻辑已保存 UnionID

### 2. 数据库模型
```python
# backend/models/social_auth.py
class SocialAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.CharField(max_length=20)  # 'qq', 'wechat', 'github'
    uid = models.CharField(max_length=100)  # QQ openid
    unionid = models.CharField(max_length=100, blank=True, null=True)  # ⭐ UnionID
    nickname = models.CharField(max_length=100, blank=True)
    avatar_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### 3. QQ OAuth 配置
```python
# Roamio QQ 应用信息
QQ_APP_ID = '102813859'
QQ_APP_KEY = 'OddPvLYXHo69wTYO'
QQ_REDIRECT_URI = 'https://app7508.acapp.acwing.com.cn/api/v1/auth/qq/callback/'
```

---

## 🚀 **迁移到腾讯云数据库计划**

### 方案 A：腾讯云 MySQL（推荐）

#### 步骤 1：购买腾讯云 MySQL
```
腾讯云控制台 → 云数据库 MySQL
- 地域：与服务器相同（华东）
- 规格：1核1G（入门级，约 ¥0.3/小时）
- 存储：20GB
- 网络：VPC（与服务器在同一 VPC）
```

#### 步骤 2：创建数据库和用户
```sql
-- 连接到 MySQL
mysql -h rm-xxx.mysql.rds.tencentcdb.com -u root -p

-- 创建数据库
CREATE DATABASE roamio_production CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建 Roamio 用户
CREATE USER 'roamio_user'@'%' IDENTIFIED BY 'roamio_secure_password_2025';
GRANT ALL PRIVILEGES ON roamio_production.* TO 'roamio_user'@'%';

-- 创建 Ralendar 用户（只读+写入必要表）
CREATE USER 'ralendar_user'@'81.71.138.122' IDENTIFIED BY 'ralendar_secure_password_2025';

-- 授予 Ralendar 访问 auth_user 表的权限
GRANT SELECT, INSERT, UPDATE ON roamio_production.auth_user TO 'ralendar_user'@'81.71.138.122';
GRANT SELECT, INSERT, UPDATE ON roamio_production.auth_permission TO 'ralendar_user'@'81.71.138.122';
GRANT SELECT, INSERT, UPDATE ON roamio_production.auth_group TO 'ralendar_user'@'81.71.138.122';
GRANT SELECT, INSERT, UPDATE ON roamio_production.django_session TO 'ralendar_user'@'81.71.138.122';
GRANT SELECT, INSERT, UPDATE ON roamio_production.social_account TO 'ralendar_user'@'81.71.138.122';

-- Ralendar 自己的表（完全控制）
GRANT ALL PRIVILEGES ON roamio_production.api_* TO 'ralendar_user'@'81.71.138.122';
GRANT ALL PRIVILEGES ON roamio_production.calendar_* TO 'ralendar_user'@'81.71.138.122';

FLUSH PRIVILEGES;
```

#### 步骤 3：配置白名单
```
腾讯云控制台 → 云数据库 MySQL → 安全组
添加入站规则：
- 来源：47.121.137.60（Roamio 服务器）
- 来源：81.71.138.122（Ralendar 服务器）
- 端口：3306
```

#### 步骤 4：迁移数据
```bash
# 1. 导出 SQLite 数据
cd ~/roamio
python3 manage.py dumpdata --natural-foreign --natural-primary \
  --exclude contenttypes --exclude auth.permission \
  > roamio_data.json

# 2. 安装 MySQL 驱动
pip install mysqlclient

# 3. 修改 settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'roamio_production',
        'USER': 'roamio_user',
        'PASSWORD': os.environ.get('DB_PASSWORD', 'roamio_secure_password_2025'),
        'HOST': 'rm-xxx.mysql.rds.tencentcdb.com',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# 4. 创建表结构
python3 manage.py migrate

# 5. 导入数据
python3 manage.py loaddata roamio_data.json

# 6. 验证数据
python3 manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.count()  # 应该显示用户数量
>>> exit()

# 7. 重启服务
pkill -f uwsgi
bash scripts/start_uwsgi.sh
```

---

## 📋 **提供给 Ralendar 的信息清单**

### 迁移完成后，提供以下信息：

```bash
# ==================== 数据库连接信息 ====================
DB_TYPE=mysql
DB_HOST=rm-xxx.mysql.rds.tencentcdb.com
DB_PORT=3306
DB_NAME=roamio_production
DB_USER=ralendar_user
DB_PASSWORD=ralendar_secure_password_2025

# ==================== Django 配置 ====================
SECRET_KEY=django-insecure-*il-h$$9=73a(2g5g_edot=!#$je=r@ey7(ov0s1uyitc@@o9m

# ==================== QQ OAuth ====================
# Roamio 的 QQ 应用信息（用于 UnionID 匹配）
ROAMIO_QQ_APP_ID=102813859
ROAMIO_QQ_APP_KEY=OddPvLYXHo69wTYO

# ==================== 服务器信息 ====================
ROAMIO_SERVER_IP=47.121.137.60
ROAMIO_DOMAIN=app7508.acapp.acwing.com.cn

# ==================== Redis（可选）====================
# 如果 Ralendar 需要共用 Redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=  # 如果有密码
```

---

## 🔐 **安全建议**

### 1. 生成新的 SECRET_KEY（推荐）
```python
import secrets
new_secret = secrets.token_urlsafe(50)
print(new_secret)
# 输出：'xK8nP2mQ4vL9sR7tY6wZ3cV5bN1aM0hG...'

# 两个项目都使用这个新密钥
```

⚠️ **注意**：修改 SECRET_KEY 后，所有现有 Token 会失效，用户需要重新登录！

### 2. 数据库密码强度
```
建议密码格式：
- 长度：至少 16 位
- 包含：大小写字母、数字、特殊字符
- 示例：Roamio@2025!SecureDB#Pass
```

### 3. 定期备份
```bash
# 每天自动备份（添加到 crontab）
0 2 * * * mysqldump -h DB_HOST -u DB_USER -pDB_PASSWORD roamio_production > /backup/roamio_$(date +\%Y\%m\%d).sql
```

---

## 📊 **数据库表结构说明**

### 共享的表（Roamio 和 Ralendar 都使用）
```
auth_user              # 用户表（核心！）
auth_permission        # 权限表
auth_group             # 用户组
django_session         # Session 表
django_content_type    # 内容类型
social_account         # 第三方登录绑定（包含 UnionID）
```

### Roamio 独有的表
```
backend_trip           # 旅行表
backend_comment        # 评论表
backend_userprofile    # 用户资料扩展
backend_sitestat       # 网站统计
backend_emailverification  # 邮箱验证
backend_tripevent      # 旅行事件（与 Ralendar 对接）
```

### Ralendar 将创建的表
```
api_event              # 日程事件
api_publiccalendar     # 公共日历
api_acwinguser         # AcWing OAuth
api_qquser             # QQ OAuth（可能与 social_account 重复）
django_celery_beat_*   # Celery 定时任务
```

---

## 🧪 **测试验证步骤**

### 测试 1：Ralendar 连接数据库
```bash
# Ralendar 服务器上
cd ~/kotlin_calendar/backend
python3 manage.py shell

from django.db import connection
connection.ensure_connection()
print("✅ 数据库连接成功！")

from django.contrib.auth.models import User
users = User.objects.all()
print(f"共有 {users.count()} 个用户")
for u in users[:5]:
    print(f"  - {u.username} ({u.email})")
exit()
```

### 测试 2：UnionID 查询
```bash
# Ralendar 服务器上
python3 manage.py shell

from backend.models import SocialAccount
from django.contrib.auth.models import User

# 查找有 UnionID 的用户
accounts_with_unionid = SocialAccount.objects.filter(
    provider='qq',
    unionid__isnull=False
).select_related('user')

print(f"有 UnionID 的用户数：{accounts_with_unionid.count()}")
for acc in accounts_with_unionid[:5]:
    print(f"  - {acc.user.username}: UnionID={acc.unionid}")
exit()
```

### 测试 3：Token 互认
```bash
# 1. 在 Roamio 登录，获取 Token
# 2. 用这个 Token 访问 Ralendar API
curl -H "Authorization: Bearer ROAMIO_TOKEN" \
  https://app7626.acapp.acwing.com.cn/api/v1/events/

# 应该返回 200，不是 401
```

---

## 📞 **联系方式**

**Roamio 团队**
- 负责人：ppshuX
- QQ/邮箱：2064747320@qq.com
- 服务器：app7508.acapp.acwing.com.cn

**Ralendar 团队**
- 负责人：ppshuX
- QQ/邮箱：2064747320@qq.com
- 服务器：app7626.acapp.acwing.com.cn

---

## 📅 **时间表**

### 本周（2025-11-08 ~ 2025-11-14）
- [ ] 购买腾讯云 MySQL 数据库
- [ ] 配置数据库和用户
- [ ] 迁移 SQLite 数据到 MySQL
- [ ] 测试 Roamio 连接云数据库
- [ ] 提供数据库信息给 Ralendar

### 下周（2025-11-15 ~ 2025-11-21）
- [ ] Ralendar 配置数据库连接
- [ ] 测试 Token 互认
- [ ] 测试 UnionID 用户匹配
- [ ] 联调测试

### 第三周（2025-11-22 ~ 2025-11-28）
- [ ] 实现旅行同步到日历功能
- [ ] 前端集成测试
- [ ] 性能优化

---

## ✅ **当前状态总结**

| 项目 | 状态 | 说明 |
|------|------|------|
| QQ UnionID 权限 | ✅ 已获取 | 已在 QQ 互联平台开启 |
| UnionID 代码支持 | ✅ 已完成 | 已添加 `unionid=1` 参数 |
| 数据库模型 | ✅ 已完成 | `SocialAccount` 有 `unionid` 字段 |
| 登录逻辑 | ✅ 已完成 | 已保存 UnionID 到数据库 |
| 云数据库迁移 | ⏳ 待完成 | 当前使用 SQLite |
| 提供数据库信息 | ⏳ 待完成 | 迁移后提供 |

---

**下一步：迁移到腾讯云 MySQL 数据库！** 🚀

