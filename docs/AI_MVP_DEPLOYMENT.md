# 🚀 AI 旅行规划助手 MVP - 快速部署指南

## ✅ 已完成的工作

### 后端代码 (Python/Django)
- ✅ `trips/utils/ai_service.py` - AI 服务核心（380行）
- ✅ `trips/api/viewsets/ai_viewset.py` - API 端点（213行）
- ✅ `trips/serializers/ai_serializer.py` - 数据验证
- ✅ `backend/api/urls.py` - 路由配置

### 前端代码 (Vue 3)
- ✅ `web/src/api/ai.js` - API 调用封装
- ✅ `web/src/components/ai/TripGenerator.vue` - 主组件（完整UI）

### API 端点
```
POST /api/v1/ai/generate-trip/    # 生成行程
POST /api/v1/ai/refine-trip/      # 优化行程
GET  /api/v1/ai/usage-stats/      # 使用统计
```

---

## 📋 部署步骤

### Step 1: 安装依赖（服务器端）

```bash
# SSH 登录到服务器
ssh user@your-server

# 进入项目目录
cd ~/roamio

# 安装 requests（如果还没有）
pip3 install requests

# 或者添加到 requirements.txt
echo "requests>=2.28.0" >> requirements.txt
pip3 install -r requirements.txt
```

### Step 2: 配置环境变量

```bash
# 编辑 .env 文件
vim ~/roamio/.env

# 添加以下配置（如果还没有）
AI_GENERATION_ENABLED=True
QWEN_API_KEY=你的API_KEY
QWEN_MODEL=qwen-plus
AI_RATE_LIMIT_FREE=5
AI_RATE_LIMIT_VIP=999
AI_MAX_TOKENS=4000
AI_TEMPERATURE=0.7
```

### Step 3: 测试后端 API

```bash
# 进入 Django shell
cd ~/roamio
python3 manage.py shell

# 测试 AI 服务
from trips.utils.ai_service import TripPlannerAI

ai = TripPlannerAI()
result = ai.generate_trip_plan(
    user_prompt="推荐北京3日游",
    preferences={'days': 3, 'budget_level': 'medium'}
)

print(result['trip_title'])
# 应该输出类似："北京3日文化之旅"

exit()
```

### Step 4: 重启后端服务

```bash
# 重启 uWSGI
sudo systemctl restart uwsgi
# 或
uwsgi --reload /tmp/uwsgi.pid

# 检查日志
tail -f /var/log/uwsgi/roamio.log
```

### Step 5: 前端集成

前端组件已经创建好了，你可以在任何页面中使用：

```vue
<template>
  <div>
    <TripGenerator @apply="handleApply" />
  </div>
</template>

<script setup>
import TripGenerator from '@/components/ai/TripGenerator.vue'

const handleApply = (tripPlan) => {
  console.log('应用行程:', tripPlan)
  // 将 tripPlan 数据填入你的表单
}
</script>
```

### Step 6: 构建前端

```bash
# 本地构建
cd web
npm run build

# 或者在服务器上构建
cd ~/roamio/web
npm run build
```

---

## 🧪 测试

### 1. 测试后端 API

```bash
# 获取 Token（先登录）
TOKEN="你的JWT_TOKEN"

# 测试生成行程
curl -X POST https://roamio.cn/api/v1/ai/generate-trip/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "我想去云南旅游5天，主要去大理和丽江",
    "preferences": {
      "days": 5,
      "budget_level": "medium",
      "travel_style": "leisure"
    }
  }'

# 测试使用统计
curl -X GET https://roamio.cn/api/v1/ai/usage-stats/ \
  -H "Authorization: Bearer $TOKEN"
```

### 2. 测试前端

1. 访问你的网站
2. 登录账号
3. 找到创建行程页面
4. 点击 "AI 智能生成" 按钮
5. 输入旅行描述
6. 点击生成
7. 查看结果

