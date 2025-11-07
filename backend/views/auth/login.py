"""
用户登录视图 - 重定向到 Vue SPA
"""
from django.shortcuts import redirect


def custom_login(request):
    """重定向到 Vue 登录页面"""
    return redirect('/login')

