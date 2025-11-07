"""
工具函数模块
"""
# 导入新功能模块
from .email_service import send_verification_email, send_verification_code
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
# 导入旧功能（从trip_utils模块）
from .trip_utils import add_trip_page_urls

# 头像下载工具
from .avatar_downloader import download_avatar_from_url, set_user_avatar_from_url

__all__ = [
    # 邮件服务
    'send_verification_email',
    'send_verification_code',
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
    # 头像下载
    'download_avatar_from_url',
    'set_user_avatar_from_url',
    # 旧功能（向后兼容）
    'add_trip_page_urls',
]

