"""
AI 旅行规划助手 API
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from datetime import date

from backend.utils.ai import TripPlannerAI, AIFormatError
from backend.serializers.ai_serializer import (
    TripGenerationRequestSerializer,
    TripRefinementRequestSerializer
)

import logging
logger = logging.getLogger(__name__)


class AIAssistantViewSet(viewsets.ViewSet):
    """AI 旅行规划助手 API"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='generate-trip')
    def generate_trip(self, request):
        """
        生成旅行计划
        
        POST /api/v1/ai/generate-trip/
        
        Request Body:
        {
            "prompt": "用户的旅行描述",
            "preferences": {
                "days": 5,
                "budget_level": "medium",
                "travel_style": "leisure",
                "start_date": "2025-12-01"
            }
        }
        
        Response:
        {
            "code": 200,
            "message": "生成成功",
            "data": {
                "trip_plan": { ... },
                "ai_metadata": {
                    "tokens_used": 3245,
                    "generation_time": 3.2,
                    "cost": 0.0065
                }
            }
        }
        """
        # 1. 数据验证
        serializer = TripGenerationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': 400,
                'message': '参数错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 2. 频率限制检查
        rate_limit_key = f"ai_generation:{request.user.id}:{date.today()}"
        generation_count = cache.get(rate_limit_key, 0)
        
        # 免费用户限制 5 次/天，VIP 无限制
        max_generations = 999 if getattr(request.user, 'is_vip', False) else 5
        
        if generation_count >= max_generations:
            return Response({
                'code': 429,
                'message': f'今日生成次数已用完（{max_generations}次/天）',
                'data': {
                    'used': generation_count,
                    'limit': max_generations,
                    'reset_at': 'tomorrow'
                }
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # 3. 调用 AI 服务
        try:
            ai_service = TripPlannerAI()
            trip_plan = ai_service.generate_trip_plan(
                user_prompt=serializer.validated_data['prompt'],
                preferences=serializer.validated_data.get('preferences', {}),
                user=request.user
            )
            
            # 4. 更新使用次数
            cache.set(rate_limit_key, generation_count + 1, timeout=86400)
            
            # 5. 计算成本（仅供参考）
            cost = self._calculate_cost(
                ai_service.tokens_used,
                ai_service.model
            )
            
            # 6. 返回结果
            return Response({
                'code': 200,
                'message': '生成成功',
                'data': {
                    'trip_plan': trip_plan,
                    'ai_metadata': {
                        'model': ai_service.model,
                        'tokens_used': ai_service.tokens_used,
                        'generation_time': round(ai_service.generation_time, 2),
                        'cost': round(cost, 4),
                        'remaining_today': max_generations - generation_count - 1
                    }
                }
            })
            
        except AIFormatError as e:
            # 特殊处理：携带原始内容片段，便于管理员调试
            logger.error(f"AI format error: {e}. Raw snippet: {getattr(e, 'raw_content', '')}")
            resp = {
                'code': 400,
                'message': "AI 返回格式错误，请重试"
            }
            # 仅对管理员返回调试字段，避免普通用户看到冗长内容
            if getattr(request.user, 'is_staff', False):
                resp['debug_raw'] = getattr(e, 'raw_content', None)
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            logger.error(f"AI generation validation error: {e}")
            return Response({
                'code': 400,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"AI generation error: {e}", exc_info=True)
            return Response({
                'code': 500,
                'message': 'AI 服务暂时不可用，请稍后重试'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='refine-trip')
    def refine_trip(self, request):
        """
        优化已有行程
        
        POST /api/v1/ai/refine-trip/
        
        Request Body:
        {
            "trip_plan": { ... },
            "feedback": "第二天太累了，想轻松一点"
        }
        """
        serializer = TripRefinementRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': 400,
                'message': '参数错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            ai_service = TripPlannerAI()
            refined_plan = ai_service.refine_trip_plan(
                existing_plan=serializer.validated_data['trip_plan'],
                user_feedback=serializer.validated_data['feedback']
            )
            
            return Response({
                'code': 200,
                'message': '优化成功',
                'data': {
                    'trip_plan': refined_plan
                }
            })
            
        except Exception as e:
            logger.error(f"Trip refinement error: {e}")
            return Response({
                'code': 500,
                'message': '优化失败，请重试'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='usage-stats')
    def usage_stats(self, request):
        """
        查询今日使用情况
        
        GET /api/v1/ai/usage-stats/
        """
        rate_limit_key = f"ai_generation:{request.user.id}:{date.today()}"
        generation_count = cache.get(rate_limit_key, 0)
        max_generations = 999 if getattr(request.user, 'is_vip', False) else 5
        
        return Response({
            'code': 200,
            'data': {
                'used': generation_count,
                'limit': max_generations,
                'remaining': max_generations - generation_count,
                'is_vip': getattr(request.user, 'is_vip', False)
            }
        })
    
    def _calculate_cost(self, tokens, model):
        """计算 API 调用成本（人民币）"""
        # 通义千问价格（元/百万tokens）
        pricing = {
            'qwen-turbo': {'input': 0.3, 'output': 0.6},
            'qwen-plus': {'input': 0.8, 'output': 2.0},
            'qwen-max': {'input': 20, 'output': 60}
        }
        
        # 简化计算：假设输入输出各占一半
        rate = pricing.get(model, pricing['qwen-plus'])
        avg_rate = (rate['input'] + rate['output']) / 2
        
        return (tokens / 1000000) * avg_rate

