from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def geocode(request):
    address = request.GET.get('address', '').strip()

    if not address:
        return Response({
            'success': False,
            'message': 'address is required'
        }, status=400)

    return Response({
        'success': False,
        'code': 'MAP_DISABLED',
        'message': 'Map geocoding is temporarily unavailable'
    })
