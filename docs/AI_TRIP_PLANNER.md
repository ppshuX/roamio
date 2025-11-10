# 🤖 AI 旅行规划助手 - 完整实施方案

## 📋 项目概述

### 功能定位
为 Roamio 用户提供 AI 辅助的旅行规划功能，用户只需用自然语言描述旅行想法，AI 自动生成结构化的行程计划，大幅降低行程创建门槛。

### 核心价值
- **降低创作门槛**：从"逐字输入"到"审核修改"
- **提升填写效率**：5 分钟生成完整行程
- **保持内容质量**：AI 按照 Roamio 固定格式输出
- **个性化推荐**：基于用户历史偏好优化

### 使用场景
```
用户输入：
"我想去云南旅游5天，主要去大理和丽江，
喜欢古城和自然风光，预算中等"

↓ AI 处理（3-5秒）↓

自动生成：
📍 Day 1: 昆明 → 大理古城
   时间：2025-12-01 09:00
   地点：大理古城
   活动：漫步古城，品尝白族美食，探访洋人街
   预算：¥500
   提示：建议穿舒适的鞋，古城石板路较多
   
📍 Day 2: 大理洱海骑行
   时间：2025-12-02 08:00
   地点：洱海生态廊道
   活动：环洱海骑行，打卡双廊古镇，观日落
   预算：¥300
   提示：提前租好电动车，注意防晒
   
... (共5天)
```

---

## 🎯 技术方案

### 1. AI 服务选型

#### 推荐方案：**通义千问 (Qwen)**

| 对比项 | 通义千问 | 文心一言 | GPT-4 |
|--------|---------|---------|-------|
| **免费额度** | 100万 tokens/月 | 50万 tokens/月 | 无 |
| **中文能力** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **旅游场景** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **稳定性** | 高 | 中 | 需代理 |
| **成本** | ¥0.3-2/百万tokens | ¥0.8-3/百万tokens | $10-30/百万tokens |
| **JSON 输出** | 原生支持 | 支持 | 支持 |
| **响应速度** | 2-4秒 | 3-5秒 | 3-6秒 |

**选择理由**：
1. ✅ 免费额度充足（预计可支持 300+ 次生成/月）
2. ✅ 阿里云生态集成（Roamio 已用阿里云服务器）
3. ✅ 中文旅游场景理解优秀
4. ✅ 国内访问稳定，无需代理
5. ✅ 支持强制 JSON 格式输出

#### 备选方案
- **文心一言**：作为降级备份
- **智谱 GLM-4**：未来高级功能可考虑

---

### 2. 系统架构设计

```
┌─────────────────────────────────────────────────────────┐
│                     前端 (Vue 3)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 创建行程页面 │  │ AI 对话面板  │  │ 行程预览组件 │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
└─────────┼──────────────────┼──────────────────┼─────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────┐
│                  Roamio Backend API                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │         /api/v1/ai/generate-trip/                │  │
│  │         /api/v1/ai/refine-trip/                  │  │
│  │         /api/v1/ai/suggest-activities/           │  │
│  └────────────────────┬─────────────────────────────┘  │
│                       │                                  │
│  ┌────────────────────▼─────────────────────────────┐  │
│  │          AI Service Layer                        │  │
│  │  - 提示词工程                                     │  │
│  │  - 响应解析                                       │  │
│  │  - 格式转换                                       │  │
│  │  - 内容审核                                       │  │
│  └────────────────────┬─────────────────────────────┘  │
└───────────────────────┼─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              通义千问 API (DashScope)                    │
│  - qwen-plus / qwen-turbo                               │
│  - JSON Mode                                            │
│  - Temperature: 0.7                                     │
└─────────────────────────────────────────────────────────┘
```

---

### 3. 数据流设计

#### 3.1 生成行程流程
```
1. 用户输入
   ├─ 自然语言描述
   ├─ 偏好设置（预算/风格/天数）
   └─ 可选：上传参考图片

2. 前端处理
   ├─ 表单验证
   ├─ 显示加载动画
   └─ 发送 POST 请求

3. 后端处理
   ├─ 身份验证
   ├─ 频率限制检查（5次/天）
   ├─ 构建提示词
   ├─ 调用通义千问 API
   ├─ 解析 JSON 响应
   ├─ 内容安全审核
   └─ 格式转换

4. AI 生成
   ├─ 理解用户意图
   ├─ 规划行程结构
   ├─ 生成每日活动
   ├─ 估算预算
   └─ 返回 JSON

5. 前端展示
   ├─ 渲染预览卡片
   ├─ 支持编辑修改
   ├─ 一键应用到行程
   └─ 保存到数据库
```

