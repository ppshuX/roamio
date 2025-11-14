# 💰 Roamio 付费功能详细方案

> **版本**: v2.0（基于用户需求定制）  
> **日期**: 2025-11-14  
> **状态**: 📋 规划中

---

## 🎯 用户方案分析

### 方案概述

**普通用户（Free）**
- ✅ 第一个旅行：免费
- 💰 第二个旅行开始：¥0.2/次 创建新旅行
- 🤖 AI 生成：2次/天

**VIP 用户**
- 🎁 每周获得免费创建旅行的次数（待确认）
- 🤖 AI 生成：5次/天

**SVIP 用户**
- ✅ 2次旅行/天（相当于无限创建）
- 🤖 AI 无限制

---

## ✅ 方案优点

1. **低门槛**：第一个旅行免费，降低用户使用门槛 ✅
2. **按需付费**：不需要订阅，按使用次数付费，灵活性高 ✅
3. **分层清晰**：普通/VIP/SVIP 三个层级，价值递进 ✅
4. **价值明确**：创建旅行是核心功能，收费合理 ✅

---

## ⚠️ 需要注意的问题

### 1. 定价策略（学习项目友好版）

**原则**：
- 既然是学习项目，价格可以非常友好
- 重点是体验商业模式和技术实现
- 可以先用低价，未来有用户再调整

**最终定价**：
- **普通用户**：¥0.1/次（超低门槛）
- **VIP**：¥1.9/月（几乎免费，方便测试）
- **SVIP**：¥4.9/月（仍然很低）

### 2. VIP/SVIP 价格（学习友好版）

**最终定价**：
- **VIP**：¥1.9/月（学习价，方便测试会员功能）
- **SVIP**：¥4.9/月（仍然很低，但体现价值差异）

**说明**：
- 既然是学习项目，价格可以非常低
- 重点是体验完整的付费流程
- 如果未来有真实用户，可以随时调整

### 3. VIP 每周免费次数（友好版）

**最终方案**：
- **VIP**：每周 5 次免费创建（更友好，方便测试）
- **SVIP**：3次/天（相当于每周 21 次，基本无限）

**说明**：
- 既然是学习项目，可以更宽松一些
- 方便测试各种场景

### 4. 支付频率问题

**问题**：
- 如果每次创建都需要支付，可能影响用户体验
- 可以考虑：次数包 + 会员制 结合

**建议**：
- 普通用户：按次付费（¥0.5/次）或购买次数包
- VIP/SVIP：会员制，免去单次支付

---

## 💡 优化建议方案

### 方案一：按次付费 + 会员制（推荐）

#### 普通用户（Free）
- ✅ 第一个旅行：免费
- 💰 第二个旅行开始：¥0.1/次（超低门槛，学习友好）
- 🤖 AI 生成：2次/天

#### VIP 用户 - ¥1.9/月（学习价）
- 🎁 每周 5 次免费创建旅行（更友好）
- 💰 超出部分：¥0.05/次（比普通用户便宜一半）
- 🤖 AI 生成：5次/天
- ✨ 其他特权：
  - 高级模板
  - 专属徽章
  - 数据分析报告

#### SVIP 用户 - ¥4.9/月（学习价）
- ✅ 3次旅行/天（相当于每月 90 次，基本无限）
- 🤖 AI 无限制
- ✨ 所有 VIP 特权 +
  - 优先客服支持
  - 导出 PDF/Word
  - 更多自定义选项

**定价说明**：
- 这是学习项目，价格非常友好
- 重点在体验商业模式和技术实现
- 未来有用户时，可以随时调整价格

---

### 方案二：纯会员制（简化版）

#### 普通用户（Free）
- ✅ 第一个旅行：免费
- 💰 第二个旅行开始：¥0.1/次（按次付费，超低门槛）
- 🤖 AI 生成：2次/天

#### VIP 用户 - ¥1.9/月
- ✅ 无限创建旅行
- 🤖 AI 生成：5次/天
- ✨ 基础特权

#### SVIP 用户 - ¥4.9/月
- ✅ 无限创建旅行
- 🤖 AI 无限制
- ✨ 所有特权

**说明**：这是学习项目，价格可以非常低，重点是体验完整流程。

---

## 🏗️ 技术实现方案

### 数据模型设计

