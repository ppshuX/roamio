"""
第三方登录绑定模型
"""
from django.db import models
from django.contrib.auth.models import User


class SocialAccount(models.Model):
    """
    第三方账号绑定表
    支持：QQ、微信、GitHub等
    """
    PROVIDER_CHOICES = [
        ('qq', 'QQ'),
        ('wechat', '微信'),
        ('github', 'GitHub'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='social_accounts',
        verbose_name='用户'
    )
    provider = models.CharField(
        max_length=20, 
        choices=PROVIDER_CHOICES,
        verbose_name='登录提供商'
    )
    uid = models.CharField(
        max_length=100, 
        db_index=True,
        verbose_name='第三方用户ID'
    )
    unionid = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name='UnionID（QQ/微信）'
    )
    nickname = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name='第三方昵称'
    )
    avatar_url = models.URLField(
        blank=True,
        verbose_name='第三方头像URL'
    )
    
    # 绑定时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'social_account'
        unique_together = [('provider', 'uid')]  # 同一平台的同一账号只能绑定一次
        indexes = [
            models.Index(fields=['provider', 'uid']),
            models.Index(fields=['user', 'provider']),
        ]
        verbose_name = '第三方账号绑定'
        verbose_name_plural = '第三方账号绑定'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_provider_display()}"

