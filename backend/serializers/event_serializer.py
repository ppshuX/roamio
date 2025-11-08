"""
旅行事件序列化器
用于 API 数据序列化和验证
"""

from rest_framework import serializers
from backend.models import TripEvent, Trip
from django.contrib.auth import get_user_model

User = get_user_model()


class TripEventSerializer(serializers.ModelSerializer):
    """旅行事件序列化器"""
    
    # 只读字段
    user = serializers.SerializerMethodField()
    trip_title = serializers.CharField(source='trip.title', read_only=True)
    location = serializers.SerializerMethodField()
    reminder = serializers.SerializerMethodField()
    baidu_map_url = serializers.SerializerMethodField()
    
    class Meta:
        model = TripEvent
        fields = [
            'id',
            'trip',
            'trip_title',
            'user',
            'title',
            'description',
            'event_time',
            'location',
            'reminder',
            'source_app',
            'source_id',
            'synced_to_ralendar',
            'ralendar_event_id',
            'is_completed',
            'is_deleted',
            'baidu_map_url',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'trip_title',
            'user',
            'synced_to_ralendar',
            'ralendar_event_id',
            'is_deleted',
            'baidu_map_url',
            'created_at',
            'updated_at',
        ]
    
    def get_user(self, obj):
        """获取用户信息"""
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'avatar_url': obj.user.profile.get_avatar_url() if hasattr(obj.user, 'profile') else None,
        }
    
    def get_location(self, obj):
        """获取地点信息"""
        return obj.location_dict
    
    def get_reminder(self, obj):
        """获取提醒信息"""
        return obj.reminder_dict
    
    def get_baidu_map_url(self, obj):
        """获取百度地图链接"""
        return obj.get_baidu_map_url()
    
    def create(self, validated_data):
        """创建事件"""
        # 从 context 中获取 request
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        
        # 从 context 中获取 trip_id
        trip_id = self.context.get('trip_id')
        if trip_id:
            validated_data['trip_id'] = trip_id
        
        return super().create(validated_data)
    
    def validate(self, data):
        """验证数据"""
        # 如果启用提醒，必须设置提醒时间
        if data.get('reminder_enabled') and not data.get('reminder_time'):
            raise serializers.ValidationError({
                'reminder_time': '启用提醒时必须设置提醒时间'
            })
        
        # 如果有坐标，必须同时有经纬度
        location_lat = data.get('location_lat')
        location_lng = data.get('location_lng')
        if (location_lat is not None and location_lng is None) or \
           (location_lat is None and location_lng is not None):
            raise serializers.ValidationError({
                'location': '经纬度必须同时提供'
            })
        
        return data


class TripEventCreateSerializer(serializers.Serializer):
    """创建事件的简化序列化器（接收前端数据）"""
    
    title = serializers.CharField(max_length=200, required=True)
    description = serializers.CharField(required=False, allow_blank=True)
    event_time = serializers.DateTimeField(required=False, allow_null=True)
    
    # 地点信息（嵌套对象）
    location = serializers.DictField(required=False, allow_null=True)
    
    # 提醒信息（嵌套对象）
    reminder = serializers.DictField(required=False, allow_null=True)
    
    # 来源标记
    source_app = serializers.CharField(max_length=50, required=False, default='roamio')
    source_id = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    def validate_location(self, value):
        """验证地点信息"""
        if not value:
            return {}
        
        # 确保字段存在
        location = {
            'name': value.get('name', ''),
            'address': value.get('address', ''),
            'lat': value.get('lat'),
            'lng': value.get('lng'),
        }
        
        # 如果有坐标，必须同时有经纬度
        if (location['lat'] is not None and location['lng'] is None) or \
           (location['lat'] is None and location['lng'] is not None):
            raise serializers.ValidationError('经纬度必须同时提供')
        
        return location
    
    def validate_reminder(self, value):
        """验证提醒信息"""
        if not value:
            return {
                'enabled': False,
                'time': None,
                'method': 'email'
            }
        
        reminder = {
            'enabled': value.get('enabled', False),
            'time': value.get('time'),
            'method': value.get('method', 'email'),
        }
        
        # 如果启用提醒，必须设置提醒时间
        if reminder['enabled'] and not reminder['time']:
            raise serializers.ValidationError('启用提醒时必须设置提醒时间')
        
        return reminder
    
    def create(self, validated_data):
        """创建事件"""
        # 提取嵌套字段
        location = validated_data.pop('location', {})
        reminder = validated_data.pop('reminder', {})
        
        # 获取 trip 和 user
        trip_id = self.context.get('trip_id')
        user = self.context.get('request').user
        
        # 创建事件
        event = TripEvent.objects.create(
            trip_id=trip_id,
            user=user,
            title=validated_data['title'],
            description=validated_data.get('description', ''),
            event_time=validated_data.get('event_time'),
            location_name=location.get('name', ''),
            location_address=location.get('address', ''),
            location_lat=location.get('lat'),
            location_lng=location.get('lng'),
            reminder_enabled=reminder.get('enabled', False),
            reminder_time=reminder.get('time'),
            reminder_method=reminder.get('method', 'email'),
            source_app=validated_data.get('source_app', 'roamio'),
            source_id=validated_data.get('source_id', ''),
        )
        
        return event


class TripEventBatchCreateSerializer(serializers.Serializer):
    """批量创建事件的序列化器（用于本地事项迁移）"""
    
    events = TripEventCreateSerializer(many=True)
    
    def create(self, validated_data):
        """批量创建事件"""
        events_data = validated_data['events']
        trip_id = self.context.get('trip_id')
        user = self.context.get('request').user
        
        created_events = []
        for event_data in events_data:
            # 提取嵌套字段
            location = event_data.pop('location', {})
            reminder = event_data.pop('reminder', {})
            
            # 创建事件
            event = TripEvent.objects.create(
                trip_id=trip_id,
                user=user,
                title=event_data['title'],
                description=event_data.get('description', ''),
                event_time=event_data.get('event_time'),
                location_name=location.get('name', ''),
                location_address=location.get('address', ''),
                location_lat=location.get('lat'),
                location_lng=location.get('lng'),
                reminder_enabled=reminder.get('enabled', False),
                reminder_time=reminder.get('time'),
                reminder_method=reminder.get('method', 'email'),
                source_app=event_data.get('source_app', 'local_migration'),
                source_id=event_data.get('source_id', ''),
            )
            created_events.append(event)
        
        return created_events


