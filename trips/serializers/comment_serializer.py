"""
评论相关序列化器
"""
from rest_framework import serializers
from ..models import Comment
from .user_serializer import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器（列表/详情）- 支持递归嵌套回复"""
    user = UserSerializer(read_only=True)
    can_delete = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    is_top_level = serializers.SerializerMethodField()
    parent_id = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()  # 递归回复
    user_liked = serializers.SerializerMethodField()  # 新增：当前用户是否已点赞
    
    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'parent_id', 'content', 'image', 'video', 
            'page', 'timestamp', 'can_delete', 'is_top_level', 'replies_count', 'replies',
            'likes', 'user_liked'  # 新增：点赞数和点赞状态
        ]
        read_only_fields = ['id', 'user', 'timestamp', 'likes']
    
    def get_image(self, obj):
        """返回图片URL（COS完整URL或本地路径）"""
        if not obj.image:
            return None
        
        # image 现在是 URLField，直接返回字符串
        image_url = obj.image
        
        # 如果是 COS URL（以 http:// 或 https:// 开头），直接返回
        if image_url.startswith('http://') or image_url.startswith('https://'):
            return image_url
        
        # 本地路径，构建完整 URL（兼容旧数据）
        request = self.context.get('request')
        if request:
            if not image_url.startswith('/'):
                image_url = f"/media/{image_url}"
            return f"{request.scheme}://{request.get_host()}{image_url}"
        else:
            return image_url
    
    def get_video(self, obj):
        """返回视频URL（COS完整URL或本地路径）"""
        if not obj.video:
            return None
        
        # video 现在是 URLField，直接返回字符串
        video_url = obj.video
        
        # 如果是 COS URL（以 http:// 或 https:// 开头），直接返回
        if video_url.startswith('http://') or video_url.startswith('https://'):
            return video_url
        
        # 本地路径，构建完整 URL（兼容旧数据）
        request = self.context.get('request')
        if request:
            if not video_url.startswith('/'):
                video_url = f"/media/{video_url}"
            return f"{request.scheme}://{request.get_host()}{video_url}"
        else:
            return video_url
    
    def get_can_delete(self, obj):
        """判断当前用户是否可以删除此评论"""
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            return False
        if not request.user.is_authenticated:
            return False
        
        # 如果是回复（有父评论）
        if obj.parent:
            # 回复只能由回复作者或旅行作者删除
            from ..models import Trip
            try:
                trip = Trip.objects.filter(slug=obj.page).first()
                # 权限：回复作者、旅行作者或管理员
                return (
                    obj.user == request.user or  # 回复作者
                    (trip and trip.user == request.user) or  # 旅行作者
                    request.user.is_superuser  # 管理员
                )
            except Exception:
                # 如果获取Trip失败，回退到原始逻辑
                return obj.user == request.user or request.user.is_superuser
        else:
            # 顶层评论只能由评论作者或管理员删除
            return obj.user == request.user or request.user.is_superuser
    
    def get_is_top_level(self, obj):
        """判断是否为顶层评论"""
        try:
            # 直接检查parent字段
            return obj.parent is None or obj.parent_id is None
        except (AttributeError, Exception):
            return obj.parent is None
    
    def get_parent_id(self, obj):
        """获取父评论ID"""
        return obj.parent_id if obj.parent else None
    
    def get_replies_count(self, obj):
        """获取回复数量"""
        return obj.replies.count()
    
    def get_user_liked(self, obj):
        """判断当前用户是否已点赞"""
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            return False
        if not request.user.is_authenticated:
            return False
        return request.user in obj.liked_by.all()
    
    def get_replies(self, obj):
        """递归获取所有嵌套回复（限制深度避免性能问题）"""
        # 检查当前递归深度
        depth = self.context.get('depth', 0)
        max_depth = self.context.get('max_depth', 5)  # 最多5层嵌套
        
        # 超过最大深度，不再递归
        if depth >= max_depth:
            return []
        
        # 获取当前评论的所有直接回复
        # 排序规则：按点赞数降序，相同点赞数按时间升序（早的在前）
        replies = obj.replies.all().order_by('-likes', 'timestamp')
        
        # 如果没有回复，直接返回空数组
        if not replies.exists():
            return []
        
        # 创建新的上下文，增加深度
        context = self.context.copy()
        context['depth'] = depth + 1
        
        # 递归序列化回复
        serializer = CommentSerializer(replies, many=True, context=context)
        return serializer.data


class CommentCreateSerializer(serializers.ModelSerializer):
    """评论创建序列化器"""
    parent = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), required=False, allow_null=True)
    content = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    # 这些字段在 viewset 中处理，不参与序列化验证
    
    class Meta:
        model = Comment
        fields = ['content', 'page', 'parent']
    
    def validate(self, attrs):
        """验证至少有一项内容"""
        # 注意：image 和 video 在 viewset 中处理上传
        # 这里只验证 content 或确保至少有文件上传
        return attrs


class CommentUpdateSerializer(serializers.ModelSerializer):
    """评论更新序列化器"""
    
    class Meta:
        model = Comment
        fields = ['content']
    
    def validate_content(self, value):
        """验证内容不为空"""
        if not value or not value.strip():
            raise serializers.ValidationError("评论内容不能为空")
        return value.strip()


class CommentListSerializer(serializers.ModelSerializer):
    """评论列表序列化器（精简版）"""
    user = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'image', 'video', 'timestamp']
    
    def get_image(self, obj):
        """返回图片URL（COS完整URL或本地路径）"""
        if not obj.image:
            return None
        
        # image 现在是 URLField，直接返回字符串
        image_url = obj.image
        
        # 如果是 COS URL（以 http:// 或 https:// 开头），直接返回
        if image_url.startswith('http://') or image_url.startswith('https://'):
            return image_url
        
        # 本地路径，构建完整 URL（兼容旧数据）
        request = self.context.get('request')
        if request:
            if not image_url.startswith('/'):
                image_url = f"/media/{image_url}"
            return f"{request.scheme}://{request.get_host()}{image_url}"
        else:
            return image_url
    
    def get_video(self, obj):
        """返回视频URL（COS完整URL或本地路径）"""
        if not obj.video:
            return None
        
        # video 现在是 URLField，直接返回字符串
        video_url = obj.video
        
        # 如果是 COS URL（以 http:// 或 https:// 开头），直接返回
        if video_url.startswith('http://') or video_url.startswith('https://'):
            return video_url
        
        # 本地路径，构建完整 URL（兼容旧数据）
        request = self.context.get('request')
        if request:
            if not video_url.startswith('/'):
                video_url = f"/media/{video_url}"
            return f"{request.scheme}://{request.get_host()}{video_url}"
        else:
            return video_url
    
    def get_user(self, obj):
        """只返回用户的基本信息"""
        try:
            avatar = obj.user.profile.get_avatar_url()
        except Exception:
            avatar = None
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'avatar': avatar
        }
