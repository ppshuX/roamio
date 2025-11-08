from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Comment, SiteStat, UserProfile, TripEvent
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

@admin.register(TripEvent)
class TripEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'trip', 'user', 'event_time', 'has_location', 'reminder_enabled', 'synced_to_ralendar', 'created_at')
    list_filter = ('reminder_enabled', 'synced_to_ralendar', 'is_completed', 'is_deleted', 'source_app', 'created_at')
    search_fields = ('title', 'description', 'location_name', 'location_address', 'user__username', 'trip__title')
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_per_page = 50
    ordering = ('-created_at',)
    
    fieldsets = (
        ('基本信息', {
            'fields': ('id', 'trip', 'user', 'title', 'description')
        }),
        ('时间信息', {
            'fields': ('event_time', 'created_at', 'updated_at')
        }),
        ('地点信息', {
            'fields': ('location_name', 'location_address', 'location_lat', 'location_lng')
        }),
        ('提醒设置', {
            'fields': ('reminder_enabled', 'reminder_time', 'reminder_method')
        }),
        ('生态融合', {
            'fields': ('source_app', 'source_id', 'synced_to_ralendar', 'ralendar_event_id')
        }),
        ('状态', {
            'fields': ('is_completed', 'is_deleted')
        }),
    )
    
    def has_location(self, obj):
        """是否有地点"""
        return '✅' if obj.has_location() else '❌'
    has_location.short_description = '地点'

# 注册 Token Blacklist 模型（覆盖默认注册，以自定义显示）
admin.site.unregister(OutstandingToken)
admin.site.unregister(BlacklistedToken)
admin.site.register(OutstandingToken, OutstandingTokenAdmin)
admin.site.register(BlacklistedToken, BlacklistedTokenAdmin)
