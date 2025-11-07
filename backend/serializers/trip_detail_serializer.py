"""
旅行计划序列化器（用于编辑器）
"""
from rest_framework import serializers
from ..models import Trip
from .user_serializer import UserSerializer


class TripCreateSerializer(serializers.ModelSerializer):
    """创建旅行序列化器"""
    
    class Meta:
        model = Trip
        fields = [
            'slug', 'title', 'description', 'icon', 'start_date', 'end_date',
            'status', 'visibility', 'config', 'overview', 
            'theme_color', 'background_music'
        ]
        read_only_fields = ['slug']
    
    def validate_title(self, value):
        """验证标题不为空"""
        if not value or not value.strip():
            raise serializers.ValidationError("旅行标题不能为空")
        return value.strip()
    
    def create(self, validated_data):
        """创建旅行，确保slug正确生成"""
        # 确保标题存在
        title = validated_data.get('title', '')
        if not title or not title.strip():
            raise serializers.ValidationError("旅行标题不能为空")
        
        # 创建旅行，Django的save方法会自动生成slug
        trip = super().create(validated_data)
        return trip


class TripDetailSerializer(serializers.ModelSerializer):
    """旅行详情序列化器"""
    author = UserSerializer(read_only=True)
    days_count = serializers.ReadOnlyField()
    is_published = serializers.ReadOnlyField()
    is_public = serializers.ReadOnlyField()
    name = serializers.CharField(source='title', read_only=True)  # 前端兼容字段
    
    class Meta:
        model = Trip
        fields = [
            'id', 'slug', 'title', 'name', 'description', 'icon',
            'author', 'start_date', 'end_date', 'days_count',
            'status', 'visibility', 'is_published', 'is_public',
            'config', 'overview', 'theme_color', 'background_music',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'author', 'created_at', 'updated_at', 'name']


class TripListSerializer(serializers.ModelSerializer):
    """旅行列表序列化器（精简版）"""
    author = serializers.StringRelatedField()
    days_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Trip
        fields = [
            'id', 'slug', 'title', 'description', 'icon',
            'author', 'days_count', 'status', 'visibility',
            'theme_color', 'background_music',
            'created_at', 'updated_at'
        ]


class TripUpdateSerializer(serializers.ModelSerializer):
    """更新旅行序列化器"""
    
    class Meta:
        model = Trip
        fields = [
            'title', 'description', 'icon', 'start_date', 'end_date',
            'status', 'visibility', 'config', 'overview',
            'theme_color', 'background_music'
        ]
    
    def validate(self, attrs):
        """确保发布时必须有标题"""
        if attrs.get('status') == 'published' and not attrs.get('title'):
            raise serializers.ValidationError({
                'title': '发布前必须设置标题'
            })
        return attrs

