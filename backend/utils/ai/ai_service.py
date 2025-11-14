"""
AI 旅行规划服务

使用通义千问 API 生成旅行行程计划
"""

import os
import json
import logging
import time
from datetime import date, timedelta

logger = logging.getLogger(__name__)


class TripPlannerAI:
    """旅行规划 AI 服务"""
    
    def __init__(self):
        """初始化 AI 客户端"""
        # 检查是否启用 AI 功能
        self.enabled = os.getenv('AI_GENERATION_ENABLED', 'False').lower() == 'true'
        
        if not self.enabled:
            logger.warning("AI generation is disabled")
            return
        
        # 初始化客户端（使用 requests 而不是 openai SDK，兼容 Python 3.8）
        self.api_key = os.getenv('QWEN_API_KEY')
        self.model = os.getenv('QWEN_MODEL', 'qwen-plus')
        self.api_base = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        
        if not self.api_key:
            logger.error("QWEN_API_KEY not configured")
            self.enabled = False
        
        # 配置参数
        self.max_tokens = int(os.getenv('AI_MAX_TOKENS', '4000'))
        self.temperature = float(os.getenv('AI_TEMPERATURE', '0.7'))
        
        # 统计信息
        self.tokens_used = 0
        self.generation_time = 0
    
    def generate_trip_plan(self, user_prompt, preferences, user=None):
        """
        生成旅行计划
        
        Args:
            user_prompt: 用户的自然语言描述
            preferences: 偏好设置字典
            user: 当前用户对象（可选）
        
        Returns:
            dict: 结构化的旅行计划
        """
        if not self.enabled:
            raise Exception("AI 服务未启用，请检查配置")
        
        start_time = time.time()
        
        try:
            # 1. 构建提示词
            system_prompt = self._build_system_prompt(preferences)
            user_full_prompt = self._build_user_prompt(
                user_prompt, preferences, user
            )
            
            # 2. 调用 AI API
            logger.info(f"Calling Qwen API with model: {self.model}")
            
            import requests
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_full_prompt}
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "response_format": {"type": "json_object"}
            }
            
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data,
                timeout=90  # 增加到 90 秒，生成详细行程需要更多时间
            )
            
            if response.status_code != 200:
                logger.error(f"API error: {response.status_code} - {response.text}")
                raise Exception(f"AI API 调用失败: {response.status_code}")
            
            result = response.json()
            
            # 3. 解析响应
            result_text = result['choices'][0]['message']['content']
            self.tokens_used = result['usage']['total_tokens']
            self.generation_time = time.time() - start_time
            
            logger.info(
                f"AI generation completed. "
                f"Tokens: {self.tokens_used}, Time: {self.generation_time:.2f}s"
            )
            
            # 4. 解析 JSON
            trip_plan = json.loads(result_text)
            
            # 5. 数据验证和清洗
            validated_plan = self._validate_and_clean(trip_plan, preferences)
            
            return validated_plan
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            raise ValueError("AI 返回格式错误，请重试")
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            raise
    
    def _build_system_prompt(self, preferences):
        """构建系统提示词"""
        budget_map = {
            'low': '经济型（人均200-300元/天）',
            'medium': '中等（人均400-600元/天）',
            'high': '舒适型（人均800-1200元/天）'
        }
        
        style_map = {
            'leisure': '休闲放松，节奏舒缓',
            'adventure': '探险刺激，挑战自我',
            'culture': '文化深度，历史人文',
            'food': '美食之旅，品味当地',
            'photography': '摄影采风，追逐美景'
        }
        
        budget_desc = budget_map.get(preferences.get('budget_level', 'medium'))
        style_desc = style_map.get(preferences.get('travel_style', 'leisure'))
        
        return f"""你是 Roamio 旅行规划助手。根据用户需求生成详细的旅行计划。

【输出格式】严格的 JSON 格式：
{{
  "trip_title": "行程标题（简洁有吸引力）",
  "summary": "行程概述（100字内，突出亮点）",
  "destination": "目的地",
  "days": 天数,
  "total_budget": 总预算（人民币）,
  "days_detail": [
    {{
      "day_number": 1,
      "date": "YYYY-MM-DD",
      "title": "Day 1: 简短标题",
      "location": "当日主要位置",
      "activities": [
        {{
          "time": "HH:MM",
          "duration": "X小时",
          "location": "具体地点名称（必填）",
          "location_type": "景点/餐厅/住宿/交通",
          "address": "详细地址（省市区街道门牌号，必填）",
          "coordinates": {{"lat": 纬度, "lng": 经度}},
          "description": "活动描述（50-100字，生动具体）",
          "estimated_cost": 预估费用,
          "tips": "实用提示"
        }}
      ],
      "accommodation": {{
        "name": "住宿名称/类型",
        "type": "酒店/民宿/客栈",
        "estimated_cost": 费用,
        "tips": "住宿建议"
      }},
      "meals": {{"breakfast": 早餐, "lunch": 午餐, "dinner": 晚餐}},
      "transportation": {{
        "type": "交通方式",
        "estimated_cost": 费用
      }},
      "day_total": 当日总花费
    }}
  ],
  "budget_breakdown": {{
    "accommodation": 住宿总计,
    "meals": 餐饮总计,
    "transportation": 交通总计,
    "tickets": 门票总计,
    "shopping": 购物预留,
    "emergency": 应急预留
  }},
  "travel_tips": ["小贴士1", "小贴士2", ...],
  "packing_list": ["物品1", "物品2", ...],
  "best_season": "最佳旅行季节",
  "weather_note": "天气注意事项"
}}

【要求】
1. **地点真实存在**：所有地点必须真实存在，优先推荐热门景点和口碑餐厅
2. **详细地址**：每个地点必须提供详细地址（省市区街道门牌号），方便导航和定位
3. **地理坐标**：每个地点必须提供准确的地理坐标（经纬度），确保地图显示和导航准确
4. **时间安排合理**：考虑交通时间、排队时间、体力消耗，预算符合{budget_desc}
5. **风格匹配**：符合旅行风格（{style_desc}）
6. **严格遵守 JSON 格式**：数字不加引号，日期 YYYY-MM-DD，时间 HH:MM
"""
    
    def _build_user_prompt(self, user_prompt, preferences, user):
        """构建用户提示词"""
        # 基础信息
        days = preferences.get('days', '未指定')
        budget = preferences.get('budget_level', 'medium')
        style = preferences.get('travel_style', 'leisure')
        
        # 处理日期信息（支持 date_range 或 start_date）
        date_info = ''
        if 'date_range' in preferences and isinstance(preferences['date_range'], dict):
            date_range = preferences['date_range']
            start_date = date_range.get('start_date', '')
            end_date = date_range.get('end_date', '')
            if start_date and end_date:
                date_info = f"{start_date} 至 {end_date}"
        elif 'start_date' in preferences:
            start_date = preferences.get('start_date', '')
            if start_date:
                date_info = start_date
        
        if not date_info:
            date_info = '待定'
        
        # 用户历史偏好（可选）
        user_context = ""
        if user:
            try:
                # 延迟导入，避免循环依赖和初始化延迟
                from django.apps import apps
                Trip = apps.get_model('backend', 'Trip')
                
                past_trips = Trip.objects.filter(
                    user=user, 
                    is_public=True
                ).order_by('-created_at')[:3]
                
                if past_trips.exists():
                    user_context = "\n\n【用户历史偏好参考】\n"
                    for trip in past_trips:
                        user_context += f"- 曾去过：{trip.title}\n"
            except Exception as e:
                logger.warning(f"Failed to load user history: {e}")
        
        prompt = f"""生成旅行计划：

需求：{user_prompt}
天数：{days}天 | 预算：{budget} | 风格：{style} | 日期：{date_info}
{user_context}

要求：每天2-4个活动，包含交通和餐饮建议，返回完整 JSON。
"""
        return prompt
    
    def _validate_and_clean(self, trip_plan, preferences):
        """验证和清洗数据"""
        # 1. 基础字段验证
        required_fields = ['trip_title', 'summary', 'days', 'days_detail']
        for field in required_fields:
            if field not in trip_plan:
                raise ValueError(f"缺少必需字段: {field}")
        
        # 2. 天数验证
        expected_days = preferences.get('days')
        if expected_days and len(trip_plan['days_detail']) != expected_days:
            logger.warning(
                f"生成天数不匹配: 期望{expected_days}天, "
                f"实际{len(trip_plan['days_detail'])}天"
            )
        
        # 3. 日期补全（支持 date_range 或 start_date）
        start_date_str = None
        
        # 优先使用 date_range
        if 'date_range' in preferences and isinstance(preferences['date_range'], dict):
            date_range = preferences['date_range']
            start_date_str = date_range.get('start_date')
            # 如果提供了 date_range，也更新天数
            if start_date_str and 'end_date' in date_range:
                try:
                    start_date = date.fromisoformat(start_date_str)
                    end_date = date.fromisoformat(date_range['end_date'])
                    calculated_days = (end_date - start_date).days + 1
                    if calculated_days > 0:
                        preferences['days'] = calculated_days
                        # 如果生成的天数不匹配，更新行程天数
                        if len(trip_plan['days_detail']) != calculated_days:
                            logger.info(f"根据日期范围调整天数: {calculated_days} 天")
                            trip_plan['days'] = calculated_days
                except ValueError as e:
                    logger.warning(f"Invalid date_range: {e}")
        
        # 如果没有 date_range，使用 start_date（向后兼容）
        if not start_date_str:
            start_date_str = preferences.get('start_date')
        
        # 填充每一天的日期
        if start_date_str:
            try:
                start_date = date.fromisoformat(start_date_str)
                for i, day in enumerate(trip_plan['days_detail']):
                    day_date = start_date + timedelta(days=i)
                    day['date'] = day_date.isoformat()
                logger.info(f"已填充日期: {start_date} 开始，共 {len(trip_plan['days_detail'])} 天")
            except ValueError as e:
                logger.warning(f"Invalid start_date: {start_date_str}, error: {e}")
        
        # 4. 预算合理性检查
        total_budget = trip_plan.get('total_budget', 0)
        if total_budget < 100 or total_budget > 100000:
            logger.warning(f"预算异常: {total_budget}")
        
        # 5. 内容安全检查（简单版）
        sensitive_words = ['政治', '赌博', '色情']
        content = json.dumps(trip_plan, ensure_ascii=False)
        for word in sensitive_words:
            if word in content:
                logger.error(f"检测到敏感词: {word}")
                raise ValueError("内容包含不当信息")
        
        return trip_plan
    
    def refine_trip_plan(self, existing_plan, user_feedback):
        """
        优化已有行程
        
        Args:
            existing_plan: 现有行程计划
            user_feedback: 用户反馈
        
        Returns:
            dict: 优化后的行程计划
        """
        if not self.enabled:
            raise Exception("AI 服务未启用")
        
        system_prompt = """你是 Roamio 旅行规划助手。
用户对已有行程提出了修改意见，请根据反馈优化行程，保持 JSON 格式。"""
        
        user_prompt = f"""【现有行程】
{json.dumps(existing_plan, ensure_ascii=False, indent=2)}

【用户反馈】
{user_feedback}

请根据反馈优化行程，返回完整的 JSON 格式。
"""
        
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": self.temperature,
                "response_format": {"type": "json_object"}
            }
            
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data,
                timeout=90  # 增加到 90 秒
            )
            
            if response.status_code != 200:
                raise Exception(f"API 调用失败: {response.status_code}")
            
            result = response.json()
            result_text = result['choices'][0]['message']['content']
            
            return json.loads(result_text)
            
        except Exception as e:
            logger.error(f"Trip refinement error: {e}")
            raise

