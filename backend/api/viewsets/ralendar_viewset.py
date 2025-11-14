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
from backend.utils.external import RalendarClient
import logging

logger = logging.getLogger(__name__)


class RalendarIntegrationViewSet(ViewSet):
    """Ralendar 集成 API"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='events')
    def list_events(self, request):
        """
        获取用户的所有事件
        
        URL: GET /api/v1/ralendar/trips/events/
        
        响应:
        {
            "results": [...]
        }
        """
        # 获取用户 Token
        user_token = self.get_user_token(request)
        if not user_token:
            logger.error("未找到用户认证信息")
            return Response(
                {'error': '未找到用户认证信息'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # 获取用户的 UnionID（用于加速匹配）
        from backend.models import SocialAccount
        unionid = None
        try:
            social_account = SocialAccount.objects.filter(
                user=request.user,
                provider='qq'
            ).first()
            
            if social_account:
                unionid = social_account.unionid
        except Exception as e:
            logger.error(f"Failed to get UnionID: {e}")
        
        # 调用 Ralendar Fusion API
        client = RalendarClient()
        
        try:
            result = client.list_events(user_token, unionid=unionid)
            # Fusion API 返回格式：{"events": [...], "events_count": 10}
            # 转换为前端期望的格式：{"results": [...]}
            response_data = {
                'results': result.get('events', []),
                'count': result.get('events_count', 0),
                'user_id': result.get('user_id'),
                'username': result.get('username')
            }
            logger.info(f"获取事件成功: {response_data['count']} 个")
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"获取事件失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return Response({
                'error': f'获取事件失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='events/create')
    def create_event(self, request):
        """
        创建单个事件到 Ralendar
        
        URL: POST /api/v1/ralendar/trips/events/create/
        
        请求体:
        {
            "title": "待办标题",
            "description": "描述",
            "start_time": "2025-11-20T09:00:00+08:00"
        }
        
        响应:
        {
            "id": 123,
            "title": "待办标题",
            ...
        }
        """
        # 获取用户 Token
        user_token = self.get_user_token(request)
        if not user_token:
            logger.error("未找到用户认证信息")
            return Response(
                {'error': '未找到用户认证信息'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # 获取用户的 OpenID 和 UnionID
        from backend.models import SocialAccount
        try:
            social_account = SocialAccount.objects.filter(
                user=request.user,
                provider='qq'
            ).first()
            
            if social_account:
                openid = social_account.uid
                unionid = social_account.unionid
            else:
                openid = None
                unionid = None
        except Exception as e:
            logger.error(f"Failed to get QQ info: {e}")
            openid = None
            unionid = None
        
        # 获取事件数据
        event_data = request.data.copy()
        event_data['source_app'] = 'roamio'
        
        # 添加 unionid 和 openid（Ralendar 的三层匹配需要）
        if unionid:
            event_data['unionid'] = unionid
        
        if openid:
            event_data['openid'] = openid
        
        # 调用 Ralendar API
        client = RalendarClient()
        
        try:
            result = client.create_event(user_token, event_data)
            logger.info(f"创建事件成功: {result.get('id')}")
            return Response(result, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"创建事件失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return Response({
                'error': f'创建事件失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], url_path='sync-ai-trip')
    def sync_ai_trip(self, request, pk=None):
        """
        将 AI 生成的行程同步到 Ralendar 日历
        
        URL: POST /api/v1/ralendar/trips/{slug}/sync-ai-trip/
        
        请求体:
        {
            "events": [
                {
                    "title": "北京五日游 - Day 1: 抵达北京",
                    "description": "抵达北京，办理入住",
                    "start_time": "2025-11-15T09:00:00+08:00",
                    "end_time": "2025-11-15T11:00:00+08:00",
                    "location": "北京首都国际机场",
                    "latitude": 40.0799,
                    "longitude": 116.6031,
                    "reminder_minutes": 30,
                    "email_reminder": true
                }
            ]
        }
        
        响应:
        {
            "code": 200,
            "message": "同步成功",
            "data": {
                "synced_count": 5,
                "failed_count": 0,
                "event_ids": [123, 124, 125, 126, 127],
                "trip_slug": "beijing-trip-2025"
            }
        }
        """
        # 获取旅行计划
        trip_slug = pk
        try:
            trip = get_object_or_404(Trip, slug=trip_slug, author=request.user)
        except Exception as e:
            logger.error(f"旅行计划不存在或无权访问: {e}")
            return Response(
                {'error': '旅行计划不存在或无权访问'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 获取用户 Token
        user_token = self.get_user_token(request)
        if not user_token:
            logger.error("未找到用户认证信息")
            return Response(
                {'error': '未找到用户认证信息'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # 获取用户的 OpenID 和 UnionID
        from backend.models import SocialAccount
        try:
            social_account = SocialAccount.objects.filter(
                user=request.user,
                provider='qq'
            ).first()
            
            if social_account:
                openid = social_account.uid
                unionid = social_account.unionid
                logger.info(f"找到 QQ 社交账号 - openid: {openid[:10] if openid else 'None'}..., unionid: {unionid[:10] if unionid else 'None'}...")
            else:
                openid = None
                unionid = None
                logger.warning(f"用户 {request.user.username} 没有绑定 QQ 账号")
        except Exception as e:
            logger.error(f"Failed to get QQ info: {e}")
            openid = None
            unionid = None
        
        # 如果没有 openid 和 unionid，提前返回友好错误
        if not openid and not unionid:
            return Response(
                {
                    'error': '需要 QQ 登录',
                    'detail': '同步到 Ralendar 需要使用 QQ 登录。请先退出登录，然后使用 QQ 账号重新登录。',
                    'code': 'QQ_LOGIN_REQUIRED'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 验证请求数据
        events = request.data.get('events', [])
        if not events or not isinstance(events, list):
            return Response(
                {'error': 'events 字段必须是非空数组'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 调用 Ralendar API 批量创建事件
        # 注意：事件数据会在 RalendarClient 中清理，移除不支持的字段
        client = RalendarClient()
        
        try:
            # 传递 unionid 和 openid 到批量创建方法
            result = client.batch_create_events(
                user_token, 
                events, 
                trip.slug,
                unionid=unionid,
                openid=openid
            )
            
            # 处理返回结果
            created_events = result.get('created', [])
            failed_events = result.get('failed', [])
            
            synced_count = len(created_events)
            failed_count = len(failed_events)
            
            # 提取事件 IDs
            event_ids = [e.get('id') for e in created_events if e.get('id')]
            
            # 更新 Trip 模型的同步状态（如果字段存在）
            try:
                if hasattr(trip, 'ralendar_synced_at'):
                    from django.utils import timezone
                    trip.ralendar_synced_at = timezone.now()
                    if hasattr(trip, 'ralendar_event_ids'):
                        trip.ralendar_event_ids = event_ids
                    trip.save(update_fields=['ralendar_synced_at', 'ralendar_event_ids'])
            except Exception as e:
                logger.warning(f"更新同步状态失败（字段可能不存在）: {e}")
            
            logger.info(f"同步成功: {synced_count} 个事件，失败: {failed_count} 个")
            
            return Response({
                'code': 200,
                'message': '同步成功' if failed_count == 0 else f'部分同步成功（{synced_count} 成功，{failed_count} 失败）',
                'data': {
                    'synced_count': synced_count,
                    'failed_count': failed_count,
                    'event_ids': event_ids,
                    'trip_slug': trip.slug,
                    'failed_events': failed_events if failed_count > 0 else []
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"同步失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return Response({
                'code': 500,
                'error': f'同步失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # 注意：更新和删除事件的功能已移至独立的 RalendarEventDetailView
    # URL: PUT/DELETE /api/v1/ralendar/events/{event_id}/
    
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
    

