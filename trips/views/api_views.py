"""
API相关视图（统计、点赞、打卡等）
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..models import SiteStat


@csrf_exempt
def like_view(request):
    """点赞功能（trip页面专用）"""
    stats = SiteStat.objects.filter(page='trip').first()
    if not stats:
        stats = SiteStat.objects.create(page='trip')
    stats.likes += 1
    stats.save()
    return JsonResponse({'likes': stats.likes})


@csrf_exempt
def checkin_view(request):
    """打卡功能（trip页面专用）"""
    stats = SiteStat.objects.get(id=1)
    stats.checked_in = True
    stats.save()
    return JsonResponse({'checked_in': True})


def trip_views_likes(request):
    """获取统计信息（trip页面专用）"""
    stats = SiteStat.objects.filter(page='trip').first()
    if not stats:
        stats = SiteStat.objects.create(page='trip')
    return JsonResponse({'views': stats.views, 'likes': stats.likes})


@csrf_exempt
def trip1_like_view(request):
    """点赞功能（trip1页面专用）"""
    stats = SiteStat.objects.filter(page='trip1').first()
    if not stats:
        stats = SiteStat.objects.create(page='trip1')
    stats.likes += 1
    stats.save()
    return JsonResponse({'likes': stats.likes})


def trip1_views_likes(request):
    """获取统计信息（trip1页面专用）"""
    stats = SiteStat.objects.filter(page='trip1').first()
    if not stats:
        stats = SiteStat.objects.create(page='trip1')
    return JsonResponse({'views': stats.views, 'likes': stats.likes})


@csrf_exempt
def trip2_like_view(request):
    """点赞功能（trip2页面专用）"""
    stats = SiteStat.objects.filter(page='trip2').first()
    if not stats:
        stats = SiteStat.objects.create(page='trip2')
    stats.likes += 1
    stats.save()
    return JsonResponse({'likes': stats.likes})


@csrf_exempt
def trip3_like_view(request):
    """点赞功能（trip3页面专用）"""
    stats = SiteStat.objects.filter(page='trip3').first()
    if not stats:
        stats = SiteStat.objects.create(page='trip3')
    stats.likes += 1
    stats.save()
    return JsonResponse({'likes': stats.likes})


@csrf_exempt
def trip4_like_view(request):
    """点赞功能（trip4页面专用）"""
    stats = SiteStat.objects.filter(page='trip4').first()
    if not stats:
        stats = SiteStat.objects.create(page='trip4')
    stats.likes += 1
    stats.save()
    return JsonResponse({'likes': stats.likes})


@csrf_exempt
def views_likes_generic(request, page_name):
    """通用获取统计信息视图"""
    stats = SiteStat.objects.filter(page=page_name).first()
    if not stats:
        stats = SiteStat.objects.create(page=page_name)
    return JsonResponse({'views': stats.views, 'likes': stats.likes})


@csrf_exempt
def like_view_generic(request, page_name):
    """通用点赞功能视图"""
    stats = SiteStat.objects.filter(page=page_name).first()
    if not stats:
        stats = SiteStat.objects.create(page=page_name)
    stats.likes += 1
    stats.save()
    return JsonResponse({'likes': stats.likes})


@csrf_exempt
def checkin_view_generic(request, page_name):
    """通用打卡功能视图"""
    stats = SiteStat.objects.filter(page=page_name).first()
    if not stats:
        stats = SiteStat.objects.create(page=page_name)
    stats.checked_in = True
    stats.save()
    return JsonResponse({'checked_in': True})

