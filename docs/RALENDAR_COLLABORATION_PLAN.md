# 🤝 Roamio × Ralendar 合作行动计划

**日期**: 2025年11月10日  
**状态**: 🟢 积极推进中  
**优先级**: 高

---

## 📋 合作概览

Ralendar 团队非常积极地回应了我们的合作提议，并承诺本周内实现多个新 API。这是一个绝佳的合作机会！

---

## 🎯 立即行动项（本周）

### 1. 接入 Ralendar 节假日 API ⭐⭐⭐

**优先级**: 最高  
**负责人**: Roamio 后端团队  
**截止日期**: 2025年11月17日

#### 任务清单

- [ ] 创建 Ralendar API 客户端
  - 文件：`backend/utils/external/ralendar_holidays.py`
  - 实现三个基础 API 调用
  - 添加错误处理和降级逻辑

- [ ] 前端日期选择器集成
  - 文件：`web/src/components/DatePicker.vue`（或现有组件）
  - 显示节假日标记（🎉 图标）
  - 显示提示信息

- [ ] AI 生成时考虑节假日
  - 修改：`backend/utils/ai/ai_service.py`
  - 在 prompt 中加入节假日信息
  - 优化推荐逻辑

#### API 端点（Ralendar 提供）

```python
# 1. 基础查询（已有）
GET https://app7626.acapp.acwing.com.cn/api/v1/holidays/?year=2025
GET https://app7626.acapp.acwing.com.cn/api/v1/holidays/check/?date=2025-10-01
GET https://app7626.acapp.acwing.com.cn/api/v1/holidays/today/

# 2. 批量查询（本周新增）
POST https://app7626.acapp.acwing.com.cn/api/v1/holidays/batch/
Body: { "dates": ["2025-10-01", "2025-10-02", ...] }

# 3. 节假日推荐（本周新增）
GET https://app7626.acapp.acwing.com.cn/api/v1/holidays/recommend/?months=3&prefer_long=true

# 4. 高峰期分析（本周新增）
GET https://app7626.acapp.acwing.com.cn/api/v1/holidays/peak-analysis/?date=2025-10-01
```

#### 实现方案

**后端客户端**：
```python
# backend/utils/external/ralendar_holidays.py

import requests
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class RalendarHolidaysClient:
    """Ralendar 节假日 API 客户端"""
    
    BASE_URL = 'https://app7626.acapp.acwing.com.cn/api/v1'
    CACHE_TIMEOUT = 86400  # 24小时缓存
    
    @classmethod
    def check_holiday(cls, date):
        """
        检查某天是否为节假日
        
        Args:
            date (str): 日期，格式 YYYY-MM-DD
            
        Returns:
            dict: {
                'is_holiday': bool,
                'holiday_name': str,
                'holiday_type': str
            }
            None: API 失败时返回 None（降级处理）
        """
        cache_key = f'ralendar_holiday_{date}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            response = requests.get(
                f'{cls.BASE_URL}/holidays/check/',
                params={'date': date},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                cache.set(cache_key, data, cls.CACHE_TIMEOUT)
                return data
            else:
                logger.warning(f'Ralendar API error: {response.status_code}')
                return None
                
        except Exception as e:
            logger.error(f'Failed to check holiday: {e}')
            return None
    
    @classmethod
    def get_holidays_batch(cls, dates):
        """批量查询节假日"""
        try:
            response = requests.post(
                f'{cls.BASE_URL}/holidays/batch/',
                json={'dates': dates},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            return {}
            
        except Exception as e:
            logger.error(f'Failed to batch check holidays: {e}')
            return {}
    
    @classmethod
    def recommend_periods(cls, months=3, prefer_long=True):
        """推荐出行时间"""
        try:
            response = requests.get(
                f'{cls.BASE_URL}/holidays/recommend/',
                params={'months': months, 'prefer_long': prefer_long},
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            return {'recommended_periods': []}
            
        except Exception as e:
            logger.error(f'Failed to get recommendations: {e}')
            return {'recommended_periods': []}
```

