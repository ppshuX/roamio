"""
Ralendar 事件 API Views
处理单个事件的更新和删除操作
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from backend.utils.external import RalendarClient
from backend.models import SocialAccount, RalendarAccount
from django.utils import timezone
import logging
import requests

logger = logging.getLogger(__name__)


class RalendarEventDetailView(APIView):
    """
    Ralendar 单个事件的详情/更新/删除
    
    支持的方法：
    - PUT: 更新事件
    - DELETE: 删除事件
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_ralendar_account(self, request):
        """获取用户的 Ralendar 账号（优先使用默认账号）"""
        ralendar_account = RalendarAccount.objects.filter(
            user=request.user,
            is_active=True,
            is_default=True
        ).first()
        
        if not ralendar_account:
            # 没有默认账号，尝试获取第一个账号
            ralendar_account = RalendarAccount.objects.filter(
                user=request.user,
                is_active=True
            ).first()
        
        return ralendar_account
    
    def get_user_identifiers(self, request, access_token):
        """
        获取用户的 unionid/openid（用于 Ralendar API）
        
        优先级：
        1. 从 OAuth token payload 中提取
        2. 从 SocialAccount 读取（兜底方案）
        """
        unionid = None
        openid = None
        
        # 尝试从 OAuth token payload 中提取
        try:
            import jwt
            try:
                decoded = jwt.decode(access_token, options={"verify_signature": False})
                unionid = decoded.get('unionid')
                openid = decoded.get('openid')
                logger.debug(f"Extracted from token: unionid={unionid}, openid={openid}")
            except Exception as e:
                logger.debug(f"Token is not JWT or cannot decode: {e}")
        except ImportError:
            logger.warning("PyJWT not installed, cannot parse token payload")
        except Exception as e:
            logger.warning(f"Failed to extract unionid/openid from token: {e}")
        
        # 如果 token 中没有，回退到从 SocialAccount 读取
        if not unionid and not openid:
            try:
                social_account = SocialAccount.objects.filter(
                    user=request.user,
                    provider='qq'
                ).first()
                if social_account:
                    unionid = social_account.unionid
                    openid = social_account.uid
                    logger.debug(f"Fallback to SocialAccount: unionid={unionid}, openid={openid}")
            except Exception as e:
                logger.warning(f"Failed to get QQ identifiers from SocialAccount: {e}")
        
        return unionid, openid
    
    def put(self, request, event_id):
        """
        更新事件（使用 Ralendar OAuth Token）
        
        URL: PUT /api/v1/ralendar/events/{event_id}/
        """
        # 获取 Ralendar 账号
        ralendar_account = self.get_ralendar_account(request)
        if not ralendar_account:
            return Response({
                'error': '尚未绑定 Ralendar 账号',
                'detail': '请先在个人中心绑定 Ralendar 账号',
                'code': 'NO_RALENDAR_ACCOUNT'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查 Token 是否过期
        if ralendar_account.is_token_expired:
            return Response({
                'error': 'Ralendar Token 已过期',
                'detail': '请重新授权 Ralendar 账号',
                'code': 'TOKEN_EXPIRED',
                'ralendar_account_id': ralendar_account.id
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 使用 Ralendar OAuth access_token
        access_token = ralendar_account.access_token
        
        # 获取用户标识
        unionid, openid = self.get_user_identifiers(request, access_token)
        
        # 检查是否有用户标识（Ralendar API 需要 unionid 或 openid）
        if not unionid and not openid:
            logger.warning(f"用户 {request.user.username} 没有 unionid 或 openid，无法调用 Ralendar API")
            return Response({
                'error': '无法识别用户身份',
                'detail': 'Ralendar API 需要 unionid 或 openid 来识别用户。请确保已通过 QQ 登录或绑定 QQ 账号。',
                'code': 'NO_USER_IDENTIFIER'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        event_data = request.data.copy()
        
        logger.info(f"准备更新事件 {event_id}")
        logger.info(f"请求数据: {event_data}")
        logger.info(f"UnionID: {unionid}, OpenID: {openid}")
        
        client = RalendarClient()
        
        try:
            logger.info(f"调用 Ralendar update_event: event_id={event_id}, unionid={unionid}, openid={openid}")
            result = client.update_event(access_token, event_id, event_data, unionid=unionid, openid=openid)
            logger.info(f"更新成功: {result}")
            return Response(result, status=status.HTTP_200_OK)
        except requests.exceptions.HTTPError as e:
            # Ralendar API 返回了 HTTP 错误
            error_detail = f"Ralendar API 错误: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_body = e.response.json()
                    error_detail = error_body.get('error', error_body.get('detail', str(e)))
                    logger.error(f"Ralendar API 错误响应: {error_body}")
                except:
                    error_detail = e.response.text or str(e)
                    logger.error(f"Ralendar API 错误响应 (非JSON): {error_detail}")
            
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"更新事件失败: {error_detail}")
            logger.error(f"完整错误堆栈:\n{error_trace}")
            
            return Response({
                'error': '更新事件失败',
                'detail': error_detail,
                'code': 'RALENDAR_API_ERROR',
                'debug': error_trace if request.user.is_staff else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"更新事件失败: {e}")
            logger.error(f"完整错误堆栈:\n{error_trace}")
            return Response({
                'error': f'更新事件失败: {str(e)}',
                'code': 'INTERNAL_ERROR',
                'detail': error_trace if request.user.is_staff else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, event_id):
        """
        删除事件（使用 Ralendar OAuth Token）
        
        URL: DELETE /api/v1/ralendar/events/{event_id}/
        """
        # 获取 Ralendar 账号
        ralendar_account = self.get_ralendar_account(request)
        if not ralendar_account:
            return Response({
                'error': '尚未绑定 Ralendar 账号',
                'detail': '请先在个人中心绑定 Ralendar 账号',
                'code': 'NO_RALENDAR_ACCOUNT'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查 Token 是否过期
        if ralendar_account.is_token_expired:
            return Response({
                'error': 'Ralendar Token 已过期',
                'detail': '请重新授权 Ralendar 账号',
                'code': 'TOKEN_EXPIRED',
                'ralendar_account_id': ralendar_account.id
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 使用 Ralendar OAuth access_token
        access_token = ralendar_account.access_token
        
        # 获取用户标识
        unionid, openid = self.get_user_identifiers(request, access_token)
        
        # 检查是否有用户标识（Ralendar API 需要 unionid 或 openid）
        if not unionid and not openid:
            logger.warning(f"用户 {request.user.username} 没有 unionid 或 openid，无法调用 Ralendar API")
            return Response({
                'error': '无法识别用户身份',
                'detail': 'Ralendar API 需要 unionid 或 openid 来识别用户。请确保已通过 QQ 登录或绑定 QQ 账号。',
                'code': 'NO_USER_IDENTIFIER'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"准备删除事件 {event_id}")
        logger.info(f"UnionID: {unionid}, OpenID: {openid}")
        
        client = RalendarClient()
        
        try:
            logger.info(f"调用 Ralendar delete_event: event_id={event_id}, unionid={unionid}, openid={openid}")
            client.delete_event(access_token, event_id, unionid=unionid, openid=openid)
            logger.info(f"删除成功: {event_id}")
            return Response({'message': '删除成功'}, status=status.HTTP_204_NO_CONTENT)
        except requests.exceptions.HTTPError as e:
            # Ralendar API 返回了 HTTP 错误
            error_detail = f"Ralendar API 错误: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_body = e.response.json()
                    error_detail = error_body.get('error', error_body.get('detail', str(e)))
                    logger.error(f"Ralendar API 错误响应: {error_body}")
                except:
                    error_detail = e.response.text or str(e)
                    logger.error(f"Ralendar API 错误响应 (非JSON): {error_detail}")
            
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"删除事件失败: {error_detail}")
            logger.error(f"完整错误堆栈:\n{error_trace}")
            
            return Response({
                'error': '删除事件失败',
                'detail': error_detail,
                'code': 'RALENDAR_API_ERROR',
                'debug': error_trace if request.user.is_staff else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"删除事件失败: {e}")
            logger.error(f"完整错误堆栈:\n{error_trace}")
            return Response({
                'error': f'删除事件失败: {str(e)}',
                'code': 'INTERNAL_ERROR',
                'detail': error_trace if request.user.is_staff else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

