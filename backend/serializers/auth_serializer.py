"""
认证相关序列化器
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    username = serializers.CharField(
        required=True,
        error_messages={'required': '请输入用户名'}
    )
    password = serializers.CharField(
        required=True, 
        write_only=True,
        style={'input_type': 'password'},
        error_messages={'required': '请输入密码'}
    )
    
    def validate_username(self, value):
        """验证用户名"""
        if not value or not value.strip():
            raise serializers.ValidationError('用户名不能为空')
        return value.strip()
    
    def validate_password(self, value):
        """验证密码"""
        if not value:
            raise serializers.ValidationError('密码不能为空')
        return value
    
    def validate(self, attrs):
        """验证用户名和密码"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError({
                    'non_field_errors': ['用户名或密码错误']
                })
            
            if not user.is_active:
                raise serializers.ValidationError({
                    'non_field_errors': ['此账号已被停用，请联系管理员']
                })
        else:
            raise serializers.ValidationError({
                'non_field_errors': ['用户名和密码不能为空']
            })
        
        attrs['user'] = user
        return attrs


class TokenObtainSerializer(serializers.Serializer):
    """Token获取序列化器"""
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        """返回用户信息"""
        from .user_serializer import UserSerializer
        user = self.context.get('user')
        if user:
            return UserSerializer(user).data
        return None


class SendVerificationCodeSerializer(serializers.Serializer):
    """发送验证码序列化器"""
    email = serializers.EmailField(required=True, error_messages={'required': '请输入邮箱地址'})
    type = serializers.ChoiceField(
        choices=[
            ('register', '注册验证'),
            ('login', '登录验证'),
            ('reset_password', '重置密码'),
            ('bind_email', '绑定邮箱'),
        ],
        required=True,
        error_messages={'required': '请选择验证类型'}
    )
    
    def validate_email(self, value):
        """验证邮箱格式"""
        if not value or not value.strip():
            raise serializers.ValidationError('邮箱地址不能为空')
        return value.strip().lower()


class VerifyCodeSerializer(serializers.Serializer):
    """验证验证码序列化器"""
    email = serializers.EmailField(required=True, error_messages={'required': '请输入邮箱地址'})
    code = serializers.CharField(
        required=True,
        max_length=10,
        error_messages={'required': '请输入验证码'}
    )
    type = serializers.ChoiceField(
        choices=[
            ('register', '注册验证'),
            ('login', '登录验证'),
            ('reset_password', '重置密码'),
            ('bind_email', '绑定邮箱'),
        ],
        required=True,
        error_messages={'required': '请选择验证类型'}
    )
    
    def validate_email(self, value):
        """验证邮箱格式"""
        if not value or not value.strip():
            raise serializers.ValidationError('邮箱地址不能为空')
        return value.strip().lower()
    
    def validate_code(self, value):
        """验证验证码格式"""
        if not value or not value.strip():
            raise serializers.ValidationError('验证码不能为空')
        if not value.isdigit():
            raise serializers.ValidationError('验证码必须是数字')
        return value.strip()


class QQLoginSerializer(serializers.Serializer):
    """QQ登录序列化器"""
    code = serializers.CharField(required=True, help_text='QQ OAuth返回的code')
    state = serializers.CharField(required=True, help_text='CSRF防护state参数')


class QQBindSerializer(serializers.Serializer):
    """QQ绑定序列化器"""
    code = serializers.CharField(required=True, help_text='QQ OAuth返回的code')
    state = serializers.CharField(required=True, help_text='CSRF防护state参数')
    email = serializers.EmailField(required=False, help_text='首次QQ登录需要绑定邮箱')
    verification_token = serializers.CharField(required=False, help_text='邮箱验证token（首次QQ登录时需要）')


class ResetPasswordSerializer(serializers.Serializer):
    """重置密码序列化器"""
    email = serializers.EmailField(required=True, error_messages={'required': '请输入邮箱地址'})
    verification_token = serializers.CharField(required=True, help_text='邮箱验证token，通过验证验证码API获取')
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
        error_messages={
            'required': '请输入新密码',
            'min_length': '密码长度至少为8位'
        }
    )
    new_password2 = serializers.CharField(
        required=True,
        write_only=True,
        error_messages={'required': '请确认新密码'}
    )
    
    def validate_email(self, value):
        """验证邮箱格式"""
        if not value or not value.strip():
            raise serializers.ValidationError('邮箱地址不能为空')
        return value.strip().lower()
    
    def validate(self, attrs):
        """验证密码一致性"""
        new_password = attrs.get('new_password')
        new_password2 = attrs.get('new_password2')
        
        if new_password and new_password2:
            if new_password != new_password2:
                raise serializers.ValidationError({
                    'new_password2': '两次输入的密码不一致'
                })
            
            # 验证密码强度
            from django.contrib.auth.password_validation import validate_password
            try:
                validate_password(new_password)
            except Exception as e:
                raise serializers.ValidationError({
                    'new_password': list(e.messages) if hasattr(e, 'messages') else ['密码不符合安全要求']
                })
        
        return attrs

