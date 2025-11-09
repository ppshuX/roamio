"""
Ralendar API 客户端
用于 Roamio 与 Ralendar 的集成
"""

import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class RalendarClient:
    """Ralendar API 客户端"""
    
    def __init__(self):
        # Ralendar API 基础 URL（来自集成文档）
        self.base_url = getattr(settings, 'RALENDAR_API_URL', 'https://app7626.acapp.acwing.com.cn/api/v1')
        self.timeout = 10
    
    def get_headers(self, user_token):
        """
        构造请求头（使用用户的 JWT Token）
        
        Args:
            user_token (str): 用户的 JWT access_token
            
        Returns:
            dict: 请求头
        """
        return {
            'Authorization': f'Bearer {user_token}',
            'Content-Type': 'application/json'
        }
    
    def create_event(self, user_token, event_data):
        """
        创建单个事件到 Ralendar（使用 Fusion API）
        
        Args:
            user_token (str): 用户的 JWT access_token
            event_data (dict): 事件数据
                {
                    "title": "行程标题",
                    "description": "详细描述",
                    "start_time": "2025-11-20T10:00:00+08:00",
                    "end_time": "2025-11-20T12:00:00+08:00",
                    "location": "北京故宫",
                    "latitude": 39.9163,
                    "longitude": 116.3972,
                    "email_reminder": True
                }
        
        Returns:
            dict: 创建成功的事件数据
            
        Raises:
            requests.exceptions.RequestException: API 请求失败
        """
        # 使用 Fusion API 的批量端点（即使只有 1 个事件）
        url = f"{self.base_url}/fusion/events/batch/"
        headers = self.get_headers(user_token)
        
        # 构造批量创建的数据格式
        data = {
            "source_app": "roamio",
            "related_trip_slug": "sidebar-todo",  # 侧边栏创建的待办
            "events": [event_data]  # 单个事件也用数组
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            
            # 返回第一个创建的事件
            if result.get('created_events'):
                created_event = result['created_events'][0]
                logger.info(f"成功创建 Ralendar 事件: {created_event.get('title')}")
                return created_event
            else:
                raise Exception("未返回创建的事件")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"创建 Ralendar 事件失败: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"响应内容: {e.response.text}")
            raise
    
    def batch_create_events(self, user_token, events_list, trip_slug):
        """
        批量创建多个事件
        
        Args:
            user_token (str): 用户的 JWT Token
            events_list (list): 事件列表
            trip_slug (str): 旅行计划的 slug
        
        Returns:
            dict: {"created": [...], "failed": [...]}
            
        Raises:
            requests.exceptions.RequestException: API 请求失败
        """
        url = f"{self.base_url}/fusion/events/batch/"
        headers = self.get_headers(user_token)
        
        data = {
            "events": events_list,
            "source_app": "roamio",
            "related_trip_slug": trip_slug
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            logger.info(f"批量创建事件成功: {len(result.get('created', []))} 个")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"批量创建事件失败: {e}")
            raise
    
    def get_trip_events(self, user_token, trip_slug):
        """
        获取某个旅行计划的所有事件
        
        Args:
            user_token (str): 用户的 JWT Token
            trip_slug (str): 旅行计划的 slug
        
        Returns:
            list: 事件列表
            
        Raises:
            requests.exceptions.RequestException: API 请求失败
        """
        url = f"{self.base_url}/fusion/events/trip/{trip_slug}/"
        headers = self.get_headers(user_token)
        
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"获取旅行事件失败: {e}")
            raise
    
    def delete_trip_events(self, user_token, trip_slug):
        """
        删除某个旅行计划的所有事件
        
        Args:
            user_token (str): 用户的 JWT Token
            trip_slug (str): 旅行计划的 slug
        
        Returns:
            dict: {"deleted_count": 5}
            
        Raises:
            requests.exceptions.RequestException: API 请求失败
        """
        url = f"{self.base_url}/fusion/events/trip/{trip_slug}/"
        headers = self.get_headers(user_token)
        
        try:
            response = requests.delete(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            logger.info(f"删除旅行事件成功: {result.get('deleted_count', 0)} 个")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"删除旅行事件失败: {e}")
            raise
    
    def update_event(self, user_token, event_id, event_data):
        """
        更新事件
        
        Args:
            user_token (str): 用户的 JWT Token
            event_id (int): 事件 ID
            event_data (dict): 更新的事件数据
        
        Returns:
            dict: 更新后的事件数据
            
        Raises:
            requests.exceptions.RequestException: API 请求失败
        """
        url = f"{self.base_url}/events/{event_id}/"
        headers = self.get_headers(user_token)
        
        try:
            response = requests.put(url, json=event_data, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            logger.info(f"更新事件成功: {event_id}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"更新事件失败: {e}")
            raise
    
    def delete_event(self, user_token, event_id):
        """
        删除单个事件
        
        Args:
            user_token (str): 用户的 JWT Token
            event_id (int): 事件 ID
        
        Returns:
            bool: 是否删除成功
            
        Raises:
            requests.exceptions.RequestException: API 请求失败
        """
        url = f"{self.base_url}/events/{event_id}/"
        headers = self.get_headers(user_token)
        
        try:
            response = requests.delete(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            logger.info(f"删除事件成功: {event_id}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"删除事件失败: {e}")
            raise

