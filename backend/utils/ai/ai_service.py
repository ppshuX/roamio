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


class AIFormatError(ValueError):
    """自定义异常：用于携带原始 AI 文本，便于上层做调试输出"""
    def __init__(self, message, raw_content=None):
        super().__init__(message)
        self.raw_content = raw_content


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
        self.max_tokens = int(os.getenv('AI_MAX_TOKENS', '8000'))  # 增加到 8000，支持更详细的行程
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
            self.tokens_used = result.get('usage', {}).get('total_tokens', 0)
            self.generation_time = time.time() - start_time
            
            logger.info(
                f"AI generation completed. "
                f"Tokens: {self.tokens_used}, Time: {self.generation_time:.2f}s"
            )
            
            # 4. 解析 JSON（带容错）
            trip_plan = self._parse_json_response(result_text)
            
            # 5. 数据验证和清洗
            validated_plan = self._validate_and_clean(trip_plan, preferences)
            
            return validated_plan
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            raise ValueError("AI 返回格式错误，请重试")
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            raise
    
    def _parse_json_response(self, content):
        """
        尝试把大模型返回内容解析为 JSON，做一层容错处理。
        有些情况下模型会在 JSON 前后加说明文字，这里尽量截取出真正的 JSON 部分。
        """
        # 如果已经是 dict，直接返回
        if isinstance(content, dict):
            return content
        
        if not isinstance(content, str):
            logger.error(f"Unexpected AI content type: {type(content)}")
            raise ValueError("AI 返回格式错误，请重试")
        
        text = content.strip()
        
        # 第一轮：直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # 第二轮：截取第一个 '{' 到最后一个 '}' 之间的内容再解析
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            candidate = text[start:end + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                logger.error(
                    "AI JSON candidate parse failed. Candidate snippet: %s",
                    candidate[:500]
                )
        
        # 第三轮：如果是数组开头（有些模型会返回 [ {...}, ... ]）
        start = text.find('[')
        end = text.rfind(']')
        if start != -1 and end != -1 and end > start:
            candidate = text[start:end + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                logger.error(
                    "AI JSON array candidate parse failed. Candidate snippet: %s",
                    candidate[:500]
                )
        
        # 第四轮：使用 ast.literal_eval 做一次宽松解析（兼容单引号等 Python 风格）
        try:
            import ast
            obj = ast.literal_eval(text)
            if isinstance(obj, (dict, list)):
                return obj
        except Exception:
            # 不记录详细异常，避免日志过长；最终会在下面统一记录一段原始内容
            pass
        
        # 仍然失败，记录原始内容方便排查
        # 保存更多内容（前2000字符）以便调试
        raw_snippet = text[:2000]
        logger.error(
            "AI response is not valid JSON. Content length: %d, Preview (first 500 chars): %s",
            len(text),
            text[:500]
        )
        # 检查是否是内容被截断（没有闭合的 JSON）
        if text.count('{') > text.count('}'):
            logger.warning("JSON appears to be truncated (unclosed braces)")
        if text.count('[') > text.count(']'):
            logger.warning("JSON appears to be truncated (unclosed brackets)")
        
        # 抛出自定义异常，方便上层在管理员用户下返回调试信息
        raise AIFormatError("AI 返回格式错误，请重试", raw_content=raw_snippet)
    
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
        
        return f"""你是 Roamio 旅行规划助手。根据用户需求生成结构清晰、内容适中且**必须是有效 JSON** 的旅行计划。

【输出格式】严格的 JSON 格式：
{{
  "trip_title": "行程标题（简洁有吸引力）",
  "summary": "行程概述（80字内，突出亮点）",
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
          "description": "活动简要描述（80-150字）：简要介绍地点特色、主要看点和推荐游玩顺序。",
          "estimated_cost": 预估费用,
          "tips": "实用提示（2-4条，简短句子）：包含门票/交通/时间/注意事项中的若干要点即可。"
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
1. **地点真实存在**：所有地点必须真实存在，优先推荐热门景点和口碑餐厅。
2. **详细地址**：每个地点必须提供详细地址（省市区或商圈 + 街道或大致位置），方便导航和定位。
3. **地理坐标**：每个地点尽量提供合理的地理坐标（经纬度），不需要完全精确，但要在该城市范围内。
4. **时间安排合理**：考虑交通时间、排队时间、体力消耗，预算大致符合{budget_desc}。
5. **风格匹配**：整体风格符合“{style_desc}”。
6. **严格遵守 JSON 格式**：
   - 顶层必须是一个对象（以 {{ 开始，以 }} 结束）；
   - 不输出任何 JSON 以外的文字（不要解释、不要前后加句子）；
   - 数字不加引号，日期用 YYYY-MM-DD，时间用 HH:MM。
7. **字数控制**：在保证信息完整的前提下，尽量使用精炼的语句，避免过长段落，确保整个 JSON 能在一次回答中完整输出。
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

【核心要求】
1. 每天安排 2-4 个主要活动（景点/体验项目）
2. 每个活动的描述必须达到 150-300 字，详细介绍地点特色、游玩路线、体验项目
3. 每个活动的实用提示必须包含 3-5 条，涵盖门票、交通、时间、注意事项、美食
4. 包含详细的交通和餐饮建议
5. 所有地点提供准确的地址和坐标
6. 返回完整、规范的 JSON 格式

【描述示例】
"故宫博物院是中国明清两代的皇家宫殿，位于北京市中心，是世界上现存规模最大、保存最完整的木质结构古建筑群。从午门进入后，依次游览太和殿、中和殿、保和殿三大殿，感受皇家建筑的宏伟壮观。推荐游览路线：午门→太和殿→养心殿→御花园→神武门，全程约需3-4小时。必看景点包括金水桥、乾清宫、坤宁宫等，不要错过珍宝馆和钟表馆的珍贵展品。建议租用语音导览（20元/次）深入了解历史文化。"

请严格按照要求生成详细、实用、有价值的旅行攻略。
"""
        return prompt
    
    def _validate_and_clean(self, trip_plan, preferences):
        """验证和清洗数据"""
        # 1. 基础字段验证（trip_title 由下面的容错逻辑补齐）
        required_fields = ['summary', 'days', 'days_detail']
        for field in required_fields:
            if field not in trip_plan:
                raise ValueError(f"缺少必需字段: {field}")

        # trip_title 容错处理：模型偶尔会漏掉标题，不能因此让整条生成链路失败
        if 'trip_title' not in trip_plan or not trip_plan.get('trip_title'):
            if trip_plan.get('destination'):
                trip_plan['trip_title'] = f"{trip_plan['destination']}之旅"
            elif trip_plan.get('days_detail') and len(trip_plan['days_detail']) > 0:
                first_day = trip_plan['days_detail'][0]
                if first_day.get('title'):
                    title = first_day['title'].replace('Day 1:', '').replace('Day 1：', '').strip()
                    trip_plan['trip_title'] = title if title else "我的旅行计划"
                else:
                    trip_plan['trip_title'] = "我的旅行计划"
            elif trip_plan.get('summary'):
                trip_plan['trip_title'] = f"{trip_plan['summary'][:20]}..."
            else:
                trip_plan['trip_title'] = "我的旅行计划"

            logger.warning("AI response missing trip_title; generated fallback: %s", trip_plan['trip_title'])
        
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
