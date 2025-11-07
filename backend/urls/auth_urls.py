"""
认证相关URL路由
"""
from django.urls import path
from ..views import custom_login, register

urlpatterns = [
    path('login/', custom_login, name='custom_login'),
    path('register/', register, name='register'),
]