#### 3.2 数据格式规范

**前端请求格式**：
```json
{
  "prompt": "我想去云南旅游5天，主要去大理和丽江，喜欢古城和自然风光，预算中等",
  "preferences": {
    "destination": "云南",
    "days": 5,
    "budget_level": "medium",
    "travel_style": "leisure",
    "interests": ["古城", "自然风光"],
    "start_date": "2025-12-01"
  }
}
```

**AI 返回格式**：
```json
{
  "trip_title": "云南大理丽江5日悠闲之旅",
  "summary": "探索云南的古城韵味与自然风光，感受白族与纳西族文化，享受慢节奏的旅行时光。",
  "destination": "云南（大理、丽江）",
  "days": 5,
  "total_budget": 4500,
  "days_detail": [
    {
      "day_number": 1,
      "date": "2025-12-01",
      "title": "昆明 → 大理古城",
      "location": "大理",
      "activities": [
        {
          "time": "09:00",
          "duration": "3小时",
          "location": "大理古城",
          "location_type": "景点",
          "description": "漫步大理古城，探访五华楼、洋人街，品尝白族特色美食如乳扇、烤饵块",
          "estimated_cost": 500,
          "tips": "建议穿舒适的鞋，古城石板路较多；上午游客较少，拍照更佳",
          "coordinates": {
            "lat": 25.6929,
            "lng": 100.1677
          }
        },
        {
          "time": "14:00",
          "duration": "2小时",
          "location": "崇圣寺三塔",
          "location_type": "景点",
          "description": "参观大理标志性建筑，了解南诏国历史，远眺苍山洱海",
          "estimated_cost": 120,
          "tips": "门票可网上预订优惠；下午光线适合拍摄三塔倒影",
          "coordinates": {
            "lat": 25.7089,
            "lng": 100.1447
          }
        }
      ],
      "accommodation": {
        "name": "大理古城客栈",
        "type": "客栈",
        "estimated_cost": 200,
        "tips": "建议住古城内，夜晚可逛夜市"
      },
      "meals": {
        "breakfast": 30,
        "lunch": 80,
        "dinner": 100
      },
      "transportation": {
        "type": "高铁+出租车",
        "estimated_cost": 150
      },
      "day_total": 1180
    }
    // ... Day 2-5
  ],
  "budget_breakdown": {
    "accommodation": 1000,
    "meals": 1500,
    "transportation": 800,
    "tickets": 600,
    "shopping": 400,
    "emergency": 200
  },
  "travel_tips": [
    "云南紫外线强，务必做好防晒",
    "高原地区注意预防高反，前两天不要剧烈运动",
    "古城内商铺可适当砍价",
    "建议提前预订客栈和门票，旺季价格较高",
    "携带常用药品：感冒药、肠胃药、创可贴"
  ],
  "packing_list": [
    "防晒霜（SPF50+）",
    "墨镜和帽子",
    "舒适的运动鞋",
    "轻薄外套（早晚温差大）",
    "充电宝和转换插头"
  ],
  "best_season": "3-5月、9-11月",
  "weather_note": "12月大理丽江气温5-15℃，早晚较冷，需带保暖衣物"
}
```

**后端响应格式**：
```json
{
  "code": 200,
  "message": "生成成功",
  "data": {
    "trip_plan": { /* 上述 AI 返回格式 */ },
    "ai_metadata": {
      "model": "qwen-plus",
      "tokens_used": 3245,
      "generation_time": 3.2,
      "cost": 0.0065
    }
  },
  "timestamp": 1699999999
}
```

---

## 💻 代码实现

### 4.1 后端实现

#### 文件结构
```
trips/
├── api/
│   └── viewsets/
│       └── ai_viewset.py          # AI API 端点
├── utils/
│   ├── ai_service.py              # AI 服务核心
│   ├── ai_prompts.py              # 提示词模板
│   └── ai_rate_limiter.py         # 频率限制
└── serializers/
    └── ai_serializer.py           # 数据验证
```

#### 核心代码

