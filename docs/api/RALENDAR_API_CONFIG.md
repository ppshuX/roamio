# 📅 Ralendar API 文档配置指南

> **适用项目**: Ralendar（日历助手）  
> **配置时机**: Ralendar 项目独立开发时  
> **参考规范**: `docs/API_STANDARDS.md`

---

## 🎯 配置目的

为 Ralendar 项目配置与 Roamio 相同的 API 文档系统，确保：
- ✅ API 文档风格统一
- ✅ 遵循相同的规范
- ✅ 未来融合时无缝对接

---

## 📋 配置步骤

### 1. 安装依赖

在 Ralendar 项目的 `requirements.txt` 中添加：

```txt
# Django REST Framework
djangorestframework==3.15.2
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.4.0
django-filter==24.3
drf-spectacular==0.27.2
```

### 2. 创建配置文件

在 Ralendar 项目中创建 `ralendar/api_docs_config.py`：

```python
"""
Ralendar API 文档配置

这个文件包含 drf-spectacular 的配置，用于生成 API 文档。
独立配置文件，方便管理和维护。

使用方式：
在 settings.py 中导入：
from ralendar.api_docs_config import SPECTACULAR_SETTINGS
"""

SPECTACULAR_SETTINGS = {
    'TITLE': 'Ralendar API 文档',
    'DESCRIPTION': '''
    📅 Ralendar - Roamio 生态日历助手
    
    ## 📚 关于 Ralendar
    Ralendar 是 Roamio 生态下的日历助手，提供：
    - 📆 日历管理（多日历支持）
    - 📝 事件管理（创建、编辑、删除）
    - 🔔 提醒功能（多种提醒方式）
    - 📬 订阅功能（节日、天气等）
    - 🔗 与 Roamio 旅行计划联动
    
    ## 🔐 认证方式
    本 API 使用 JWT (JSON Web Token) 进行身份认证。
    
    ### 获取 Token
    1. 通过 `/api/v1/auth/login/` 登录获取 access_token
    2. 在请求头中添加: `Authorization: Bearer <your_access_token>`
    
    ### Token 有效期
    - Access Token: 1 天
    - Refresh Token: 7 天
    
    ## 📡 API 版本
    当前版本: **v1**
    
    ## 🌐 多端支持
    - Android 原生端（主要）
    - Web 端（规划中）
    - 小程序端（规划中）
    
    ## 🔗 Roamio 生态
    - 🌍 Roamio: 旅行平台（主轴）
    - 📝 Rote: 笔记工具（规划中）
    - 📸 Rapture: 照片管理（规划中）
    
    ## 📋 API 规范
    详细的 API 规范请参考 Roamio 项目的 `docs/API_STANDARDS.md`
    ''',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'CONTACT': {
        'name': 'Roamio Team',
        'email': '2064747320@qq.com',
    },
    'LICENSE': {
        'name': 'MIT License',
    },
    
    # API 分组
    'TAGS': [
        {'name': '认证 (Auth)', 'description': '用户注册、登录、Token 管理等'},
        {'name': '日历 (Calendars)', 'description': '日历管理、多日历支持'},
        {'name': '事件 (Events)', 'description': '事件创建、编辑、删除、查询'},
        {'name': '提醒 (Reminders)', 'description': '提醒设置、通知管理'},
        {'name': '订阅 (Subscriptions)', 'description': '节日订阅、天气订阅等'},
        {'name': '同步 (Sync)', 'description': '与 Roamio 数据同步'},
    ],
    
    # 认证配置
    'SECURITY': [{'Bearer': []}],
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/v1',
    
    # UI 配置
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'filter': True,
        'defaultModelsExpandDepth': 2,
        'defaultModelExpandDepth': 2,
    },
    
    # 语言
    'LANGUAGE': 'zh-hans',
}
```

### 3. 更新 settings.py

在 Ralendar 项目的 `settings.py` 中：

#### 3.1 添加到 INSTALLED_APPS

```python
INSTALLED_APPS = [
    # ... 其他 apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',  # ⭐ API 文档
]
```

#### 3.2 配置 REST_FRAMEWORK

```python
REST_FRAMEWORK = {
    # 认证 - 统一使用 JWT
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    # 权限
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    # 分页
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    # 过滤、搜索、排序
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    # ⭐ API文档
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # 日期时间格式
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
}
```

#### 3.3 导入 API 文档配置

```python
# ==================== drf-spectacular API文档配置 ====================
# API 文档配置已移至独立文件，方便管理和维护
from ralendar.api_docs_config import SPECTACULAR_SETTINGS
```

#### 3.4 配置 JWT

```python
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),        # access token有效期1天
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),       # refresh token有效期7天
    'ROTATE_REFRESH_TOKENS': True,                     # 刷新token时返回新的refresh token
    'BLACKLIST_AFTER_ROTATION': True,                  # 旧token加入黑名单
    'UPDATE_LAST_LOGIN': True,                         # 更新最后登录时间
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}
```

### 4. 配置 URL 路由

在 Ralendar 项目的 `urls.py` 中：

```python
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # ==================== RESTful API路由 ====================
    path('api/v1/', include('your_app.api.urls')),
    
    # ==================== API 文档 📚 ====================
    # OpenAPI Schema (JSON格式)
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    # Swagger UI (交互式文档)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='api-schema'), name='api-docs'),
    # ReDoc (美观的文档)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='api-schema'), name='api-redoc'),
    
    # Django Admin
    path('admin/', admin.site.urls),
]
```

---

## 🌐 访问 API 文档

配置完成后，启动服务器，访问：

- **Swagger UI**（交互式）: `http://localhost:8000/api/docs/`
- **ReDoc**（美观）: `http://localhost:8000/api/redoc/`
- **OpenAPI Schema**（JSON）: `http://localhost:8000/api/schema/`

---

## 📋 API 模块规划

根据 `docs/API_STANDARDS.md` 规范，Ralendar 的 API 应该遵循以下结构：

```
/api/v1/ralendar/calendars/      # 日历管理
/api/v1/ralendar/events/         # 事件管理
/api/v1/ralendar/subscriptions/  # 订阅管理
/api/v1/ralendar/reminders/      # 提醒管理
/api/v1/ralendar/sync/           # 与 Roamio 同步
```

---

## ✅ 检查清单

配置完成后，请确认：

- [ ] `drf-spectacular` 已安装
- [ ] `api_docs_config.py` 已创建
- [ ] `settings.py` 已正确配置
- [ ] `urls.py` 已添加文档路由
- [ ] 可以访问 `/api/docs/` 和 `/api/redoc/`
- [ ] API 命名遵循 `API_STANDARDS.md` 规范
- [ ] 错误码遵循统一规范（1xxx-9xxx）
- [ ] JWT 认证配置正确

---

## 🔗 相关文档

- **统一 API 规范**: `docs/API_STANDARDS.md`
- **Roamio API 配置**: `roamio/api_docs_config.py`
- **drf-spectacular 官方文档**: https://drf-spectacular.readthedocs.io/

---

**最后更新**: 2025-11-07  
**维护者**: Roamio Team

