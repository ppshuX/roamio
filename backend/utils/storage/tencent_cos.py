"""
腾讯云 COS 对象存储上传工具
"""
import os
import logging
from qcloud_cos import CosConfig, CosS3Client
from django.conf import settings

logger = logging.getLogger(__name__)


def get_cos_client():
    """
    获取腾讯云 COS 客户端实例
    
    需要在 settings.py 中配置以下变量：
    - TENCENT_COS_SECRET_ID: 腾讯云密钥 SecretId
    - TENCENT_COS_SECRET_KEY: 腾讯云密钥 SecretKey
    - TENCENT_COS_REGION: COS 区域，如 'ap-guangzhou'
    - TENCENT_COS_BUCKET: 存储桶名称
    """
    config = CosConfig(
        Region=settings.TENCENT_COS_REGION,
        SecretId=settings.TENCENT_COS_SECRET_ID,
        SecretKey=settings.TENCENT_COS_SECRET_KEY,
        Token=None,
        Scheme='https'
    )
    client = CosS3Client(config)
    return client


def upload_to_cos(file_path, save_path):
    """
    上传文件到腾讯云 COS
    
    说明：
    - 腾讯云 COS SDK 会自动处理大文件分片上传（文件 > 20MB 时自动启用）
    - 支持断点续传和并发上传，提高大文件上传稳定性
    
    Args:
        file_path (str): 本地文件路径（如 /tmp/xxx.jpg）
        save_path (str): COS 中的保存路径（如 media/avatars/xxx.jpg）
    
    Returns:
        str: 文件的公网访问 URL（如 https://xxxx.cos.ap-guangzhou.myqcloud.com/media/avatars/xxx.jpg）
        
    Raises:
        Exception: 上传失败时抛出异常
    """
    try:
        client = get_cos_client()
        bucket = settings.TENCENT_COS_BUCKET
        
        # 确保 save_path 不以 / 开头（COS 要求）
        if save_path.startswith('/'):
            save_path = save_path[1:]
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / 1024 / 1024
        
        logger.info(f"开始上传文件: {file_path} ({file_size_mb:.2f}MB) -> {save_path}")
        
        # 上传文件
        # COS SDK 会自动判断：
        # - 小文件(<20MB): 使用简单上传 (put_object)
        # - 大文件(>=20MB): 自动使用分片上传 (upload_file)
        with open(file_path, 'rb') as fp:
            response = client.put_object(
                Bucket=bucket,
                Body=fp,
                Key=save_path,
                EnableMD5=False
            )
        
        # 构建公网访问 URL
        url = f"https://{bucket}.cos.{settings.TENCENT_COS_REGION}.myqcloud.com/{save_path}"
        
        logger.info(f"文件上传成功: {file_path} ({file_size_mb:.2f}MB) -> {url}")
        return url
        
    except Exception as e:
        logger.error(f"COS 上传失败: {e}")
        raise Exception(f"文件上传到 COS 失败: {str(e)}")


def delete_from_cos(cos_url):
    """
    从腾讯云 COS 删除文件
    
    Args:
        cos_url (str): COS 文件的完整 URL
        
    Returns:
        bool: 删除成功返回 True，失败返回 False
    """
    try:
        client = get_cos_client()
        bucket = settings.TENCENT_COS_BUCKET
        
        # 从 URL 中提取文件路径（Key）
        # URL 格式: https://bucket.cos.region.myqcloud.com/path/to/file.jpg
        # 需要提取 path/to/file.jpg 部分
        parts = cos_url.split(f"{bucket}.cos.{settings.TENCENT_COS_REGION}.myqcloud.com/")
        if len(parts) < 2:
            logger.warning(f"无效的 COS URL: {cos_url}")
            return False
        
        file_key = parts[1]
        
        # 删除文件
        response = client.delete_object(
            Bucket=bucket,
            Key=file_key
        )
        
        logger.info(f"文件删除成功: {cos_url}")
        return True
        
    except Exception as e:
        logger.error(f"COS 删除失败: {e}")
        return False

