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
                timeout=30
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
        
        return f"""你是 Roamio 专业旅行规划助手，擅长为中国用户规划详细的旅行行程。

【核心任务】
根据用户需求，生成结构化、可执行的旅行计划，包含每日详细活动、时间安排、预算估算和实用建议。

【输出格式要求】
必须返回严格的 JSON 格式，结构如下：
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
          "location": "具体地点名称",
          "location_type": "景点/餐厅/住宿/交通",
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

【内容要求】
1. **真实性**：所有地点必须真实存在，优先推荐热门景点和口碑餐厅
2. **可行性**：时间安排合理，考虑交通时间、排队时间、体力消耗
3. **预算准确**：符合用户要求（{budget_desc}），价格贴近实际
4. **风格匹配**：符合旅行风格（{style_desc}）
5. **详细实用**：每个活动包含具体建议，避免空泛描述
6. **本地化**：使用中国地名、景点名称，价格用人民币

【语言风格】
- 亲切专业，像朋友推荐
- 描述生动但简洁，避免堆砌形容词
- 适度使用 emoji 增加可读性（每段1-2个）
- 避免过于书面化的表达

【特别注意】
- 必须严格遵守 JSON 格式，不要添加任何注释
- 所有数字类型不要加引号
- 日期格式统一为 YYYY-MM-DD
- 时间格式统一为 HH:MM（24小时制）
- 确保 JSON 可以被 Python json.loads() 解析
"""
    
    def _build_user_prompt(self, user_prompt, preferences, user):
        """构建用户提示词"""
        # 基础信息
        days = preferences.get('days', '未指定')
        budget = preferences.get('budget_level', 'medium')
        style = preferences.get('travel_style', 'leisure')
        start_date = preferences.get('start_date', '')
        
        # 用户历史偏好（可选）
        user_context = ""
        if user:
            try:
                from backend.models import Trip
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
        
        prompt = f"""请根据以下信息生成详细的旅行计划：

【用户需求】
{user_prompt}

【偏好设置】
- 旅行天数：{days}天
- 预算等级：{budget}
- 旅行风格：{style}
- 出发日期：{start_date if start_date else '待定'}
{user_context}

【特别要求】
1. 每天安排 2-4 个主要活动，不要过于紧凑
2. 预留用餐和休息时间
3. 考虑景点开放时间和最佳游览时段
4. 提供具体的交通方式和大致费用
5. 包含实用的旅行建议（天气、穿着、注意事项）
6. 确保返回完整的 JSON 格式

请开始生成行程计划。
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
        
        # 3. 日期补全
        start_date_str = preferences.get('start_date')
        if start_date_str:
            try:
                start_date = date.fromisoformat(start_date_str)
                for i, day in enumerate(trip_plan['days_detail']):
                    day['date'] = (start_date + timedelta(days=i)).isoformat()
            except ValueError:
                logger.warning(f"Invalid start_date: {start_date_str}")
        
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
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"API 调用失败: {response.status_code}")
            
            result = response.json()
            result_text = result['choices'][0]['message']['content']
            
            return json.loads(result_text)
            
        except Exception as e:
            logger.error(f"Trip refinement error: {e}")
            raise

