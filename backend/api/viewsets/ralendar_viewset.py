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
        
        logger.info(f"获取事件列表，Token: {user_token[:20]}...")
        
        # 调用 Ralendar API
        client = RalendarClient()
        
        try:
            result = client.list_events(user_token)
            logger.info(f"获取事件成功: {len(result.get('results', []))} 个")
            return Response(result, status=status.HTTP_200_OK)
        
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
        
        print(f"[DEBUG] User Token: {user_token[:20]}...")
        
        # 获取用户的 OpenID 和 UnionID
        from backend.models import SocialAccount
        try:
            print(f"[DEBUG] Query QQ info for user {request.user.id}...")
            social_account = SocialAccount.objects.filter(
                user=request.user,
                provider='qq'
            ).first()
            
            if social_account:
                openid = social_account.uid
                unionid = social_account.unionid
                print(f"[DEBUG] User OpenID: {openid}")
                print(f"[DEBUG] User UnionID: {unionid}")
            else:
                openid = None
                unionid = None
                print(f"[WARNING] No QQ account found for user {request.user.id}")
        except Exception as e:
            print(f"[ERROR] Failed to get QQ info: {e}")
            import traceback
            traceback.print_exc()
            openid = None
            unionid = None
        
        # 获取事件数据
        event_data = request.data.copy()
        event_data['source_app'] = 'roamio'
        
        # 添加 unionid 和 openid（Ralendar 的三层匹配需要）
        if unionid:
            event_data['unionid'] = unionid
            print(f"[DEBUG] Added UnionID to event data")
        
        if openid:
            event_data['openid'] = openid
            print(f"[DEBUG] Added OpenID to event data")
        
        print(f"[DEBUG] Event data: {event_data}")
        
        # 调用 Ralendar API
        print(f"[DEBUG] Calling RalendarClient...")
        client = RalendarClient()
        
        try:
            print(f"[DEBUG] Creating event...")
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
    

