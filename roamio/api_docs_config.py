"""
Roamio API 文档配置

这个文件包含 drf-spectacular 的配置，用于生成 API 文档。
独立配置文件，方便管理和维护。

使用方式：
在 settings.py 中导入：
from roamio.api_docs_config import SPECTACULAR_SETTINGS
"""

SPECTACULAR_SETTINGS = {
    'TITLE': 'Roamio API 文档',
    'DESCRIPTION': '''
    🌍 Roamio 生态系统 - 统一 API 文档
    
    ## 📚 关于 Roamio
    Roamio 是一个围绕旅行与记录的综合平台，提供：
    - 🗺️ 旅行计划制定与管理
    - 📍 旅行打卡与记录
    - 💬 内容分享与社交
    - 👤 用户中心与资料管理
    
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
    - Web 端: https://roamio.cn
    - 小程序端: 开发中
    - Android 端: 开发中
    
    ## 🔗 相关项目
    - 📅 Ralendar: 日历助手（独立开发中）
    - 📝 Rote: 笔记工具（规划中）
    - 📸 Rapture: 照片管理（规划中）
    
    ## 📋 API 规范
    详细的 API 规范请参考: `docs/API_STANDARDS.md`
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
        {'name': '认证 (Auth)', 'description': '用户注册、登录、QQ授权等'},
        {'name': '用户 (Users)', 'description': '用户资料、头像、个人中心等'},
        {'name': '旅行 (Trips)', 'description': '旅行计划、打卡记录、分享等'},
        {'name': '评论 (Comments)', 'description': '评论管理、点赞、回复等'},
        {'name': '统计 (Stats)', 'description': '网站统计、用户统计等'},
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