**`trips/utils/ai_service.py`**：
```python
import os
import json
import logging
from openai import OpenAI
from django.core.cache import cache
from datetime import date, timedelta

logger = logging.getLogger(__name__)

class TripPlannerAI:
    """旅行规划 AI 服务"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv('QWEN_API_KEY'),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.model = os.getenv('QWEN_MODEL', 'qwen-plus')
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
        import time
        start_time = time.time()
        
        try:
            # 1. 构建提示词
            system_prompt = self._build_system_prompt(preferences)
            user_full_prompt = self._build_user_prompt(
                user_prompt, preferences, user
            )
            
            # 2. 调用 AI
            logger.info(f"Calling Qwen API with model: {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_full_prompt}
                ],
                temperature=0.7,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            # 3. 解析响应
            result_text = response.choices[0].message.content
            self.tokens_used = response.usage.total_tokens
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
          "tips": "实用提示",
          "coordinates": {{"lat": 纬度, "lng": 经度}}
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
6. **坐标准确**：提供正确的经纬度坐标（用于地图展示）

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
            past_trips = user.trips.filter(is_public=True).order_by('-created_at')[:3]
            if past_trips.exists():
                user_context = "\n\n【用户历史偏好参考】\n"
                for trip in past_trips:
                    user_context += f"- 曾去过：{trip.title}\n"
        
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
            start_date = date.fromisoformat(start_date_str)
            for i, day in enumerate(trip_plan['days_detail']):
                day['date'] = (start_date + timedelta(days=i)).isoformat()
        
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
        """优化已有行程"""
        system_prompt = """你是 Roamio 旅行规划助手。
用户对已有行程提出了修改意见，请根据反馈优化行程，保持 JSON 格式。"""
        
        user_prompt = f"""【现有行程】
{json.dumps(existing_plan, ensure_ascii=False, indent=2)}

【用户反馈】
{user_feedback}

请根据反馈优化行程，返回完整的 JSON 格式。
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
```

**`trips/api/viewsets/ai_viewset.py`**：
```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from datetime import date

from trips.utils.ai_service import TripPlannerAI
from trips.serializers.ai_serializer import (
    TripGenerationRequestSerializer,
    TripRefinementRequestSerializer
)

import logging
logger = logging.getLogger(__name__)


class AIAssistantViewSet(viewsets.ViewSet):
    """AI 旅行规划助手 API"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='generate-trip')
    def generate_trip(self, request):
        """
        生成旅行计划
        
        POST /api/v1/ai/generate-trip/
        
        Request Body:
        {
            "prompt": "用户的旅行描述",
            "preferences": {
                "days": 5,
                "budget_level": "medium",
                "travel_style": "leisure",
                "start_date": "2025-12-01"
            }
        }
        
        Response:
        {
            "code": 200,
            "message": "生成成功",
            "data": {
                "trip_plan": { ... },
                "ai_metadata": {
                    "tokens_used": 3245,
                    "generation_time": 3.2,
                    "cost": 0.0065
                }
            }
        }
        """
        # 1. 数据验证
        serializer = TripGenerationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': 400,
                'message': '参数错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 2. 频率限制检查
        rate_limit_key = f"ai_generation:{request.user.id}:{date.today()}"
        generation_count = cache.get(rate_limit_key, 0)
        
        # 免费用户限制 5 次/天
        max_generations = 5 if not request.user.is_vip else 999
        
        if generation_count >= max_generations:
            return Response({
                'code': 429,
                'message': f'今日生成次数已用完（{max_generations}次/天）',
                'data': {
                    'used': generation_count,
                    'limit': max_generations,
                    'reset_at': 'tomorrow'
                }
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # 3. 调用 AI 服务
        try:
            ai_service = TripPlannerAI()
            trip_plan = ai_service.generate_trip_plan(
                user_prompt=serializer.validated_data['prompt'],
                preferences=serializer.validated_data.get('preferences', {}),
                user=request.user
            )
            
            # 4. 更新使用次数
            cache.set(rate_limit_key, generation_count + 1, timeout=86400)
            
            # 5. 计算成本（仅供参考）
            cost = self._calculate_cost(
                ai_service.tokens_used,
                ai_service.model
            )
            
            # 6. 返回结果
            return Response({
                'code': 200,
                'message': '生成成功',
                'data': {
                    'trip_plan': trip_plan,
                    'ai_metadata': {
                        'model': ai_service.model,
                        'tokens_used': ai_service.tokens_used,
                        'generation_time': round(ai_service.generation_time, 2),
                        'cost': round(cost, 4),
                        'remaining_today': max_generations - generation_count - 1
                    }
                }
            })
            
        except ValueError as e:
            logger.error(f"AI generation validation error: {e}")
            return Response({
                'code': 400,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"AI generation error: {e}", exc_info=True)
            return Response({
                'code': 500,
                'message': 'AI 服务暂时不可用，请稍后重试'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='refine-trip')
    def refine_trip(self, request):
        """
        优化已有行程
        
        POST /api/v1/ai/refine-trip/
        
        Request Body:
        {
            "trip_plan": { ... },
            "feedback": "第二天太累了，想轻松一点"
        }
        """
        serializer = TripRefinementRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': 400,
                'message': '参数错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            ai_service = TripPlannerAI()
            refined_plan = ai_service.refine_trip_plan(
                existing_plan=serializer.validated_data['trip_plan'],
                user_feedback=serializer.validated_data['feedback']
            )
            
            return Response({
                'code': 200,
                'message': '优化成功',
                'data': {
                    'trip_plan': refined_plan
                }
            })
            
        except Exception as e:
            logger.error(f"Trip refinement error: {e}")
            return Response({
                'code': 500,
                'message': '优化失败，请重试'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='usage-stats')
    def usage_stats(self, request):
        """
        查询今日使用情况
        
        GET /api/v1/ai/usage-stats/
        """
        rate_limit_key = f"ai_generation:{request.user.id}:{date.today()}"
        generation_count = cache.get(rate_limit_key, 0)
        max_generations = 5 if not request.user.is_vip else 999
        
        return Response({
            'code': 200,
            'data': {
                'used': generation_count,
                'limit': max_generations,
                'remaining': max_generations - generation_count,
                'is_vip': request.user.is_vip
            }
        })
    
    def _calculate_cost(self, tokens, model):
        """计算 API 调用成本（人民币）"""
        # 通义千问价格（元/百万tokens）
        pricing = {
            'qwen-turbo': {'input': 0.3, 'output': 0.6},
            'qwen-plus': {'input': 0.8, 'output': 2.0},
            'qwen-max': {'input': 20, 'output': 60}
        }
        
        # 简化计算：假设输入输出各占一半
        rate = pricing.get(model, pricing['qwen-plus'])
        avg_rate = (rate['input'] + rate['output']) / 2
        
        return (tokens / 1000000) * avg_rate
```

