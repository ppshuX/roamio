"""
Ralendar 集成 API ViewSet
处理旅行计划与日历的同步
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet
from django.shortcuts import get_object_or_404

from backend.models import Trip
from backend.utils.ralendar_client import RalendarClient
import logging

logger = logging.getLogger(__name__)


class RalendarIntegrationViewSet(ViewSet):
    """Ralendar 集成 API"""
    
    permission_classes = [IsAuthenticated]
    
    def get_user_token(self, request):
        """
        获取用户的 JWT Token
        
        Args:
            request: Django request 对象
            
        Returns:
            str: JWT Token
        """
        # 从 Authorization header 中提取 token
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        
        # 如果使用 rest_framework_simplejwt
        if hasattr(request.auth, 'token'):
            return str(request.auth.token)
        
        return str(request.auth) if request.auth else None
    
    @action(detail=True, methods=['post'], url_path='add-to-calendar')
    def add_to_calendar(self, request, pk=None):
        """
        将旅行计划添加到 Ralendar 日历
        
        URL: POST /api/v1/trips/{trip_slug}/add-to-calendar/
        
        请求体:
        {
            "events": [
                {
                    "title": "参观故宫",
                    "start_time": "2025-11-20T09:00:00+08:00",
                    "end_time": "2025-11-20T12:00:00+08:00",
                    "location": "北京故宫",
                    "latitude": 39.9163,
                    "longitude": 116.3972,
                    "email_reminder": true,
                    "description": "游览故宫博物院"
                }
            ]
        }
        
        响应:
        {
            "success": true,
            "created_count": 1,
            "failed_count": 0,
            "details": {
                "created": [...],
                "failed": []
            }
        }
        """
        # 获取旅行计划
        trip = get_object_or_404(Trip, slug=pk)
        
        # 检查权限
        if trip.author != request.user:
            return Response(
                {'error': '您没有权限操作此旅行计划'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 获取用户 Token
        user_token = self.get_user_token(request)
        if not user_token:
            return Response(
                {'error': '未找到用户认证信息'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # 获取事件列表
        events = request.data.get('events', [])
        
        if not events:
            return Response(
                {'error': '事件列表不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 为每个事件添加 source_app 和 related_trip_slug
        for event in events:
            event['source_app'] = 'roamio'
            event['related_trip_slug'] = trip.slug
            
            # 如果没有提供描述，使用旅行计划的描述
            if not event.get('description'):
                event['description'] = f"来自 Roamio 旅行计划: {trip.title}"
        
        # 调用 Ralendar API
        client = RalendarClient()
        
        try:
            result = client.batch_create_events(user_token, events, trip.slug)
            
            return Response({
                'success': True,
                'created_count': len(result.get('created', [])),
                'failed_count': len(result.get('failed', [])),
                'details': result
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"添加到日历失败: {e}")
            return Response({
                'success': False,
                'error': f'创建事件失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'], url_path='calendar-events')
    def get_calendar_events(self, request, pk=None):
        """
        获取旅行计划关联的日历事件
        
        URL: GET /api/v1/trips/{trip_slug}/calendar-events/
        
        响应:
        {
            "events": [...]
        }
        """
        # 获取旅行计划
        trip = get_object_or_404(Trip, slug=pk)
        
        # 检查权限
        if trip.author != request.user:
            return Response(
                {'error': '您没有权限查看此旅行计划的事件'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 获取用户 Token
        user_token = self.get_user_token(request)
        if not user_token:
            return Response(
                {'error': '未找到用户认证信息'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # 调用 Ralendar API
        client = RalendarClient()
        
        try:
            events = client.get_trip_events(user_token, trip.slug)
            return Response({'events': events}, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"获取日历事件失败: {e}")
            return Response({
                'error': f'获取事件失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['delete'], url_path='calendar-events')
    def delete_calendar_events(self, request, pk=None):
        """
        删除旅行计划关联的所有日历事件
        
        URL: DELETE /api/v1/trips/{trip_slug}/calendar-events/
        
        响应:
        {
            "success": true,
            "deleted_count": 5
        }
        """
        # 获取旅行计划
        trip = get_object_or_404(Trip, slug=pk)
        
        # 检查权限
        if trip.author != request.user:
            return Response(
                {'error': '您没有权限操作此旅行计划'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 获取用户 Token
        user_token = self.get_user_token(request)
        if not user_token:
            return Response(
                {'error': '未找到用户认证信息'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # 调用 Ralendar API
        client = RalendarClient()
        
        try:
            result = client.delete_trip_events(user_token, trip.slug)
            return Response({
                'success': True,
                'deleted_count': result.get('deleted_count', 0)
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"删除日历事件失败: {e}")
            return Response({
                'success': False,
                'error': f'删除事件失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

