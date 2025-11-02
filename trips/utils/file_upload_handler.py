"""
统一文件上传处理器
处理所有媒体文件的上传逻辑：临时保存、压缩、上传到COS、删除临时文件
"""
import os
import uuid
import tempfile
import logging
from django.utils import timezone
from PIL import Image
from .tencent_cos import upload_to_cos, delete_from_cos

logger = logging.getLogger(__name__)


class FileUploadHandler:
    """文件上传处理器"""
    
    @staticmethod
    def generate_unique_filename(original_filename, prefix=''):
        """
        生成唯一的文件名
        
        Args:
            original_filename (str): 原始文件名
            prefix (str): 文件名前缀（如用户ID）
            
        Returns:
            str: 唯一的文件名
        """
        ext = os.path.splitext(original_filename)[-1].lower()
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        unique_id = uuid.uuid4().hex[:8]
        
        if prefix:
            return f"{prefix}_{timestamp}_{unique_id}{ext}"
        return f"{timestamp}_{unique_id}{ext}"
    
    @staticmethod
    def compress_image(temp_file_path, max_width=1920, quality=85):
        """
        压缩图片
        
        Args:
            temp_file_path (str): 临时文件路径
            max_width (int): 最大宽度（默认 1920px）
            quality (int): JPEG 质量（默认 85）
        """
        try:
            img = Image.open(temp_file_path)
            
            # 如果宽度超过限制，缩放
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # 转换为 RGB（处理 PNG 等格式）
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 保存为 JPEG
            img.save(temp_file_path, format='JPEG', quality=quality)
            
            # 如果文件仍然很大（> 3MB），进一步压缩
            if os.path.getsize(temp_file_path) > 3 * 1024 * 1024:
                img.save(temp_file_path, format='JPEG', quality=70)
            
            logger.info(f"图片压缩完成: {temp_file_path}, 大小: {os.path.getsize(temp_file_path) / 1024:.1f}KB")
            
        except Exception as e:
            logger.warning(f"图片压缩失败（将上传原图）: {e}")
    
    @staticmethod
    def upload_file(uploaded_file, save_dir='media', filename_prefix='', compress_image=True):
        """
        处理文件上传到 COS（支持图片压缩）
        
        Args:
            uploaded_file: Django UploadedFile 对象
            save_dir (str): COS 中的保存目录（如 'media/avatars'）
            filename_prefix (str): 文件名前缀（如用户ID）
            compress_image (bool): 是否压缩图片（默认 True）
            
        Returns:
            str: 文件的 COS 公网访问 URL
            
        Raises:
            Exception: 上传失败时抛出异常
        """
        temp_file_path = None
        
        try:
            # 生成唯一文件名
            unique_filename = FileUploadHandler.generate_unique_filename(
                uploaded_file.name, 
                prefix=filename_prefix
            )
            
            # 创建临时文件
            temp_dir = tempfile.gettempdir()
            temp_file_path = os.path.join(temp_dir, unique_filename)
            
            # 保存上传的文件到临时目录
            with open(temp_file_path, 'wb+') as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
            
            logger.info(f"临时文件已保存: {temp_file_path}")
            
            # 如果是图片且需要压缩
            if compress_image and uploaded_file.content_type.startswith('image/'):
                FileUploadHandler.compress_image(temp_file_path)
            
            # 构建 COS 保存路径
            cos_save_path = f"{save_dir}/{unique_filename}"
            
            # 上传到 COS
            cos_url = upload_to_cos(temp_file_path, cos_save_path)
            
            return cos_url
            
        except Exception as e:
            logger.error(f"文件上传失败: {e}")
            raise
            
        finally:
            # 删除临时文件
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    logger.info(f"临时文件已删除: {temp_file_path}")
                except Exception as e:
                    logger.warning(f"删除临时文件失败: {e}")
    
    @staticmethod
    def delete_file(cos_url):
        """
        从 COS 删除文件
        
        Args:
            cos_url (str): COS 文件的完整 URL
            
        Returns:
            bool: 删除成功返回 True，失败返回 False
        """
        if not cos_url:
            return False
        
        return delete_from_cos(cos_url)
    
    @staticmethod
    def upload_avatar(uploaded_file, user_id):
        """
        上传用户头像（会压缩为 300x300 正方形）
        
        Args:
            uploaded_file: Django UploadedFile 对象
            user_id (int): 用户ID
            
        Returns:
            str: 头像的 COS 公网访问 URL
        """
        temp_file_path = None
        
        try:
            # 生成唯一文件名
            unique_filename = FileUploadHandler.generate_unique_filename(
                uploaded_file.name,
                prefix=f'user{user_id}'
            )
            
            # 创建临时文件
            temp_dir = tempfile.gettempdir()
            temp_file_path = os.path.join(temp_dir, unique_filename)
            
            # 保存上传的文件到临时目录
            with open(temp_file_path, 'wb+') as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
            
            # 头像特殊处理：裁剪为正方形并缩放到 300x300
            try:
                img = Image.open(temp_file_path)
                
                # 裁剪为正方形
                min_side = min(img.width, img.height)
                left = (img.width - min_side) // 2
                top = (img.height - min_side) // 2
                right = left + min_side
                bottom = top + min_side
                img = img.crop((left, top, right, bottom))
                
                # 调整为 300x300 像素
                img = img.resize((300, 300), Image.Resampling.LANCZOS)
                
                # 转换为 RGB 并保存
                img = img.convert('RGB')
                img.save(temp_file_path, format='JPEG', quality=90)
                
                logger.info(f"头像处理完成: 300x300, {os.path.getsize(temp_file_path) / 1024:.1f}KB")
            except Exception as e:
                logger.warning(f"头像处理失败（将上传原图）: {e}")
            
            # 上传到 COS
            cos_save_path = f"media/avatars/{unique_filename}"
            cos_url = upload_to_cos(temp_file_path, cos_save_path)
            
            return cos_url
            
        finally:
            # 删除临时文件
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except:
                    pass
    
    @staticmethod
    def upload_comment_image(uploaded_file, user_id):
        """
        上传评论图片
        
        Args:
            uploaded_file: Django UploadedFile 对象
            user_id (int): 用户ID
            
        Returns:
            str: 图片的 COS 公网访问 URL
        """
        return FileUploadHandler.upload_file(
            uploaded_file,
            save_dir='media/comments/images',
            filename_prefix=f'user{user_id}'
        )
    
    @staticmethod
    def upload_comment_video(uploaded_file, user_id):
        """
        上传评论视频（不压缩）
        
        Args:
            uploaded_file: Django UploadedFile 对象
            user_id (int): 用户ID
            
        Returns:
            str: 视频的 COS 公网访问 URL
        """
        return FileUploadHandler.upload_file(
            uploaded_file,
            save_dir='media/comments/videos',
            filename_prefix=f'user{user_id}',
            compress_image=False  # 视频不压缩
        )