**`trips/serializers/ai_serializer.py`**：
```python
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
            raise serializers.ValidationError("描述太简短，请详细说明旅行想法")
        return value.strip()
    
    def validate_preferences(self, value):
        """验证偏好设置"""
        # 验证天数
        if 'days' in value:
            try:
                days = int(value['days'])
                if days < 1 or days > 30:
                    raise serializers.ValidationError("天数必须在 1-30 之间")
            except ValueError:
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
```

**`trips/urls/api_urls.py`** (添加路由)：
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from trips.api.viewsets.ai_viewset import AIAssistantViewSet

router = DefaultRouter()
router.register(r'ai', AIAssistantViewSet, basename='ai')

urlpatterns = [
    path('', include(router.urls)),
    # ... 其他路由
]
```

---

### 4.2 前端实现

#### 文件结构
```
web/src/
├── components/
│   └── ai/
│       ├── TripGenerator.vue      # AI 生成主组件
│       ├── PromptInput.vue        # 输入面板
│       ├── TripPreview.vue        # 预览组件
│       └── GenerationProgress.vue # 加载动画
├── api/
│   └── ai.js                      # AI API 调用
└── views/
    └── TripCreate.vue             # 创建行程页面
```

#### 核心组件

**`web/src/components/ai/TripGenerator.vue`**：
```vue
<template>
  <div class="ai-trip-generator">
    <!-- 头部 -->
    <div class="generator-header">
      <h2>🤖 AI 智能生成行程</h2>
      <p class="subtitle">告诉我你的旅行想法，AI 为你规划完美行程</p>
    </div>

    <!-- 输入区 -->
    <div class="input-section" v-if="!isGenerating && !generatedTrip">
      <div class="prompt-area">
        <label>描述你的旅行计划</label>
        <textarea
          v-model="userPrompt"
          placeholder="例如：我想去云南旅游5天，主要去大理和丽江，喜欢古城和自然风光，预算中等。希望节奏不要太紧张，每天2-3个景点就好。"
          rows="6"
          maxlength="2000"
        ></textarea>
        <div class="char-count">{{ userPrompt.length }}/2000</div>
      </div>

      <!-- 偏好设置 -->
      <div class="preferences">
        <h3>偏好设置</h3>
        <div class="pref-grid">
          <div class="pref-item">
            <label>旅行天数</label>
            <input
              type="number"
              v-model.number="preferences.days"
              min="1"
              max="30"
              placeholder="5"
            />
          </div>

          <div class="pref-item">
            <label>预算等级</label>
            <select v-model="preferences.budget_level">
              <option value="low">经济型 (¥200-300/天)</option>
              <option value="medium">中等 (¥400-600/天)</option>
              <option value="high">舒适型 (¥800-1200/天)</option>
            </select>
          </div>

          <div class="pref-item">
            <label>旅行风格</label>
            <select v-model="preferences.travel_style">
              <option value="leisure">休闲放松</option>
              <option value="adventure">探险刺激</option>
              <option value="culture">文化深度</option>
              <option value="food">美食之旅</option>
              <option value="photography">摄影采风</option>
            </select>
          </div>

          <div class="pref-item">
            <label>出发日期</label>
            <input
              type="date"
              v-model="preferences.start_date"
              :min="today"
            />
          </div>
        </div>
      </div>

      <!-- 生成按钮 -->
      <div class="action-buttons">
        <button
          class="btn-generate"
          @click="generateTrip"
          :disabled="!canGenerate"
        >
          ✨ AI 生成行程
        </button>
        <div class="usage-info" v-if="usageStats">
          今日剩余次数: {{ usageStats.remaining }}/{{ usageStats.limit }}
        </div>
      </div>
    </div>

    <!-- 生成中 -->
    <GenerationProgress v-if="isGenerating" />

    <!-- 预览区 -->
    <TripPreview
      v-if="generatedTrip"
      :trip="generatedTrip"
      @apply="applyTrip"
      @regenerate="regenerate"
      @refine="showRefineDialog"
    />

    <!-- 优化对话框 -->
    <el-dialog
      v-model="refineDialogVisible"
      title="优化行程"
      width="500px"
    >
      <el-input
        v-model="refineFeedback"
        type="textarea"
        rows="4"
        placeholder="告诉 AI 你想如何调整，例如：第二天太累了，想轻松一点"
      />
      <template #footer>
        <el-button @click="refineDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="refineTrip">确认优化</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElDialog, ElInput, ElButton } from 'element-plus'
