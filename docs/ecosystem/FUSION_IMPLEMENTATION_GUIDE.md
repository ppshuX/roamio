# 🔗 Roamio × Ralendar 融合实施指南

> **版本**: v1.0.0  
> **更新日期**: 2025-11-07  
> **状态**: QQ 授权已通过，准备实施  
> **预计时间**: 4-6 小时

---

## 🎯 融合目标

实现 Roamio 和 Ralendar 的深度融合：
1. ✅ **统一用户体系** - 一个账号，全生态通用
2. ✅ **JWT Token 互通** - 一次登录，处处可用
3. ✅ **数据互通** - 旅行计划 ↔ 日历事件
4. ✅ **功能联动** - 提醒、同步、推荐

---

## 🏗️ 融合架构

### **方案：共享数据库 + 统一认证**

```
┌─────────────────────────────────────────────────────────┐
│                  统一数据库（PostgreSQL/MySQL）          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  auth_user (Django 内置)                         │  │
│  │  ├── id, username, email, password               │  │
│  │  └── 两个项目共享                                 │  │
│  ├──────────────────────────────────────────────────┤  │
│  │  backend_userprofile (Roamio)                    │  │
│  │  backend_socialaccount (Roamio)                  │  │
│  │  backend_trip (Roamio)                           │  │
│  │  backend_comment (Roamio)                        │  │
│  ├──────────────────────────────────────────────────┤  │
│  │  ralendar_event (Ralendar)                       │  │
│  │  ralendar_calendar (Ralendar)                    │  │
│  │  ralendar_subscription (Ralendar)                │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
    Roamio Backend                      Ralendar Backend
    (Django on 8000)                    (Django on 8001)
        │                                     │
        └──────────────────┬──────────────────┘
                           │
                    相同的 SECRET_KEY
                    (JWT Token 互通)
```

---

## 📋 实施步骤

### **Phase 1: 数据库准备**

#### 1.1 安装 PostgreSQL（推荐）

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### 1.2 创建共享数据库

```bash
# 切换到 postgres 用户
sudo -u postgres psql

# 创建数据库
CREATE DATABASE roamio_ecosystem;

# 创建用户
CREATE USER roamio_user WITH PASSWORD 'your_secure_password_here';

# 授权
GRANT ALL PRIVILEGES ON DATABASE roamio_ecosystem TO roamio_user;

# 退出
\q
```

#### 1.3 安装 Python 依赖

```bash
# Roamio
cd ~/roamio
pip3 install psycopg2-binary

# Ralendar
cd ~/ralendar
pip3 install psycopg2-binary
```

---

### **Phase 2: Roamio 数据迁移**

#### 2.1 备份当前数据

```bash
cd ~/roamio

# 备份 SQLite 数据库
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)
```

#### 2.2 导出数据

```bash
# 导出所有数据为 JSON
python3 manage.py dumpdata --natural-foreign --natural-primary \
    --exclude contenttypes --exclude auth.permission \
    --exclude sessions.session --exclude admin.logentry \
    > roamio_data_backup.json
```

#### 2.3 更新 Roamio 配置

```python
# roamio/settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'roamio_ecosystem',
        'USER': 'roamio_user',
        'PASSWORD': 'your_secure_password_here',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# ⭐ 统一 SECRET_KEY（重要！）
SECRET_KEY = 'roamio-ecosystem-unified-secret-key-2025-secure-random-string'
```

#### 2.4 迁移数据到 PostgreSQL

```bash
# 创建表结构
python3 manage.py migrate

# 导入数据
python3 manage.py loaddata roamio_data_backup.json

# 验证数据
python3 manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.count()
>>> exit()
```

---

### **Phase 3: Ralendar 配置**

#### 3.1 更新 Ralendar 配置

```python
# ralendar/settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'roamio_ecosystem',  # ⭐ 相同的数据库
        'USER': 'roamio_user',
        'PASSWORD': 'your_secure_password_here',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# ⭐ 相同的 SECRET_KEY（重要！）
SECRET_KEY = 'roamio-ecosystem-unified-secret-key-2025-secure-random-string'

# JWT 配置（与 Roamio 保持一致）
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,  # ⭐ 使用相同的密钥
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

#### 3.2 迁移 Ralendar 数据

```bash
cd ~/ralendar

# 备份当前数据
python3 manage.py dumpdata > ralendar_data_backup.json

# 迁移表结构
python3 manage.py migrate

