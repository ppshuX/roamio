"""
Ralendar OAuth 集成 ViewSet
处理 Ralendar 账号的 OAuth 授权流程
"""
import secrets
import logging
from datetime import timedelta
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from backend.models import RalendarAccount
from backend.api.serializers.ralendar_serializers import RalendarAccountSerializer


logger = logging.getLogger(__name__)


class RalendarOAuthViewSet(viewsets.ViewSet):
    """
    Ralendar OAuth 授权流程
    """
    
    @action(detail=False, methods=['get'], url_path='authorize-url', permission_classes=[IsAuthenticated])
    def authorize_url(self, request):
        """
        获取 Ralendar OAuth 授权 URL
        
        GET /api/v1/ralendar-oauth/authorize-url/
        
        响应：
        {
            "authorize_url": "https://ralendar.com/oauth/authorize?client_id=...",
            "state": "random_string"
        }
        """
        # 生成随机 state（防 CSRF）
        state = secrets.token_urlsafe(32)
        
        # 缓存 state，10 分钟有效
        cache_key = f'ralendar_oauth_state:{state}'
        cache.set(cache_key, {
            'user_id': request.user.id,
            'created_at': timezone.now().isoformat()
        }, 600)  # 10 分钟
        
        # 构造授权 URL
        params = {
            'client_id': settings.RALENDAR_OAUTH_CLIENT_ID,
            'redirect_uri': settings.RALENDAR_OAUTH_REDIRECT_URI,
            'response_type': 'code',
            'state': state,
            'scope': 'calendar:read calendar:write user:read'
        }
        
        authorize_url = f"{settings.RALENDAR_OAUTH_AUTHORIZE_URL}?{urlencode(params)}"
        
        logger.info(f"生成 Ralendar OAuth 授权 URL: user={request.user.username}, state={state[:10]}...")
        
        return Response({
            'authorize_url': authorize_url,
            'state': state
        })
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def callback(self, request):
        """
        处理 Ralendar OAuth 回调
        
        POST /api/v1/ralendar-oauth/callback/
        
        请求体：
        {
            "code": "AUTHORIZATION_CODE",
            "state": "random_string"
        }
        
        响应：
        {
            "success": true,
            "account": {
                "id": 1,
                "ralendar_username": "张三",
                "ralendar_email": "zhangsan@example.com",
                "is_default": true
            },
            "message": "Ralendar 账号绑定成功"
        }
        """
        code = request.data.get('code')
        state = request.data.get('state')
        
        if not code or not state:
            return Response({
                'error': '缺少必要参数'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证 state
        cache_key = f'ralendar_oauth_state:{state}'
        cached_data = cache.get(cache_key)
        
        if not cached_data:
            return Response({
                'error': 'state 无效或已过期',
                'code': 'INVALID_STATE'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user_id = cached_data.get('user_id')
        if not user_id:
            return Response({
                'error': '无法获取用户信息'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 删除 state（一次性使用）
        cache.delete(cache_key)
        
        # 用 code 换取 access_token
        try:
            token_response = self._exchange_code_for_token(code)
        except Exception as e:
            logger.error(f"换取 token 失败: {e}")
            return Response({
                'error': f'换取 token 失败: {str(e)}',
                'code': 'TOKEN_EXCHANGE_FAILED'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        access_token = token_response.get('access_token')
        refresh_token = token_response.get('refresh_token')
        expires_in = token_response.get('expires_in', 7200)  # 默认 2 小时
        token_scope = token_response.get('scope', 'calendar:read calendar:write')
        
        # 记录 token 信息（用于调试）
        logger.info(f"Ralendar token response: expires_in={expires_in}, has_refresh_token={bool(refresh_token)}")
        
        if not access_token:
            return Response({
                'error': '未能获取 access_token'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取 Ralendar 用户信息
        try:
            user_info = self._get_ralendar_user_info(access_token)
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return Response({
                'error': f'获取用户信息失败: {str(e)}',
                'code': 'USERINFO_FETCH_FAILED'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        ralendar_user_id = user_info.get('user_id')
        ralendar_username = user_info.get('username', 'Ralendar 用户')
        ralendar_email = user_info.get('email')
        ralendar_avatar = user_info.get('avatar')
        ralendar_provider = user_info.get('provider')
        
        if not ralendar_user_id:
            return Response({
                'error': '无法获取 Ralendar 用户 ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取 Roamio 用户
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'error': '用户不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 计算 token 过期时间
        # 如果 expires_in 为 0 或负数，说明 token 可能已经过期或无效
        if expires_in <= 0:
            logger.warning(f"Ralendar returned invalid expires_in: {expires_in}, using default 7200")
            expires_in = 7200
        
        token_expires_at = timezone.now() + timedelta(seconds=expires_in)
        logger.info(f"Token expires at: {token_expires_at} (in {expires_in} seconds, current time: {timezone.now()})")
        
        # 检查是否已绑定该 Ralendar 账号
        ralendar_account, created = RalendarAccount.objects.update_or_create(
            user=user,
            ralendar_user_id=ralendar_user_id,
            defaults={
                'ralendar_username': ralendar_username,
                'ralendar_email': ralendar_email,
                'ralendar_avatar': ralendar_avatar,
                'ralendar_provider': ralendar_provider,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_expires_at': token_expires_at,
                'scope': token_scope,
                'is_active': True
            }
        )
        
        # 如果是新绑定且是用户的第一个账号，自动设为默认
        if created:
            if not RalendarAccount.objects.filter(user=user).exclude(id=ralendar_account.id).exists():
                ralendar_account.is_default = True
                ralendar_account.save(update_fields=['is_default'])
        
        logger.info(f"Ralendar 账号{'绑定' if created else '更新'}成功: user={user.username}, ralendar_user_id={ralendar_user_id}")
        
        # 序列化返回
        serializer = RalendarAccountSerializer(ralendar_account)
        
        return Response({
            'success': True,
            'account': serializer.data,
            'message': f"Ralendar 账号{'绑定' if created else '更新'}成功"
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def accounts(self, request):
        """
        获取当前用户的所有 Ralendar 账号
        
        GET /api/v1/ralendar-oauth/accounts/
        
        响应：
        {
            "accounts": [
                {
                    "id": 1,
                    "ralendar_username": "张三",
                    "ralendar_email": "zhangsan@example.com",
                    "is_default": true,
                    "is_token_expired": false
                }
            ]
        }
        """
        accounts = RalendarAccount.objects.filter(
            user=request.user,
            is_active=True
        ).order_by('-is_default', '-created_at')
        
        serializer = RalendarAccountSerializer(accounts, many=True)
        
        return Response({
            'accounts': serializer.data
        })
    
    @action(detail=True, methods=['post'], url_path='set-default', permission_classes=[IsAuthenticated])
    def set_default(self, request, pk=None):
        """
        设置默认 Ralendar 账号
        
        POST /api/v1/ralendar-oauth/{id}/set-default/
        
        响应：
        {
            "success": true,
            "message": "已设为默认账号"
        }
        """
        try:
            account = RalendarAccount.objects.get(
                id=pk,
                user=request.user,
                is_active=True
            )
        except RalendarAccount.DoesNotExist:
            return Response({
                'error': '账号不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        account.set_as_default()
        
        logger.info(f"设置默认 Ralendar 账号: user={request.user.username}, account_id={account.id}")
        
        return Response({
            'success': True,
            'message': '已设为默认账号'
        })
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def unbind(self, request, pk=None):
        """
        解绑 Ralendar 账号
        
        DELETE /api/v1/ralendar-oauth/{id}/unbind/
        
        响应：
        {
            "success": true,
            "message": "已解绑 Ralendar 账号"
        }
        """
        try:
            account = RalendarAccount.objects.get(
                id=pk,
                user=request.user
            )
        except RalendarAccount.DoesNotExist:
            return Response({
                'error': '账号不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 如果是默认账号，尝试将另一个账号设为默认
        if account.is_default:
            other_account = RalendarAccount.objects.filter(
                user=request.user,
                is_active=True
            ).exclude(id=account.id).first()
            
            if other_account:
                other_account.is_default = True
                other_account.save(update_fields=['is_default'])
        
        account.delete()
        
        logger.info(f"解绑 Ralendar 账号: user={request.user.username}, account_id={account.id}")
        
        return Response({
            'success': True,
            'message': '已解绑 Ralendar 账号'
        })
    
    def _exchange_code_for_token(self, code):
        """
        用授权码换取 access_token
        
        Args:
            code (str): 授权码
        
        Returns:
            dict: Token 响应
        """
        url = settings.RALENDAR_OAUTH_TOKEN_URL
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': settings.RALENDAR_OAUTH_CLIENT_ID,
            'client_secret': settings.RALENDAR_OAUTH_CLIENT_SECRET,
            'redirect_uri': settings.RALENDAR_OAUTH_REDIRECT_URI
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code != 200:
            error_msg = f"Token 请求失败: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        return response.json()
    
    def _get_ralendar_user_info(self, access_token):
        """
        获取 Ralendar 用户信息
        
        Args:
            access_token (str): Access Token
        
        Returns:
            dict: 用户信息
        """
        url = settings.RALENDAR_OAUTH_USERINFO_URL
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            error_msg = f"用户信息请求失败: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        return response.json()

