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
    
    # 1. 尝试从缓存获取（缓存5分钟）
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
    api_key = os.environ.get('AMAP_API_KEY', '53b6a185427e97b53e16c8786a272f62')
    
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
    api_key = os.environ.get('AMAP_API_KEY', '53b6a185427e97b53e16c8786a272f62')
    
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

