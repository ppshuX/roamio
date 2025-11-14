"""
旅行计划模型
"""
import hashlib
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid


class Trip(models.Model):
    """旅行计划模型"""
    
    # 基本字段
    slug = models.SlugField(max_length=100, unique=True, help_text='URL标识符')
    title = models.CharField(max_length=200, help_text='旅行标题')
    description = models.TextField(blank=True, help_text='简介描述')
    icon = models.CharField(max_length=10, default='🗺️', help_text='旅行图标')
    
    # 作者
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips')
    
    # 日期
    start_date = models.DateField(null=True, blank=True, help_text='开始日期')
    end_date = models.DateField(null=True, blank=True, help_text='结束日期')
    
    # 状态与可见性
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', help_text='状态')
    
    VISIBILITY_CHOICES = [
        ('private', '私有'),
        ('public', '公开'),
    ]
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private', help_text='可见性')
    
    # 配置（JSON字段）- 存储启用的模块
    config = models.JSONField(default=dict, blank=True, help_text='模块配置')
    # 示例: {"enabledModules": ["basicInfo", "highlights", "itinerary", "budget", "tips"]}
    
    # 内容（JSON字段）- 存储详细内容
    overview = models.JSONField(default=dict, blank=True, help_text='行程内容')
    # 示例: {"basicInfo": {...}, "highlights": [...], "itinerary": [...]}
    
    # 主题设置
    theme_color = models.CharField(max_length=20, default='#f0e68c', help_text='主题颜色')
    background_music = models.CharField(max_length=100, blank=True, help_text='背景音乐URL')
    
    # Ralendar 同步状态（可选）
    ralendar_synced_at = models.DateTimeField(null=True, blank=True, help_text='同步到 Ralendar 的时间')
    ralendar_event_ids = models.JSONField(default=list, blank=True, help_text='Ralendar 事件 IDs')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '旅行计划'
        verbose_name_plural = '旅行计划'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # 如果没有slug，自动生成
        if not self.slug:
            # 使用哈希编码生成slug，确保唯一性和安全性
            import time
            from django.utils import timezone
            
            # 组合标题、UUID和时间戳生成唯一哈希
            unique_id = str(uuid.uuid4())
            timestamp = str(timezone.now().timestamp())
            hash_string = f"{self.title}_{unique_id}_{timestamp}"
            
            # 使用MD5生成32位哈希，截取前12位作为slug
            hash_obj = hashlib.md5(hash_string.encode())
            hash_hex = hash_obj.hexdigest()[:12]
            
            self.slug = hash_hex
            
            # 确保slug唯一（理论上已经很唯一了，但加上保险）
            counter = 1
            while Trip.objects.filter(slug=self.slug).exists():
                # 如果哈希冲突，生成新的哈希
                hash_string = f"{self.title}_{uuid.uuid4()}_{timestamp}_{counter}"
                hash_obj = hashlib.md5(hash_string.encode())
                hash_hex = hash_obj.hexdigest()[:12]
                self.slug = hash_hex
                counter += 1
        
        super().save(*args, **kwargs)
    
    @property
    def days_count(self):
        """计算旅行天数"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0
    
    @property
    def is_published(self):
        """是否已发布"""
        return self.status == 'published'
    
    @property
    def is_public(self):
        """是否公开"""
        return self.visibility == 'public'
    
    @property
    def is_synced_to_ralendar(self):
        """是否已同步到 Ralendar"""
        return self.ralendar_synced_at is not None and len(self.ralendar_event_ids) > 0

