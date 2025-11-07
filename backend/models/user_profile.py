"""
用户配置文件模型
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """用户配置文件模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.URLField(max_length=500, blank=True, null=True, 
                            help_text='用户头像URL（存储在腾讯云COS）')
    
    # ========== 邮箱验证相关 ==========
    email_verified = models.BooleanField(default=False, verbose_name='邮箱已验证')
    email_verified_at = models.DateTimeField(null=True, blank=True, verbose_name='邮箱验证时间')
    
    # ========== 扩展字段 - 旅行者信息 ==========
    # 个人简介
    bio = models.TextField(blank=True, max_length=500, help_text='个人简介')
    
    # 生日
    birthday = models.DateField(blank=True, null=True, help_text='生日')
    
    # 用户标签（如：摄影爱好者、美食达人等）
    tags = models.CharField(
        max_length=200, 
        blank=True,
        help_text='用户标签，逗号分隔'
    )
    
    # 访问统计（可选 - 用于缓存）
    visited_countries = models.CharField(
        max_length=200, 
        blank=True,
        help_text='访问过的国家'
    )
    
    # 用户等级
    LEVEL_CHOICES = [
        ('novice', '新手'),
        ('explorer', '探索者'),
        ('wanderer', '漫游者'),
        ('adventurer', '冒险家'),
        ('master', '旅行大师'),
    ]
    level = models.CharField(
        max_length=20, 
        choices=LEVEL_CHOICES, 
        default='novice',
        help_text='用户等级'
    )
    
    def __str__(self):
        return f"{self.user.username}的配置"
    
    @property
    def get_username(self):
        """获取用户名"""
        return self.user.username
    
    @property
    def get_comments(self):
        """获取该用户的所有评论"""
        return self.user.comment_set.all()
    
    @property
    def get_trips(self):
        """获取该用户的所有旅行计划"""
        return self.user.trips.all()
    
    @property
    def get_public_trips(self):
        """获取公开的旅行计划"""
        return self.user.trips.filter(visibility='public')
    
    def calculate_level(self):
        """根据旅行和评论数量自动计算等级"""
        # 只计算公开的旅行数量，用于等级提升
        trips_count = self.user.trips.filter(visibility='public').count()
        comments_count = self.user.comments.count()  # 使用 'comments' 因为 Comment 模型的 related_name 是 'comments'
        
        # 等级计算逻辑（必须同时满足旅行数和评论数）
        # 新手：无要求
        # 探索者：至少1个公开旅行 AND 5条评论
        # 漫游者：至少3个公开旅行 AND 20条评论
        # 冒险家：至少6个公开旅行 AND 50条评论
        # 旅行大师：至少10个公开旅行 AND 100条评论
        
        if trips_count >= 10 and comments_count >= 100:
            self.level = 'master'
        elif trips_count >= 6 and comments_count >= 50:
            self.level = 'adventurer'
        elif trips_count >= 3 and comments_count >= 20:
            self.level = 'wanderer'
        elif trips_count >= 1 and comments_count >= 5:
            self.level = 'explorer'
        else:
            self.level = 'novice'
    
    def get_avatar_url(self):
        """获取头像URL，如果没有头像则返回默认头像"""
        if self.avatar:
            # avatar 现在是 URLField，直接返回 URL 字符串
            return self.avatar
        else:
            # 返回默认头像路径（后端公共资源）
            return '/static/images/default_avatar.png'


# 自动为新用户创建配置文件
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)

