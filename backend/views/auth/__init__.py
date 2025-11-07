"""
用户认证相关视图
统一导入认证相关的视图函数
"""
from .login import custom_login
from .register import register
from .logout import custom_logout

__all__ = [
    'custom_login',
    'register',
    'custom_logout',
]

