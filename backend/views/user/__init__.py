"""
用户中心相关视图
统一导入用户中心相关的视图函数
"""
from .profile import user_center
from .avatar import upload_avatar

__all__ = [
    'user_center',
    'upload_avatar',
]

