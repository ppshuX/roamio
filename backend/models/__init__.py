"""
模型模块
统一导入所有模型，保持向后兼容性
"""
from .user_profile import UserProfile
from .comment import Comment
from .site_stat import SiteStat
from .trip import Trip
from .social_auth import SocialAccount
from .email_verification import EmailVerificationCode

__all__ = [
    'UserProfile',
    'Comment',
    'SiteStat',
    'Trip',
    'SocialAccount',
    'EmailVerificationCode',
]

