"""
用户中心相关URL路由
"""
from django.urls import path
from ..views import user_center, upload_avatar

urlpatterns = [
    path('user_center/', user_center, name='user_center'),
    path('upload_avatar/', upload_avatar, name='upload_avatar'),
]

