# 📅 Ralendar × Roamio 融合计划

> **版本**: v1.0.0  
> **更新日期**: 2025-11-07  
> **状态**: 等待 QQ 授权通过后启动

---

## 🎯 融合目标

将 Ralendar（日历助手）与 Roamio（旅行平台）深度融合，实现：

1. ✅ **数据互通** - 旅行计划自动同步到日历
2. ✅ **功能联动** - 日历提醒推动旅行准备
3. ✅ **用户体验** - 一个账号，无缝切换
4. ✅ **技术复用** - 统一后端 API，降低成本

---

## 🏗️ 技术架构

### 当前状态

```
┌─────────────────┐          ┌─────────────────┐
│   Roamio Web    │          │  Ralendar App   │
│   (Vue 3 SPA)   │          │  (Kotlin/Java)  │
└────────┬────────┘          └────────┬────────┘
         │                            │
         │  JWT Token                 │  JWT Token
         │                            │
┌────────▼────────┐          ┌────────▼────────┐
│  Roamio Backend │          │ Ralendar Backend│
│   (Django API)  │          │   (Django API)  │
└────────┬────────┘          └────────┬────────┘
         │                            │
┌────────▼────────┐          ┌────────▼────────┐
│  Roamio DB      │          │  Ralendar DB    │
│   (SQLite)      │          │   (SQLite)      │
└─────────────────┘          └─────────────────┘
```

### 融合后架构

```
┌─────────────────┐          ┌─────────────────┐
│   Roamio Web    │          │  Ralendar App   │
│   (Vue 3 SPA)   │          │  (Kotlin/Java)  │
└────────┬────────┘          └────────┬────────┘
         │                            │
         │         JWT Token          │
         │  (统一认证)                │
         └────────┬───────────────────┘
                  │
         ┌────────▼────────┐
         │  Roamio Backend │  ⭐ 统一后端
         │   (Django API)  │
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │   Unified DB    │  ⭐ 统一数据库
         │  ┌──────────┐   │
         │  │ Roamio   │   │
         │  │ Ralendar │   │
         │  └──────────┘   │
         └─────────────────┘
```

---

## 📊 数据库设计

### Ralendar 核心模型

```python
# backend/models/calendar.py

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Calendar(models.Model):
    """日历（用户可以有多个日历）"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calendars')
    name = models.CharField(max_length=100, help_text='日历名称')
    color = models.CharField(max_length=7, default='#3788d8', help_text='日历颜色')
    is_default = models.BooleanField(default=False, help_text='是否默认日历')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'backend_calendar'
        verbose_name = '日历'
        verbose_name_plural = '日历'
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"


class Event(models.Model):
    """日程事件"""
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200, help_text='事件标题')
    description = models.TextField(blank=True, help_text='事件描述')
    start_time = models.DateTimeField(help_text='开始时间')
    end_time = models.DateTimeField(help_text='结束时间')
    all_day = models.BooleanField(default=False, help_text='是否全天事件')
    location = models.CharField(max_length=200, blank=True, help_text='地点')
    
    # ⭐ 关联到 Roamio 的旅行计划（可选）
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')
    
    # 提醒设置
    reminder_minutes = models.IntegerField(default=0, help_text='提前提醒分钟数')
    
    # 状态
    STATUS_CHOICES = [
        ('pending', '待进行'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'backend_event'
        verbose_name = '事件'
        verbose_name_plural = '事件'
        ordering = ['start_time']
    
    def __str__(self):
        return f"{self.title} ({self.start_time.date()})"


class Subscription(models.Model):
    """订阅（如樱花季、假期提醒等）"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    name = models.CharField(max_length=100, help_text='订阅名称')
    
    CATEGORY_CHOICES = [
        ('travel', '旅行'),
        ('holiday', '节日'),
        ('weather', '天气'),
        ('custom', '自定义'),
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, help_text='分类')
    
    is_active = models.BooleanField(default=True, help_text='是否启用')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'backend_subscription'
        verbose_name = '订阅'
        verbose_name_plural = '订阅'
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
```

---

## 🔌 API 设计

### 1. 旅行计划 → 日历同步

**接口**: `POST /api/v1/trips/{trip_id}/sync_to_calendar/`

**请求**:
```json
{
  "calendar_id": 1,  // 可选，不传则使用默认日历
  "create_reminders": true  // 是否创建提醒
}
```

**响应**:
```json
{
  "message": "同步成功",
  "events_created": 5,
  "events": [
    {
      "id": 1,
      "title": "准备出发：云南7日游",
      "start_time": "2025-11-28 00:00:00",
      "type": "preparation"
    },
    {
      "id": 2,
      "title": "云南7日游 - 第1天",
      "start_time": "2025-12-01 00:00:00",
      "type": "daily"
    }
  ]
}
```

