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
import requests

logger = logging.getLogger(__name__)


class RalendarIntegrationViewSet(ViewSet):
    """Ralendar 集成 API"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='events')
    def list_events(self, request):
        """
        获取用户的所有事件（使用 Ralendar OAuth Token）
        
        URL: GET /api/v1/ralendar/trips/events/
        
        响应:
        {
            "results": [...]
        }
        """
        from backend.models import RalendarAccount
        
        # 获取 Ralendar 账号（优先使用默认账号）
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
        
        # 优先从 RalendarAccount 中读取 unionid/openid（从 Ralendar userinfo 获取，最准确）
        unionid = ralendar_account.ralendar_unionid
        openid = ralendar_account.ralendar_openid
        
        if unionid or openid:
            logger.debug(f"从 RalendarAccount 获取用户标识: unionid={unionid}, openid={openid}")
        
        # 如果 RalendarAccount 中没有，尝试从 OAuth token payload 中提取（兜底方案 1）
        if not unionid and not openid:
            try:
                import jwt
                # 尝试解析 JWT token（不验证签名，因为我们只需要读取 payload）
                try:
                    # 解码 token（不验证签名）
                    decoded = jwt.decode(access_token, options={"verify_signature": False})
                    unionid = decoded.get('unionid')
                    openid = decoded.get('openid')
                    logger.debug(f"从 token payload 提取: unionid={unionid}, openid={openid}")
                except Exception as e:
                    logger.debug(f"Token is not JWT or cannot decode: {e}")
            except ImportError:
                # 如果没有 PyJWT，跳过 token 解析
                logger.warning("PyJWT not installed, cannot parse token payload")
            except Exception as e:
                logger.warning(f"Failed to extract unionid/openid from token: {e}")
        
        # 如果 token 中也没有，回退到从 SocialAccount 读取（兜底方案 2）
        if not unionid and not openid:
            try:
                from backend.models import SocialAccount
                social_account = SocialAccount.objects.filter(
                    user=request.user,
                    provider='qq'
                ).first()
                
                if social_account:
                    unionid = social_account.unionid
                    openid = social_account.uid
                    logger.debug(f"从 SocialAccount 回退: unionid={unionid}, openid={openid}")
            except Exception as e:
                logger.warning(f"Failed to get QQ identifiers from SocialAccount: {e}")
        
        # 检查是否有用户标识（Ralendar API 需要 unionid 或 openid）
        if not unionid and not openid:
            logger.warning(f"用户 {request.user.username} 没有 unionid 或 openid，无法调用 Ralendar API")
            return Response({
                'error': '无法识别用户身份',
                'detail': 'Ralendar API 需要 unionid 或 openid 来识别用户。请确保已通过 QQ 登录或绑定 QQ 账号。',
                'code': 'NO_USER_IDENTIFIER'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 调用 Ralendar Fusion API
        client = RalendarClient()
        
        try:
            logger.info(f"调用 Ralendar list_events: unionid={unionid}, openid={openid}")
            result = client.list_events(access_token, unionid=unionid, openid=openid)
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
            
            logger.error(f"获取事件失败: {error_detail}")
            import traceback
            logger.error(traceback.format_exc())
            
            return Response({
                'error': '获取事件失败',
                'detail': error_detail,
                'code': 'RALENDAR_API_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            logger.error(f"获取事件失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return Response({
                'error': f'获取事件失败: {str(e)}',
                'code': 'INTERNAL_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='events/create')
    def create_event(self, request):
        """
        创建单个事件到 Ralendar（使用 Ralendar OAuth Token）
        
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
        from backend.models import RalendarAccount
        
        # 获取 Ralendar 账号（优先使用默认账号）
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
        
        # 尝试从 OAuth token payload 中提取 unionid/openid
        unionid = None
        openid = None
        
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
        
        # 如果 token 中没有，回退到从 SocialAccount 读取（兜底方案）
        if not unionid and not openid:
            try:
                from backend.models import SocialAccount
                social_account = SocialAccount.objects.filter(
                    user=request.user,
                    provider='qq'
                ).first()
                if social_account:
                    unionid = social_account.unionid
                    openid = social_account.uid
                    logger.debug(f"Fallback to SocialAccount: unionid={unionid}, openid={openid}")
            except Exception as e:
                logger.warning(f"Failed to load QQ identifiers from SocialAccount: {e}")
        
        # 获取事件数据
        event_data = request.data.copy()
        event_data['source_app'] = 'roamio'
        
        # 检查是否有用户标识（Ralendar API 需要 unionid 或 openid）
        if not unionid and not openid:
            logger.warning(f"用户 {request.user.username} 没有 unionid 或 openid，无法调用 Ralendar API")
            return Response({
                'error': '无法识别用户身份',
                'detail': 'Ralendar API 需要 unionid 或 openid 来识别用户。请确保已通过 QQ 登录或绑定 QQ 账号。',
                'code': 'NO_USER_IDENTIFIER'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 添加用户标识（优先级：unionid > openid）
        if unionid:
            event_data['unionid'] = unionid
        elif openid:
            event_data['openid'] = openid
        
        # 调用 Ralendar API
        client = RalendarClient()
        
        try:
            logger.info(f"调用 Ralendar create_event: unionid={unionid}, openid={openid}")
            result = client.create_event(access_token, event_data, unionid=unionid, openid=openid)
            logger.info(f"创建事件成功: {result.get('id')}")
            return Response(result, status=status.HTTP_201_CREATED)
        
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
            
            logger.error(f"创建事件失败: {error_detail}")
            import traceback
            logger.error(traceback.format_exc())
            
            return Response({
                'error': '创建事件失败',
                'detail': error_detail,
                'code': 'RALENDAR_API_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            logger.error(f"创建事件失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return Response({
                'error': f'创建事件失败: {str(e)}',
                'code': 'INTERNAL_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], url_path='sync-ai-trip')
    def sync_ai_trip(self, request, pk=None):
        """
        将 AI 生成的行程同步到 Ralendar 日历（使用 OAuth Token）
        
        URL: POST /api/v1/ralendar/trips/{slug}/sync-ai-trip/
        
        请求体:
        {
            "ralendar_account_id": 1,  # 可选，不传则使用默认账号
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
                "trip_slug": "beijing-trip-2025",
                "ralendar_account": "张三 (zhangsan@example.com)"
            }
        }
        """
        from backend.models import RalendarAccount
        
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
        
        # 获取 Ralendar 账号
        ralendar_account_id = request.data.get('ralendar_account_id')
        
        if ralendar_account_id:
            # 使用指定的账号
            try:
                ralendar_account = RalendarAccount.objects.get(
                    id=ralendar_account_id,
                    user=request.user,
                    is_active=True
                )
            except RalendarAccount.DoesNotExist:
                return Response({
                    'error': '指定的 Ralendar 账号不存在或已失效',
                    'code': 'RALENDAR_ACCOUNT_NOT_FOUND'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # 使用默认账号
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
            
            if not ralendar_account:
                return Response({
                    'error': '尚未绑定 Ralendar 账号',
                    'detail': '请先在个人中心绑定 Ralendar 账号，然后再同步',
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
        
        # 验证请求数据
        events = request.data.get('events', [])
        if not events or not isinstance(events, list):
            return Response(
                {'error': 'events 字段必须是非空数组'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 使用 Ralendar 账号的 access_token
        access_token = ralendar_account.access_token
        
        # 优先从 RalendarAccount 中读取 unionid/openid（从 Ralendar userinfo 获取，最准确）
        unionid = ralendar_account.ralendar_unionid
        openid = ralendar_account.ralendar_openid
        
        if unionid or openid:
            logger.debug(f"从 RalendarAccount 获取用户标识: unionid={unionid}, openid={openid}")
        
        # 如果 RalendarAccount 中没有，尝试从 OAuth token payload 中提取（兜底方案 1）
        if not unionid and not openid:
            try:
                import jwt
                # 尝试解析 JWT token（不验证签名，因为我们只需要读取 payload）
                try:
                    # 解码 token（不验证签名）
                    decoded = jwt.decode(access_token, options={"verify_signature": False})
                    unionid = decoded.get('unionid')
                    openid = decoded.get('openid')
                    logger.debug(f"从 token payload 提取: unionid={unionid}, openid={openid}")
                except Exception as e:
                    logger.debug(f"Token is not JWT or cannot decode: {e}")
            except ImportError:
                # 如果没有 PyJWT，跳过 token 解析
                logger.warning("PyJWT not installed, cannot parse token payload")
            except Exception as e:
                logger.warning(f"Failed to extract unionid/openid from token: {e}")
        
        # 如果 token 中也没有，回退到从 SocialAccount 读取（兜底方案 2）
        if not unionid and not openid:
            try:
                from backend.models import SocialAccount
                social_account = SocialAccount.objects.filter(
                    user=request.user,
                    provider='qq'
                ).first()
                if social_account:
                    unionid = social_account.unionid
                    openid = social_account.uid
                    logger.debug(f"从 SocialAccount 回退: unionid={unionid}, openid={openid}")
            except Exception as e:
                logger.warning(f"Failed to load QQ identifiers from SocialAccount: {e}")
        
        # 检查是否有用户标识（Ralendar API 需要 unionid 或 openid）
        if not unionid and not openid:
            logger.warning(f"用户 {request.user.username} 没有 unionid 或 openid，无法调用 Ralendar API")
            return Response({
                'code': 400,
                'error': '无法识别用户身份',
                'detail': 'Ralendar API 需要 unionid 或 openid 来识别用户。请确保已通过 QQ 登录或绑定 QQ 账号。',
                'message': '同步失败：无法识别用户身份'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 调用 Ralendar API 批量创建事件
        client = RalendarClient()
        
        try:
            logger.info(f"调用 Ralendar batch_create_events: trip_slug={trip.slug}, unionid={unionid}, openid={openid}, events_count={len(events)}")
            # 使用 OAuth access_token，并在顶层传递 unionid/openid
            result = client.batch_create_events(
                access_token,
                events,
                trip.slug,
                unionid=unionid,
                openid=openid,
            )
            
            # 处理返回结果
            created_events = result.get('created', [])
            failed_events = result.get('failed', [])
            
            synced_count = len(created_events)
            failed_count = len(failed_events)
            
            # 提取事件 IDs
            event_ids = [e.get('id') for e in created_events if e.get('id')]
            
            # 更新 Ralendar 账号的同步时间
            ralendar_account.update_sync_time()
            
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
            
            logger.info(f"同步成功: {synced_count} 个事件，失败: {failed_count} 个，Ralendar账号: {ralendar_account.display_name}")
            
            return Response({
                'code': 200,
                'message': '同步成功' if failed_count == 0 else f'部分同步成功（{synced_count} 成功，{failed_count} 失败）',
                'data': {
                    'synced_count': synced_count,
                    'failed_count': failed_count,
                    'event_ids': event_ids,
                    'trip_slug': trip.slug,
                    'ralendar_account': ralendar_account.display_name,
                    'failed_events': failed_events if failed_count > 0 else []
                }
            }, status=status.HTTP_200_OK)
            
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
            
            logger.error(f"同步失败: {error_detail}")
            import traceback
            logger.error(traceback.format_exc())
            
            return Response({
                'code': 500,
                'error': '同步失败',
                'detail': error_detail,
                'message': f'同步失败: {error_detail}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            logger.error(f"同步失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return Response({
                'code': 500,
                'error': f'同步失败: {str(e)}',
                'message': f'同步失败: {str(e)}'
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
    