import GenerationProgress from './GenerationProgress.vue'
import TripPreview from './TripPreview.vue'
import { generateTripPlan, refineTripPlan, getUsageStats } from '@/api/ai'

// 数据
const userPrompt = ref('')
const preferences = ref({
  days: 5,
  budget_level: 'medium',
  travel_style: 'leisure',
  start_date: ''
})

const isGenerating = ref(false)
const generatedTrip = ref(null)
const usageStats = ref(null)
const refineDialogVisible = ref(false)
const refineFeedback = ref('')

// 计算属性
const today = computed(() => {
  return new Date().toISOString().split('T')[0]
})

const canGenerate = computed(() => {
  return userPrompt.value.trim().length >= 10
})

// 方法
const loadUsageStats = async () => {
  try {
    const response = await getUsageStats()
    usageStats.value = response.data
  } catch (error) {
    console.error('加载使用统计失败:', error)
  }
}

const generateTrip = async () => {
  if (!canGenerate.value) {
    ElMessage.warning('请详细描述你的旅行想法')
    return
  }

  isGenerating.value = true

  try {
    const response = await generateTripPlan({
      prompt: userPrompt.value,
      preferences: preferences.value
    })

    generatedTrip.value = response.data.trip_plan

    ElMessage.success('行程生成成功！')

    // 更新使用统计
    await loadUsageStats()
  } catch (error) {
    console.error('生成失败:', error)
    
    if (error.response?.status === 429) {
      ElMessage.error('今日生成次数已用完，请明天再试')
    } else {
      ElMessage.error(error.response?.data?.message || '生成失败，请重试')
    }
  } finally {
    isGenerating.value = false
  }
}

const applyTrip = () => {
  // 将生成的行程应用到创建表单
  emit('apply', generatedTrip.value)
  ElMessage.success('已应用到行程，你可以继续编辑')
}

const regenerate = () => {
  generatedTrip.value = null
  ElMessage.info('请重新描述你的旅行想法')
}

const showRefineDialog = () => {
  refineDialogVisible.value = true
  refineFeedback.value = ''
}

