"""
旅行页面相关 ViewSet
处理旅行页面的展示、点赞、打卡、评论等功能
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from django.db.models import Count, Q

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
    # 关闭全局 DjangoFilterBackend / SearchFilter / OrderingFilter：本 ViewSet 未配置 filterset，
    # django-filter 部分版本/配置下会对列表请求抛异常导致 500。
    filter_backends = []

    def get_queryset(self):
        """首页旅行树列表来自真实 Trip 表，仅展示公开已发布旅行。"""
        if self.action == 'list':
            # 排除空 slug / 占位标题；同时排除仅空白字符的 slug（与 exclude(slug='') 在部分库上不等价）
            trip_qs = Trip.objects.filter(
                status='published',
                visibility='public',
            ).exclude(
                Q(slug__isnull=True) | Q(slug__exact='') | Q(slug__regex=r'^\s*$'),
            ).exclude(
                title__in=['<SLUG>', '<slug>', 'SLUG', 'slug'],
            ).order_by('-created_at')
            # 线上若尚未录入公开 Trip，避免出现「只有敬请期待」的空首页
            if trip_qs.exists():
                return trip_qs
            return SiteStat.objects.exclude(page__startswith='tp:').order_by('-id')
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
        rows = self._build_trip_tree_rows()

        page = self.paginate_queryset(rows)
        if page is not None:
            return self.get_paginated_response(page)

        return Response(rows)

    def _build_trip_tree_rows(self):
        """Build the public trip tree list with bounded, batched queries."""
        trips = list(
            Trip.objects.filter(
                status='published',
                visibility='public',
            ).exclude(
                Q(slug__isnull=True) | Q(slug__exact=''),
            ).exclude(
                title__in=['<SLUG>', '<slug>', 'SLUG', 'slug'],
            ).only(
                'id', 'slug', 'title', 'description', 'created_at'
            ).order_by('-created_at')[:100]
        )
        trips = [trip for trip in trips if (trip.slug or '').strip()]

        if trips:
            return self._serialize_trip_tree_rows(trips)

        stats = list(
            SiteStat.objects.exclude(page__startswith='tp:')
            .only('page', 'views', 'likes', 'checked_in')
            .order_by('-id')[:100]
        )
        return [self.get_serializer(stat).data for stat in stats]

    def _serialize_trip_tree_rows(self, trips):
        stat_pages = []
        for trip in trips:
            slug = trip.slug
            stat_pages.extend([slug, f'tp:{slug}'])

        stats_by_page = {
            stat.page: stat
            for stat in SiteStat.objects.filter(page__in=stat_pages)
        }
        comments_by_page = {
            item['page']: item['total']
            for item in Comment.objects.filter(page__in=stat_pages)
            .values('page')
            .annotate(total=Count('id'))
        }

        rows = []
        for trip in trips:
            slug = trip.slug
            stat = stats_by_page.get(slug) or stats_by_page.get(f'tp:{slug}')
            page = stat.page if stat else f'tp:{slug}'
            page_keys = [slug, f'tp:{slug}']
            rows.append({
                'slug': slug,
                'name': trip.title,
                'description': trip.description or trip.title,
                'stats': {
                    'page': page,
                    'views': stat.views if stat else 0,
                    'likes': stat.likes if stat else 0,
                    'checked_in': stat.checked_in if stat else False,
                    'comments_count': sum(comments_by_page.get(key, 0) for key in page_keys),
                },
            })
        return rows
    
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
