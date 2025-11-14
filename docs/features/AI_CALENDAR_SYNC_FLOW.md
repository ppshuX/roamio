# AI 行程生成 + Ralendar 同步流程

## 📋 完整流程概览

### 场景 1：选择日期范围（推荐）

```
1. 用户打开 AI 生成界面
   ↓
2. 用户填写旅行描述
   ↓
3. 用户选择"日期范围"
   ↓
4. 用户选择出发日期和返回日期
   ↓
5. 系统自动计算天数
   ↓
6. 用户点击"✨ AI 生成行程"
   ↓
7. 前端发送请求到后端：
   {
     prompt: "用户描述",
     preferences: {
       days: 5,  // 自动计算
       budget_level: "medium",
       date_range: {
         start_date: "2025-12-01",
         end_date: "2025-12-05"
       }
     }
   }
   ↓
8. 后端验证日期范围
   - 验证日期格式
   - 验证返回日期不早于出发日期
   - 验证天数在 1-30 天之间
   ↓
9. AI 服务生成行程
   - 使用日期范围信息生成提示词
   - AI 生成包含每天活动的行程
   - 后端自动填充每一天的日期
   ↓
10. 返回生成的行程给前端
    {
      trip_title: "行程标题",
      days_detail: [
        { date: "2025-12-01", activities: [...] },
        { date: "2025-12-02", activities: [...] },
        ...
      ],
      date_type: "range",
      date_range: {
        start_date: "2025-12-01",
        end_date: "2025-12-05"
      }
    }
    ↓
11. 用户点击"🗓️ 同步到日历"
    ↓
12. 前端检查日期：
    - 发现 date_type === 'range'
    - 发现 date_range.start_date 存在
    - ✅ 有有效日期
    ↓
13. 直接转换行程为日历事件
    - 使用 date_range.start_date 作为开始日期
    - 转换每一天的活动为日历事件
    - 包含：标题、描述、时间、地点、坐标、提醒
    ↓
14. 打开日历同步选择界面
    - 显示所有可同步的事件
    - 用户可以：
      - 全选/取消全选
      - 单独选择/取消选择
      - 编辑每个事件的详细信息
      - 查看地点坐标和地图
    ↓
15. 用户选择要同步的事件
    ↓
16. 用户点击"确认同步"
    ↓
17. 前端发送请求到后端：
    POST /api/v1/ralendar/trips/{slug}/sync-ai-trip/
    {
      events: [
        {
          title: "行程标题 - Day 1: 地点",
          description: "活动描述",
          start_time: "2025-12-01T09:00:00+08:00",
          end_time: "2025-12-01T11:00:00+08:00",
          location: "地点名称（详细地址）",
          location_name: "地点名称",
          location_address: "详细地址",
          location_type: "景点",
          latitude: 39.9163,
          longitude: 116.3972,
          reminder_minutes: 30,
          email_reminder: true
        },
        ...
      ]
    }
    ↓
18. 后端同步到 Ralendar
    - 验证用户身份
    - 获取用户的 QQ OpenID/UnionID
    - 批量创建事件到 Ralendar
    - 更新 Trip 模型的同步状态
    ↓
19. 返回同步结果
    {
      code: 200,
      message: "同步成功",
      data: {
        synced_count: 5,
        failed_count: 0,
        event_ids: [123, 124, 125, 126, 127],
        trip_slug: "trip-slug"
      }
    }
    ↓
20. 前端显示成功提示
    - "✅ 成功同步 5 个事件到 Ralendar"
    - 关闭选择界面
    ↓
21. 完成！用户在 Ralendar 中可以看到所有行程事件
```

### 场景 2：选择天数

```
1. 用户打开 AI 生成界面
   ↓
2. 用户填写旅行描述
   ↓
3. 用户选择"天数"
   ↓
4. 用户输入天数（如 5 天）
   ↓
5. 用户点击"✨ AI 生成行程"
   ↓
6. 前端发送请求到后端：
   {
     prompt: "用户描述",
     preferences: {
       days: 5,
       budget_level: "medium"
     }
   }
   ↓
7. 后端验证天数
   - 验证天数在 1-30 之间
   ↓
8. AI 服务生成行程
   - 使用天数信息生成提示词
   - AI 生成包含每天活动的行程
   - 没有具体日期（date 字段可能为占位符或空）
   ↓
9. 返回生成的行程给前端
    {
      trip_title: "行程标题",
      days_detail: [
        { date: "YYYY-MM-DD", activities: [...] },  // 占位符
        { date: "YYYY-MM-DD", activities: [...] },
        ...
      ],
      date_type: "days",
      days: 5
    }
    ↓
10. 用户点击"🗓️ 同步到日历"
    ↓
11. 前端检查日期：
    - 发现 date_type === 'days'
    - 没有 date_range
    - 检查 days_detail[0].date
    - 发现是占位符 "YYYY-MM-DD"
    - ❌ 没有有效日期
    ↓
12. 显示日期选择器
    - 关闭 AI 生成弹窗
    - 打开日期选择器
    - 显示行程预览（第1天、第2天...）
    ↓
13. 用户选择出发日期
    - 选择日期（如 2025-12-01）
    - 查看行程预览
    - 点击"确认"
    ↓
14. 前端更新 tripData
    - tripData.start_date = "2025-12-01"
    - tripData.end_date = "2025-12-05" (自动计算)
    ↓
15. 转换行程为日历事件
    - 使用用户选择的日期作为开始日期
    - 转换每一天的活动为日历事件
    ↓
16. 打开日历同步选择界面
    - 显示所有可同步的事件
    - 用户可以选择和编辑
    ↓
17. 用户选择要同步的事件
    ↓
18. 用户点击"确认同步"
    ↓
19. 后端同步到 Ralendar
    ↓
20. 返回同步结果
    ↓
21. 完成！
```

