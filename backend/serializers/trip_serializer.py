"""
旅行和统计相关序列化器
"""
from rest_framework import serializers
from ..models import SiteStat, Comment, Trip



class SiteStatSerializer(serializers.ModelSerializer):
    """网站统计序列化器"""
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SiteStat
        fields = ['page', 'views', 'likes', 'checked_in', 'comments_count']
        read_only_fields = ['page', 'views', 'likes', 'checked_in']
    
    def get_comments_count(self, obj):
        """获取评论数量，兼容新老页面键：'slug' 与 'tp:slug' 均计入"""
        page_key = obj.page
        if page_key.startswith('tp:'):
            raw = page_key[3:]
            return Comment.objects.filter(page__in=[page_key, raw]).count()
        return Comment.objects.filter(page=page_key).count()


class TripSerializer(serializers.Serializer):
    """旅行页面序列化器"""
    slug = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    stats = serializers.DictField(read_only=True)
    
    def to_representation(self, instance):
        """自定义返回格式"""
        # 页面信息映射
        page_info = {
            'trip': {
                'name': '厦门三天两晚游',
                'description': '探索厦门的植物园、鼓浪屿、八市美食',
            },
            'trip1': {
                'name': '三岔河一日游',
                'description': '龙凤寺、白水塘、紫溪湿地自然之旅',
            },
            'trip2': {
                'name': '曲靖二日游',
                'description': '感受曲靖的文化景点和自然风光',
            },
            'trip3': {
                'name': '昆明旅行',
                'description': '探索春城昆明的自然与人文',
            },
            'trip4': {
                'name': '长沙三天两夜慢旅行',
                'description': '深度体验长沙的文化美食和历史',
            },
        }
        
        page = instance.page
        
        # 尝试从Trip模型获取标题和描述
        try:
            trip = Trip.objects.get(slug=page)
            info = {
                'name': trip.title,
                'description': trip.description or f'{trip.title}',
            }
        except Trip.DoesNotExist:
            # 使用默认映射
            info = page_info.get(page, {
                'name': page.upper(),
                'description': f'{page} 旅行计划'
            })
        
        return {
            'slug': page,
            'name': info['name'],
            'description': info['description'],
            'stats': SiteStatSerializer(instance).data,
        }


class TripListSerializer(serializers.Serializer):
    """旅行列表序列化器（精简版）"""
    slug = serializers.CharField(source='page')
    name = serializers.CharField()
    views = serializers.IntegerField()
    likes = serializers.IntegerField()

