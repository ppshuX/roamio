"""
AI 旅行规划 API 序列化器
"""

from rest_framework import serializers


class TripGenerationRequestSerializer(serializers.Serializer):
    """生成行程请求验证"""
    
    prompt = serializers.CharField(
        max_length=2000,
        required=True,
        help_text="用户的旅行描述"
    )
    
    preferences = serializers.DictField(
        required=False,
        default=dict,
        child=serializers.CharField(),
        help_text="偏好设置"
    )
    
    def validate_prompt(self, value):
        """验证提示词"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("描述太简短，请详细说明旅行想法（至少10个字）")
        return value.strip()
    
    def validate_preferences(self, value):
        """验证偏好设置"""
        # 验证天数
        if 'days' in value:
            try:
                days = int(value['days'])
                if days < 1 or days > 30:
                    raise serializers.ValidationError("天数必须在 1-30 之间")
                value['days'] = days  # 转换为整数
            except (ValueError, TypeError):
                raise serializers.ValidationError("天数必须是数字")
        
        # 验证预算等级
        if 'budget_level' in value:
            if value['budget_level'] not in ['low', 'medium', 'high']:
                raise serializers.ValidationError(
                    "预算等级必须是 low/medium/high"
                )
        
        # 验证旅行风格
        if 'travel_style' in value:
            valid_styles = ['leisure', 'adventure', 'culture', 'food', 'photography']
            if value['travel_style'] not in valid_styles:
                raise serializers.ValidationError(
                    f"旅行风格必须是 {'/'.join(valid_styles)}"
                )
        
        # 验证日期格式
        if 'start_date' in value:
            from datetime import datetime
            try:
                datetime.fromisoformat(value['start_date'])
            except ValueError:
                raise serializers.ValidationError(
                    "日期格式错误，应为 YYYY-MM-DD"
                )
        
        return value


class TripRefinementRequestSerializer(serializers.Serializer):
    """优化行程请求验证"""
    
    trip_plan = serializers.DictField(
        required=True,
        help_text="现有行程计划"
    )
    
    feedback = serializers.CharField(
        max_length=1000,
        required=True,
        help_text="用户反馈"
    )
    
    def validate_feedback(self, value):
        """验证反馈内容"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError("反馈太简短，请详细说明需要调整的内容")
        return value.strip()