const refineTrip = async () => {
  if (!refineFeedback.value.trim()) {
    ElMessage.warning('请输入优化建议')
    return
  }

  try {
    const response = await refineTripPlan({
      trip_plan: generatedTrip.value,
      feedback: refineFeedback.value
    })

    generatedTrip.value = response.data.trip_plan
    refineDialogVisible.value = false

    ElMessage.success('行程已优化')
  } catch (error) {
    console.error('优化失败:', error)
    ElMessage.error('优化失败，请重试')
  }
}

// 生命周期
onMounted(() => {
  loadUsageStats()
})

// 事件
const emit = defineEmits(['apply'])
</script>

<style scoped lang="scss">
.ai-trip-generator {
  max-width: 900px;
  margin: 0 auto;
  padding: 30px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.generator-header {
  text-align: center;
  margin-bottom: 30px;

  h2 {
    font-size: 28px;
    color: #333;
    margin-bottom: 10px;
  }

  .subtitle {
    color: #666;
    font-size: 14px;
  }
}

.input-section {
  .prompt-area {
    margin-bottom: 30px;
    position: relative;

    label {
      display: block;
      font-weight: 600;
      margin-bottom: 10px;
      color: #333;
    }

    textarea {
      width: 100%;
      padding: 15px;
      border: 2px solid #e0e0e0;
      border-radius: 8px;
      font-size: 14px;
      line-height: 1.6;
      resize: vertical;
      transition: border-color 0.3s;

      &:focus {
        outline: none;
        border-color: #409eff;
      }
    }

    .char-count {
      position: absolute;
      right: 10px;
      bottom: 10px;
      font-size: 12px;
      color: #999;
    }
  }

  .preferences {
    margin-bottom: 30px;

    h3 {
      font-size: 18px;
      margin-bottom: 15px;
      color: #333;
    }

    .pref-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 20px;

      @media (max-width: 768px) {
        grid-template-columns: 1fr;
      }
    }

    .pref-item {
      label {
        display: block;
        font-size: 14px;
        margin-bottom: 8px;
        color: #666;
      }

      input,
      select {
        width: 100%;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 6px;
        font-size: 14px;

        &:focus {
          outline: none;
          border-color: #409eff;
        }
      }
    }
  }

  .action-buttons {
    text-align: center;

    .btn-generate {
      padding: 15px 50px;
      font-size: 16px;
      font-weight: 600;
      color: #fff;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border: none;
      border-radius: 25px;
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;

      &:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
      }

      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }
    }

    .usage-info {
      margin-top: 15px;
      font-size: 13px;
      color: #999;
    }
  }
}
</style>
```

**`web/src/api/ai.js`**：
```javascript
import request from '@/utils/request'

/**
 * 生成旅行计划
 */
export function generateTripPlan(data) {
  return request({
    url: '/api/v1/ai/generate-trip/',
    method: 'post',
    data
  })
}

/**
 * 优化旅行计划
 */
export function refineTripPlan(data) {
  return request({
    url: '/api/v1/ai/refine-trip/',
    method: 'post',
    data
  })
}

/**
 * 获取使用统计
 */
export function getUsageStats() {
  return request({
    url: '/api/v1/ai/usage-stats/',
    method: 'get'
  })
}
```

---

## 📊 成本与收益分析

### 成本估算

#### API 调用成本
```
通义千问 qwen-plus 定价：
- 输入：¥0.8 / 百万 tokens
- 输出：¥2.0 / 百万 tokens

单次生成消耗：
- 输入：~1000 tokens (系统提示词 + 用户输入)
- 输出：~2500 tokens (5天详细行程)
- 总计：~3500 tokens

单次成本：
- 输入：0.001 * 0.8 = ¥0.0008
- 输出：0.0025 * 2.0 = ¥0.005
- 合计：¥0.0058 ≈ ¥0.006/次

月度成本预估：
- 100 次生成：¥0.6
- 500 次生成：¥3
- 1000 次生成：¥6
- 5000 次生成：¥30

免费额度：100万 tokens/月
可支持约 285 次免费生成
```

#### 服务器成本
- 无额外成本（使用现有服务器）
- Redis 缓存（频率限制）：已有

#### 总成本
- **初期（<1000用户）**：几乎免费
- **成长期（1000-5000用户）**：¥10-50/月
- **成熟期（>5000用户）**：¥50-200/月

### 收益分析

#### 用户价值
- **节省时间**：从 2小时 → 5分钟
- **降低门槛**：不知道怎么写 → 一键生成
- **提升质量**：专业规划 + 实用建议

#### 商业价值
1. **用户增长**：差异化功能吸引新用户
2. **用户留存**：提升产品体验，增加粘性
3. **付费转化**：VIP 功能（无限生成）
4. **数据价值**：收集旅游偏好，优化推荐

#### ROI 估算
```
假设：
- 月活用户：1000
- AI 功能使用率：30%
- 付费转化率：5%
- VIP 价格：¥19/月

