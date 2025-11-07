from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Comment, SiteStat, UserProfile
from rest_framework_simplejwt.token_blacklist.admin import OutstandingTokenAdmin, BlacklistedTokenAdmin
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

# Register your models here.

# 内联显示UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = '用户配置'
    fields = ('avatar', 'bio', 'tags', 'level', 'visited_countries')

# 自定义User管理界面
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')

# 重新注册User模型
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# 单独注册UserProfile（可选）
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'avatar')
    search_fields = ('user__username', 'user__email', 'tags')
    list_filter = ('level',)
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'avatar')
        }),
        ('旅行者信息', {
            'fields': ('bio', 'tags', 'level', 'visited_countries')
        }),
    )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_preview', 'page', 'parent_id', 'likes', 'timestamp', 'has_image', 'has_video')
    list_filter = ('page', 'timestamp', 'is_pinned')
    search_fields = ('user__username', 'content', 'page')
    readonly_fields = ('id', 'timestamp', 'likes')
    list_per_page = 50
    ordering = ('-timestamp',)
    
    fieldsets = (
        ('基本信息', {
            'fields': ('id', 'user', 'page', 'parent', 'is_pinned')
        }),
        ('内容', {
            'fields': ('content', 'image', 'video')
        }),
        ('互动数据', {
            'fields': ('likes', 'liked_by', 'timestamp')
        }),
    )
    
    def content_preview(self, obj):
        """内容预览（前30个字符）"""
        if obj.content:
            return obj.content[:30] + ('...' if len(obj.content) > 30 else '')
        return '（无文字内容）'
    content_preview.short_description = '内容预览'
    
    def parent_id(self, obj):
        """父评论ID"""
        return obj.parent_id if obj.parent else '-'
    parent_id.short_description = '父评论ID'
    
    def has_image(self, obj):
        """是否有图片"""
        return '✅' if obj.image else '❌'
    has_image.short_description = '图片'
    
    def has_video(self, obj):
        """是否有视频"""
        return '✅' if obj.video else '❌'
    has_video.short_description = '视频'

admin.site.register(SiteStat)

# 注册 Token Blacklist 模型（覆盖默认注册，以自定义显示）
admin.site.unregister(OutstandingToken)
admin.site.unregister(BlacklistedToken)
admin.site.register(OutstandingToken, OutstandingTokenAdmin)
admin.site.register(BlacklistedToken, BlacklistedTokenAdmin)
