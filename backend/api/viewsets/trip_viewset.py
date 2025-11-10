"""
旅行页面相关 ViewSet
处理旅行页面的展示、点赞、打卡、评论等功能
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from ...models import SiteStat, Comment
from ...serializers import (
    TripSerializer,
    SiteStatSerializer,
    CommentSerializer,
)


class TripViewSet(viewsets.ReadOnlyModelViewSet):
    """旅行页面ViewSet"""
    # 仅展示手动"运用到旅行树"的条目：排除以"tp:"开头的统计（用于TripPlan即时统计）
    # 最新的旅行排在最前面（符合社交媒体习惯）
    queryset = SiteStat.objects.exclude(page__startswith='tp:').order_by('-id')
    serializer_class = TripSerializer
    lookup_field = 'page'
    permission_classes = [AllowAny]
    
    def get_object(self):
        """确保旧页面或树上页面即使未初始化也能有统计记录"""
        from ...models import Trip  # TripPlan模型
        
        lookup_value = self.kwargs.get(self.lookup_field)
        
        # ⚠️ 防止为TripPlan意外创建不带'tp:'前缀的SiteStat
        # 检查该slug是否对应一个TripPlan
        if Trip.objects.filter(slug=lookup_value).exists():
            # 如果是TripPlan，应该通过TripPlanViewSet访问
            # 不应该在这里创建SiteStat记录
            # 尝试获取已存在的记录，如果不存在则抛出404
            from rest_framework.exceptions import NotFound
            try:
                return SiteStat.objects.get(page=lookup_value)
            except SiteStat.DoesNotExist:
                raise NotFound("该旅行计划不存在或已被删除")
        
        # 旅行树页面已排除 tp: 前缀；其余页面如不存在则初始化
        stat, _ = SiteStat.objects.get_or_create(
            page=lookup_value,
            defaults={
                'views': 0,
                'likes': 0,
                'checked_in': False,
            }
        )
        return stat
    
    def list(self, request, *args, **kwargs):
        """获取旅行列表"""
        queryset = self.get_queryset()
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """获取旅行详情，并增加浏览量"""
        instance = self.get_object()
        instance.views += 1
        instance.save()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def like(self, request, page=None):
        """点赞"""
        stat = self.get_object()
        stat.likes += 1
        stat.save()
        return Response({'likes': stat.likes})
    
    @action(detail=True, methods=['post'])
    def checkin(self, request, page=None):
        """打卡"""
        stat = self.get_object()
        stat.checked_in = True
        stat.save()
        return Response({'checked_in': True})
    
    @action(detail=True, methods=['get'])
    def stats(self, request, page=None):
        """获取统计信息"""
        stat = self.get_object()
        serializer = SiteStatSerializer(stat)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def comments(self, request, page=None):
        """获取该页面的评论列表"""
        stat = self.get_object()
        comments = Comment.objects.filter(page=stat.page).order_by('-timestamp')
        
        # 分页
        page_obj = self.paginate_queryset(comments)
        if page_obj is not None:
            serializer = CommentSerializer(page_obj, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data)
