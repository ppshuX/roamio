"""
旅行页面相关视图
"""
from django.shortcuts import redirect
from ..models.trip import Trip


def redirect_old_trip(request, old_page_name):
    """将旧URL重定向到新的旅行计划"""
    try:
        trip = Trip.objects.filter(slug=old_page_name).first()
        if trip:
            # 重定向到新的旅行计划URL
            return redirect(f'/trip/{trip.slug}/', permanent=True)
    except Exception:
        pass
    
    # 如果找不到，重定向到首页
    return redirect('/', permanent=False)


def trip_page(request):
    """厦门旅行页面 - 重定向"""
    return redirect_old_trip(request, 'trip')


def trip1(request):
    """三岔河一日游页面 - 重定向"""
    return redirect_old_trip(request, 'trip1')


def trip2(request):
    """曲靖二日游页面 - 重定向"""
    return redirect_old_trip(request, 'trip2')


def trip4(request):
    """长沙慢旅行页面 - 重定向"""
    return redirect_old_trip(request, 'trip4')


def trip_page_generic(request, page_name):
    """通用旅行页面渲染函数 - 重定向"""
    return redirect_old_trip(request, page_name)

