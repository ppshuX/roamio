"""
序列化器模块
将Django模型转换为JSON格式，用于API响应
"""
from .user_serializer import (
    UserSerializer, 
    UserProfileSerializer, 
    RegisterSerializer,
    UpdateUserSerializer,
    UserProfileUpdateSerializer,
    AvatarUploadSerializer,
)
from .comment_serializer import CommentSerializer, CommentCreateSerializer, CommentUpdateSerializer
from .trip_serializer import TripSerializer, SiteStatSerializer
from .trip_detail_serializer import (
    TripCreateSerializer,
    TripDetailSerializer,
    TripListSerializer,
    TripUpdateSerializer,
)
from .auth_serializer import (
    LoginSerializer, 
    TokenObtainSerializer,
    SendVerificationCodeSerializer,
    VerifyCodeSerializer,
    QQLoginSerializer,
    QQBindSerializer,
    ResetPasswordSerializer,
)

__all__ = [
    # 用户
    'UserSerializer',
    'UserProfileSerializer',
    'RegisterSerializer',
    'UpdateUserSerializer',
    'UserProfileUpdateSerializer',
    'AvatarUploadSerializer',
    # 评论
    'CommentSerializer',
    'CommentCreateSerializer',
    'CommentUpdateSerializer',
    # 旅行（旧）
    'TripSerializer',
    'SiteStatSerializer',
    # 旅行（新）
    'TripCreateSerializer',
    'TripDetailSerializer',
    'TripListSerializer',
    'TripUpdateSerializer',
    # 认证
    'LoginSerializer',
    'TokenObtainSerializer',
    'SendVerificationCodeSerializer',
    'VerifyCodeSerializer',
    'QQLoginSerializer',
    'QQBindSerializer',
    'ResetPasswordSerializer',
]