```python
# backend/models/subscription.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

class Subscription(models.Model):
    """会员订阅模型"""
    
    SUBSCRIPTION_TYPE_CHOICES = [
        ('free', '普通用户'),
        ('vip', 'VIP 用户'),
        ('svip', 'SVIP 用户'),
    ]
    
    STATUS_CHOICES = [
        ('active', '活跃'),
        ('expired', '已过期'),
        ('cancelled', '已取消'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='subscription'
    )
    
    subscription_type = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_TYPE_CHOICES,
        default='free',
        verbose_name='会员类型'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='状态'
    )
    
    started_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='开始时间'
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='到期时间'
    )
    
    # 旅行创建相关
    trips_count = models.IntegerField(
        default=0,
        verbose_name='已创建旅行数量'
    )
    
    trips_created_today = models.IntegerField(
        default=0,
        verbose_name='今日已创建旅行数量'
    )
    
    trips_reset_date = models.DateField(
        default=timezone.now,
        verbose_name='上次重置日期（用于每日/每周限制）'
    )
    
    # VIP 每周免费次数
    weekly_free_trips_remaining = models.IntegerField(
        default=0,
        verbose_name='本周剩余免费旅行次数'
    )
    
    weekly_reset_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='上次周重置日期'
    )
    
    # AI 相关
    ai_remaining = models.IntegerField(
        default=2,  # 默认 2次/天
        verbose_name='剩余 AI 次数'
    )
    
    ai_total = models.IntegerField(
        default=2,  # 默认 2次/天
        verbose_name='总 AI 次数（每日重置）'
    )
    
    last_ai_reset_date = models.DateField(
        default=timezone.now,
        verbose_name='上次 AI 重置日期'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        verbose_name = '会员订阅'
        verbose_name_plural = '会员订阅'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_subscription_type_display()}"
    
    @property
    def is_vip(self):
        """是否 VIP"""
        return self.subscription_type == 'vip'
    
    @property
    def is_svip(self):
        """是否 SVIP"""
        return self.subscription_type == 'svip'
    
    @property
    def is_premium(self):
        """是否会员（VIP 或 SVIP）"""
        return self.subscription_type in ['vip', 'svip']
    
    @property
    def is_active(self):
        """是否有效"""
        if self.status != 'active':
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True
    
    def can_create_trip(self):
        """是否可以创建旅行"""
        # 第一个旅行免费
        if self.trips_count == 0:
            return True, 'free'
        
        # SVIP：2次/天
        if self.is_svip:
            self._reset_daily_trips_if_needed()
            if self.trips_created_today < 2:
                return True, 'free'
            return False, 'daily_limit'
        
        # VIP：每周 3 次免费
        if self.is_vip:
            self._reset_weekly_trips_if_needed()
            if self.weekly_free_trips_remaining > 0:
                return True, 'free'
            # VIP 超出后需要付费
            return True, 'paid'
        
        # 普通用户：需要付费
        return True, 'paid'
    
    def can_use_ai(self):
        """是否可以使用 AI"""
        self._reset_daily_ai_if_needed()
        
        # SVIP：无限制
        if self.is_svip:
            return True
        
        # VIP：5次/天
        if self.is_vip:
            self.ai_total = 5
            if self.ai_remaining < self.ai_total:
                self.ai_remaining = self.ai_total
            return self.ai_remaining > 0
        
        # 普通用户：2次/天
        return self.ai_remaining > 0
    
    def consume_ai_usage(self):
        """消费 AI 使用次数"""
        if not self.can_use_ai():
            return False
        if not self.is_svip:
            self.ai_remaining -= 1
            self.save()
        return True
    
    def consume_trip_creation(self):
        """消费旅行创建次数"""
        can_create, cost_type = self.can_create_trip()
        if not can_create:
            return False, cost_type
        
        # 第一个旅行免费
        if self.trips_count == 0:
            self.trips_count += 1
            self.save()
            return True, 'free'
        
        # SVIP：每日限制
        if self.is_svip:
            self.trips_created_today += 1
            self.trips_count += 1
            self.save()
            return True, 'free'
        
        # VIP：每周免费次数
        if self.is_vip and self.weekly_free_trips_remaining > 0:
            self.weekly_free_trips_remaining -= 1
            self.trips_count += 1
            self.save()
            return True, 'free'
        
        # 需要付费
        return True, 'paid'
    
    def _reset_daily_trips_if_needed(self):
        """重置每日旅行创建次数（SVIP）"""
        if self.is_svip:
            today = timezone.now().date()
            if self.trips_reset_date < today:
                self.trips_created_today = 0
                self.trips_reset_date = today
                self.save()
    
    def _reset_weekly_trips_if_needed(self):
        """重置每周免费旅行次数（VIP）"""
        if self.is_vip:
            today = timezone.now().date()
            # 计算本周一
            days_since_monday = today.weekday()
            this_monday = today - timedelta(days=days_since_monday)
            
            if not self.weekly_reset_date or self.weekly_reset_date < this_monday:
                self.weekly_free_trips_remaining = 3  # VIP 每周 3 次
                self.weekly_reset_date = this_monday
                self.save()
    
    def _reset_daily_ai_if_needed(self):
        """重置每日 AI 次数"""
        today = timezone.now().date()
        if self.last_ai_reset_date < today:
            if self.is_svip:
                # SVIP 无限制，不需要重置
                pass
            elif self.is_vip:
                self.ai_total = 5
                self.ai_remaining = 5
            else:
                self.ai_total = 2
                self.ai_remaining = 2
            self.last_ai_reset_date = today
            self.save()


class TripCreationOrder(models.Model):
    """旅行创建订单模型（按次付费）"""
    
    ORDER_STATUS_CHOICES = [
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('failed', '支付失败'),
        ('refunded', '已退款'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('wechat', '微信支付'),
        ('alipay', '支付宝'),
    ]
    
    order_id = models.CharField(
        max_length=64,
        unique=True,
        verbose_name='订单号'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='trip_creation_orders',
        verbose_name='用户'
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='金额'
    )
    
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='支付方式'
    )
    
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending',
        verbose_name='订单状态'
    )
    
    third_party_order_id = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name='第三方订单号'
    )
    
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='支付时间'
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='订单过期时间'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        verbose_name = '旅行创建订单'
        verbose_name_plural = '旅行创建订单'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order_id} - {self.user.username} - ¥{self.amount}"
```

