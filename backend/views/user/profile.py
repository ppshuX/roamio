"""
用户个人中心视图 - 重定向到 Vue SPA
"""
from django.shortcuts import redirect


def user_center(request):
    """重定向到 Vue 个人中心页面"""
    return redirect('/user-center')

