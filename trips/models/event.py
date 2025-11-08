"""
旅行事件模型
用于 Roamio v2.0 智能旅行助手功能
"""

from django.db import models
from django.contrib.auth.models import User
from .trip import Trip


class TripEvent(models.Model):
    """
    旅行事件模型
    
    支持用户在旅行详情中添加待办事件，包括：
    - 基础信息：标题、描述
    - 时间信息：事件时间、提醒时间
    - 地点信息：名称、地址、坐标
    - 提醒设置：是否启用、提醒方式
    - 生态融合：来源标记、Ralendar 同步
    """
    
    # ========== 关联字段 ==========
    trip = models.ForeignKey(
        Trip, 
        on_delete=models.CASCADE, 
        related_name='events',
        verbose_name='关联旅行'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='trip_events',
        verbose_name='创建用户'
    )
    
    # ========== 基础字段 ==========
    title = models.CharField(
        max_length=200, 
        verbose_name='事件标题',
        help_text='必填，例如：参观故宫'
    )
    description = models.TextField(
        blank=True, 
        verbose_name='事件描述',
        help_text='选填，添加更多细节'
    )
    
    # ========== 时间字段 ==========
    event_time = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name='事件时间',
        help_text='选填，事件发生的时间'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    # ========== 地点字段 ==========
    location_name = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name='地点名称',
        help_text='例如：故宫博物院'
    )
    location_address = models.CharField(
        max_length=500, 
        blank=True, 
        verbose_name='详细地址',
        help_text='例如：北京市东城区景山前街4号'
    )
    location_lat = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        null=True, 
        blank=True, 
        verbose_name='纬度',
        help_text='地理坐标纬度'
    )
    location_lng = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        null=True, 
        blank=True, 
        verbose_name='经度',
        help_text='地理坐标经度'
    )
    
    # ========== 提醒字段 ==========
    reminder_enabled = models.BooleanField(
        default=False, 
        verbose_name='启用提醒',
        help_text='是否启用提醒功能'
    )
    reminder_time = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name='提醒时间',
        help_text='提醒的具体时间'
    )
    
    REMINDER_METHOD_CHOICES = [
        ('email', '邮件提醒'),
        ('system', '系统通知'),
    ]
    reminder_method = models.CharField(
        max_length=20, 
        choices=REMINDER_METHOD_CHOICES,
        default='email',
        verbose_name='提醒方式'
    )
    
    # ========== 来源标记（生态融合） ==========
    SOURCE_APP_CHOICES = [
        ('roamio', 'Roamio'),
        ('ralendar', 'Ralendar'),
        ('rote', 'Rote'),
        ('local_migration', '本地迁移'),
    ]
    source_app = models.CharField(
        max_length=50, 
        choices=SOURCE_APP_CHOICES,
        default='roamio',
        verbose_name='来源应用',
        help_text='标记事件来源于哪个应用'
    )
    source_id = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name='来源ID',
        help_text='原应用中的事件ID'
    )
    
    # ========== Ralendar 同步 ==========
    synced_to_ralendar = models.BooleanField(
        default=False, 
        verbose_name='已同步到Ralendar',
        help_text='是否已同步到 Ralendar 日历系统'
    )
    ralendar_event_id = models.IntegerField(
        null=True, 
        blank=True, 
        verbose_name='Ralendar事件ID',
        help_text='在 Ralendar 中的事件ID'
    )
    
    # ========== 状态字段 ==========
    is_completed = models.BooleanField(
        default=False, 
        verbose_name='已完成',
        help_text='事件是否已完成'
    )
    is_deleted = models.BooleanField(
        default=False, 
        verbose_name='已删除',
        help_text='软删除标记'
    )
    
    class Meta:
        db_table = 'trips_event'
        ordering = ['-created_at']
        verbose_name = '旅行事件'
        verbose_name_plural = '旅行事件'
        indexes = [
            models.Index(fields=['trip', 'user'], name='idx_trip_user'),
            models.Index(fields=['event_time'], name='idx_event_time'),
            models.Index(fields=['ralendar_event_id'], name='idx_ralendar_id'),
            models.Index(fields=['is_deleted'], name='idx_is_deleted'),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.trip.title}"
    
    def has_location(self):
        """是否有地点信息"""
        return bool(self.location_name or self.location_address)
    
    def has_coordinates(self):
        """是否有坐标信息"""
        return self.location_lat is not None and self.location_lng is not None
    
    def get_baidu_map_url(self):
        """获取百度地图导航链接"""
        if not self.has_coordinates():
            return None
        
        # 百度地图 URL Scheme
        # https://lbsyun.baidu.com/index.php?title=uri/api/web
        return f"https://api.map.baidu.com/marker?location={self.location_lat},{self.location_lng}&title={self.location_name}&content={self.location_address}&output=html"
    
    def should_sync_to_ralendar(self):
        """是否应该同步到 Ralendar"""
        # 只有启用提醒的事件才同步到 Ralendar
        return self.reminder_enabled and self.reminder_time is not None
    
    @property
    def location_dict(self):
        """返回地点信息字典（用于序列化）"""
        return {
            'name': self.location_name,
            'address': self.location_address,
            'lat': float(self.location_lat) if self.location_lat else None,
            'lng': float(self.location_lng) if self.location_lng else None,
        }
    
    @property
    def reminder_dict(self):
        """返回提醒信息字典（用于序列化）"""
        return {
            'enabled': self.reminder_enabled,
            'time': self.reminder_time.isoformat() if self.reminder_time else None,
            'method': self.reminder_method,
        }


