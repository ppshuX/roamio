"""
邮箱验证码模型
"""
import secrets
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class EmailVerificationCode(models.Model):
    """
    邮箱验证码存储
    """
    VERIFICATION_TYPES = [
        ('register', '注册验证'),
        ('login', '登录验证'),
        ('reset_password', '重置密码'),
        ('bind_email', '绑定邮箱'),
    ]
    
    email = models.EmailField(verbose_name='邮箱地址', db_index=True)
    code = models.CharField(max_length=10, verbose_name='验证码')
    verification_type = models.CharField(
        max_length=20, 
        choices=VERIFICATION_TYPES,
        verbose_name='验证类型'
    )
    
    # 状态管理
    is_used = models.BooleanField(default=False, verbose_name='已使用')
    expires_at = models.DateTimeField(verbose_name='过期时间')
    
    # 关联用户（注册时可能还没有用户）
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='verification_codes'
    )
    
    # IP和元数据
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    used_at = models.DateTimeField(null=True, blank=True, verbose_name='使用时间')
    
    class Meta:
        db_table = 'email_verification_code'
        indexes = [
            models.Index(fields=['email', 'code', 'is_used']),
            models.Index(fields=['expires_at']),
        ]
        verbose_name = '邮箱验证码'
        verbose_name_plural = '邮箱验证码'
        ordering = ['-created_at']
    
    @classmethod
    def generate_code(cls, length=6):
        """生成数字验证码"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(length)])
    
    @classmethod
    def create_code(cls, email, verification_type, user=None, ip_address=None, expires_in_minutes=10):
        """
        创建验证码
        
        Args:
            email: 邮箱地址
            verification_type: 验证类型
            user: 关联用户（可选）
            ip_address: IP地址（可选）
            expires_in_minutes: 过期时间（分钟）
        
        Returns:
            EmailVerificationCode实例
        """
        code = cls.generate_code()
        expires_at = timezone.now() + timedelta(minutes=expires_in_minutes)
        
        return cls.objects.create(
            email=email,
            code=code,
            verification_type=verification_type,
            user=user,
            ip_address=ip_address,
            expires_at=expires_at
        )
    
    def is_valid(self):
        """检查验证码是否有效"""
        return not self.is_used and self.expires_at > timezone.now()
    
    def mark_as_used(self):
        """标记验证码为已使用"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save()
    
    def __str__(self):
        return f"{self.email} - {self.code} ({self.get_verification_type_display()})"

