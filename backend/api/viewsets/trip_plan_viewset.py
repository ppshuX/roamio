"""
旅行计划相关 ViewSet
处理旅行计划的 CRUD、克隆、添加到旅行树等功能
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models

from ...models import Trip, SiteStat
from ...serializers import (
    TripCreateSerializer,
    TripDetailSerializer,
    TripListSerializer,
    TripUpdateSerializer,
    SiteStatSerializer,
)


class TripPlanViewSet(viewsets.ModelViewSet):
    """旅行计划ViewSet（用于编辑器）"""
    queryset = Trip.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """根据action选择序列化器"""
        if self.action == 'create':
            return TripCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TripUpdateSerializer
        elif self.action == 'list':
            return TripListSerializer
        return TripDetailSerializer
    
    def get_permissions(self):
        """根据action设置权限"""
        # 需要登录的操作
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'my_trips']:
            return [IsAuthenticated()]
        # 公开操作（任何人都可以访问公开内容，包括点赞）
        if self.action in ['retrieve', 'list', 'stats', 'view', 'like']:
            return [AllowAny()]
        # 其他操作
        return [IsAuthenticatedOrReadOnly()]
    
    def get_queryset(self):
        """过滤查询集"""
        queryset = Trip.objects.all()
        
        # 如果是my_trips action，只返回当前用户的
        if self.action == 'my_trips':
            if self.request.user.is_authenticated:
                return queryset.filter(author=self.request.user)
            return queryset.none()
        
        # 详情查看（retrieve）：只有公开的或作者本人可以访问
        if self.action == 'retrieve':
            if self.request.user.is_authenticated:
                return queryset.filter(
                    models.Q(visibility='public') | models.Q(author=self.request.user)
                )
            return queryset.filter(visibility='public')
        
        # 普通列表：只返回公开的或自己的
        if self.action == 'list':
            if self.request.user.is_authenticated:
                return queryset.filter(
                    models.Q(visibility='public') | models.Q(author=self.request.user)
                )
            return queryset.filter(visibility='public')
        
        # 公开接口（stats, view, like）：公开的旅行或自己的
        if self.action in ['stats', 'view', 'like']:
            if self.request.user.is_authenticated:
                return queryset.filter(
                    models.Q(visibility='public') | models.Q(author=self.request.user)
                )
            return queryset.filter(visibility='public')
        
        return queryset
    
    def perform_create(self, serializer):
        """创建时自动设置作者"""
        serializer.save(author=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """重写create方法，返回完整数据（包括slug）"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # 获取创建后的对象
        instance = serializer.instance
        
        # 清除预取缓存，确保获取最新数据
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        
        # 返回完整数据（使用TripDetailSerializer）
        detail_serializer = TripDetailSerializer(instance)
        headers = self.get_success_headers(detail_serializer.data)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def retrieve(self, request, *args, **kwargs):
        """重写retrieve方法，添加访问控制"""
        instance = self.get_object()
        
        # 检查访问权限：必须是公开的或是作者本人
        if instance.visibility != 'public' and instance.author != request.user:
            raise NotFound("该旅行计划不可访问")
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def _assert_can_modify_trip(self, trip, message):
        if trip.author != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied(message)
    
    def perform_update(self, serializer):
        """更新时检查权限"""
        trip = self.get_object()
        self._assert_can_modify_trip(trip, "无权修改他人的旅行计划")
        serializer.save()
    
    def update(self, request, *args, **kwargs):
        """重写update方法，返回完整数据（包括slug）"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # 重新获取更新后的对象（因为serializer.save()可能返回新的实例）
        updated_instance = serializer.instance
        
        # 清除预取缓存，确保获取最新数据
        if getattr(updated_instance, '_prefetched_objects_cache', None):
            updated_instance._prefetched_objects_cache = {}
        
        # 返回完整数据（使用TripDetailSerializer）
        detail_serializer = TripDetailSerializer(updated_instance)
        return Response(detail_serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        """重写partial_update方法，返回完整数据（包括slug）"""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def perform_destroy(self, instance):
        """删除旅行计划：若在旅行树中，连同对应SiteStat一起删除"""
        self._assert_can_modify_trip(instance, "无权删除他人的旅行计划")
        # 先尝试从旅行树移除（非 tp: 前缀，树用的是裸 slug）
        try:
            site_stat = SiteStat.objects.get(page=instance.slug)
            site_stat.delete()
        except SiteStat.DoesNotExist:
            pass
        # 再删除Trip本身
        instance.delete()
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_trips(self, request):
        """获取我的旅行列表"""
        queryset = self.get_queryset()
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TripListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TripListSerializer(queryset, many=True)
        return Response(serializer.data)

    # ==================== 公共统计接口（新Trip也可点赞/统计） ====================
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def stats(self, request, slug=None):
        """获取该旅行的统计信息（自动创建）"""
        trip = self.get_object()
        stat, _ = SiteStat.objects.get_or_create(page=f'tp:{trip.slug}', defaults={
            'views': 0,
            'likes': 0,
            'checked_in': False,
        })
        serializer = SiteStatSerializer(stat)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def like(self, request, slug=None):
        """点赞（公开与私有均可，但通常用于公开）"""
        trip = self.get_object()
        stat, _ = SiteStat.objects.get_or_create(page=f'tp:{trip.slug}', defaults={
            'views': 0,
            'likes': 0,
            'checked_in': False,
        })
        stat.likes += 1
        stat.save()
        return Response({'likes': stat.likes})

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def view(self, request, slug=None):
        """记录浏览量（幂等性由前端控制频率）"""
        trip = self.get_object()
        stat, _ = SiteStat.objects.get_or_create(page=f'tp:{trip.slug}', defaults={
            'views': 0,
            'likes': 0,
            'checked_in': False,
        })
        stat.views += 1
        stat.save()
        return Response({'views': stat.views})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def clone(self, request, slug=None):
        """复制旅行计划"""
        source_trip = self.get_object()
        
        # 创建副本
        new_trip = Trip.objects.create(
            author=request.user,
            title=f"{source_trip.title} (副本)",
            description=source_trip.description,
            icon=source_trip.icon,
            start_date=source_trip.start_date,
            end_date=source_trip.end_date,
            status='draft',
            visibility='private',
            config=source_trip.config.copy() if source_trip.config else {},
            overview=source_trip.overview.copy() if source_trip.overview else {},
            theme_color=source_trip.theme_color,
            background_music=source_trip.background_music,
        )
        
        serializer = TripDetailSerializer(new_trip)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_to_tree(self, request, slug=None):
        """将旅行计划添加到旅行树（创建SiteStat）"""
        # 检查是否为管理员
        if not request.user.is_superuser:
            return Response({
                'detail': '当前未开放此功能'
            }, status=status.HTTP_403_FORBIDDEN)
        
        trip = self.get_object()
        
        # 检查权限
        self._assert_can_modify_trip(trip, "无权将此旅行添加到旅行树")
        
        # 检查是否已存在
        try:
            SiteStat.objects.get(page=trip.slug)
            return Response({
                'detail': '该旅行已存在于旅行树中',
                'slug': trip.slug
            }, status=status.HTTP_200_OK)
        except SiteStat.DoesNotExist:
            # 创建新的SiteStat
            site_stat = SiteStat.objects.create(
                page=trip.slug,
                views=0,
                likes=0,
                checked_in=False
            )
            
            serializer = SiteStatSerializer(site_stat)
            return Response({
                'detail': '旅行已成功添加到旅行树',
                'stat': serializer.data,
                'slug': trip.slug
            }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def remove_from_tree(self, request, slug=None):
        """从旅行树移除旅行计划（删除SiteStat）"""
        # 检查是否为管理员
        if not request.user.is_superuser:
            return Response({
                'detail': '当前未开放此功能'
            }, status=status.HTTP_403_FORBIDDEN)
        
        trip = self.get_object()
        
        # 检查权限
        self._assert_can_modify_trip(trip, "无权从旅行树移除此旅行")
        
        # 删除SiteStat
        try:
            site_stat = SiteStat.objects.get(page=trip.slug)
            site_stat.delete()
            return Response({
                'detail': '旅行已成功从旅行树移除',
                'slug': trip.slug
            }, status=status.HTTP_200_OK)
        except SiteStat.DoesNotExist:
            return Response({
                'detail': '该旅行不存在于旅行树中',
                'slug': trip.slug
            }, status=status.HTTP_404_NOT_FOUND)
