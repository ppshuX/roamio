"""
API URL路由配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .viewsets import (
    UserViewSet, 
    CommentViewSet, 
    TripViewSet, 
    TripPlanViewSet, 
    AuthViewSet,
    TripEventViewSet,
)
from .viewsets.ralendar_viewset import RalendarIntegrationViewSet
from .viewsets.ralendar_oauth_viewset import RalendarOAuthViewSet
from .viewsets.ai_viewset import AIAssistantViewSet
from .views.external import weather
from .views.ralendar_events import RalendarEventDetailView

# 创建主路由器
router = DefaultRouter()

# 注册ViewSets
router.register(r'users', UserViewSet, basename='user')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'trips', TripViewSet, basename='trip')  # 旧的SiteStat接口（保持兼容）
router.register(r'trip-plans', TripPlanViewSet, basename='trip-plan')  # 新的Trip编辑接口
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'ralendar/trips', RalendarIntegrationViewSet, basename='ralendar-trips')  # Ralendar 集成
router.register(r'ralendar-oauth', RalendarOAuthViewSet, basename='ralendar-oauth')  # Ralendar OAuth
router.register(r'ai', AIAssistantViewSet, basename='ai')  # AI 旅行规划助手

# 创建嵌套路由器：/api/v1/trip-plans/{trip_pk}/events/
trip_plans_router = routers.NestedDefaultRouter(router, r'trip-plans', lookup='trip')
trip_plans_router.register(r'events', TripEventViewSet, basename='trip-plan-events')

# URL配置
urlpatterns = [
    # ViewSets路由
    path('', include(router.urls)),
    
    # 嵌套路由
    path('', include(trip_plans_router.urls)),
    
    # JWT Token路由
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 天气查询API（公开接口）
    path('weather/', weather.get_weather, name='get_weather'),
    path('location/', weather.get_location_by_ip, name='get_location'),
    
    # Ralendar 单个事件操作（支持 PUT/DELETE）
    path('ralendar/events/<int:event_id>/', RalendarEventDetailView.as_view(), name='ralendar-event-detail'),
]

