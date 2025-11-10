"""
旅行事件 API ViewSet
提供事件的 CRUD 操作和同步功能
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import models

logger = logging.getLogger(__name__)

from backend.models import TripEvent, Trip
from backend.serializers import (
    TripEventSerializer,
    TripEventCreateSerializer,
    TripEventBatchCreateSerializer,
)


class TripEventViewSet(viewsets.ModelViewSet):
    """
    旅行事件 API
    
    提供以下功能：
    - 列表查询：GET /api/v1/trips/{trip_id}/events/
    - 创建事件：POST /api/v1/trips/{trip_id}/events/
    - 获取详情：GET /api/v1/trips/{trip_id}/events/{id}/
    - 更新事件：PUT/PATCH /api/v1/trips/{trip_id}/events/{id}/
    - 删除事件：DELETE /api/v1/trips/{trip_id}/events/{id}/
    - 批量导入：POST /api/v1/trips/{trip_id}/events/batch_create_from_local/
    - 同步到 Ralendar：POST /api/v1/trips/{trip_id}/events/{id}/sync_to_ralendar/
    """
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        """根据操作选择序列化器"""
        if self.action == 'create':
            return TripEventCreateSerializer
        elif self.action == 'batch_create_from_local':
            return TripEventBatchCreateSerializer
        return TripEventSerializer
    
    def get_queryset(self):
        """获取查询集"""
        trip_id = self.kwargs.get('trip_pk')
        
        # 基础查询：未删除的事件
        queryset = TripEvent.objects.filter(
            trip_id=trip_id,
            is_deleted=False
        ).select_related('user', 'user__profile', 'trip')
        
        # 如果是游客，只能看到公开的旅行的事件
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(trip__is_public=True)
        # 如果是登录用户，可以看到自己的事件 + 公开旅行的事件
        else:
            queryset = queryset.filter(
                models.Q(user=self.request.user) | models.Q(trip__is_public=True)
            )
        
        return queryset.order_by('-created_at')
    
    def get_serializer_context(self):
        """添加额外的上下文"""
        context = super().get_serializer_context()
        context['trip_id'] = self.kwargs.get('trip_pk')
        return context
    
    def perform_create(self, serializer):
        """创建事件"""
        trip_id = self.kwargs.get('trip_pk')
        
        # 验证旅行是否存在
        trip = get_object_or_404(Trip, id=trip_id)
        
        # 保存事件
        event = serializer.save()
        
        # 如果启用提醒且应该同步到 Ralendar
        if event.should_sync_to_ralendar():
            self._sync_to_ralendar(event)
    
    def perform_update(self, serializer):
        """更新事件"""
        event = serializer.save()
        
        # 如果启用提醒且应该同步到 Ralendar
        if event.should_sync_to_ralendar():
            if event.synced_to_ralendar:
                # 已同步，更新
                self._update_ralendar_event(event)
            else:
                # 未同步，创建
                self._sync_to_ralendar(event)
        elif event.synced_to_ralendar:
            # 取消提醒，删除 Ralendar 中的事件
            self._delete_ralendar_event(event)
    
    def perform_destroy(self, instance):
        """删除事件（软删除）"""
        instance.is_deleted = True
        instance.save()
        
        # 如果已同步到 Ralendar，也删除那边的事件
        if instance.synced_to_ralendar:
            self._delete_ralendar_event(instance)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def batch_create_from_local(self, request, trip_pk=None):
        """
        批量导入本地事项
        
        POST /api/v1/trips/{trip_id}/events/batch_create_from_local/
        Body: {
            "events": [
                {
                    "title": "参观故宫",
                    "description": "上午9点到达",
                    "event_time": "2025-12-01T09:00:00",
                    "location": {
                        "name": "故宫博物院",
                        "address": "北京市东城区景山前街4号",
                        "lat": 39.916527,
                        "lng": 116.397026
                    },
                    "reminder": {
                        "enabled": false
                    }
                }
            ]
        }
        """
        # 验证旅行是否存在
        trip = get_object_or_404(Trip, id=trip_pk)
        
        # 验证权限：只能导入到自己的旅行
        if trip.author != request.user:
            return Response(
                {'error': '无权限操作此旅行'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 序列化并创建
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created_events = serializer.save()
        
        # 返回创建的事件
        return Response({
            'count': len(created_events),
            'events': TripEventSerializer(created_events, many=True, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def sync_to_ralendar(self, request, trip_pk=None, pk=None):
        """
        手动同步到 Ralendar
        
        POST /api/v1/trips/{trip_id}/events/{id}/sync_to_ralendar/
        """
        event = self.get_object()
        
        # 验证权限：只能同步自己的事件
        if event.user != request.user:
            return Response(
                {'error': '无权限操作此事件'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 验证是否启用提醒
        if not event.reminder_enabled or not event.reminder_time:
            return Response(
                {'error': '只有启用提醒的事件才能同步到 Ralendar'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 同步
        if event.synced_to_ralendar:
            success = self._update_ralendar_event(event)
            message = '更新成功' if success else '更新失败'
        else:
            success = self._sync_to_ralendar(event)
            message = '同步成功' if success else '同步失败'
        
        if success:
            return Response({
                'status': 'success',
                'message': message,
                'ralendar_event_id': event.ralendar_event_id
            })
        else:
            return Response({
                'status': 'error',
                'message': message
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_complete(self, request, trip_pk=None, pk=None):
        """
        切换完成状态
        
        POST /api/v1/trips/{trip_id}/events/{id}/toggle_complete/
        """
        event = self.get_object()
        
        # 验证权限
        if event.user != request.user:
            return Response(
                {'error': '无权限操作此事件'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 切换状态
        event.is_completed = not event.is_completed
        event.save()
        
        return Response({
            'status': 'success',
            'is_completed': event.is_completed
        })
    
    # ========== 私有方法：Ralendar 同步 ==========
    
    def _sync_to_ralendar(self, event):
        """同步事件到 Ralendar"""
        # TODO: 实现跨项目 API 调用
        # 当前阶段先返回 False，等 Ralendar 完成后再实现
        
        try:
            # from backend.utils.ralendar_sync import RalendarSyncService
            # service = RalendarSyncService()
            # result = service.create_event(event)
            # return result is not None
            
            # 临时：标记为已同步（用于测试）
            event.synced_to_ralendar = True
            event.ralendar_event_id = 999  # 临时 ID
            event.save()
            return True
        except Exception as e:
            logger.error(f'同步到 Ralendar 失败: {e}')
            return False
    
    def _update_ralendar_event(self, event):
        """更新 Ralendar 中的事件"""
        # TODO: 实现跨项目 API 调用
        try:
            # from backend.utils.ralendar_sync import RalendarSyncService
            # service = RalendarSyncService()
            # result = service.update_event(event)
            # return result is not None
            
            return True
        except Exception as e:
            logger.error(f'更新 Ralendar 事件失败: {e}')
            return False
    
    def _delete_ralendar_event(self, event):
        """删除 Ralendar 中的事件"""
        # TODO: 实现跨项目 API 调用
        try:
            # from backend.utils.ralendar_sync import RalendarSyncService
            # service = RalendarSyncService()
            # result = service.delete_event(event)
            # return result is not None
            
            event.synced_to_ralendar = False
            event.ralendar_event_id = None
            event.save()
            return True
        except Exception as e:
            logger.error(f'删除 Ralendar 事件失败: {e}')
            return False