**后端实现**:
```python
# backend/api/viewsets/trip_viewset.py

from rest_framework.decorators import action
from rest_framework.response import Response
from backend.models import Trip, Calendar, Event
from datetime import timedelta

class TripViewSet(viewsets.ModelViewSet):
    
    @action(detail=True, methods=['post'])
    def sync_to_calendar(self, request, pk=None):
        """将旅行计划同步到日历"""
        trip = self.get_object()
        calendar_id = request.data.get('calendar_id')
        create_reminders = request.data.get('create_reminders', True)
        
        # 获取或创建默认日历
        if calendar_id:
            calendar = Calendar.objects.get(id=calendar_id, user=request.user)
        else:
            calendar, _ = Calendar.objects.get_or_create(
                user=request.user,
                is_default=True,
                defaults={'name': '我的日历'}
            )
        
        events_created = []
        
        # 1. 创建出发前提醒（提前3天）
        if trip.start_date:
            prep_event = Event.objects.create(
                calendar=calendar,
                title=f"准备出发：{trip.title}",
                description="检查证件、打包行李、确认酒店",
                start_time=trip.start_date - timedelta(days=3),
                end_time=trip.start_date - timedelta(days=3, hours=-1),
                all_day=True,
                related_object=trip,
                reminder_minutes=1440 if create_reminders else 0  # 提前1天提醒
            )
            events_created.append(prep_event)
        
        # 2. 创建每日行程
        if trip.start_date and trip.end_date:
            current_date = trip.start_date
            day_number = 1
            while current_date <= trip.end_date:
                daily_event = Event.objects.create(
                    calendar=calendar,
                    title=f"{trip.title} - 第{day_number}天",
                    description=trip.description,
                    start_time=current_date,
                    end_time=current_date + timedelta(hours=23, minutes=59),
                    all_day=True,
                    related_object=trip,
                    reminder_minutes=480 if create_reminders else 0  # 提前8小时提醒
                )
                events_created.append(daily_event)
                current_date += timedelta(days=1)
                day_number += 1
        
        # 3. 创建回来后整理提醒（结束后1天）
        if trip.end_date:
            review_event = Event.objects.create(
                calendar=calendar,
                title=f"整理回忆：{trip.title}",
                description="整理照片、写游记、分享体验",
                start_time=trip.end_date + timedelta(days=1),
                end_time=trip.end_date + timedelta(days=1, hours=1),
                all_day=True,
                related_object=trip,
                reminder_minutes=480 if create_reminders else 0
            )
            events_created.append(review_event)
        
        return Response({
            'message': '同步成功',
            'events_created': len(events_created),
            'events': [
                {
                    'id': e.id,
                    'title': e.title,
                    'start_time': e.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'type': 'preparation' if '准备' in e.title else 'daily' if '第' in e.title else 'review'
                }
                for e in events_created
            ]
        })
```

### 2. 日历事件查询

**接口**: `GET /api/v1/ralendar/events/`

**查询参数**:
- `calendar_id`: 日历ID（可选）
- `start_date`: 开始日期
- `end_date`: 结束日期
- `status`: 状态（pending/in_progress/completed/cancelled）

**响应**:
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "title": "云南7日游 - 第1天",
      "start_time": "2025-12-01 00:00:00",
      "end_time": "2025-12-01 23:59:00",
      "all_day": true,
      "status": "pending",
      "related_trip": {
        "id": 1,
        "title": "云南7日游",
        "slug": "yunnan-7-days"
      }
    }
  ]
}
```

---

## 🔗 功能联动场景

### 场景 1：旅行计划 → 日历提醒

**用户操作**:
1. 在 Roamio 创建"云南7日游"（12月1日-7日）
2. 点击"同步到日历"

**系统行为**:
1. ✅ 在 Ralendar 创建出发前提醒（11月28日）
2. ✅ 创建每日行程（12月1日-7日）
3. ✅ 创建回来后整理提醒（12月8日）
4. ✅ 设置智能提醒（提前1天/8小时）

### 场景 2：日历订阅 → 旅行灵感

**用户操作**:
1. 在 Ralendar 订阅"樱花季提醒"

**系统行为**:
1. ✅ 3月初推送通知："日本樱花季即将到来"
2. ✅ Roamio 推送相关攻略："京都赏樱最佳路线"
3. ✅ 一键创建旅行计划

### 场景 3：打卡记录 → 时间轴

**用户操作**:
1. 在 Roamio 打卡"长城"

**系统行为**:
1. ✅ Ralendar 自动标记：2025-11-07 游览长城
2. ✅ 生成时间轴视图
3. ✅ 关联照片和评论

---

## 🚀 实施步骤

### Phase 1: 基础准备（当前）
- ✅ 制定 API 规范（`docs/api/API_STANDARDS.md`）
- ✅ 设计数据库模型
- ✅ 创建融合计划文档

### Phase 2: 独立开发（等待 QQ 授权）
- [ ] Ralendar 独立项目开发
- [ ] 实现基础 CRUD API
- [ ] Android 客户端开发

### Phase 3: 后端融合（QQ 授权通过后）
- [ ] 将 Ralendar 模型迁移到 Roamio 后端
- [ ] 实现旅行计划同步 API
- [ ] 统一 JWT 认证

### Phase 4: 功能联动
- [ ] 实现日历订阅功能
- [ ] 实现打卡时间轴
- [ ] 实现智能提醒

### Phase 5: 前端集成
- [ ] Roamio Web 新增"日历"入口
- [ ] Ralendar App 新增"旅行"入口
- [ ] 统一 UI 风格

---

## ✅ 检查清单

融合前确认：

- [ ] Ralendar 独立项目完成基础功能
- [ ] QQ 授权通过，可以进行融合
- [ ] 数据库模型设计完成
- [ ] API 接口设计完成
- [ ] 统一认证方案确定
- [ ] 数据迁移方案确定

融合后验证：

- [ ] 用户可以使用同一账号登录两个平台
- [ ] 旅行计划可以同步到日历
- [ ] 日历提醒正常工作
- [ ] 数据互通无误
- [ ] 性能测试通过

---

## 📞 联系方式

- **邮箱**: 2064747320@qq.com
- **项目地址**: https://github.com/ppshuX/roamio

---

**Roamio × Ralendar - 从计划到执行，完整的旅行体验！** 🌍📅✨

**最后更新**: 2025-11-07  
**维护者**: Roamio Team