收入：
- 免费用户：300 * 0 = ¥0
- VIP 用户：300 * 0.05 * 19 = ¥285

成本：
- API 调用：¥10

净收益：¥275/月

ROI：2750%
```

---

## 🚀 实施计划

### Phase 1: MVP (1-2周) ✅

**目标**：实现基础 AI 生成功能

**任务清单**：
- [ ] 注册通义千问账号，获取 API Key
- [ ] 后端实现
  - [ ] 创建 `ai_service.py` 核心服务
  - [ ] 创建 `ai_viewset.py` API 端点
  - [ ] 创建 `ai_serializer.py` 数据验证
  - [ ] 添加路由配置
  - [ ] 配置环境变量
- [ ] 前端实现
  - [ ] 创建 `TripGenerator.vue` 主组件
  - [ ] 创建 `ai.js` API 调用
  - [ ] 集成到创建行程页面
- [ ] 测试
  - [ ] 单元测试（后端）
  - [ ] 集成测试
  - [ ] 用户体验测试

**验收标准**：
- ✅ 用户可以输入描述生成行程
- ✅ 返回结构化的 JSON 数据
- ✅ 前端正确展示生成结果
- ✅ 频率限制生效（5次/天）

---

### Phase 2: 优化迭代 (2-3周) 🔄

**目标**：提升生成质量和用户体验

**任务清单**：
- [ ] 提示词优化
  - [ ] A/B 测试不同提示词
  - [ ] 收集用户反馈优化
  - [ ] 增加示例和约束
- [ ] 功能增强
  - [ ] 实现"优化行程"功能
  - [ ] 支持多轮对话
  - [ ] 增加用户历史偏好学习
- [ ] UI/UX 优化
  - [ ] 美化生成动画
  - [ ] 增加进度提示
  - [ ] 优化移动端体验
- [ ] 数据分析
  - [ ] 埋点统计使用情况
  - [ ] 分析生成质量
  - [ ] 收集用户满意度

---

### Phase 3: 高级功能 (未来规划) 🔮

**可选功能**：
1. **联网搜索**
   - 实时查询天气、门票价格
   - 获取最新景点信息
   - 推荐热门餐厅

2. **图片生成**
   - AI 生成旅行封面图
   - 景点图片自动匹配

3. **语音输入**
   - 语音描述旅行想法
   - 语音播报行程

4. **智能推荐**
   - 基于用户画像推荐目的地
   - 相似行程推荐

5. **社交分享**
   - 生成精美行程卡片
   - 一键分享到社交平台

---

## 🔐 安全与合规

### 1. API Key 安全

**环境变量配置**：
```bash
# .env
QWEN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
QWEN_MODEL=qwen-plus
AI_GENERATION_ENABLED=True
```

**代码中使用**：
```python
import os
api_key = os.getenv('QWEN_API_KEY')
```

**注意事项**：
- ✅ 不要硬编码 API Key
- ✅ 不要提交到 Git
- ✅ 定期轮换密钥
- ✅ 监控 API 调用量

### 2. 内容安全

**敏感词过滤**：
```python
SENSITIVE_WORDS = [
    '政治', '赌博', '色情', '暴力',
    # ... 更多敏感词
]

def content_safety_check(content):
    for word in SENSITIVE_WORDS:
        if word in content:
            raise ValueError(f"内容包含敏感词: {word}")
```

**用户输入验证**：
- 长度限制：2000 字符
- 格式检查：去除特殊字符
- 频率限制：防止滥用

### 3. 成本控制

**频率限制**：
```python
# 免费用户：5次/天
# VIP 用户：无限制
MAX_GENERATIONS_FREE = 5
MAX_GENERATIONS_VIP = 999
```

**Token 限制**：
```python
max_tokens=4000  # 限制输出长度
```

**异常监控**：
- 监控 API 调用失败率
- 监控响应时间
- 监控成本超支

### 4. 数据隐私

**用户数据**：
- 不存储用户输入的原始文本
- 仅记录使用次数和元数据
- 遵守 GDPR/PIPL 规范

**日志脱敏**：
```python
logger.info(f"User {user.id[:8]}*** generated trip")
```

---

## 📈 监控与分析

### 关键指标

#### 1. 使用指标
- **生成次数**：日/周/月
- **成功率**：生成成功 / 总请求
- **平均响应时间**：秒
- **Token 消耗**：总量和平均值

#### 2. 质量指标
- **应用率**：生成后实际使用的比例
- **编辑率**：用户修改生成内容的比例
- **满意度**：用户评分（1-5星）

#### 3. 商业指标
- **转化率**：免费 → VIP
- **留存率**：使用 AI 功能的用户留存
- **ROI**：收入 / 成本

### 数据埋点

```javascript
// 前端埋点
trackEvent('ai_generation_start', {
  prompt_length: userPrompt.length,
  days: preferences.days,
  budget: preferences.budget_level
})

