"""
旅行页面工具函数（从旧utils.py迁移）
"""
from django.urls import path
from django.views.decorators.csrf import csrf_exempt


def add_trip_page_urls(page_name):
    """
    为新的trip页面生成URL配置
    
    使用方法：
    from backend.utils import add_trip_page_urls
    from backend import views
    
    # 在urls.py中添加
    urlpatterns.extend(add_trip_page_urls('trip2'))
    """
    from backend import views
    
    # 创建包装函数以确保装饰器正确应用
    def make_trip_view(page_name):
        def view(request):
            return views.trip_page_generic(request, page_name)
        return view
    
    def make_add_comment_view(page_name):
        @csrf_exempt
        def view(request):
            return views.add_comment_generic(request, page_name)
        return view
    
    def make_delete_comment_view(page_name):
        @csrf_exempt
        def view(request, comment_id):
            return views.delete_comment_generic(request, page_name, comment_id)
        return view
    
    def make_views_likes_view(page_name):
        def view(request):
            return views.views_likes_generic(request, page_name)
        return view
    
    def make_checkin_view(page_name):
        @csrf_exempt
        def view(request):
            return views.checkin_view_generic(request, page_name)
        return view
    
    urls = [
        path(f'{page_name}/', make_trip_view(page_name), name=f'{page_name}'),
        path(f'{page_name}/add_comment/', make_add_comment_view(page_name), name=f'{page_name}_add_comment'),
        path(f'{page_name}/delete_comment/<int:comment_id>/', make_delete_comment_view(page_name), name=f'{page_name}_delete_comment'),
        path(f'{page_name}/views_likes/', make_views_likes_view(page_name), name=f'{page_name}_views_likes'),
        path(f'{page_name}/checkin/', make_checkin_view(page_name), name=f'{page_name}_checkin'),
    ]
    
    # trip4使用专门的点赞函数，不使用通用函数
    if page_name != 'trip4':
        @csrf_exempt
        def make_like_view(page_name):
            def view(request):
                return views.like_view_generic(request, page_name)
            return view
        urls.append(path(f'{page_name}/like/', make_like_view(page_name), name=f'{page_name}_like'))
    
    return urls
