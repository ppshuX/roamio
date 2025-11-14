"""
会员订阅模型
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class Subscription(models.Model):
    """会员订阅模型"""
    
    SUBSCRIPTION_TYPE_CHOICES = [
        ('free', '普通用户'),
        ('vip', 'VIP 用户'),
        ('svip', 'SVIP 用户'),
    ]
    
    STATUS_CHOICES = [
        ('active', '活跃'),
        ('expired', '已过期'),
        ('cancelled', '已取消'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='subscription',
        verbose_name='用户'
    )
    
    subscription_type = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_TYPE_CHOICES,
        default='free',
        verbose_name='会员类型'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='状态'
    )
    
    started_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='开始时间'
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='到期时间'
    )
    
    # 旅行创建相关
    trips_count = models.IntegerField(
        default=0,
        verbose_name='已创建旅行数量'
    )
    
    trips_created_today = models.IntegerField(
        default=0,
        verbose_name='今日已创建旅行数量'
    )
    
    trips_reset_date = models.DateField(
        default=timezone.now,
        verbose_name='上次重置日期（用于每日限制）'
    )
    
    # VIP 每周免费次数
    weekly_free_trips_remaining = models.IntegerField(
        default=0,
        verbose_name='本周剩余免费旅行次数'
    )
    
    weekly_reset_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='上次周重置日期'
    )
    
    # AI 相关
    ai_remaining = models.IntegerField(
        default=2,  # 默认 2次/天
        verbose_name='剩余 AI 次数'
    )
    
    ai_total = models.IntegerField(
        default=2,  # 默认 2次/天
        verbose_name='总 AI 次数（每日重置）'
    )
    
    last_ai_reset_date = models.DateField(
        default=timezone.now,
        verbose_name='上次 AI 重置日期'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        verbose_name = '会员订阅'
        verbose_name_plural = '会员订阅'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_subscription_type_display()}"
    
    @property
    def is_vip(self):
        """是否 VIP"""
        return self.subscription_type == 'vip'
    
    @property
    def is_svip(self):
        """是否 SVIP"""
        return self.subscription_type == 'svip'
    
    @property
    def is_premium(self):
        """是否会员（VIP 或 SVIP）"""
        return self.subscription_type in ['vip', 'svip']
    
    @property
    def is_active(self):
        """是否有效"""
        if self.status != 'active':
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True
    
    def can_create_trip(self):
        """
        检查是否可以创建旅行
        
        Returns:
            tuple: (can_create: bool, cost_type: str)
                cost_type: 'free' 免费, 'paid' 需要付费, 'daily_limit' 每日限制
        """
        # 第一个旅行免费
        if self.trips_count == 0:
            return True, 'free'
        
        # SVIP：3次/天
        if self.is_svip:
            self._reset_daily_trips_if_needed()
            if self.trips_created_today < 3:
                return True, 'free'
            return False, 'daily_limit'
        
        # VIP：每周 5 次免费
        if self.is_vip:
            self._reset_weekly_trips_if_needed()
            if self.weekly_free_trips_remaining > 0:
                return True, 'free'
            # VIP 超出后需要付费（¥0.05/次）
            return True, 'paid'
        
        # 普通用户：需要付费（¥0.1/次）
        return True, 'paid'
    
    def can_use_ai(self):
        """是否可以使用 AI"""
        self._reset_daily_ai_if_needed()
        
        # SVIP：无限制
        if self.is_svip:
            return True
        
        # VIP：5次/天
        if self.is_vip:
            self.ai_total = 5
            if self.ai_remaining < self.ai_total:
                self.ai_remaining = self.ai_total
            return self.ai_remaining > 0
        
        # 普通用户：2次/天
        return self.ai_remaining > 0
    
    def consume_ai_usage(self):
        """消费 AI 使用次数"""
        if not self.can_use_ai():
            return False
        if not self.is_svip:
            self.ai_remaining -= 1
            self.save()
        return True
    
    def consume_trip_creation(self, paid=False):
        """
        消费旅行创建次数
        
        Args:
            paid: 是否已付费（如果 cost_type 是 'paid'，必须传入 True）
        
        Returns:
            tuple: (success: bool, message: str)
        """
        can_create, cost_type = self.can_create_trip()
        
        if not can_create:
            if cost_type == 'daily_limit':
                return False, '今日创建次数已达上限（SVIP 每天 3 次）'
            return False, '无法创建旅行'
        
        # 第一个旅行免费
        if self.trips_count == 0:
            self.trips_count += 1
            self.save()
            return True, '第一个旅行免费创建成功'
        
        # SVIP：每日限制
        if self.is_svip:
            if cost_type == 'free':
                self.trips_created_today += 1
                self.trips_count += 1
                self.save()
                return True, '创建成功'
            else:
                return False, '今日创建次数已达上限'
        
        # VIP：每周免费次数
        if self.is_vip and cost_type == 'free':
            self.weekly_free_trips_remaining -= 1
            self.trips_count += 1
            self.save()
            return True, '创建成功（使用本周免费次数）'
        
        # 需要付费
        if cost_type == 'paid' and not paid:
            return False, '需要付费'
        
        # 已付费，创建成功
        if cost_type == 'paid' and paid:
            self.trips_count += 1
            if self.is_vip:
                # VIP 超出部分不计入每日/每周限制
                pass
            self.save()
            return True, '创建成功（已付费）'
        
        return False, '未知错误'
    
    def get_trip_creation_price(self):
        """获取创建旅行的价格（如果需要付费）"""
        can_create, cost_type = self.can_create_trip()
        
        if cost_type == 'free':
            return 0
        
        # VIP 超出部分：¥0.05/次
        if self.is_vip:
            return 0.05
        
        # 普通用户：¥0.1/次
        return 0.1
    
    def _reset_daily_trips_if_needed(self):
        """重置每日旅行创建次数（SVIP）"""
        if self.is_svip:
            today = timezone.now().date()
            if self.trips_reset_date < today:
                self.trips_created_today = 0
                self.trips_reset_date = today
                self.save()
    
    def _reset_weekly_trips_if_needed(self):
        """重置每周免费旅行次数（VIP）"""
        if self.is_vip:
            today = timezone.now().date()
            # 计算本周一
            days_since_monday = today.weekday()
            this_monday = today - timedelta(days=days_since_monday)
            
            if not self.weekly_reset_date or self.weekly_reset_date < this_monday:
                self.weekly_free_trips_remaining = 5  # VIP 每周 5 次
                self.weekly_reset_date = this_monday
                self.save()
    
    def _reset_daily_ai_if_needed(self):
        """重置每日 AI 次数"""
        today = timezone.now().date()
        if self.last_ai_reset_date < today:
            if self.is_svip:
                # SVIP 无限制，不需要重置
                pass
            elif self.is_vip:
                self.ai_total = 5
                self.ai_remaining = 5
            else:
                self.ai_total = 2
                self.ai_remaining = 2
            self.last_ai_reset_date = today
            self.save()


# 自动为新用户创建订阅记录
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_subscription(sender, instance, created, **kwargs):
    """为新用户自动创建订阅记录"""
    if created:
        Subscription.objects.get_or_create(
            user=instance,
            defaults={'subscription_type': 'free'}
        )