**前端集成**：
```javascript
// web/src/api/ralendar.js

import request from './request'

const RALENDAR_BASE = 'https://app7626.acapp.acwing.com.cn/api/v1'

export const checkHoliday = (date) => {
  return fetch(`${RALENDAR_BASE}/holidays/check/?date=${date}`)
    .then(res => res.json())
    .catch(err => {
      console.error('节假日查询失败:', err)
      return null
    })
}

export const getHolidaysBatch = (dates) => {
  return fetch(`${RALENDAR_BASE}/holidays/batch/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dates })
  })
    .then(res => res.json())
    .catch(err => {
      console.error('批量查询失败:', err)
      return {}
    })
}
```

---

### 2. 分享 AI 实现经验 ⭐⭐

**优先级**: 高  
**负责人**: Roamio 技术团队  
**截止日期**: 本周内

#### 准备材料

- [ ] 整理 Prompt 工程文档
- [ ] 分享核心代码片段
- [ ] 总结经验和教训
- [ ] 成本控制策略

#### 文档内容

**创建**: `docs/AI_PROMPT_ENGINEERING.md`

包含：
- Prompt 设计原则
- JSON 格式化技巧
- 错误处理策略
- 成本优化方法
- 代码示例

---

### 3. 测试 Ralendar 新 API ⭐⭐

**优先级**: 高  
**负责人**: Roamio 前端团队  
**时间**: Ralendar API 完成后

#### 测试清单

- [ ] 批量查询 API
  - 测试 1 天、7 天、30 天
  - 测试性能和响应时间
  - 测试错误处理

- [ ] 节假日推荐 API
  - 测试不同参数组合
  - 验证推荐结果合理性
  - 测试边界情况

- [ ] 高峰期分析 API
  - 测试各种日期
  - 验证分析准确性
  - 测试建议实用性

---

## 📅 中期计划（本月）

### 1. 联合推荐功能实现 ⭐⭐⭐

**目标**: 实现第一个联合推荐场景

#### 场景：智能出行时间推荐

**流程**：
```
用户输入: "我想去云南"
    ↓
Roamio AI 调用 Ralendar API:
GET /api/v1/holidays/recommend/?months=3&prefer_long=true
    ↓
获取推荐假期: 劳动节（5天）
    ↓
AI Prompt 加入: "用户想在劳动节（5天假期）去云南"
    ↓
生成: 完整的 5 天云南行程
    ↓
展示: "💡 AI 建议：劳动节去云南最合适！"
```

**实现步骤**：
1. Ralendar 实现推荐 API
2. Roamio 集成到 AI 生成流程
3. 优化 Prompt 模板
4. 测试和优化

---

### 2. 数据互通设计 ⭐⭐

**目标**: 设计双向数据交换方案

#### Roamio 提供的 API

**创建**: `backend/api/viewsets/public_stats_viewset.py`

```python
# 1. 目的地热度
GET /api/v1/public/destination-stats/?destination=云南
Response: {
    "destination": "云南",
    "views": 1000,
    "trips_count": 50,
    "popular_months": [7, 8, 10],
    "avg_budget": 3500,
    "avg_days": 5
}

# 2. 热门目的地
GET /api/v1/public/trending-destinations/?limit=10
Response: [
    {"name": "云南", "trips": 50, "trend": "up"},
    {"name": "海南", "trips": 30, "trend": "stable"}
]

