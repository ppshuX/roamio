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
        help_text="偏好设置"
    )
    
    def validate_prompt(self, value):
        """验证提示词"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("描述太简短，请详细说明旅行想法（至少10个字）")
        return value.strip()
    
    def validate_preferences(self, value):
        """验证偏好设置"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("偏好设置必须是字典格式")
        
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
            if not isinstance(value['budget_level'], str):
                raise serializers.ValidationError("预算等级必须是字符串")
            if value['budget_level'] not in ['low', 'medium', 'high']:
                raise serializers.ValidationError(
                    "预算等级必须是 low/medium/high"
                )
        
        # 验证旅行风格
        if 'travel_style' in value:
            if not isinstance(value['travel_style'], str):
                raise serializers.ValidationError("旅行风格必须是字符串")
            valid_styles = ['leisure', 'adventure', 'culture', 'food', 'photography']
            if value['travel_style'] not in valid_styles:
                raise serializers.ValidationError(
                    f"旅行风格必须是 {'/'.join(valid_styles)}"
                )
        
        # 验证日期范围（新增）
        if 'date_range' in value:
            if not isinstance(value['date_range'], dict):
                raise serializers.ValidationError("日期范围必须是字典格式")
            
            date_range = value['date_range']
            if 'start_date' not in date_range or 'end_date' not in date_range:
                raise serializers.ValidationError("日期范围必须包含 start_date 和 end_date")
            
            from datetime import datetime
            try:
                start_date = datetime.fromisoformat(date_range['start_date'])
                end_date = datetime.fromisoformat(date_range['end_date'])
                
                if end_date < start_date:
                    raise serializers.ValidationError("返回日期不能早于出发日期")
                
                # 计算天数
                days_diff = (end_date - start_date).days + 1
                if days_diff < 1 or days_diff > 30:
                    raise serializers.ValidationError("旅行天数必须在 1-30 天之间")
                    
            except ValueError:
                raise serializers.ValidationError(
                    "日期格式错误，应为 YYYY-MM-DD"
                )
        
        # 验证单个日期格式（向后兼容）
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

