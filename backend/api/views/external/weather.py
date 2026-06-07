"""
天气查询API - 调用高德地图天气API
"""
import os
import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


def _get_amap_api_key():
    return os.environ.get('AMAP_API_KEY', '').strip()


def _missing_amap_key_response():
    return Response({
        'success': False,
        'code': 'WEATHER_DISABLED',
        'message': 'Weather service is not configured'
    })


@api_view(['GET'])
@permission_classes([AllowAny])  # 公开API，无需登录
def get_weather(request):
    """
    获取指定城市的天气信息
    
    参数:
        location: 城市名（支持中文，如"北京"、"上海"）
    
    返回:
        {
            "success": true,
            "data": {
                "location": "北京",
                "temperature": "15",
                "weather": "晴",
                "windDir": "东北",
                "windScale": "3",
                "humidity": "45",
                "updateTime": "2024-01-01 12:00:00"
            }
        }
    """
    location = request.GET.get('location', '').strip()
    
    if not location:
        return Response({
            'success': False,
            'message': '请提供城市名称'
        }, status=400)
    
    # 1. IP限流：同一IP每分钟最多20次请求
    ip = request.META.get('REMOTE_ADDR', 'unknown')
    rate_limit_key = f'weather_rate_{ip}'
    request_count = cache.get(rate_limit_key, 0)
    
    if request_count >= 20:
        logger.warning(f'IP限流触发: {ip}')
        return Response({
            'success': False,
            'message': '请求过于频繁，请稍后再试'
        }, status=429)
    
    # 增加请求计数
    cache.set(rate_limit_key, request_count + 1, 60)  # 60秒后重置
    
    # 2. 尝试从缓存获取（缓存5分钟）
    cache_key = f'weather_{location}'
    cached_data = cache.get(cache_key)
    if cached_data:
        logger.info(f'从缓存获取天气数据: {location}')
        return Response({
            'success': True,
            'data': cached_data,
            'cached': True
        })
    
    # 2. 从环境变量读取API Key
    api_key = _get_amap_api_key()
    if not api_key:
        return _missing_amap_key_response()
    
    try:
        # 3. 调用高德地图天气API
        url = 'https://restapi.amap.com/v3/weather/weatherInfo'
        params = {
            'city': location,  # 支持中文城市名或adcode
            'key': api_key,
            'extensions': 'base'  # base=实时天气，all=预报天气
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        # 4. 检查API返回状态
        if data.get('status') != '1':
            logger.warning(f'高德API返回错误: {data.get("info")}')
            return Response({
                'success': False,
                'message': data.get('info', '获取天气失败')
            }, status=400)
        
        if not data.get('lives') or len(data['lives']) == 0:
            logger.warning(f'未找到城市天气数据: {location}')
            return Response({
                'success': False,
                'message': '未找到该城市的天气信息'
            }, status=404)
        
        # 5. 提取天气数据
        live = data['lives'][0]
        weather_data = {
            'location': live['city'],
            'temperature': live['temperature'],
            'weather': live['weather'],
            'windDir': live['winddirection'],
            'windScale': live['windpower'],
            'humidity': live['humidity'],
            'updateTime': live['reporttime']
        }
        
        # 6. 缓存数据（5分钟）
        cache.set(cache_key, weather_data, 300)
        
        logger.info(f'成功获取天气数据: {location}')
        return Response({
            'success': True,
            'data': weather_data,
            'cached': False
        })
        
    except requests.Timeout:
        logger.error(f'获取天气超时: {location}')
        return Response({
            'success': False,
            'message': '获取天气信息超时，请稍后重试'
        }, status=504)
        
    except requests.RequestException as e:
        logger.error(f'请求高德API失败: {str(e)}')
        return Response({
            'success': False,
            'message': '网络请求失败，请稍后重试'
        }, status=503)
        
    except Exception as e:
        logger.error(f'获取天气异常: {str(e)}')
        return Response({
            'success': False,
            'message': '服务器内部错误'
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_location_by_ip(request):
    """
    通过IP获取用户当前城市（用于自动定位）
    
    返回:
        {
            "success": true,
            "data": {
                "city": "北京市",
                "adcode": "110000"
            }
        }
    """
    # IP限流：同一IP每分钟最多3次定位请求
    ip = request.META.get('REMOTE_ADDR', 'unknown')
    rate_limit_key = f'location_rate_{ip}'
    request_count = cache.get(rate_limit_key, 0)
    
    if request_count >= 3:
        logger.warning(f'定位接口IP限流触发: {ip}')
        return Response({
            'success': False,
            'message': '请求过于频繁'
        }, status=429)
    
    # 增加请求计数
    cache.set(rate_limit_key, request_count + 1, 60)  # 60秒后重置
    
    # 缓存IP定位结果（24小时）- 同一IP不需要重复定位
    ip_cache_key = f'ip_location_{ip}'
    cached_location = cache.get(ip_cache_key)
    if cached_location:
        logger.info(f'从缓存获取IP定位: {ip}')
        return Response({
            'success': True,
            'data': cached_location,
            'cached': True
        })
    
    api_key = _get_amap_api_key()
    if not api_key:
        return _missing_amap_key_response()
    
    try:
        # 高德IP定位API
        url = 'https://restapi.amap.com/v3/ip'
        params = {
            'key': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('status') != '1':
            return Response({
                'success': False,
                'message': data.get('info', '定位失败')
            }, status=400)
        
        location_data = {
            'city': data.get('city', ''),
            'adcode': data.get('adcode', ''),
            'province': data.get('province', '')
        }
        
        # 缓存IP定位结果（24小时）
        cache.set(ip_cache_key, location_data, 86400)
        
        return Response({
            'success': True,
            'data': location_data
        })
        
    except Exception as e:
        logger.error(f'IP定位失败: {str(e)}')
        return Response({
            'success': False,
            'message': '定位失败'
        }, status=500)

