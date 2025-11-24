# 🚀 AI 旅行规划助手 - 快速部署清单

## ✅ 准备工作（已完成）

- [x] **通义千问 API Key 已获取**
  - API Key: `sk-****************************d34e` (已配置)
  - 描述: Roamio
  - 创建时间: 2025-11-09 21:42:50
  - 免费额度: 100万 tokens/月

- [x] **配置文件已更新**
  - 文件: `cloud_settings/env.example`
  - 已添加 AI 服务配置段

---

## 📋 部署步骤

### Step 1: 安装依赖包

```bash
# 进入项目目录
cd ~/roamio

# 安装 OpenAI SDK（通义千问兼容）
pip install openai

# 或者添加到 requirements.txt
echo "openai>=1.0.0" >> requirements.txt
pip install -r requirements.txt
```

### Step 2: 更新服务器 .env 配置

```bash
# 编辑服务器上的 .env 文件
vim ~/roamio/.env

# 添加以下配置（复制粘贴）
# ==================== AI 服务配置 ====================
QWEN_API_KEY=你的API_KEY  # 从阿里云百炼获取
QWEN_MODEL=qwen-plus
AI_GENERATION_ENABLED=True
AI_RATE_LIMIT_FREE=5
AI_RATE_LIMIT_VIP=999
AI_MAX_TOKENS=4000
AI_TEMPERATURE=0.7
```

### Step 3: 创建后端代码

#### 3.1 创建 AI 服务核心
```bash
# 创建文件
touch trips/utils/ai_service.py
```

**内容参考**: `docs/AI_TRIP_PLANNER.md` 第 4.1 节

#### 3.2 创建 API ViewSet
```bash
# 创建文件
touch trips/api/viewsets/ai_viewset.py
```

**内容参考**: `docs/AI_TRIP_PLANNER.md` 第 4.1 节

#### 3.3 创建序列化器
```bash
# 创建文件
touch trips/serializers/ai_serializer.py
```

**内容参考**: `docs/AI_TRIP_PLANNER.md` 第 4.1 节

#### 3.4 添加路由
编辑 `trips/urls/api_urls.py`，添加：
```python
from trips.api.viewsets.ai_viewset import AIAssistantViewSet

router.register(r'ai', AIAssistantViewSet, basename='ai')
```

### Step 4: 创建前端代码

#### 4.1 创建 AI 组件目录
```bash
mkdir -p web/src/components/ai
```

#### 4.2 创建主组件
```bash
touch web/src/components/ai/TripGenerator.vue
touch web/src/components/ai/GenerationProgress.vue
touch web/src/components/ai/TripPreview.vue
```

**内容参考**: `docs/AI_TRIP_PLANNER.md` 第 4.2 节

#### 4.3 创建 API 调用
```bash
touch web/src/api/ai.js
```

**内容参考**: `docs/AI_TRIP_PLANNER.md` 第 4.2 节

### Step 5: 测试 API 连接

创建测试脚本 `test_ai_api.py`：
```python
import os
from openai import OpenAI

# 设置 API Key
client = OpenAI(
    api_key="你的API_KEY",  # 从环境变量或配置文件读取
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 测试调用
try:
    response = client.chat.completions.create(
        model="qwen-plus",
        messages=[
            {"role": "system", "content": "你是一个旅行规划助手"},
            {"role": "user", "content": "推荐北京3日游"}
        ],
        temperature=0.7,
        max_tokens=500
    )
    
    print("✅ API 连接成功！")
    print(f"响应: {response.choices[0].message.content}")
    print(f"Token 消耗: {response.usage.total_tokens}")
    
except Exception as e:
    print(f"❌ API 连接失败: {e}")
```

运行测试：
```bash
python test_ai_api.py
```

### Step 6: 重启服务

```bash
# 重启 uWSGI
sudo systemctl restart uwsgi
# 或
uwsgi --reload /tmp/uwsgi.pid

# 重启前端（如果需要）
cd web
npm run build
```

### Step 7: 功能测试

