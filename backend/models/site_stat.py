"""
网站统计模型
"""
from django.db import models


class SiteStat(models.Model):
    """网站统计模型"""
    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    checked_in = models.BooleanField(default=False)
    page = models.CharField(max_length=16, default='trip')  # 区分不同页面
    created_at = models.DateTimeField(auto_now_add=True, null=True)  # 创建时间

    def __str__(self):
        return f"{self.page} 页面统计"
    
    class Meta:
        verbose_name = "页面统计"
        verbose_name_plural = "页面统计"
        ordering = ['id']  # 按ID排序，保持时间顺序

