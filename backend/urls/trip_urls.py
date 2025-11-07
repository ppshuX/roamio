"""
旅行页面相关URL路由
"""
from django.urls import path
from ..views import (
    trip_page, trip1, trip2, trip4,
    add_comment, delete_comment, like_view, checkin_view, trip_views_likes,
    trip1_add_comment, trip1_delete_comment, trip1_like_view, trip1_views_likes,
    trip2_like_view, trip3_like_view, trip4_like_view,
)
from ..utils import add_trip_page_urls

urlpatterns = [
    # trip页面（厦门旅行）
    path('trip/', trip_page, name='trip_page'),
    path('trip/add_comment/', add_comment, name='add_comment'),
    path('trip/like/', like_view, name='like_view'),
    path('trip/checkin/', checkin_view, name='checkin_view'),
    path('trip/delete_comment/<int:comment_id>/', delete_comment, name='delete_comment'),
    path('trip/views_likes/', trip_views_likes, name='trip_views_likes'),
    
    # trip1页面（三岔河一日游）
    path('trip1/', trip1, name='trip1'),
    path('trip1/views_likes/', trip1_views_likes, name='trip1_views_likes'),
    path('trip1/like/', trip1_like_view, name='trip1_like_view'),
    path('trip1/add_comment/', trip1_add_comment, name='trip1_add_comment'),
    path('trip1/delete_comment/<int:comment_id>/', trip1_delete_comment, name='trip1_delete_comment'),
    
    # 专用点赞路由（为了保持向后兼容性）
    path('trip2/like/', trip2_like_view, name='trip2_like_view'),
    path('trip3/like/', trip3_like_view, name='trip3_like_view'),
    path('trip4/like/', trip4_like_view, name='trip4_like_view'),
]

# 动态添加 trip2 路由
urlpatterns.extend(add_trip_page_urls('trip2'))

# 动态添加 trip3 路由
urlpatterns.extend(add_trip_page_urls('trip3'))

# 动态添加 trip4 路由
urlpatterns.extend(add_trip_page_urls('trip4'))

