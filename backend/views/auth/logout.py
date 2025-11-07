"""
用户登出视图
"""
from django.shortcuts import redirect
from django.contrib.auth import logout


def custom_logout(request):
    """自定义登出视图，支持next参数跳转"""
    logout(request)
    # 获取next参数，如果没有就跳转到首页
    next_url = request.GET.get('next') or request.POST.get('next') or '/'
    return redirect(next_url)

