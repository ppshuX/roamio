"""
API URL路由配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .viewsets import UserViewSet, CommentViewSet, TripViewSet, TripPlanViewSet, AuthViewSet

# 创建路由器
router = DefaultRouter()

# 注册ViewSets
router.register(r'users', UserViewSet, basename='user')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'trips', TripViewSet, basename='trip')  # 旧的SiteStat接口（保持兼容）
router.register(r'trip-plans', TripPlanViewSet, basename='trip-plan')  # 新的Trip编辑接口
router.register(r'auth', AuthViewSet, basename='auth')

# URL配置
urlpatterns = [
    # ViewSets路由
    path('', include(router.urls)),
    
    # JWT Token路由
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

