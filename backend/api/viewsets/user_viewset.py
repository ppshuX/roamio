"""
用户相关 ViewSet
处理用户信息的查询、更新、头像上传等功能
"""
import logging
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.contrib.auth.models import User

from ...models import Comment
from ...serializers import (
    UserSerializer,
    UserProfileSerializer,
    UpdateUserSerializer,
    UserProfileUpdateSerializer,
    AvatarUploadSerializer,
)
from ...utils.file_upload_handler import FileUploadHandler

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ReadOnlyModelViewSet,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin):
    """用户ViewSet"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def destroy(self, request, *args, **kwargs):
        """删除用户账号（只能删除自己的）"""
        user = self.get_object()
        
        # 权限检查：只能删除自己的账号
        if user != request.user:
            return Response(
                {'detail': '无权删除他人账号'},
                status=403  # HTTP_403_FORBIDDEN
            )
        
        # 调用父类的删除方法
        return super().destroy(request, *args, **kwargs)
    
    def get_serializer_class(self):
        """根据action选择序列化器"""
        if self.action in ['update', 'partial_update']:
            return UpdateUserSerializer
        return UserSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """获取用户详情时自动计算等级"""
        response = super().retrieve(request, *args, **kwargs)
        user = self.get_object()
        # 自动计算并更新等级
        if hasattr(user, 'profile') and user.profile:
            user.profile.calculate_level()
            user.profile.save()
        return response
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_avatar(self, request, pk=None):
        """上传头像到腾讯云 COS"""
        user = self.get_object()
        
        # 权限检查：只能修改自己的头像
        if user != request.user and not request.user.is_superuser:
            return Response(
                {'detail': '无权修改他人头像'},
                status=403  # HTTP_403_FORBIDDEN
            )
        
        serializer = AvatarUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        avatar_file = serializer.validated_data['avatar']
        profile = user.profile
        
        try:
            # 删除旧头像（如果存在）
            if profile.avatar:
                old_avatar_url = profile.avatar
                # 在后台删除旧文件（不阻塞响应）
                try:
                    FileUploadHandler.delete_file(old_avatar_url)
                except Exception as e:
                    logger.warning(f"删除旧头像失败（已忽略）: {e}")
            
            # 上传新头像到 COS
            avatar_url = FileUploadHandler.upload_avatar(avatar_file, user.id)
            
            # 保存 COS URL 到数据库
            profile.avatar = avatar_url
            profile.save()
            
            return Response({
                'avatar_url': profile.get_avatar_url(),
                'detail': '头像上传成功'
            })
            
        except Exception as e:
            return Response(
                {'detail': f'头像上传失败: {str(e)}'},
                status=500
            )
    
    @action(detail=False, methods=['patch', 'put'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """更新个人资料（包括 bio, tags, visited_countries）"""
        profile = request.user.profile
        serializer = UserProfileUpdateSerializer(
            profile, 
            data=request.data, 
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # 自动计算等级
        profile.calculate_level()
        profile.save()
        
        return Response({
            'detail': '个人资料更新成功',
            'profile': UserProfileSerializer(profile).data
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def bind_email(self, request):
        """
        绑定邮箱（需要邮箱验证码验证）
        
        流程：
        1. 前端发送验证码（type=bind_email）
        2. 前端验证验证码获取verification_token
        3. 调用此接口，传入email和verification_token，完成绑定并标记邮箱为已验证
        """
        from django.core.cache import cache
        from django.utils import timezone
        
        email = request.data.get('email', '').strip().lower()
        verification_token = request.data.get('verification_token', '')
        
        if not email:
            return Response({
                'error': '邮箱地址不能为空'
            }, status=400)
        
        if not verification_token:
            return Response({
                'error': '验证token不能为空'
            }, status=400)
        
        # 验证邮箱验证token
        cache_key = f'email_verified_token:{verification_token}'
        token_data = cache.get(cache_key)
        
        if not token_data:
            return Response({
                'error': '验证token无效或已过期，请重新验证邮箱'
            }, status=400)
        
        # 检查token中的邮箱是否匹配
        if token_data.get('email') != email:
            return Response({
                'error': '验证token与邮箱地址不匹配'
            }, status=400)
        
        # 检查验证类型是否为绑定邮箱
        if token_data.get('verification_type') != 'bind_email':
            return Response({
                'error': '验证token类型错误'
            }, status=400)
        
        # 检查邮箱是否已被其他用户使用
        if User.objects.exclude(pk=request.user.pk).filter(email=email).exists():
            return Response({
                'error': '该邮箱已被其他用户使用'
            }, status=400)
        
        # 更新用户邮箱
        request.user.email = email
        request.user.save()
        
        # 标记邮箱为已验证
        if hasattr(request.user, 'profile'):
            request.user.profile.email_verified = True
            request.user.profile.email_verified_at = timezone.now()
            request.user.profile.save()
        
        # 删除验证token（只能使用一次）
        cache.delete(cache_key)
        
        return Response({
            'success': True,
            'message': '邮箱绑定成功，邮箱已标记为已验证',
            'email': email
        })
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """获取用户统计信息"""
        user = self.get_object()
        comments_count = Comment.objects.filter(user=user).count()
        
        return Response({
            'comments_count': comments_count,
        })
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticatedOrReadOnly])
    def profile(self, request, pk=None):
        """获取用户公开资料（包含统计信息）"""
        user = self.get_object()
        
        # 自动计算并更新等级
        if hasattr(user, 'profile') and user.profile:
            user.profile.calculate_level()
            user.profile.save()
        
        # 序列化用户信息
        serializer = UserSerializer(user)
        data = serializer.data
        
        # 添加是否为管理员标识
        data['is_admin'] = user.is_superuser or user.is_staff
        
        return Response(data)