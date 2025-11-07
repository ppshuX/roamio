"""
基础页面视图
"""
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import os


def main_menu(request):
    """主菜单页面 - 重定向到 Vue 首页"""
    from django.shortcuts import redirect
    return redirect('/')


def vue_app(request):
    """
    Vue单页应用入口
    提供Vue构建后的index.html
    """
    vue_index_path = os.path.join(settings.BASE_DIR, 'static', 'vue', 'index.html')
    
    try:
        with open(vue_index_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return HttpResponse(html_content, content_type='text/html')
    except FileNotFoundError:
        return HttpResponse(
            '<h1>Vue应用未构建</h1>'
            '<p>请先运行: <code>cd web && npm run build</code></p>',
            status=404
        )