trackEvent('ai_generation_success', {
  generation_time: response.ai_metadata.generation_time,
  tokens_used: response.ai_metadata.tokens_used
})

trackEvent('ai_trip_applied', {
  trip_id: appliedTripId
})
```

---

## 🎯 成功标准

### MVP 阶段
- ✅ 生成成功率 > 95%
- ✅ 平均响应时间 < 5秒
- ✅ 用户应用率 > 60%
- ✅ 无重大 Bug

### 优化阶段
- ✅ 生成成功率 > 98%
- ✅ 平均响应时间 < 3秒
- ✅ 用户应用率 > 75%
- ✅ 用户满意度 > 4.0/5.0

### 成熟阶段
- ✅ 月活用户使用率 > 30%
- ✅ VIP 转化率 > 5%
- ✅ 用户留存提升 > 20%
- ✅ 正向 ROI

---

## 📚 参考资源

### 官方文档
- [通义千问 API 文档](https://help.aliyun.com/zh/dashscope/)
- [OpenAI SDK 文档](https://platform.openai.com/docs/api-reference)

### 提示词工程
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [OpenAI Best Practices](https://platform.openai.com/docs/guides/prompt-engineering)

### 相关技术
- Django REST Framework
- Vue 3 Composition API
- Element Plus

---

## 🤝 团队协作

### 角色分工
- **后端开发**：AI 服务、API 开发
- **前端开发**：UI 组件、交互逻辑
- **产品经理**：需求定义、用户测试
- **运营**：用户反馈收集、数据分析

### 沟通机制
- **每日站会**：同步进度和问题
- **周度回顾**：复盘和优化
- **用户反馈会**：收集和响应用户需求

---

## 📝 附录

### A. 环境变量配置示例

```bash
# cloud_settings/.env

# ==================== AI 服务配置 ====================
# 通义千问 API
QWEN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
QWEN_MODEL=qwen-plus  # qwen-turbo / qwen-plus / qwen-max
AI_GENERATION_ENABLED=True

# AI 功能开关
AI_RATE_LIMIT_FREE=5      # 免费用户每日限制
AI_RATE_LIMIT_VIP=999     # VIP 用户每日限制
AI_MAX_TOKENS=4000        # 最大输出 tokens
AI_TEMPERATURE=0.7        # 创意性 (0-1)
```

### B. 测试用例

```python
# tests/test_ai_service.py

def test_generate_trip_plan():
    """测试生成行程"""
    ai_service = TripPlannerAI()
    
    result = ai_service.generate_trip_plan(
        user_prompt="我想去北京旅游3天，看故宫长城",
        preferences={
            'days': 3,
            'budget_level': 'medium',
            'travel_style': 'culture'
        }
    )
    
    assert 'trip_title' in result
    assert len(result['days_detail']) == 3
    assert result['total_budget'] > 0
```

### C. 常见问题

**Q: AI 生成的内容不准确怎么办？**
A: 优化提示词，增加约束条件，收集反馈持续改进。

**Q: API 调用失败如何处理？**
A: 实现重试机制，提供降级方案（使用模板）。

**Q: 成本超支怎么办？**
A: 设置预算告警，降低 token 限制，使用更便宜的模型。

**Q: 如何防止滥用？**
A: 实施频率限制，验证码验证，监控异常调用。

---

## 🎉 总结

AI 旅行规划助手是 Roamio 的重要差异化功能，能够：

1. **大幅降低用户创作门槛**
2. **提升产品竞争力和用户体验**
3. **为未来 AI 功能打下基础**
4. **成本可控，ROI 高**

**建议立即启动 MVP 开发！** 🚀

---

*文档版本：v1.0*  
*最后更新：2025-11-09*  
*维护者：Roamio 开发团队*

