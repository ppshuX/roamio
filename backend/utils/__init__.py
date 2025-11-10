"""
工具函数模块

重构后的模块结构：
- ai/         - AI 相关（旅行规划）
- auth/       - 认证相关（OAuth、频率限制）
- external/   - 外部服务（Ralendar、邮件）
- storage/    - 存储相关（COS、文件上传）
- helpers/    - 辅助工具（行程工具）
"""

# ==================== 新的分类导入 ====================
# AI 模块
from .ai import TripPlannerAI

# 认证模块
from .auth import (
    generate_state,
    get_qq_authorize_url,
    get_qq_access_token,
    get_qq_openid,
    get_qq_user_info,
    get_qq_user_info_by_code,
    check_email_rate_limit,
    check_ip_rate_limit,
    get_client_ip,
)

# 外部服务模块
from .external import (
    RalendarClient,
    send_verification_email,
    send_verification_code,
)

# 存储模块（保持向后兼容，从旧文件导入）
from .avatar_downloader import download_avatar_from_url, set_user_avatar_from_url

# 辅助工具
from .helpers import add_trip_page_urls

__all__ = [
    # AI 服务
    'TripPlannerAI',
    
    # 外部服务
    'RalendarClient',
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
    
    # 存储
    'download_avatar_from_url',
    'set_user_avatar_from_url',
    
    # 辅助工具
    'add_trip_page_urls',
]

