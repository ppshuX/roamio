"""
Ping++ 聚合支付客户端
用于处理微信支付和支付宝支付
"""

import os
import logging
import requests
from django.conf import settings
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class PingPPClient:
    """Ping++ 支付客户端"""
    
    def __init__(self):
        # Ping++ API 配置
        self.api_key = os.getenv('PINGPP_API_KEY', '')
        self.api_base = 'https://api.pingxx.com/v1'
        
        # 测试环境 API Key（如果配置了）
        self.test_api_key = os.getenv('PINGPP_TEST_API_KEY', '')
        
        # 是否启用 Ping++（如果未配置 API Key，使用模拟支付）
        self.enabled = bool(self.api_key or self.test_api_key)
        
        # 应用 ID（在 Ping++ 控制台获取，如：app_1unjXLmPCCeL90q9）
        self.app_id = os.getenv('PINGPP_APP_ID', '')
        
        # 回调 URL
        self.callback_url = os.getenv('PINGPP_CALLBACK_URL', '')
        
        # 是否使用测试环境
        self.use_test = os.getenv('PINGPP_USE_TEST', 'True').lower() == 'true'
        
        if not self.enabled:
            logger.info("Ping++ 未启用，将使用模拟支付（适合开发测试）")
        else:
            logger.info(f"Ping++ 已启用，使用{'测试' if self.use_test else '生产'}环境")
    
    def get_headers(self):
        """获取请求头（包含 API Key）"""
        api_key = self.test_api_key if self.use_test else self.api_key
        if not api_key:
            return {}
        
        return {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def create_charge(self, order_id, amount, subject, body, user, payment_method='wx'):
        """
        创建支付订单（Charge）
        
        Args:
            order_id: 订单号
            amount: 金额（元，如 0.1）
            subject: 订单标题
            body: 订单描述
            user: 用户对象
            payment_method: 支付方式 ('wx' 微信, 'alipay' 支付宝)
        
        Returns:
            dict: Ping++ Charge 对象（包含支付 URL/二维码）
        """
        if not self.enabled:
            # 如果未启用，返回模拟数据
            return {
                'id': f'mock_charge_{order_id}',
                'object': 'charge',
                'order_no': order_id,
                'paid': False,
                'amount': int(amount * 100),  # 转换为分
                'subject': subject,
                'body': body,
                'channel': payment_method,
                'mock': True
            }
        
        url = f"{self.api_base}/charges"
        
        # 构建请求数据
        data = {
            'order_no': order_id,
            'amount': int(amount * 100),  # 金额（分）
            'currency': 'cny',
            'subject': subject,
            'body': body,
            'channel': payment_method,  # wx 或 alipay
            'app': {
                'id': self.app_id
            },
            'client_ip': self._get_client_ip(),
            'extra': {
                'user_id': str(user.id),
                'username': user.username
            }
        }
        
        # 回调 URL
        if self.callback_url:
            data['extra']['callback_url'] = self.callback_url
        
        try:
            headers = self.get_headers()
            response = requests.post(url, json=data, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Ping++ Charge 创建成功: {result.get('id')}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ping++ Charge 创建失败: {e}")
            raise Exception(f"创建支付订单失败: {str(e)}")
    
    def get_charge(self, charge_id):
        """
        查询支付订单状态
        
        Args:
            charge_id: Ping++ Charge ID
        
        Returns:
            dict: Charge 对象
        """
        if not self.enabled:
            # 模拟返回
            return {
                'id': charge_id,
                'object': 'charge',
                'paid': False,
                'mock': True
            }
        
        url = f"{self.api_base}/charges/{charge_id}"
        
        try:
            headers = self.get_headers()
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"查询 Ping++ Charge 失败: {e}")
            raise Exception(f"查询支付订单失败: {str(e)}")
    
    def verify_webhook(self, raw_data, signature):
        """
        验证 Ping++ Webhook 签名
        
        Args:
            raw_data: 原始数据（字符串）
            signature: 签名（从请求头 X-Pingplusplus-Signature 获取）
        
        Returns:
            bool: 验证是否通过
        """
        # TODO: 实现签名验证（需要配置 Webhook Secret）
        # 参考：https://www.pingxx.com/docs/server/webhook
        return True
    
    def _get_client_ip(self):
        """获取客户端 IP（用于 Ping++）"""
        # 这里可以从 request 对象获取，暂时返回一个默认值
        return '127.0.0.1'
    
    def format_payment_url(self, charge):
        """
        格式化支付 URL（用于前端跳转）
        
        Args:
            charge: Ping++ Charge 对象
        
        Returns:
            str: 支付 URL
        """
        if charge.get('mock'):
            # 模拟支付，返回空
            return None
        
        # 微信支付：返回二维码 URL 或跳转 URL
        if charge.get('channel') == 'wx':
            return charge.get('credential', {}).get('wx', {}).get('qr_code_url')
        
        # 支付宝：返回跳转 URL
        if charge.get('channel') == 'alipay':
            return charge.get('credential', {}).get('alipay', {}).get('url')
        
        return None


# 创建全局实例
pingpp_client = PingPPClient()

