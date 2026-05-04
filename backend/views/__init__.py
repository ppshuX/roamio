"""
视图模块
统一导入所有视图函数，保持向后兼容性
"""
# 基础页面视图
from .base_views import (
    main_menu,
    vue_app,
)

# 认证相关视图
from .auth import (
    custom_login,
    register,
    custom_logout,
)

# 旅行页面视图
from .trip_views import (
    trip_page,
    trip1,
    trip2,
    trip4,
    trip_page_generic,
)

# 评论相关视图
from .comment_views import (
    add_comment,
    delete_comment,
    trip1_add_comment,
    trip1_delete_comment,
    add_comment_generic,
    delete_comment_generic,
)

# 用户中心视图
from .user import (
    user_center,
    upload_avatar,
)

# API视图
from .api_views import (
    like_view,
    checkin_view,
    trip_views_likes,
    trip1_like_view,
    trip1_views_likes,
    trip2_like_view,
    trip3_like_view,
    trip4_like_view,
    views_likes_generic,
    like_view_generic,
    checkin_view_generic,
)

__all__ = [
    # 基础页面
    'main_menu',
    'vue_app',
    # 认证
    'custom_login',
    'register',
    'custom_logout',
    # 旅行页面
    'trip_page',
    'trip1',
    'trip2',
    'trip4',
    'trip_page_generic',
    # 评论
    'add_comment',
    'delete_comment',
    'trip1_add_comment',
    'trip1_delete_comment',
    'add_comment_generic',
    'delete_comment_generic',
    # 用户中心
    'user_center',
    'upload_avatar',
    # API
    'like_view',
    'checkin_view',
    'trip_views_likes',
    'trip1_like_view',
    'trip1_views_likes',
    'trip2_like_view',
    'trip3_like_view',
    'trip4_like_view',
    'views_likes_generic',
    'like_view_generic',
    'checkin_view_generic',
]