---

## 📋 实施计划

### Phase 1: 核心功能（1-2周）

1. ✅ 创建 Subscription 模型
2. ✅ 创建 TripCreationOrder 模型
3. ✅ 实现权限检查逻辑
4. ✅ 修改 Trip 创建接口，添加付费检查
5. ✅ 修改 AI 接口，添加次数限制
6. ✅ 集成支付 SDK（微信/支付宝）

### Phase 2: 前端展示（1周）

1. ✅ 会员状态组件
2. ✅ 创建旅行时的付费提示
3. ✅ AI 使用次数显示
4. ✅ 订阅页面
5. ✅ 支付流程

---

## 💰 价格建议（学习项目友好版）

> **定位**：这是学习项目，重点是体验商业模式和实现技术，定价以友好和实用为主。

### 最终方案（推荐）

| 项目 | 普通用户 | VIP | SVIP |
|------|---------|-----|------|
| **创建旅行** | 第1个免费，之后¥0.1/次 | 每周5次免费，超出¥0.05/次 | 3次/天（基本无限） |
| **AI 生成** | 2次/天 | 5次/天 | 无限制 |
| **价格** | 免费 | ¥1.9/月（学习价） | ¥4.9/月（学习价） |

### 为什么这样定价？

1. **学习友好**：
   - ¥0.1/次：超低门槛，用户可以轻松体验
   - ¥1.9/月 VIP：几乎免费，方便测试会员功能
   - ¥4.9/月 SVIP：仍然很低，但体现了价值差异

2. **技术实现**：
   - 重点在实现付费流程、权限控制等技术
   - 低价格不影响学习效果

3. **未来调整**：
   - 如果后续有真实用户，可以随时调整价格
   - 现在先用低价格验证整个流程

### 支付方式选择：Ping++ 聚合支付 ✅

**选择 Ping++ 的原因**：
- ✅ **个人开发者友好**：不需要企业认证，个人开发者可用
- ✅ **聚合支付**：统一接口，同时支持微信和支付宝
- ✅ **简单易用**：快速集成，文档完善
- ✅ **测试方便**：可以用 1 分钱测试完整流程

**集成步骤**：
1. 注册 Ping++ 账号（https://www.pingxx.com）
2. 在控制台勾选微信和支付宝支付渠道
3. 上传身份证和银行卡进行认证（个人开发者可用）
4. 获取 API Key（测试环境和生产环境）
5. 后端集成 Ping++ SDK
6. 前端调用支付接口

**支付流程**：
```
用户点击支付 → 后端创建 Ping++ 订单 → 返回支付 URL/二维码
→ 用户扫码/跳转支付 → Ping++ 回调 → 更新订单状态 → 完成
```

**同时提供模拟支付**：
- 开发环境：提供"模拟支付"按钮，直接完成（方便测试）
- 生产环境：使用 Ping++ 真实支付

### 代码实现优先级

1. **核心逻辑**（最重要）：
   - ✅ 会员系统
   - ✅ 权限控制
   - ✅ 次数限制
   - ✅ 订单系统

2. **支付集成**（可简化）：
   - ✅ 先实现订单创建
   - ✅ 支付回调处理
   - 🔄 可以先模拟支付，后续接入真实支付

3. **前端展示**：
   - ✅ 会员状态
   - ✅ 付费提示
   - ✅ 支付流程

---

## 🎯 下一步

请确认：
1. 定价是否合适？
2. VIP/SVIP 功能是否满足需求？
3. 是否开始实现代码？

确认后我可以立即开始实现！🚀

