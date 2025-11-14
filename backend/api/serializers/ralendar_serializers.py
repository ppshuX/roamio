"""
Ralendar 相关序列化器
"""
from rest_framework import serializers
from backend.models import RalendarAccount


class RalendarAccountSerializer(serializers.ModelSerializer):
    """
    Ralendar 账号序列化器
    """
    is_token_expired = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()
    
    class Meta:
        model = RalendarAccount
        fields = [
            'id',
            'ralendar_user_id',
            'ralendar_username',
            'ralendar_email',
            'ralendar_avatar',
            'ralendar_provider',
            'is_default',
            'is_active',
            'is_token_expired',
            'display_name',
            'created_at',
            'last_synced_at'
        ]
        read_only_fields = [
            'id',
            'ralendar_user_id',
            'ralendar_username',
            'ralendar_email',
            'ralendar_avatar',
            'ralendar_provider',
            'created_at',
            'last_synced_at'
        ]

