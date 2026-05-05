"""
旅行页面相关 ViewSet
处理旅行页面的展示、点赞、打卡、评论等功能
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from ...models import SiteStat, Comment, Trip
from ...serializers import (
    TripSerializer,
    SiteStatSerializer,
    CommentSerializer,
)


class TripViewSet(viewsets.ReadOnlyModelViewSet):
    """旅行页面ViewSet"""
    queryset = Trip.objects.none()
    serializer_class = TripSerializer
    lookup_field = 'page'
    permission_classes = [AllowAny]

    def get_queryset(self):
        """首页旅行树列表来自真实 Trip 表，仅展示公开已发布旅行。"""
        if self.action == 'list':
            return Trip.objects.filter(
                status='published',
                visibility='public',
            ).exclude(
                slug='',
            ).exclude(
                title__in=['<SLUG>', '<slug>', 'SLUG', 'slug'],
            ).order_by('-created_at')
        return SiteStat.objects.exclude(page__startswith='tp:').order_by('-id')

    def _public_trip_queryset(self):
        return Trip.objects.filter(status='published', visibility='public')

    def _trip_aliases(self, trip):
        """Return all stable page aliases for one trip."""
        aliases = []
        slug = (trip.slug or '').strip()
        if slug:
            aliases.append(slug)
        fallback_slug = f'trip-{trip.id}'
        if fallback_slug not in aliases:
            aliases.append(fallback_slug)
        return aliases

    def _trip_from_lookup(self, lookup_value):
        """Support lookup by real slug and fallback slug format: trip-{id}."""
        if not lookup_value:
            return None

        trips = self._public_trip_queryset()
        trip = trips.filter(slug=lookup_value).first()
        if trip:
            return trip

        if isinstance(lookup_value, str) and lookup_value.startswith('trip-'):
            trip_id = lookup_value[len('trip-'):]
            if trip_id.isdigit():
                return trips.filter(id=int(trip_id)).first()
        return None
    
    def get_object(self):
        """确保旧页面或树上页面即使未初始化也能有统计记录"""
        lookup_value = self.kwargs.get(self.lookup_field)

        trip = self._trip_from_lookup(lookup_value)
        if trip:
            return trip

        # 防止为非公开 Trip 意外创建不带 "tp:" 前缀的 SiteStat。
        if Trip.objects.filter(slug=lookup_value).exists():
            from rest_framework.exceptions import NotFound
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

    def _get_stat_for_instance(self, instance):
        if isinstance(instance, Trip):
            aliases = self._trip_aliases(instance)

            # 兼容历史数据：优先命中旧的非 tp key
            for alias in aliases:
                stat = SiteStat.objects.filter(page=alias).first()
                if stat:
                    return stat

            # 再尝试 tp:key（含 fallback slug）
            for alias in aliases:
                stat = SiteStat.objects.filter(page=f'tp:{alias}').first()
                if stat:
                    return stat

            stat, _ = SiteStat.objects.get_or_create(
                page=f'tp:{aliases[0]}',
                defaults={
                    'views': 0,
                    'likes': 0,
                    'checked_in': False,
                }
            )
            return stat
        return instance
    
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
        stat = self._get_stat_for_instance(instance)
        stat.views += 1
        stat.save()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def like(self, request, page=None):
        """点赞"""
        stat = self._get_stat_for_instance(self.get_object())
        stat.likes += 1
        stat.save()
        return Response({'likes': stat.likes})
    
    @action(detail=True, methods=['post'])
    def checkin(self, request, page=None):
        """打卡"""
        stat = self._get_stat_for_instance(self.get_object())
        stat.checked_in = True
        stat.save()
        return Response({'checked_in': True})
    
    @action(detail=True, methods=['get'])
    def stats(self, request, page=None):
        """获取统计信息"""
        stat = self._get_stat_for_instance(self.get_object())
        serializer = SiteStatSerializer(stat)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def comments(self, request, page=None):
        """获取该页面的评论列表"""
        instance = self.get_object()
        if isinstance(instance, Trip):
            page_keys = []
            for alias in self._trip_aliases(instance):
                page_keys.extend([f'tp:{alias}', alias])
        else:
            page_keys = [instance.page]
        page_keys = list(dict.fromkeys(page_keys))
        comments = Comment.objects.filter(page__in=page_keys).order_by('-timestamp')
        
        # 分页
        page_obj = self.paginate_queryset(comments)
        if page_obj is not None:
            serializer = CommentSerializer(page_obj, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data)
