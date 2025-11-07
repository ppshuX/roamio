"""
用户注册视图 - 重定向到 Vue SPA
"""
from django.shortcuts import redirect


def register(request):
    """重定向到 Vue 注册页面"""
    return redirect('/register')

