"""
认证相关工具模块
"""

from .qq_oauth import (
    generate_state,
    get_qq_authorize_url,
    get_qq_access_token,
    get_qq_openid,
    get_qq_user_info,
    get_qq_user_info_by_code,
)

from .rate_limit import (
    check_email_rate_limit,
    check_ip_rate_limit,
    get_client_ip,
)

__all__ = [
    # QQ OAuth
    'generate_state',
    'get_qq_authorize_url',
    'get_qq_access_token',
    'get_qq_openid',
    'get_qq_user_info',
    'get_qq_user_info_by_code',
    
    # 频率限制
    'check_email_rate_limit',
    'check_ip_rate_limit',
    'get_client_ip',
]