# 导入数据
python3 manage.py loaddata ralendar_data_backup.json
```

---

### **Phase 4: 测试融合效果**

#### 4.1 测试跨项目登录

```bash
# 测试 1：在 Roamio 登录
curl -X POST https://app7508.acapp.acwing.com.cn/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "test_user", "password": "test_password"}'

# 获取 access_token

# 测试 2：使用相同 Token 访问 Ralendar
curl -X GET https://ralendar.com/api/auth/me/ \
  -H "Authorization: Bearer <access_token>"

# 应该返回相同的用户信息
```

#### 4.2 测试 QQ 登录互通

```
1. 用户在 Roamio 使用 QQ 登录
   ↓
2. 获取 JWT Token
   ↓
3. 使用相同 Token 访问 Ralendar
   ↓
4. Ralendar 自动识别用户（因为共享 auth_user 表）
```

---

### **Phase 5: 实现数据互通 API**

#### 5.1 旅行计划同步到日历

在 Roamio 中添加同步接口：

```python
# backend/api/viewsets/trip_viewset.py

from rest_framework.decorators import action
from rest_framework.response import Response
import requests

class TripViewSet(viewsets.ModelViewSet):
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def sync_to_calendar(self, request, slug=None):
        """
        将旅行计划同步到 Ralendar 日历
        
        这个接口会：
        1. 提取旅行计划的日期和行程
        2. 调用 Ralendar API 创建对应的日程事件
        3. 返回同步结果
        """
        trip = self.get_object()
        
        # 检查权限：只有作者可以同步
        if trip.author != request.user:
            return Response({
                'error': '只有作者可以同步旅行计划'
            }, status=403)
        
        # 获取用户的 JWT Token
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        user_token = auth_header.replace('Bearer ', '')
        
        # 准备同步的事件
        events_to_create = []
        
        # 1. 出发前提醒（提前3天）
        if trip.start_date:
            events_to_create.append({
                'title': f'准备出发：{trip.title}',
                'description': '检查证件、打包行李、确认酒店',
                'start_time': (trip.start_date - timedelta(days=3)).isoformat(),
                'reminder_minutes': 1440,  # 提前1天提醒
                'related_trip_slug': trip.slug
            })
        
        # 2. 每日行程
        if trip.start_date and trip.end_date:
            current_date = trip.start_date
            day_number = 1
            while current_date <= trip.end_date:
                events_to_create.append({
                    'title': f'{trip.title} - 第{day_number}天',
                    'description': trip.description,
                    'start_time': current_date.isoformat(),
                    'all_day': True,
                    'related_trip_slug': trip.slug
                })
                current_date += timedelta(days=1)
                day_number += 1
        
        # 3. 回来后整理提醒（结束后1天）
        if trip.end_date:
            events_to_create.append({
                'title': f'整理回忆：{trip.title}',
                'description': '整理照片、写游记、分享体验',
                'start_time': (trip.end_date + timedelta(days=1)).isoformat(),
                'reminder_minutes': 480  # 提前8小时提醒
            })
        
        # 调用 Ralendar API 批量创建事件
        ralendar_api_base = 'http://localhost:8001/api'  # Ralendar API 地址
        synced_events = []
        
        for event_data in events_to_create:
            try:
                response = requests.post(
                    f'{ralendar_api_base}/events/',
                    json=event_data,
                    headers={'Authorization': f'Bearer {user_token}'},
                    timeout=10
                )
                
                if response.status_code == 201:
                    synced_events.append(response.json())
            except Exception as e:
                print(f'Failed to sync event: {e}')
        
        return Response({
            'success': True,
            'message': f'成功同步 {len(synced_events)} 个事件到日历',
            'synced_events': synced_events
        })
```

#### 5.2 在 Ralendar 中添加接收接口

```python
# ralendar/api/views/events.py

class EventViewSet(viewsets.ModelViewSet):
    
    def perform_create(self, serializer):
        """创建事件时自动设置用户"""
        serializer.save(user=self.request.user)
```

---

## 🔐 安全考虑

### **1. SECRET_KEY 管理**

```bash
# 生成安全的 SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# 将其保存到环境变量
echo "SECRET_KEY='your_generated_key'" >> ~/.bashrc
source ~/.bashrc
```

### **2. 数据库密码**

```bash
# 使用强密码
# 至少 16 位，包含大小写字母、数字、特殊字符
```

### **3. CORS 配置**

```python
# Roamio settings.py
CORS_ALLOWED_ORIGINS = [
    'https://app7508.acapp.acwing.com.cn',  # Roamio
    'https://app7626.acapp.acwing.com.cn',  # Ralendar
]