# 3. 热门路线
GET /api/v1/public/popular-routes/
Response: [
    {
        "route": "昆明 → 大理 → 丽江",
        "trips": 20,
        "avg_days": 5,
        "avg_budget": 3500
    }
]
```

#### Ralendar 使用场景

- 在日程规划时推荐热门目的地
- 显示"最近 XX 人去了云南"
- 提供预算参考

---

### 3. 黄历功能评估 ⭐

**目标**: 评估是否接入黄历功能

#### 评估维度

1. **用户需求**
   - 发起用户调研
   - 收集反馈意见
   - 分析使用意愿

2. **技术可行性**
   - 测试 Ralendar 的黄历 API
   - 评估集成难度
   - 设计展示方案

3. **产品定位**
   - 作为趣味功能
   - 不影响核心体验
   - 可选开关

#### 决策标准

- ✅ 用户感兴趣 > 50%
- ✅ 技术实现简单
- ✅ 不引起负面反馈
- ✅ 增加产品差异化

---

## 🔮 长期愿景（3-6个月）

### 智能生活助手生态

```
┌─────────────────────────────────────────┐
│         AI 智能决策中心                  │
│  (Roamio AI + Ralendar 数据)            │
└─────────────────────────────────────────┘
         │              │              │
    ┌────┴────┐    ┌────┴────┐    ┌────┴────┐
    │ Roamio  │    │Ralendar │    │第三方   │
    │旅行规划 │    │日程管理 │    │服务     │
    └─────────┘    └─────────┘    └─────────┘
         │              │              │
    ┌────┴──────────────┴──────────────┴────┐
    │           统一用户体验                 │
    │  • 智能推荐                            │
    │  • 数据互通                            │
    │  • 无缝切换                            │
    └────────────────────────────────────────┘
```

### 商业化探索

**可能的方向**：
1. **VIP 会员**
   - Roamio: 更多 AI 次数
   - Ralendar: 高级提醒功能
   - 联合会员：打包优惠

2. **B2B 服务**
   - 企业团建规划
   - 商旅管理
   - 团队协作

3. **平台合作**
   - 旅游平台导流
   - 酒店预订分成
   - 交通票务合作

---

## 📊 技术交流计划

### 分享给 Ralendar 的内容

#### 1. AI Prompt 工程文档

**创建**: `docs/AI_PROMPT_ENGINEERING.md`

**内容**：
- Prompt 设计原则
- JSON 格式化技巧
- 温度和 token 控制
- 错误处理策略
- 成本优化方法

#### 2. 架构重构经验

**创建**: `docs/BACKEND_REFACTORING_GUIDE.md`

**内容**：
- 为什么重构
- 如何拆分模块
- 向后兼容策略
- 测试和验证
- 经验和教训

#### 3. 核心代码分享

**可以分享**：
- `backend/utils/ai/ai_service.py`（AI 核心逻辑）
- `backend/utils/__init__.py`（模块化导出）
- `web/src/components/ai/TripGeneratorSimple.vue`（前端组件）

---

### 从 Ralendar 学习的内容

#### 1. 节假日数据管理

**学习点**：
- 如何定期同步数据
- Django 命令的使用
- 定时任务的配置

#### 2. 管理后台优化

**学习点**：
- Django Admin 定制
- 可视化展示
- 批量操作

#### 3. API 设计规范

**学习点**：
- RESTful 设计
- 错误处理
- 文档规范

---

## 🎨 UI/UX 协作

### 节假日展示规范

#### 颜色体系（采纳 Ralendar 建议）

```css
/* 法定假日 */
.holiday-major {
  color: #ff6b6b;
  background: #ffe0e0;
  border-color: #ff6b6b;
}

/* 调休工作日 */
.holiday-workday {
  color: #f39c12;
  background: #fff5e0;
  border-color: #f39c12;
}

/* 传统节日 */
.holiday-traditional {
  color: #ffd93d;
  background: #fffbe0;
  border-color: #ffd93d;
}
```

#### Emoji 统一

| 节日 | Emoji | 颜色 |
|------|-------|------|
| 元旦 | 🎊 | #ff6b6b |
| 春节 | 🧨 | #ff6b6b |
| 清明 | 🌿 | #4caf50 |
| 劳动节 | 💪 | #ff6b6b |
| 端午 | 🐉 | #4caf50 |
| 中秋 | 🥮 | #ffd93d |
| 国庆 | 🇨🇳 | #ff6b6b |

---

## 🔧 技术实现细节

### 1. 日期选择器集成

**文件**: `web/src/components/DatePicker.vue`（需要创建或修改现有）

```vue
<template>
  <div class="date-picker">
    <input 
      type="date" 
      v-model="selectedDate"
      @change="checkHoliday"
    />
    
    <!-- 节假日提示 -->
    <div v-if="holidayInfo" class="holiday-badge">
      {{ holidayInfo.emoji }} {{ holidayInfo.name }}
      <small>{{ holidayInfo.tip }}</small>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { checkHoliday } from '@/api/ralendar'

