"""
频率限制工具
"""
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from ..models import EmailVerificationCode


def check_email_rate_limit(email, minutes=5, max_requests=3):
    """
    检查邮箱发送验证码的频率限制
    
    Args:
        email: 邮箱地址
        minutes: 时间窗口（分钟）
        max_requests: 最大请求次数
    
    Returns:
        tuple: (allowed: bool, remaining_seconds: int, error_message: str)
    """
    cache_key = f'email_verification_rate_limit:{email}'
    
    # 获取当前计数
    count = cache.get(cache_key, 0)
    
    if count >= max_requests:
        # 计算剩余时间
        ttl = cache.ttl(cache_key)
        if ttl is None:
            ttl = minutes * 60
        
        minutes_remaining = (ttl // 60) + 1
        return False, ttl, f"发送过于频繁，请{minutes_remaining}分钟后再试"
    
    # 增加计数
    cache.set(cache_key, count + 1, timeout=minutes * 60)
    return True, 0, None


def check_ip_rate_limit(ip_address, hours=1, max_requests=10):
    """
    检查IP发送验证码的频率限制
    
    Args:
        ip_address: IP地址
        hours: 时间窗口（小时）
        max_requests: 最大请求次数
    
    Returns:
        tuple: (allowed: bool, remaining_seconds: int, error_message: str)
    """
    cache_key = f'ip_verification_rate_limit:{ip_address}'
    
    # 获取当前计数
    count = cache.get(cache_key, 0)
    
    if count >= max_requests:
        # 计算剩余时间
        ttl = cache.ttl(cache_key)
        if ttl is None:
            ttl = hours * 3600
        
        hours_remaining = (ttl // 3600) + 1
        return False, ttl, f"IP请求过于频繁，请{hours_remaining}小时后再试"
    
    # 增加计数
    cache.set(cache_key, count + 1, timeout=hours * 3600)
    return True, 0, None


def get_client_ip(request):
    """
    获取客户端IP地址
    
    Args:
        request: Django request对象
    
    Returns:
        str: IP地址
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

