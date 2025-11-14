"""
邮箱可用性检查工具
用于在 Roamio 内部以及与 Ralendar 通信时检测邮箱是否已被占用
"""

from django.contrib.auth import get_user_model

from backend.models import SocialAccount
from backend.utils.external import RalendarClient

import logging

logger = logging.getLogger(__name__)
User = get_user_model()


def _get_user_unionid(user):
    """获取用户绑定的 QQ unionid（如果存在）"""
    if not user or not getattr(user, "id", None):
        return None
    
    try:
        social_account = SocialAccount.objects.filter(
            user=user,
            provider='qq'
        ).first()
        
        if social_account:
            return social_account.unionid or social_account.uid
    except Exception as exc:
        logger.warning(f"Failed to fetch unionid for user {user.id}: {exc}")
    
    return None


def check_email_availability(email, *, current_user=None, include_remote=True):
    """
    检查邮箱是否可用
    
    Args:
        email (str): 待检查邮箱
        current_user (User, optional): 当前用户（用于更换邮箱的场景）
        include_remote (bool): 是否调用 Ralendar API 进行校验
    
    Returns:
        dict: {
            "email": "test@example.com",
            "available": False,
            "conflicts": [
                {"source": "roamio", "type": "local_user", "user_id": 1, "username": "alice"},
                {"source": "ralendar", "type": "remote_user", "owner": {...}}
            ],
            "remote_checked": True/False,
            "remote_error": "error message" or None,
            "matched_unionid": True/False
        }
    """
    normalized_email = (email or '').strip().lower()
    result = {
        "email": normalized_email,
        "available": True,
        "conflicts": [],
        "remote_checked": False,
        "remote_error": None,
        "matched_unionid": False
    }
    
    if not normalized_email:
        result["available"] = False
        result["conflicts"].append({
            "source": "validation",
            "type": "empty_email"
        })
        return result
    
    # ---- 本地检查 ----
    local_qs = User.objects.filter(email=normalized_email)
    if current_user and current_user.pk:
        local_qs = local_qs.exclude(pk=current_user.pk)
    
    if local_qs.exists():
        user = local_qs.first()
        result["available"] = False
        result["conflicts"].append({
            "source": "roamio",
            "type": "local_user",
            "user_id": user.id,
            "username": user.username
        })
    
    # ---- Ralendar 远程检查 ----
    if include_remote:
        client = RalendarClient()
        try:
            remote_result = client.check_email_exists(normalized_email)
            result["remote_checked"] = True
            
            if remote_result.get("exists"):
                owner = remote_result.get("owner") or {}
                owner_unionid = owner.get("unionid")
                current_unionid = _get_user_unionid(current_user) if current_user else None
                
                if owner_unionid and current_unionid and owner_unionid == current_unionid:
                    # 同一 QQ 用户，允许
                    result["matched_unionid"] = True
                else:
                    result["available"] = False
                    conflict = {
                        "source": "ralendar",
                        "type": remote_result.get("match_type", "remote_user"),
                        "owner": owner
                    }
                    if remote_result.get("provider"):
                        conflict["provider"] = remote_result.get("provider")
                    result["conflicts"].append(conflict)
        except Exception as exc:
            result["remote_error"] = str(exc)
            logger.warning(f"Skip Ralendar email check due to error: {exc}")
    
    return result