#### 7.1 后端 API 测试
```bash
# 测试生成行程
curl -X POST https://roamio.cn/api/v1/ai/generate-trip/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
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
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 7.2 前端测试
1. 访问创建行程页面
2. 点击 "AI 智能生成" 按钮
3. 输入旅行描述
4. 查看生成结果
5. 测试应用到行程功能

---

## 🔍 验证清单

### 后端验证
- [ ] API Key 配置正确
- [ ] OpenAI SDK 安装成功
- [ ] AI ViewSet 路由注册
- [ ] 频率限制功能正常
- [ ] 日志记录正常

### 前端验证
- [ ] AI 组件正常渲染
- [ ] 输入验证生效
- [ ] 加载动画显示
- [ ] 生成结果正确展示
- [ ] 应用到行程功能正常

### 功能验证
- [ ] 生成成功率 > 95%
- [ ] 响应时间 < 5秒
- [ ] JSON 格式正确
- [ ] 内容质量符合预期
- [ ] 错误处理正常

---

## 🐛 常见问题排查

### 问题 1: API 连接失败
```
错误: Connection timeout / 401 Unauthorized
```

**解决方案**:
1. 检查 API Key 是否正确
2. 检查网络连接（服务器能否访问阿里云）
3. 检查 API Key 是否过期
4. 查看阿里云控制台是否有限制

### 问题 2: JSON 解析错误
```
错误: JSONDecodeError
```

**解决方案**:
1. 检查提示词是否正确
2. 确保使用 `response_format={"type": "json_object"}`
3. 增加输出 token 限制
4. 优化系统提示词

### 问题 3: 频率限制不生效
```
错误: Redis 连接失败
```

**解决方案**:
1. 检查 Redis 是否运行
2. 检查 Redis 配置
3. 测试 Redis 连接: `redis-cli ping`

### 问题 4: 生成内容质量差
**解决方案**:
1. 优化系统提示词
2. 调整 temperature 参数
3. 增加约束条件
4. 收集用户反馈持续改进

---

## 📊 监控指标

### 需要监控的数据
```python
# 在 Django Admin 或日志中查看
- 每日生成次数
- 成功率
- 平均响应时间
- Token 消耗量
- 错误类型分布
```

### 日志查看
```bash
# 查看 uWSGI 日志
tail -f /var/log/uwsgi/roamio.log | grep "AI generation"

# 查看 Django 日志
tail -f ~/roamio/logs/django.log | grep "ai_service"
```

---

## 💰 成本监控

### 查看 API 使用情况
1. 访问: https://bailian.console.aliyun.com/
2. 进入 "密钥管理"
3. 查看 API 调用统计
4. 监控免费额度使用情况

### 成本告警设置
- 当免费额度使用超过 80% 时告警
- 当单日调用超过 100 次时告警
- 当成本超过预算时告警

---

## 🎯 下一步优化

### 短期（1-2周）
- [ ] 收集用户反馈
- [ ] 优化提示词
- [ ] 增加更多示例
- [ ] 改进错误处理

### 中期（1个月）
- [ ] 实现"优化行程"功能
- [ ] 增加用户偏好学习
- [ ] 优化 UI/UX
- [ ] 增加数据分析

### 长期（3个月）
- [ ] 联网搜索功能
- [ ] 图片生成功能
- [ ] 语音输入
- [ ] 多语言支持

---

## 📞 技术支持

### 阿里云百炼
- 文档: https://help.aliyun.com/zh/dashscope/
- 控制台: https://bailian.console.aliyun.com/
- 工单: https://selfservice.console.aliyun.com/ticket/

### Roamio 团队
- 开发文档: `docs/AI_TRIP_PLANNER.md`
- 技术方案: 详见完整方案文档

---

## ✅ 完成标志

当以下条件全部满足时，部署完成：

- [x] API Key 配置正确
- [ ] 后端代码部署完成
- [ ] 前端代码部署完成
- [ ] 测试用例全部通过
- [ ] 生成功能正常工作
- [ ] 用户可以正常使用
- [ ] 监控和日志正常

---

*最后更新: 2025-11-09*  
*维护者: Roamio 开发团队*

