"""
评论模型
"""
from django.db import models
from django.contrib.auth.models import User


class Comment(models.Model):
    """评论模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')  # 谁发的评论
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')  # 父评论（用于回复）
    content = models.TextField(blank=True, default='')  # 允许空白内容
    image = models.URLField(max_length=500, blank=True, null=True, help_text='图片URL（存储在腾讯云COS）')  # 图片字段
    video = models.URLField(max_length=500, blank=True, null=True, help_text='视频URL（存储在腾讯云COS）')  # 视频字段
    timestamp = models.DateTimeField(auto_now_add=True)
    page = models.CharField(max_length=16, default='trip')  # 区分不同页面
    is_pinned = models.BooleanField(default=False)  # 是否置顶
    likes = models.IntegerField(default=0, help_text='点赞数')  # 新增：点赞数
    liked_by = models.ManyToManyField(User, related_name='liked_comments', blank=True, help_text='点赞用户列表')  # 新增：点赞用户

    class Meta:
        ordering = ['-is_pinned', '-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.content[:20]}"
    
    @property
    def is_top_level(self):
        """判断是否为顶层评论"""
        return self.parent is None
    
    @property
    def author_page(self):
        """获取评论所属的页面（旅行）"""
        return self.page