---

## 📊 功能验证清单

### 后端
- [ ] AI 服务初始化成功
- [ ] API 端点可访问
- [ ] 频率限制生效（5次/天）
- [ ] 生成结果格式正确
- [ ] 错误处理正常

### 前端
- [ ] 组件正常渲染
- [ ] 输入验证生效
- [ ] 加载动画显示
- [ ] 生成结果正确展示
- [ ] 应用功能正常

### 集成
- [ ] Token 认证正常
- [ ] CORS 配置正确
- [ ] 响应时间 < 10秒
- [ ] 错误提示友好

---

## 🎯 使用说明

### 用户流程

1. **输入描述**
   ```
   我想去云南旅游5天，主要去大理和丽江，
   喜欢古城和自然风光，预算中等
   ```

2. **设置偏好**（可选）
   - 天数：5天
   - 预算：中等
   - 风格：休闲放松
   - 日期：2025-12-01

3. **点击生成**
   - 等待 3-5 秒
   - AI 生成完整行程

4. **查看结果**
   - 行程标题和概述
   - 每日详细活动
   - 预算明细
   - 旅行建议

5. **应用到行程**
   - 点击"应用到行程"
   - 数据自动填入表单
   - 可继续编辑

---

## 💰 成本监控

### 查看 API 使用情况

1. 访问：https://bailian.console.aliyun.com/
2. 进入"密钥管理"
3. 查看调用统计

### 预期成本

```
单次生成：~3500 tokens ≈ ¥0.006
月度 1000 次：¥6
免费额度：100万 tokens/月（约 285 次）
```

---

## 🐛 故障排查

### 问题 1: 后端报错 "AI 服务未启用"

**原因**: 环境变量未配置

**解决**:
```bash
# 检查配置
cat ~/roamio/.env | grep AI

# 确保有以下配置
AI_GENERATION_ENABLED=True
QWEN_API_KEY=sk-...
```

### 问题 2: 前端报错 401 Unauthorized

**原因**: 未登录或 Token 过期

**解决**:
- 确保用户已登录
- 检查 Token 是否有效
- 重新登录

### 问题 3: 生成失败 "API 调用失败"

**原因**: API Key 无效或网络问题

**解决**:
```bash
# 测试 API 连接
python3 test_qwen_simple.py

# 检查网络
ping dashscope.aliyuncs.com
```

### 问题 4: 生成速度慢

**原因**: 网络延迟或模型负载

**解决**:
- 正常响应时间：3-5秒
- 如果超过 10秒，检查网络
- 考虑降级到 qwen-turbo

---

## 📈 后续优化

### Phase 2: RAG 增强（未来）

当前 MVP 使用纯 AI 生成，未来可以：

1. **爬取真实攻略**
   - 小红书、马蜂窝、知乎
   - 构建私域知识库

2. **实现 RAG 检索**
   - 向量化存储
   - 语义检索
   - 融合生成

3. **提升内容质量**
   - 更真实的景点推荐
   - 更准确的预算估算
   - 更实用的旅行建议

详见：`docs/AI_TRIP_PLANNER.md` Phase 2 部分

---

## ✅ 部署完成标志

当以下条件全部满足时，部署完成：

- [x] 后端代码已创建
- [x] 前端代码已创建
- [ ] 环境变量已配置
- [ ] 服务已重启
- [ ] API 测试通过
- [ ] 前端测试通过
- [ ] 用户可以正常使用

---

## 🎉 恭喜！

AI 旅行规划助手 MVP 已经准备就绪！

**下一步**：
1. 部署到服务器
2. 测试功能
3. 收集用户反馈
4. 迭代优化

**需要帮助？**
- 查看完整文档：`docs/AI_TRIP_PLANNER.md`
- 查看安全指南：`docs/SECURITY_CHECKLIST.md`

---

*最后更新: 2025-11-10*  
*维护者: Roamio 开发团队*