## 🔑 关键决策点

### 1. 日期选择方式
- **日期范围**：用户明确知道出发和返回日期
- **天数**：用户只知道旅行天数，日期待定

### 2. 日期验证逻辑
- 优先检查 `date_range.start_date`
- 其次检查 `tripData.start_date`
- 最后检查 `days_detail[0].date`
- 如果都没有，显示日期选择器

### 3. 日期填充时机
- **后端**：AI 生成后自动填充（如果有日期范围）
- **前端**：生成后再次填充（双重保险）
- **同步时**：如果没有日期，强制用户选择

## 📊 数据流转

### 前端 → 后端
```json
{
  "prompt": "用户描述",
  "preferences": {
    "days": 5,
    "budget_level": "medium",
    "date_range": {
      "start_date": "2025-12-01",
      "end_date": "2025-12-05"
    }
  }
}
```

### 后端 → 前端
```json
{
  "code": 200,
  "data": {
    "trip_plan": {
      "trip_title": "行程标题",
      "days": 5,
      "days_detail": [
        {
          "date": "2025-12-01",
          "title": "Day 1: 标题",
          "activities": [
            {
              "time": "09:00",
              "location": "地点名称",
              "address": "详细地址",
              "location_type": "景点",
              "coordinates": {
                "lat": 39.9163,
                "lng": 116.3972
              },
              "description": "活动描述",
              "duration": "2小时",
              "estimated_cost": 100,
              "tips": "实用提示"
            }
          ]
        }
      ],
      "date_type": "range",
      "date_range": {
        "start_date": "2025-12-01",
        "end_date": "2025-12-05"
      }
    }
  }
}
```

### 前端 → Ralendar API
```json
{
  "events": [
    {
      "title": "行程标题 - Day 1: 地点名称",
      "description": "活动描述\n\n💡 提示: 实用提示\n\n💰 预估费用: ¥100\n\n(来自 Roamio AI 生成的行程)",
      "start_time": "2025-12-01T09:00:00+08:00",
      "end_time": "2025-12-01T11:00:00+08:00",
      "location": "地点名称（详细地址）",
      "location_name": "地点名称",
      "location_address": "详细地址",
      "location_type": "景点",
      "latitude": 39.9163,
      "longitude": 116.3972,
      "reminder_minutes": 30,
      "email_reminder": true,
      "source_app": "roamio",
      "unionid": "用户 UnionID",
      "openid": "用户 OpenID"
    }
  ]
}
```

## 🎯 用户体验优化

### 1. 智能日期处理
- ✅ 日期范围：同步时无需再次选择日期
- ✅ 天数：同步时强制选择日期（确保数据完整）

### 2. 详细的日期信息
- ✅ 地点名称 + 详细地址
- ✅ 地理坐标（经纬度）
- ✅ 地点类型（景点/餐厅/住宿等）
- ✅ 地图查看功能

### 3. 灵活的事件管理
- ✅ 全选/取消全选
- ✅ 单独选择/取消选择
- ✅ 编辑事件详细信息
- ✅ 查看地点坐标和地图

### 4. 错误处理
- ✅ 详细的错误提示
- ✅ 诊断信息（帮助用户理解问题）
- ✅ 日志记录（便于调试）

## 🔄 状态流转

```
初始状态
  ↓
填写描述 + 选择日期方式
  ↓
生成中...
  ↓
生成成功
  ↓
[选择日期范围] → 有日期 → 直接转换 → 选择界面
[选择天数] → 无日期 → 日期选择器 → 转换 → 选择界面
  ↓
选择事件
  ↓
编辑事件（可选）
  ↓
确认同步
  ↓
同步中...
  ↓
同步成功
  ↓
完成！
```

## 📝 注意事项

1. **日期必填**：同步到 Ralendar 时，日期是必填的
2. **日期验证**：多重验证确保日期有效
3. **向后兼容**：仍支持单独的 `start_date` 字段
4. **错误恢复**：如果日期无效，自动使用今天作为默认值
5. **数据完整性**：确保每个事件都有完整的信息（时间、地点、坐标等）


