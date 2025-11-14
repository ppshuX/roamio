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
        
        # 获取 unionid 和 openid（如果存在），并从 event_data 中移除（避免重复）
        unionid = event_data.get('unionid', None)
        openid = event_data.get('openid', None)
        
        # 从事件数据中移除 unionid 和 openid（只放在顶层）
        cleaned_event_data = {k: v for k, v in event_data.items() 
                              if k not in ['unionid', 'openid']}
        
        # 构造批量创建的数据格式
        data = {
            "source_app": "roamio",
            "related_trip_slug": "sidebar-todo",  # 侧边栏创建的待办
            "events": [cleaned_event_data]  # 单个事件也用数组（不包含 unionid 和 openid）
        }
        
        # 只在顶层添加 unionid 和 openid
        if unionid:
            data['unionid'] = unionid
        
        if openid:
            data['openid'] = openid
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            
            # Adapt to different response formats
            if result.get('events') and len(result['events']) > 0:
                # Format 1: {"events": [...]}
                return result['events'][0]
            elif result.get('created_events'):
                # Format 2: {"created_events": [...]}
                return result['created_events'][0]
            elif result.get('created'):
                # Format 3: {"created": [...]}
                return result['created'][0]
            elif isinstance(result, list) and len(result) > 0:
                # Format 4: Direct array
                return result[0]
            elif result.get('id'):
                # Format 5: Direct object
                return result
            else:
                logger.error(f"Unknown Ralendar response format: {result}")
                raise Exception(f"Unknown response format")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Ralendar API request failed: {e}")
            raise
    
    def batch_create_events(self, user_token, events_list, trip_slug, unionid=None, openid=None):
        """
        批量创建多个事件
        
        Args:
            user_token (str): 用户的 JWT Token
            events_list (list): 事件列表
            trip_slug (str): 旅行计划的 slug
            unionid (str, optional): UnionID，用于用户匹配
            openid (str, optional): OpenID，用于用户匹配
        
        Returns:
            dict: {"created": [...], "failed": [...]}
            
        Raises:
            requests.exceptions.RequestException: API 请求失败
        """
        url = f"{self.base_url}/fusion/events/batch/"
        headers = self.get_headers(user_token)
        
        # 清理事件数据，移除 Ralendar API 不支持的字段
        cleaned_events = []
        for event in events_list:
            # 只保留 Ralendar API 支持的字段
            # 注意：title, start_time 是必填字段
            cleaned_event = {
                'title': event.get('title', ''),
                'description': event.get('description', ''),
                'start_time': event.get('start_time'),
                'end_time': event.get('end_time'),
            }
            
            # location 处理：优先使用 location，如果没有则使用 location_name
            # 注意：如果 location 为空字符串或只有空白，不添加该字段
            location = event.get('location') or event.get('location_name') or ''
            location = location.strip() if location else ''
            # 只有当 location 不为空时才添加
            if location and location != '未指定地点':
                cleaned_event['location'] = location
            
            # 坐标处理（可选）
            if event.get('latitude') is not None:
                cleaned_event['latitude'] = float(event.get('latitude'))
            if event.get('longitude') is not None:
                cleaned_event['longitude'] = float(event.get('longitude'))
            
            # 提醒设置
            cleaned_event['reminder_minutes'] = event.get('reminder_minutes', 30)
            if event.get('email_reminder') is not None:
                cleaned_event['email_reminder'] = bool(event.get('email_reminder'))
            
            # 注意：unionid 和 openid 只放在顶层，不在每个事件对象中
            # 这样可以避免 Ralendar API 解析错误
            
            # 验证必填字段
            title = cleaned_event.get('title', '').strip()
            start_time = cleaned_event.get('start_time')
            
            if not title:
                logger.warning(f"Event missing title, skipping: {event}")
                continue
            
            if not start_time:
                logger.warning(f"Event missing start_time, skipping: {event}")
                continue
            
            # 验证 start_time 格式（应该是 ISO 8601 格式，包含时区）
            try:
                # 尝试解析时间字符串，确保格式正确
                from datetime import datetime
                if isinstance(start_time, str):
                    # 尝试解析 ISO 8601 格式
                    datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except (ValueError, AttributeError) as e:
                logger.warning(f"Event start_time format invalid: {start_time}, error: {e}, skipping: {event}")
                continue
            
            # 更新 title（去除前后空白）
            cleaned_event['title'] = title
            
            # 验证并格式化 description
            description = cleaned_event.get('description', '')
            if description:
                cleaned_event['description'] = description.strip()
            else:
                cleaned_event['description'] = ''  # 保持空字符串
            
            # 验证 end_time 格式（如果存在）
            end_time = cleaned_event.get('end_time')
            if end_time:
                try:
                    if isinstance(end_time, str):
                        datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Event end_time format invalid: {end_time}, error: {e}, removing end_time")
                    # 如果 end_time 格式无效，移除它（Ralendar API 可能不接受）
                    del cleaned_event['end_time']
            
            logger.debug(f"Validated event: title={title}, start_time={start_time}, location={cleaned_event.get('location', 'N/A')}")
            cleaned_events.append(cleaned_event)
        
        # 如果清理后没有有效事件，抛出异常
        if not cleaned_events:
            error_msg = "没有有效的事件数据（所有事件都缺少必填字段）"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        data = {
            "events": cleaned_events,
            "source_app": "roamio",
            "related_trip_slug": trip_slug
        }
        
        # 同时在顶层添加 unionid 和 openid（双重保险）
        if unionid:
            data['unionid'] = unionid
        if openid:
            data['openid'] = openid
        
        try:
            logger.info(f"Sending batch create request: {len(cleaned_events)} events, trip_slug={trip_slug}")
            logger.debug(f"Request data keys: {list(data.keys())}")
            logger.debug(f"First event sample: {cleaned_events[0] if cleaned_events else 'No events'}")
            
            response = requests.post(url, json=data, headers=headers, timeout=self.timeout)
            
            # 记录响应详情以便调试
            logger.info(f"Ralendar API response status: {response.status_code}")
            if response.status_code != 200:
                logger.error(f"Ralendar API returned {response.status_code}: {response.text}")
                # 对于 502 Bad Gateway，提供更友好的错误信息
                if response.status_code == 502:
                    error_msg = f"Ralendar API 服务暂时不可用 (502 Bad Gateway)，请稍后重试"
                    logger.error(error_msg)
                    raise requests.exceptions.HTTPError(error_msg, response=response)
            
            response.raise_for_status()
            result = response.json()
            
            # 记录完整的响应以便调试
            logger.info(f"Ralendar API full response: {result}")
            logger.info(f"Ralendar API response keys: {list(result.keys())}")
            
            # 根据文档，Ralendar API 返回格式为：
            # {
            #   "success": true,
            #   "created_count": 1,
            #   "failed_count": 0,
            #   "details": {
            #     "created": [...],
            #     "failed": []
            #   }
            # }
            # 
            # 但为了兼容性，也支持直接返回 { "created": [...], "failed": [...] } 的格式
            
            # 优先从 details 中获取（文档中的标准格式）
            created_events = []
            failed_events = []
            
            if 'details' in result:
                # 格式1：details 存在（标准格式）
                details = result.get('details')
                if isinstance(details, dict):
                    created_events = details.get('created', [])
                    failed_events = details.get('failed', [])
                    logger.info(f"Parsed from details: created={len(created_events)}, failed={len(failed_events)}")
                else:
                    logger.warning(f"details is not a dict: {type(details)}, value: {details}")
            
            # 如果 details 中没有找到，尝试从顶层获取（兼容其他格式）
            if not created_events and not failed_events:
                if 'created' in result or 'failed' in result:
                    created_events = result.get('created', [])
                    failed_events = result.get('failed', [])
                    logger.info(f"Parsed from top level: created={len(created_events)}, failed={len(failed_events)}")
            
            # 确保 created_events 和 failed_events 是列表
            if not isinstance(created_events, list):
                logger.warning(f"created_events is not a list: {type(created_events)}, value: {created_events}")
                created_events = []
            if not isinstance(failed_events, list):
                logger.warning(f"failed_events is not a list: {type(failed_events)}, value: {failed_events}")
                failed_events = []
            
            created_count = len(created_events)
            failed_count = len(failed_events)
            
            logger.info(f"Ralendar API response: created={created_count}, failed={failed_count}")
            
            # 如果有失败的事件，记录详细信息
            if failed_count > 0:
                logger.warning(f"Failed events: {failed_events}")
                for failed_event in failed_events:
                    logger.warning(f"Failed event details: {failed_event}")
            
            # 如果创建成功的事件，记录详细信息
            if created_count > 0:
                logger.info(f"Created events IDs: {[e.get('id') for e in created_events if e.get('id')]}")
            
            # 返回统一格式，确保包含 created 和 failed 数组
            return {
                'created': created_events,
                'failed': failed_events,
                'created_count': created_count,
                'failed_count': failed_count
            }
        except requests.exceptions.HTTPError as e:
            # 处理 HTTP 错误（包括 502）
            logger.error(f"Ralendar API HTTP error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
                # 对于 502，提供更友好的错误信息
                if e.response.status_code == 502:
                    raise Exception("Ralendar API 服务暂时不可用，请稍后重试")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Batch create failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise
    
    def list_events(self, user_token, unionid=None):
        """
        获取用户的所有事件（使用 Fusion API）
        
        Args:
            user_token (str): 用户的 JWT Token
            unionid (str, optional): UnionID，可选，用于加速匹配
        
        Returns:
            dict: {"events": [...], "user_id": 2, "username": "...", "events_count": 10}
            
        Raises:
            requests.exceptions.RequestException: API 请求失败
        """
        url = f"{self.base_url}/fusion/events/"
        headers = self.get_headers(user_token)
        params = {}
        
        if unionid:
            params['unionid'] = unionid
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Got {result.get('events_count', 0)} events for user {result.get('username')}")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"List events failed: {e}")
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
            logger.error(f"Get trip events failed: {e}")
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
            logger.info(f"Deleted {result.get('deleted_count', 0)} trip events")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"Delete trip events failed: {e}")
            raise
    
    def update_event(self, user_token, event_id, event_data, unionid=None):
        """
        更新事件（使用 Fusion API）
        
        Args:
            user_token (str): 用户的 JWT Token
            event_id (int): 事件 ID
            event_data (dict): 更新的事件数据
            unionid (str, optional): UnionID，用于加速匹配
        
        Returns:
            dict: 更新后的事件数据
            
        Raises:
            requests.exceptions.RequestException: API 请求失败
        """
        url = f"{self.base_url}/fusion/events/{event_id}/"
        headers = self.get_headers(user_token)
        
        # ⚠️ 重要：unionid 必须放在请求体中，不是 URL 参数
        request_data = event_data.copy()
        if unionid:
            request_data['unionid'] = unionid
        
        try:
            response = requests.put(url, json=request_data, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            logger.info(f"Updated event {event_id}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Update event failed: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise
    
    def delete_event(self, user_token, event_id, unionid=None):
        """
        删除单个事件（使用 Fusion API）
        
        Args:
            user_token (str): 用户的 JWT Token
            event_id (int): 事件 ID
            unionid (str, optional): UnionID，用于加速匹配
        
        Returns:
            bool: 是否删除成功
            
        Raises:
            requests.exceptions.RequestException: API 请求失败
        """
        url = f"{self.base_url}/fusion/events/{event_id}/"
        headers = self.get_headers(user_token)
        
        # ⚠️ 重要：unionid 必须放在请求体中，不是 URL 参数
        request_data = {}
        if unionid:
            request_data['unionid'] = unionid
        
        try:
            # DELETE请求也可以有body
            response = requests.delete(url, json=request_data if request_data else None, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            logger.info(f"Deleted event {event_id}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Delete event failed: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise

