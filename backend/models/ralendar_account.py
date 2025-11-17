"""
Ralendar 账号模型
存储用户与 Ralendar 账号的绑定关系和 OAuth token
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class RalendarAccount(models.Model):
    """
    Ralendar 账号绑定
    
    一个 Roamio 用户可以绑定多个 Ralendar 账号
    """
    # Roamio 用户
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ralendar_accounts',
        help_text='Roamio 用户'
    )
    
    # Ralendar 账号信息
    ralendar_user_id = models.IntegerField(
        help_text='Ralendar 用户 ID'
    )
    ralendar_username = models.CharField(
        max_length=100,
        help_text='Ralendar 用户名'
    )
    ralendar_email = models.EmailField(
        blank=True,
        null=True,
        help_text='Ralendar 邮箱'
    )
    ralendar_avatar = models.URLField(
        blank=True,
        null=True,
        help_text='Ralendar 头像 URL'
    )
    ralendar_provider = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text='Ralendar 登录方式：qq/acwing/email'
    )
    ralendar_unionid = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Ralendar 用户的 UnionID（QQ/微信）'
    )
    ralendar_openid = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Ralendar 用户的 OpenID（QQ/微信）'
    )
    
    # OAuth Token
    access_token = models.TextField(
        help_text='Ralendar Access Token（JWT）'
    )
    refresh_token = models.TextField(
        blank=True,
        null=True,
        help_text='Ralendar Refresh Token（可选）'
    )
    token_type = models.CharField(
        max_length=20,
        default='Bearer',
        help_text='Token 类型'
    )
    token_expires_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Token 过期时间'
    )
    scope = models.CharField(
        max_length=200,
        default='calendar:read calendar:write',
        help_text='授权的权限范围'
    )
    
    # 状态
    is_active = models.BooleanField(
        default=True,
        help_text='是否激活'
    )
    is_default = models.BooleanField(
        default=False,
        help_text='是否为默认账号（同步时默认使用此账号）'
    )
    
    # 时间戳
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='绑定时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='更新时间'
    )
    last_synced_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='最后同步时间'
    )
    
    class Meta:
        db_table = 'ralendar_accounts'
        verbose_name = 'Ralendar 账号'
        verbose_name_plural = 'Ralendar 账号'
        ordering = ['-is_default', '-created_at']
        # 确保同一个 Ralendar 账号只能被一个 Roamio 用户绑定
        unique_together = [['user', 'ralendar_user_id']]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['user', 'is_default']),
        ]
    
    def __str__(self):
        return f"{self.user.username} → Ralendar({self.ralendar_username})"
    
    @property
    def is_token_expired(self):
        """
        检查 token 是否过期
        
        提前 5 分钟判断为过期，以便用户有时间刷新 token
        """
        if not self.token_expires_at:
            # 如果没有设置过期时间，视为不过期（可能是长期有效的 token）
            return False
        
        # 提前 5 分钟判断为过期
        buffer_time = timezone.timedelta(minutes=5)
        expired = timezone.now() >= (self.token_expires_at - buffer_time)
        
        if expired:
            # 记录过期信息（用于调试）
            import logging
            logger = logging.getLogger(__name__)
            remaining = (self.token_expires_at - timezone.now()).total_seconds()
            logger.debug(f"Token expired: expires_at={self.token_expires_at}, now={timezone.now()}, remaining={remaining:.0f}s")
        
        return expired
    
    @property
    def display_name(self):
        """显示名称（用于前端展示）"""
        if self.ralendar_email:
            return f"{self.ralendar_username} ({self.ralendar_email})"
        return self.ralendar_username
    
    def set_as_default(self):
        """将此账号设为默认账号"""
        # 取消当前用户的其他默认账号
        RalendarAccount.objects.filter(
            user=self.user,
            is_default=True
        ).exclude(id=self.id).update(is_default=False)
        
        # 设置为默认
        self.is_default = True
        self.save(update_fields=['is_default', 'updated_at'])
    
    def update_sync_time(self):
        """更新最后同步时间"""
        self.last_synced_at = timezone.now()
        self.save(update_fields=['last_synced_at', 'updated_at'])
    
    def save(self, *args, **kwargs):
        """保存时自动处理默认账号逻辑"""
        # 如果这是用户的第一个账号，自动设为默认
        if not self.pk and self.is_default is False:
            if not RalendarAccount.objects.filter(user=self.user).exists():
                self.is_default = True
        
        # 如果设为默认，取消其他账号的默认状态
        if self.is_default:
            RalendarAccount.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(id=self.id).update(is_default=False)
        
        super().save(*args, **kwargs)

