"""
支付订单模型
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

class TripCreationOrder(models.Model):
    """旅行创建订单模型（按次付费）"""
    
    ORDER_STATUS_CHOICES = [
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('failed', '支付失败'),
        ('refunded', '已退款'),
        ('cancelled', '已取消'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('wechat', '微信支付'),
        ('alipay', '支付宝'),
        ('mock', '模拟支付'),
    ]
    
    order_id = models.CharField(
        max_length=64,
        unique=True,
        verbose_name='订单号'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='trip_creation_orders',
        verbose_name='用户'
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='金额'
    )
    
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='支付方式'
    )
    
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending',
        verbose_name='订单状态'
    )
    
    # Ping++ 相关
    pingpp_charge_id = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name='Ping++ Charge ID'
    )
    
    pingpp_order_id = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name='Ping++ Order ID'
    )
    
    # 订单描述
    description = models.CharField(
        max_length=200,
        default='创建新旅行',
        verbose_name='订单描述'
    )
    
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='支付时间'
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='订单过期时间'
    )
    
    # 回调信息
    callback_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='支付回调数据'
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
        verbose_name = '旅行创建订单'
        verbose_name_plural = '旅行创建订单'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order_id} - {self.user.username} - ¥{self.amount}"
    
    @property
    def is_paid(self):
        """是否已支付"""
        return self.status == 'paid'
    
    @property
    def is_expired(self):
        """是否已过期"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def mark_as_paid(self, pingpp_charge_id=None, callback_data=None):
        """标记为已支付"""
        self.status = 'paid'
        self.paid_at = timezone.now()
        if pingpp_charge_id:
            self.pingpp_charge_id = pingpp_charge_id
        if callback_data:
            self.callback_data = callback_data
        self.save()


class SubscriptionOrder(models.Model):
    """会员订阅订单模型"""
    
    ORDER_STATUS_CHOICES = [
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('failed', '支付失败'),
        ('refunded', '已退款'),
        ('cancelled', '已取消'),
    ]
    
    SUBSCRIPTION_TYPE_CHOICES = [
        ('vip', 'VIP'),
        ('svip', 'SVIP'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('wechat', '微信支付'),
        ('alipay', '支付宝'),
        ('mock', '模拟支付'),
    ]
    
    order_id = models.CharField(
        max_length=64,
        unique=True,
        verbose_name='订单号'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscription_orders',
        verbose_name='用户'
    )
    
    subscription_type = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_TYPE_CHOICES,
        verbose_name='订阅类型'
    )
    
    duration_months = models.IntegerField(
        default=1,
        verbose_name='订阅时长（月）'
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='金额'
    )
    
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='支付方式'
    )
    
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending',
        verbose_name='订单状态'
    )
    
    # Ping++ 相关
    pingpp_charge_id = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name='Ping++ Charge ID'
    )
    
    pingpp_order_id = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name='Ping++ Order ID'
    )
    
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='支付时间'
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='订单过期时间'
    )
    
    # 回调信息
    callback_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='支付回调数据'
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
        verbose_name = '会员订阅订单'
        verbose_name_plural = '会员订阅订单'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order_id} - {self.user.username} - {self.get_subscription_type_display()}"
    
    @property
    def is_paid(self):
        """是否已支付"""
        return self.status == 'paid'
    
    def mark_as_paid(self, pingpp_charge_id=None, callback_data=None):
        """标记为已支付"""
        self.status = 'paid'
        self.paid_at = timezone.now()
        if pingpp_charge_id:
            self.pingpp_charge_id = pingpp_charge_id
        if callback_data:
            self.callback_data = callback_data
        self.save()
        
        # 更新用户订阅
        from .subscription import Subscription
        subscription, _ = Subscription.objects.get_or_create(user=self.user)
        subscription.subscription_type = self.subscription_type
        subscription.status = 'active'
        subscription.started_at = timezone.now()
        
        # 计算到期时间
        if self.duration_months == 12:
            # 年付：12个月
            subscription.expires_at = timezone.now() + timedelta(days=365)
        else:
            # 月付
            subscription.expires_at = timezone.now() + timedelta(days=30 * self.duration_months)
        
        subscription.save()

