"""
评论相关 ViewSet
处理评论的 CRUD 操作、文件上传等功能
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import CharFilter
from django_filters.rest_framework import FilterSet

logger = logging.getLogger(__name__)

from ...models import Comment, Trip
from ...serializers import (
    CommentSerializer,
    CommentCreateSerializer,
    CommentUpdateSerializer,
)
from ...utils.file_upload_handler import FileUploadHandler


class NoPagination(PageNumberPagination):
    """无分页类 - 用于禁用分页"""
    page_size = None
    
    def paginate_queryset(self, queryset, request, view=None):
        """
        重写此方法以禁用分页
        返回 None 表示不使用分页，直接返回所有数据
        """
        return None
    
    def get_paginated_response(self, data):
        """
        即使不使用分页，也确保返回正确的响应格式
        """
        from rest_framework.response import Response
        return Response(data)


class CommentFilter(FilterSet):
    """评论过滤器 - 使用 'trip' 参数代替 'page' 以避免与分页冲突"""
    trip = CharFilter(field_name='page', lookup_expr='exact')
    include_replies = CharFilter(method='filter_replies', help_text='包含回复：yes/no')
    
    def filter_replies(self, queryset, name, value):
        """根据参数决定是否包含回复"""
        if value and value.lower() == 'yes':
            # 返回所有评论（包括回复）
            return Comment.objects.all()
        # 默认只返回顶层评论
        return queryset.filter(parent__isnull=True)
    
    class Meta:
        model = Comment
        fields = {
            'user': ['exact'],
        }


class CommentViewSet(viewsets.ModelViewSet):
    """评论ViewSet"""
    queryset = Comment.objects.all().order_by('-timestamp')  # 默认包含所有评论
    permission_classes = [AllowAny]  # 允许所有人查看评论
    filter_backends = [DjangoFilterBackend]
    pagination_class = NoPagination  # 禁用分页，显示所有评论
    # 使用自定义过滤器类，将 'trip' 参数映射到模型的 'page' 字段
    filterset_class = CommentFilter
    
    def get_serializer_class(self):
        """根据action选择序列化器"""
        if self.action == 'create':
            return CommentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CommentUpdateSerializer
        return CommentSerializer
    
    def get_queryset(self):
        """根据action过滤queryset"""
        if self.action == 'list':
            # 列表页面只返回顶层评论
            return Comment.objects.filter(parent__isnull=True).order_by('-timestamp')
        # 其他action（包括retrieve, destroy等）需要访问所有评论
        return Comment.objects.all().order_by('-timestamp')
    
    def get_permissions(self):
        """根据action设置权限"""
        if self.action == 'create':
            # 任何登录用户都可以创建评论
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        else:
            # list和retrieve允许所有人访问
            return [AllowAny()]
    
    def perform_create(self, serializer):
        """创建评论时自动设置用户并上传文件到COS"""
        image = self.request.FILES.get('image')
        video = self.request.FILES.get('video')
        content = serializer.validated_data.get('content', '').strip() if serializer.validated_data.get('content') else ''
        
        # 验证至少有一项内容
        if not content and not image and not video:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'detail': '评论内容、图片或视频至少需要提供一项'})
        
        # 上传文件到 COS 并获取 URL
        image_url = None
        video_url = None
        
        try:
            if image:
                image_url = FileUploadHandler.upload_comment_image(image, self.request.user.id)
            
            if video:
                video_url = FileUploadHandler.upload_comment_video(video, self.request.user.id)
        except Exception as e:
            raise PermissionDenied(f'文件上传失败: {str(e)}')
        
        try:
            parent = serializer.validated_data.get('parent')
            page = serializer.validated_data.get('page')
            
            # 如果没有parent，说明要创建顶层评论，需要检查权限
            if not parent:
                # 尝试通过page找到对应的Trip
                trip = None
                try:
                    # page可能是slug，尝试查找Trip
                    trip = Trip.objects.filter(slug=page).first()
                except Exception:
                    pass
                
                # 如果找到Trip，检查是否为作者
                if trip:
                    if trip.author != self.request.user and not self.request.user.is_superuser:
                        raise PermissionDenied('只有旅行作者可以创建评论，其他人只能回复')
                else:
                    # 如果没有找到Trip，检查是否已有顶层评论
                    existing_top_level = Comment.objects.filter(page=page, parent__isnull=True).first()
                    
                    # 如果有顶层评论，检查是否为该评论的作者
                    if existing_top_level:
                        if existing_top_level.user != self.request.user and not self.request.user.is_superuser:
                            raise PermissionDenied('只有评论作者可以创建新的顶层评论，其他人只能回复')
            
            # 如果有parent，说明是回复
            if parent:
                # 获取父评论所属的页面
                parent_page = parent.page
                
                # 确保回复的页面与父评论一致
                if 'page' in serializer.validated_data and serializer.validated_data['page'] != parent_page:
                    from rest_framework.exceptions import ValidationError
                    raise ValidationError({'detail': '回复必须与父评论在同一页面'})
                
                # 将page设置为父评论的页面
                serializer.validated_data['page'] = parent_page
            
            # 将上传的文件 URL 添加到 validated_data
            if image_url:
                serializer.validated_data['image'] = image_url
            if video_url:
                serializer.validated_data['video'] = video_url
            
            serializer.save(user=self.request.user)
        except Exception as e:
            logger.error(f"创建评论时发生错误: {e}", exc_info=True)
            raise
    
    def perform_update(self, serializer):
        """更新评论时检查权限并处理文件上传"""
        comment = self.get_object()
        # 权限检查：只有评论作者或管理员可以修改
        if comment.user != self.request.user and not self.request.user.is_superuser:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('无权修改此评论')
        
        # 处理图片和视频上传（如果有）
        image = self.request.FILES.get('image')
        video = self.request.FILES.get('video')
        
        # 如果上传了新图片
        if image:
            try:
                # 删除旧图片
                if comment.image:
                    FileUploadHandler.delete_file(comment.image)
                
                # 上传新图片到 COS
                image_url = FileUploadHandler.upload_comment_image(image, self.request.user.id)
                serializer.validated_data['image'] = image_url
            except Exception as e:
                raise PermissionDenied(f'图片上传失败: {str(e)}')
        
        # 如果上传了新视频
        if video:
            try:
                # 删除旧视频
                if comment.video:
                    FileUploadHandler.delete_file(comment.video)
                
                # 上传新视频到 COS
                video_url = FileUploadHandler.upload_comment_video(video, self.request.user.id)
                serializer.validated_data['video'] = video_url
            except Exception as e:
                raise PermissionDenied(f'视频上传失败: {str(e)}')
        
        serializer.save()
    
    def destroy(self, request, *args, **kwargs):
        """删除评论"""
        try:
            # 手动获取评论对象，确保能够找到（包括回复）
            comment_id = kwargs.get('pk')
            try:
                comment = Comment.objects.get(id=comment_id)
            except Comment.DoesNotExist:
                return Response(
                    {'detail': '评论不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            user = request.user
            
            # 权限检查：回复只能由回复作者或旅行作者删除
            if comment.parent:  # 这是一个回复
                # 获取旅行作者
                trip = None
                try:
                    trip = Trip.objects.filter(slug=comment.page).first()
                except Exception:
                    pass
                
                # 检查权限：回复作者、旅行作者或管理员可以删除
                has_permission = (
                    comment.user == user or  # 回复作者
                    (trip and trip.author == user) or  # 旅行作者
                    user.is_superuser  # 管理员
                )
                
                if not has_permission:
                    return Response(
                        {'detail': '无权删除此回复（只有回复作者或旅行作者可以删除）'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            else:  # 这是顶层评论
                # 只有评论作者或管理员可以删除顶层评论
                if comment.user != user and not user.is_superuser:
                    return Response(
                        {'detail': '无权删除此评论'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            # 执行删除操作
            self.perform_destroy(comment)
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            logger.error(f"删除评论时发生错误: {e}", exc_info=True)
            return Response(
                {'detail': f'删除失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def perform_destroy(self, instance):
        """删除评论时同时删除 COS 上的文件（包括所有回复的文件）"""
        # 收集当前评论的文件 URL
        files_to_delete = []
        
        if instance.image:
            files_to_delete.append(('image', instance.image))
        if instance.video:
            files_to_delete.append(('video', instance.video))
        
        # 如果这是父评论，收集所有回复的文件 URL（递归）
        if instance.is_top_level:
            def collect_reply_files(comment):
                """递归收集回复的文件"""
                for reply in comment.replies.all():
                    if reply.image:
                        files_to_delete.append(('image', reply.image))
                    if reply.video:
                        files_to_delete.append(('video', reply.video))
                    # 递归处理回复的回复
                    collect_reply_files(reply)
            
            collect_reply_files(instance)
            logger.info(f"准备删除评论及其 {len(files_to_delete)} 个关联文件")
        
        # 删除评论对象（Django 自动级联删除所有回复）
        try:
            instance.delete()
            logger.info(f"评论 {instance.id} 及其所有回复已从数据库删除")
        except Exception as e:
            logger.error(f"删除评论对象失败: {e}")
            raise
        
        # 从 COS 删除所有收集到的文件
        for file_type, file_url in files_to_delete:
            try:
                FileUploadHandler.delete_file(file_url)
                logger.info(f"成功删除{file_type}文件: {file_url}")
            except Exception as e:
                logger.warning(f"删除{file_type}文件失败: {e} - {file_url}")
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def replies(self, request, pk=None):
        """获取评论的回复列表"""
        comment = self.get_object()
        replies = Comment.objects.filter(parent_id=comment.id).order_by('timestamp')
        serializer = CommentSerializer(replies, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """点赞/取消点赞"""
        comment = self.get_object()
        user = request.user
        
        # 检查用户是否已经点赞
        if user in comment.liked_by.all():
            # 取消点赞
            comment.liked_by.remove(user)
            comment.likes = max(0, comment.likes - 1)  # 防止负数
            comment.save()
            return Response({
                'liked': False,
                'likes': comment.likes,
                'message': '已取消点赞'
            })
        else:
            # 点赞
            comment.liked_by.add(user)
            comment.likes += 1
            comment.save()
            return Response({
                'liked': True,
                'likes': comment.likes,
                'message': '点赞成功'
            })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_image(self, request, pk=None):
        """为评论添加或替换图片（上传到COS）"""
        comment = self.get_object()
        
        # 权限检查：只有评论作者或管理员可以修改图片
        if comment.user != request.user and not request.user.is_superuser:
            return Response(
                {'detail': '无权修改此评论'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 获取上传的图片
        image = request.FILES.get('image')
        if not image:
            return Response(
                {'detail': '请上传图片'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 验证图片大小（放宽到 20MB）
        if image.size > 20 * 1024 * 1024:
            return Response(
                {'detail': '图片大小不能超过20MB'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 如果评论已有图片，删除旧图片
            if comment.image:
                old_image_url = comment.image
                try:
                    FileUploadHandler.delete_file(old_image_url)
                    logger.info(f"成功删除旧图片: {old_image_url}")
                except Exception as e:
                    logger.warning(f"删除旧图片失败（已忽略）: {e}")
            
            # 上传新图片到 COS
            image_url = FileUploadHandler.upload_comment_image(image, request.user.id)
            
            # 保存新图片 URL
            comment.image = image_url
            comment.save()
            
            # 返回更新后的评论
            serializer = CommentSerializer(comment, context={'request': request})
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"添加图片失败: {e}", exc_info=True)
            return Response(
                {'detail': f'添加图片失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