const selectedDate = ref('')
const holidayInfo = ref(null)

const checkHoliday = async () => {
  const info = await checkHoliday(selectedDate.value)
  if (info && info.is_holiday) {
    holidayInfo.value = {
      emoji: getHolidayEmoji(info.holiday_name),
      name: info.holiday_name,
      tip: info.holiday_type === 'major' ? '建议提前预订' : ''
    }
  } else {
    holidayInfo.value = null
  }
}
</script>
```

---

### 2. AI 生成时考虑节假日

**修改**: `backend/utils/ai/ai_service.py`

```python
def _build_user_prompt(self, user_prompt, preferences, user):
    """构建用户提示词"""
    
    # ... 现有代码 ...
    
    # 检查是否有节假日
    holiday_context = ""
    start_date = preferences.get('start_date')
    if start_date:
        from backend.utils.external.ralendar_holidays import RalendarHolidaysClient
        holiday_info = RalendarHolidaysClient.check_holiday(start_date)
        
        if holiday_info and holiday_info.get('is_holiday'):
            holiday_name = holiday_info.get('holiday_name')
            holiday_context = f"\n\n【节假日提示】\n出发日期是{holiday_name}，属于出行高峰期，建议：\n"
            holiday_context += "- 预算增加 20-30%\n"
            holiday_context += "- 提前 1 个月预订住宿\n"
            holiday_context += "- 避开热门景点高峰时段\n"
    
    prompt = f"""生成旅行计划：

需求：{user_prompt}
天数：{days}天 | 预算：{budget} | 风格：{style} | 日期：{start_date if start_date else '待定'}
{user_context}
{holiday_context}

要求：每天2-4个活动，包含交通和餐饮建议，返回完整 JSON。
"""
    return prompt
```

---

### 3. 详情页显示节假日

**修改**: `web/src/views/TripDetailView.vue`

```vue
<template>
  <!-- 旅行进度条 -->
  <TripProgress
    :start-date="trip.start_date"
    :end-date="trip.end_date"
  />
  
  <!-- 节假日提示 -->
  <div v-if="holidayInfo" class="card mb-3">
    <div class="card-body">
      <h5>📅 节假日提示</h5>
      <div class="alert alert-info">
        {{ holidayInfo.emoji }} 您的旅行包含 <strong>{{ holidayInfo.name }}</strong>
        <br>
        <small>{{ holidayInfo.tip }}</small>
      </div>
    </div>
  </div>
  
  <!-- 行程概览 -->
  <TripOverview>
    ...
  </TripOverview>
</template>

<script>
import { checkHoliday } from '@/api/ralendar'

const holidayInfo = ref(null)

