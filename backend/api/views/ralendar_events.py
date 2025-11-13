"""
Ralendar 事件 API Views
处理单个事件的更新和删除操作
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from backend.utils.external import RalendarClient
from backend.models import SocialAccount
import logging

logger = logging.getLogger(__name__)


class RalendarEventDetailView(APIView):
    """
    Ralendar 单个事件的详情/更新/删除
    
    支持的方法：
    - PUT: 更新事件
    - DELETE: 删除事件
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_user_token(self, request):
        """从请求中获取用户Token"""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        return None
    
    def get_unionid(self, request):
        """获取用户的UnionID"""
        try:
            social_account = SocialAccount.objects.filter(
                user=request.user,
                provider='qq'
            ).first()
            return social_account.unionid if social_account else None
        except Exception as e:
            logger.error(f"Failed to get UnionID: {e}")
            return None
    
    def put(self, request, event_id):
        """
        更新事件
        
        URL: PUT /api/v1/ralendar/events/{event_id}/
        """
        user_token = self.get_user_token(request)
        if not user_token:
            return Response(
                {'error': '未找到用户认证信息'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        unionid = self.get_unionid(request)
        event_data = request.data.copy()
        
        logger.info(f"准备更新事件 {event_id}")
        logger.info(f"请求数据: {event_data}")
        logger.info(f"UnionID: {unionid}")
        
        client = RalendarClient()
        
        try:
            result = client.update_event(user_token, event_id, event_data, unionid=unionid)
            logger.info(f"更新成功: {result}")
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"更新事件失败: {e}")
            logger.error(f"完整错误堆栈:\n{error_trace}")
            return Response({
                'error': f'更新事件失败: {str(e)}',
                'detail': error_trace if request.user.is_staff else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, event_id):
        """
        删除事件
        
        URL: DELETE /api/v1/ralendar/events/{event_id}/
        """
        user_token = self.get_user_token(request)
        if not user_token:
            return Response(
                {'error': '未找到用户认证信息'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        unionid = self.get_unionid(request)
        
        logger.info(f"准备删除事件 {event_id}")
        logger.info(f"UnionID: {unionid}")
        
        client = RalendarClient()
        
        try:
            client.delete_event(user_token, event_id, unionid=unionid)
            logger.info(f"删除成功: {event_id}")
            return Response({'message': '删除成功'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"删除事件失败: {e}")
            logger.error(f"完整错误堆栈:\n{error_trace}")
            return Response({
                'error': f'删除事件失败: {str(e)}',
                'detail': error_trace if request.user.is_staff else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