# Ralendar settings.py
CORS_ALLOWED_ORIGINS = [
    'https://app7508.acapp.acwing.com.cn',  # Roamio
    'https://app7626.acapp.acwing.com.cn',  # Ralendar
]
```

---

## 🧪 测试方案

### **测试 1：跨项目登录**

```bash
# 1. 在 Roamio 登录
TOKEN=$(curl -X POST https://app7508.acapp.acwing.com.cn/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test"}' \
  | jq -r '.access')

# 2. 使用相同 Token 访问 Ralendar
curl -X GET http://localhost:8001/api/auth/me/ \
  -H "Authorization: Bearer $TOKEN"

# 应该返回相同的用户信息
```

### **测试 2：QQ 登录互通**

```
1. 用户在 Roamio 使用 QQ 登录
2. 获取 JWT Token
3. 在 Ralendar 中使用相同 Token
4. 验证用户信息一致
```

### **测试 3：数据同步**

```
1. 在 Roamio 创建旅行计划
2. 点击"同步到日历"
3. 在 Ralendar 中查看日程
4. 验证事件已创建
```

---

## ⚠️ 注意事项

### **1. 数据库迁移顺序**

```
重要：必须按顺序执行！

1. 备份 Roamio 数据（SQLite）
2. 备份 Ralendar 数据（SQLite）
3. 创建 PostgreSQL 数据库
4. 迁移 Roamio 数据
5. 迁移 Ralendar 数据
6. 测试验证
```

### **2. SECRET_KEY 同步**

```
⚠️ 两个项目必须使用完全相同的 SECRET_KEY！
否则 JWT Token 无法互通！
```

### **3. 数据库表前缀**

```
Roamio 表：backend_xxx
Ralendar 表：ralendar_xxx

不会冲突，可以共存！
```

### **4. 回滚方案**

```bash
# 如果出现问题，可以快速回滚

# Roamio 回滚
cd ~/roamio
cp db.sqlite3.backup db.sqlite3
# 恢复 settings.py 中的数据库配置

# Ralendar 回滚
cd ~/ralendar
# 恢复 settings.py 中的数据库配置
```

---

## 📊 融合前后对比

### **融合前**

| 特性 | Roamio | Ralendar |
|------|--------|----------|
| 用户表 | 独立 | 独立 |
| 数据库 | SQLite | SQLite |
| Token | 不互通 | 不互通 |
| 数据 | 隔离 | 隔离 |

**问题**：
- ❌ 用户需要注册两次
- ❌ 数据无法互通
- ❌ 功能无法联动

### **融合后**

| 特性 | Roamio | Ralendar |
|------|--------|----------|
| 用户表 | **共享** | **共享** |
| 数据库 | **PostgreSQL** | **PostgreSQL** |
| Token | **互通** | **互通** |
| 数据 | **互通** | **互通** |

**优势**：
- ✅ 一个账号，全生态通用
- ✅ 数据实时同步
- ✅ 功能深度联动
- ✅ 用户体验极佳

---

## 🚀 融合后的功能

### **1. 统一登录**

```
用户在 Roamio 注册/登录
    ↓
获取 JWT Token
    ↓
在 Ralendar 中使用相同 Token
    ↓
自动识别用户，无需重新登录
```

### **2. 旅行 → 日历**

```
用户在 Roamio 创建"云南7日游"
    ↓
点击"同步到日历"
    ↓
Ralendar 自动创建：
- 出发前提醒（提前3天）
- 每日行程（7个事件）
- 回来后整理提醒（结束后1天）
```

### **3. 日历 → 旅行**

```
用户在 Ralendar 订阅"樱花季提醒"
    ↓
3月初收到提醒
    ↓
Roamio 推送相关攻略
    ↓
一键创建旅行计划
```

---

## 📞 联系方式

- **邮箱**: 2064747320@qq.com
- **项目地址**: https://github.com/ppshuX/roamio

---

## 🎯 下一步行动

### **立即执行**（QQ 授权已通过）

1. ⏰ **今天**：数据库准备 + Roamio 迁移
2. ⏰ **明天**：Ralendar 配置 + 测试融合
3. ⏰ **后天**：实现数据互通 API

### **本周完成**

- ✅ 统一用户体系
- ✅ JWT Token 互通
- ✅ 基础数据同步

### **下周完成**

- ✅ 功能深度联动
- ✅ 前端集成
- ✅ 完整测试

---

**最后更新**: 2025-11-07  
**维护者**: Roamio Team  
**状态**: 准备实施 🚀