const checkTripHolidays = async () => {
  if (trip.value.start_date) {
    const info = await checkHoliday(trip.value.start_date)
    if (info && info.is_holiday) {
      holidayInfo.value = {
        emoji: getHolidayEmoji(info.holiday_name),
        name: info.holiday_name,
        tip: '建议提前预订，避开高峰期'
      }
    }
  }
}
</script>
```

---

## 📝 文档计划

### 需要创建的文档

1. **AI_PROMPT_ENGINEERING.md** - AI Prompt 工程指南
2. **BACKEND_REFACTORING_GUIDE.md** - 后端重构经验
3. **RALENDAR_API_INTEGRATION.md** - Ralendar API 集成指南
4. **HOLIDAY_DISPLAY_GUIDE.md** - 节假日展示规范

### 需要更新的文档

1. **AI_ROADMAP.md** - 添加节假日集成
2. **API_DOCUMENTATION.md** - 添加公开统计 API
3. **DEPLOYMENT_GUIDE.md** - 添加 Ralendar 依赖说明

---

## 🤝 沟通机制

### 日常沟通

**渠道**：
- GitHub Issues（技术问题）
- 文档交流（详细方案）
- 即时通讯（快速响应）

**响应时间**：
- 紧急问题：2 小时内
- 一般问题：24 小时内
- 功能需求：48 小时内评估

### 技术评审

**频率**: 每两周一次（可选）  
**形式**: 线上会议或文档交流  
**内容**:
- API 变更通知
- 新功能演示
- 问题讨论
- 经验分享

### 紧急联系

**场景**：
- API 故障
- 安全问题
- 数据异常
- 重大 Bug

**机制**：
- 建立紧急联系群
- 留备用联系方式
- 24/7 监控（如果可能）

---

## 💰 成本和收益

### 开发成本

**Roamio 侧**：
- 节假日 API 集成：2-3 天
- AI 优化（考虑节假日）：1-2 天
- 前端展示：1-2 天
- 测试和优化：1-2 天
- **总计**: 约 1 周

**Ralendar 侧**：
- 新 API 开发：2-3 天
- 文档编写：1 天
- 测试和优化：1 天
- **总计**: 约 1 周

### 预期收益

**用户体验**：
- ✅ 更智能的日期建议
- ✅ 避开高峰期提示
- ✅ 预算更准确
- ✅ 行程更合理

**产品价值**：
- ✅ 差异化功能
- ✅ 用户粘性提升
- ✅ 口碑传播
- ✅ 商业化基础

**技术提升**：
- ✅ API 集成经验
- ✅ 跨应用协作
- ✅ 数据驱动决策
- ✅ AI 能力增强

---

## 🎯 成功指标

### 短期指标（1 个月）

- ✅ 节假日 API 成功集成
- ✅ 日期选择器显示节假日
- ✅ AI 生成考虑节假日
- ✅ 用户反馈正面

### 中期指标（3 个月）

- ✅ 联合推荐功能上线
- ✅ 数据互通实现
- ✅ 用户使用率 > 30%
- ✅ 用户满意度 > 80%

### 长期指标（6 个月）

- ✅ 生态初步建立
- ✅ 商业化探索
- ✅ 用户增长 > 50%
- ✅ 合作深化

---

## 📞 行动检查清单

### 本周必做

- [ ] 创建 Ralendar API 客户端
- [ ] 实现节假日查询功能
- [ ] 前端日期选择器集成
- [ ] AI Prompt 优化
- [ ] 测试 Ralendar 新 API
- [ ] 准备 AI 经验分享文档
- [ ] 与 Ralendar 确认 API 细节

### 本月必做

- [ ] 联合推荐功能实现
- [ ] 数据互通 API 设计
- [ ] 黄历功能评估
- [ ] 用户调研
- [ ] 性能优化
- [ ] 文档完善

---

## 🎊 合作原则

### 技术层面
- ✅ 保持独立性（各自部署）
- ✅ API 通信（松耦合）
- ✅ 降级处理（容错性）
- ✅ 文档清晰（易维护）

### 产品层面
- ✅ 用户至上（体验第一）
- ✅ 互相增强（双赢）
- ✅ 差异化定位（不竞争）
- ✅ 共同成长（长期合作）

### 合作层面
- ✅ 开放沟通（坦诚相待）
- ✅ 快速响应（积极配合）
- ✅ 互相学习（共同进步）
- ✅ 稳步推进（不急不躁）

---

## 📚 相关文档

- [AI 集成里程碑](./AI_INTEGRATION_MILESTONE.md)
- [回复 Ralendar 团队](./REPLY_TO_RALENDAR_20251110.md)
- [AI 技术方案](./AI_TRIP_PLANNER.md)
- [AI Phase 2 计划](./AI_PHASE2_RAG_PLAN.md)
- [后端架构重构](./REFACTOR_COMPLETE_SUMMARY.md)

---

## 🎯 下一步行动

1. **立即**: 回复 Ralendar 团队，确认合作意向
2. **今天**: 开始准备 AI 经验分享文档
3. **明天**: 开始实现 Ralendar API 客户端
4. **本周**: 完成节假日功能集成
5. **本月**: 实现联合推荐功能

---

**让我们一起打造智能生活助手生态！** 🚀✨

---

*文档版本: 1.0*  
*最后更新: 2025-11-10*  
*负责人: Roamio 技术团队*

