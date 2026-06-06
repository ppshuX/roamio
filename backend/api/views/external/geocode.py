import os
import logging

import requests
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

logger = logging.getLogger(__name__)


def _get_amap_api_key():
    return os.environ.get('AMAP_API_KEY', '').strip()


def _missing_amap_key_response():
    return Response({
        'success': False,
        'message': 'AMAP_API_KEY is not configured'
    }, status=503)


@api_view(['GET'])
@permission_classes([AllowAny])
def geocode(request):
    address = request.GET.get('address', '').strip()

    if not address:
        return Response({
            'success': False,
            'message': 'address is required'
        }, status=400)

    api_key = _get_amap_api_key()
    if not api_key:
        return _missing_amap_key_response()

    cache_key = f'geocode_{address}'
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response({
            'success': True,
            'data': cached_data,
            'cached': True
        })

    try:
        response = requests.get(
            'https://restapi.amap.com/v3/geocode/geo',
            params={
                'address': address,
                'key': api_key,
            },
            timeout=10,
        )
        data = response.json()

        if data.get('status') != '1':
            return Response({
                'success': False,
                'message': data.get('info', 'geocode failed')
            }, status=400)

        geocodes = data.get('geocodes') or []
        if not geocodes:
            return Response({
                'success': False,
                'message': 'address not found'
            }, status=404)

        location = geocodes[0].get('location', '')
        if ',' not in location:
            return Response({
                'success': False,
                'message': 'invalid geocode response'
            }, status=502)

        lng, lat = location.split(',', 1)
        geocode_data = {
            'lat': float(lat),
            'lng': float(lng),
            'formattedAddress': geocodes[0].get('formatted_address') or address,
        }
        cache.set(cache_key, geocode_data, 86400)

        return Response({
            'success': True,
            'data': geocode_data,
            'cached': False
        })

    except requests.Timeout:
        return Response({
            'success': False,
            'message': 'geocode request timed out'
        }, status=504)
    except requests.RequestException:
        return Response({
            'success': False,
            'message': 'geocode request failed'
        }, status=503)
    except Exception as e:
        logger.error(f'Geocode failed: {str(e)}')
        return Response({
            'success': False,
            'message': 'geocode failed'
        }, status=500)
