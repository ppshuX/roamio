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
        
        # 获取 unionid 和 openid（如果存在），但不从 event_data 中移除
        unionid = event_data.get('unionid', None)
        openid = event_data.get('openid', None)
        
        # 构造批量创建的数据格式
        data = {
            "source_app": "roamio",
            "related_trip_slug": "sidebar-todo",  # 侧边栏创建的待办
            "events": [event_data]  # 单个事件也用数组（包含 unionid 和 openid）
        }
        
        # 同时也添加 unionid 和 openid 到顶层（双重保险）
        if unionid:
            data['unionid'] = unionid
            print(f"[DEBUG] UnionID in both top-level and event data: {unionid}")
        
        if openid:
            data['openid'] = openid
            print(f"[DEBUG] OpenID in both top-level and event data: {openid}")
        
        # 详细日志：发送给 Ralendar 的完整数据
        print("=" * 80)
        print("[DEBUG] Sending request to Ralendar:")
        print(f"   URL: {url}")
        print(f"   Data: {data}")
        print("=" * 80)
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=self.timeout)
            
            # 详细日志：Ralendar 的响应
            print(f"[DEBUG] Ralendar response status: {response.status_code}")
            
            # 检查响应状态
            if response.status_code >= 400:
                # 错误响应 - 直接抛出异常，不打印响应体（避免编码错误）
                print(f"[ERROR] Ralendar returned {response.status_code}")
                print(f"[ERROR] Response length: {len(response.text)} bytes")
                try:
                    error_data = response.json()
                    # 只打印 error 字段的前 200 个字符（ASCII 安全）
                    error_msg = str(error_data).encode('ascii', errors='ignore').decode('ascii')[:200]
                    print(f"[ERROR] Error (ASCII only): {error_msg}")
                    raise Exception(f"Ralendar API error {response.status_code}")
                except:
                    raise Exception(f"Ralendar API error {response.status_code}")
            
            response.raise_for_status()
            result = response.json()
            
            print("[DEBUG] Ralendar API success")
            
            # Adapt to different response formats
            if result.get('events') and len(result['events']) > 0:
                # Format 1: {"events": [...]}
                created_event = result['events'][0]
                print(f"[DEBUG] Created event ID: {created_event.get('id')}")
                return created_event
            elif result.get('created_events'):
                # Format 2: {"created_events": [...]}
                created_event = result['created_events'][0]
                print(f"[DEBUG] Created event ID: {created_event.get('id')}")
                return created_event
            elif result.get('created'):
                # Format 3: {"created": [...]}
                created_event = result['created'][0]
                print(f"[DEBUG] Created event ID: {created_event.get('id')}")
                return created_event
            elif isinstance(result, list) and len(result) > 0:
                # Format 4: Direct array
                created_event = result[0]
                print(f"[DEBUG] Created event ID: {created_event.get('id')}")
                return created_event
            elif result.get('id'):
                # Format 5: Direct object
                print(f"[DEBUG] Created event ID: {result.get('id')}")
                return result
            else:
                print(f"[ERROR] Unknown response format")
                raise Exception(f"Unknown response format")
                
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request failed: {type(e).__name__}")
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
            print(f"[DEBUG] Batch created {len(result.get('created', []))} events")
            return result
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Batch create failed: {type(e).__name__}")
            raise
    
    def list_events(self, user_token):
        """
        获取用户的所有事件
        
        Args:
            user_token (str): 用户的 JWT Token
        
        Returns:
            dict: {"results": [...]}
            
        Raises:
            requests.exceptions.RequestException: API 请求失败
        """
        url = f"{self.base_url}/events/"
        headers = self.get_headers(user_token)
        
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            print(f"[DEBUG] Got {len(result.get('results', []))} events")
            return result
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] List events failed: {type(e).__name__}")
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
            print(f"[ERROR] Get trip events failed: {type(e).__name__}")
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
            print(f"[DEBUG] Deleted {result.get('deleted_count', 0)} trip events")
            return result
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Delete trip events failed: {type(e).__name__}")
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
            print(f"[DEBUG] Updated event {event_id}")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Update event failed: {type(e).__name__}")
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
            print(f"[DEBUG] Deleted event {event_id}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Delete event failed: {type(e).__name__}")
            raise

