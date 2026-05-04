"""
用户头像上传视图 - 上传到腾讯云COS
"""
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from ...utils.storage.file_upload_handler import FileUploadHandler

logger = logging.getLogger(__name__)


@csrf_exempt
@login_required
def upload_avatar(request):
    """上传头像到腾讯云 COS"""
    if request.method == 'POST' and request.FILES.get('avatar'):
        avatar_file = request.FILES['avatar']
        
        # 验证文件类型
        if not avatar_file.content_type.startswith('image/'):
            return JsonResponse({'success': False, 'error': '请上传图片文件'})
        
        # 验证文件大小（放宽到 10MB）
        if avatar_file.size > 10 * 1024 * 1024:
            return JsonResponse({'success': False, 'error': '图片大小不能超过10MB'})
        
        try:
            profile = request.user.profile
            
            # 删除旧头像（如果存在）
            if profile.avatar:
                old_avatar_url = profile.avatar
                try:
                    FileUploadHandler.delete_file(old_avatar_url)
                except Exception as e:
                    logger.warning(f"删除旧头像失败（已忽略）: {e}")
            
            # 上传新头像到 COS
            avatar_url = FileUploadHandler.upload_avatar(avatar_file, request.user.id)
            
            # 保存 COS URL 到数据库
            profile.avatar = avatar_url
            profile.save()
            
            return JsonResponse({
                'success': True, 
                'avatar_url': profile.get_avatar_url(),
                'message': '头像上传成功！'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'上传失败：{str(e)}'})
    
    return JsonResponse({'success': False, 'error': '请选择要上传的图片'})

