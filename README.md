# 🌍 Roamio - 智能旅行记录与分享平台

> **记录旅程，分享故事，让每一段体验都值得被铭记**

**从旅行开始，走向体验经济的未来** ✈️🌄✨

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2+-092E20.svg)](https://www.djangoproject.com/)
[![Vue](https://img.shields.io/badge/Vue-3.0+-4FC08D.svg)](https://vuejs.org/)

[在线演示](https://roamio.cn/) · [项目文档](docs/) · [问题反馈](https://github.com/ppshuX/roamio/issues)

---

## 🎯 项目简介

Roamio 是一个**真实部署在生产环境**的现代化旅行记录与分享平台，采用前后端分离架构。

**核心特色**：
- ✅ **AI 智能行程规划** - 通义千问大模型，自然语言生成完整行程
- ✅ **Ralendar 日历集成** - OAuth 2.0 授权，一键同步到日历
- ✅ **结构化旅程记录** - 策划 → 实时更新 → 回忆
- ✅ **丰富的社交互动** - 评论、图片、视频、点赞
- ✅ **性能优化实践** - 图片流量节省 95%
- ✅ **完整的技术栈** - Django 5.2 + Vue 3 + MySQL + Redis + 腾讯云

**未来愿景**：从旅行扩展到巡演、马拉松、学习等多种场景，最终成为一个跨场景的体验记录与分享平台，并探索场景化支付等创新功能。

详见：**[商业计划书](docs/BUSINESS_PLAN.md)**

---

## 📚 项目文档

> **完整文档索引**: [docs/README.md](docs/README.md)

### 🔌 API 文档
- **[生态系统 API 文档](docs/api/ECOSYSTEM_API_DOCUMENTATION.md)** - ⭐ 完整的 API 参考（Roamio + Ralendar，2185行）
- **[API 统一规范](docs/api/API_STANDARDS.md)** - Roamio 生态系统 API 标准
- **[Ralendar API 配置](docs/api/RALENDAR_API_CONFIG.md)** - 日历助手 API 配置指南
- **[在线 API 文档](https://roamio.cn/api/docs/)** - Swagger UI 交互式文档

### 🏗️ 架构设计
- **[架构分析报告](docs/architecture/ARCHITECTURE_ANALYSIS.md)** - 前后端分离架构详解
- **[项目评价报告](docs/architecture/PROJECT_EVALUATION.md)** - 技术、产品、商业价值评估

### 📖 开发指南
- **[腾讯云 COS 配置](docs/guides/TENCENT_COS_SETUP.md)** - 对象存储配置指南
- **[旅行分享功能](docs/guides/TRIP_SHARING_GUIDE.md)** - 分享功能使用说明
- **[AI 功能部署](docs/AI_MVP_DEPLOYMENT.md)** - AI 旅行规划部署指南

### 🌍 生态系统
- **[生态系统概览](docs/ecosystem/ECOSYSTEM_OVERVIEW.md)** - Roamio + Ralendar + Rote + Rapture
- **[Ralendar 融合计划](docs/ecosystem/RALENDAR_INTEGRATION.md)** - 日历助手集成方案
- **[Ralendar OAuth 集成](docs/integration/RALENDAR_OAUTH_INTEGRATION_SPEC.md)** - OAuth 2.0 集成技术规范
- **[商业计划摘要](docs/ecosystem/BUSINESS_PLAN.md)** - 商业价值与融资规划

### 📝 工作总结
- **[项目状态报告](docs/summaries/PROJECT_STATUS.md)** - 当前进展和待办事项
- **[每日工作总结](docs/summaries/)** - 开发日志和问题记录

---

## 🌟 核心功能

### 🤖 AI 智能行程规划
- **自然语言输入** - 用户只需描述旅行想法，AI 自动生成完整行程
- **通义千问大模型** - 使用阿里云通义千问 qwen-plus 模型
- **结构化输出** - 自动生成标题、概述、每日行程、预算、建议
- **偏好设置** - 支持天数、预算等级、旅行风格、出发日期
- **频率限制** - 免费用户 5次/天，防止滥用
- **使用统计** - 实时查看 AI 使用次数和剩余额度

### 📅 Ralendar 日历集成
- **OAuth 2.0 授权** - 标准 OAuth 流程，安全可靠
- **多账号绑定** - 支持绑定多个 Ralendar 账号
- **一键同步** - AI 生成的行程一键同步到日历
- **事件管理** - 在 Roamio 侧边栏直接管理日历事件
- **实时同步** - 支持创建、更新、删除日历事件

### ✈️ 旅程管理
- **创建旅程** - 设置标题、描述、封面图片
- **AI 辅助生成** - 使用 AI 快速生成完整行程
- **唯一链接分享** - 每个旅程有独立的 slug 链接
- **旅程列表** - 浏览所有公开旅程
- **旅程详情** - 完整展示旅程信息和互动内容
- **地图选择器** - 支持百度地图、高德地图选择地点

### 💬 社交互动
- **发布评论** - 支持文字、图片、视频
- **嵌套回复** - 二级评论系统
- **点赞功能** - 为评论点赞
- **实时更新** - 旅程进行中实时发布动态
- **用户资料卡片** - 鼠标悬停查看用户信息

### 👤 用户系统
- **邮箱注册登录** - 邮箱验证码注册
- **QQ 快捷登录** - OAuth 2.0 第三方登录，支持 UnionID
- **个人中心** - 用户资料、头像上传、等级系统
- **邮箱绑定** - 支持绑定/更换邮箱，邮箱验证
- **旅程管理** - 查看自己创建的旅程
- **用户等级** - 根据旅行和评论数量自动计算等级

### 🚀 性能优化
- **图片懒加载** - 减少首屏加载时间
- **视频懒加载** - 优化网络流量
- **图片压缩** - 腾讯云 COS 图片处理
- **Redis 缓存** - 热点数据缓存（天气、用户信息等）
- **CDN 加速** - 静态资源全球加速

**优化成果**：图片流量从 1.9 MB（116 次请求）优化到仅 **几十 KB**，节省约 **95%** 流量！

---

## 🔮 未来规划

### 短期（0-6 个月）
- [ ] **AI RAG 增强** - 构建旅行知识库，提升 AI 生成质量
- [ ] **地图集成优化** - 完善地图选择器，支持更多地图服务
- [ ] **行程规划工具** - 拖拽式时间线编辑器
- [ ] **预算管理** - 旅行预算计算与跟踪
- [ ] **移动端 APP** - React Native 开发

### 中期（6-18 个月）
- [ ] **多场景扩展** - 支持巡演、马拉松、读书等场景
- [ ] **团队协作** - 多人共同编辑一个旅程
- [ ] **内容付费** - 优质旅行计划售卖
- [ ] **任务悬赏** - 用户发布/接单完成任务
- [ ] **VIP 会员** - 高级功能订阅

### 长期（18-36 个月）
- [ ] **场景化支付** - 支付与场景深度绑定（探索性功能）
- [ ] **AI 智能管家** - 预算分析、消费监督、省钱建议
- [ ] **多设备生态** - 手机、AI 眼镜、手表等（前瞻性规划）
- [ ] **国际化** - 多语言支持、全球市场

详见：**[商业计划书](docs/BUSINESS_PLAN.md)** | **[AI 路线图](docs/AI_ROADMAP.md)**

---

## 🛠️ 技术栈

**后端**:
- Django 5.2.1 + Django REST Framework
- MySQL（生产环境，腾讯云 CDB）
- Redis 6.0（缓存）
- uWSGI + Nginx
- JWT 认证（Simple JWT）
- OAuth 2.0（QQ、Ralendar）

**前端**:
- Vue 3 + Vue Router + Pinia
- Bootstrap 5
- Axios（HTTP 请求）
- 百度地图 API / 高德地图 API

**AI 服务**:
- 阿里云通义千问（qwen-plus）
- JSON 格式输出
- 智能提示词工程

**云服务**:
- 腾讯云 COS（对象存储）
- 腾讯云 CDN（内容分发）
- 腾讯云 MySQL（数据库）
- QQ OAuth 2.0（第三方登录）

**部署**:
- Linux（Ubuntu/Debian）
- Nginx（反向代理）
- uWSGI（WSGI 服务器）
- 域名：roamio.cn（ICP 备案 + 公安备案）

---

## 🚀 快速开始

### 本地开发

```bash
# 1. 克隆项目
git clone https://github.com/ppshuX/roamio.git
cd roamio

# 2. 后端设置
pip install -r requirements.txt

# 3. 配置环境变量
cp cloud_settings/env.example .env
# 编辑 .env 文件，配置数据库、Redis、COS、QQ OAuth 等

# 4. 数据库迁移
python manage.py migrate

# 5. 创建超级用户
python manage.py createsuperuser

# 6. 运行后端（开发模式）
python manage.py runserver  # 运行在 http://127.0.0.1:8000/

# 7. 前端设置（新终端）
cd web
npm install
npm run serve  # 运行在 http://localhost:8080/
```

### 生产部署

```bash
# 1. 构建前端
cd web
npm run build
cd ..

# 2. 收集静态文件
python manage.py collectstatic --noinput

# 3. 启动服务
pkill -9 uwsgi || true
uwsgi --ini scripts/uwsgi.ini --daemonize /tmp/uwsgi.log
sudo systemctl restart nginx
```

详细部署指南：**[Docker 重建完整指南](docs/DOCKER_REBUILD_COMPLETE_GUIDE.md)**

### 环境变量配置

关键环境变量（参考 `cloud_settings/env.example`）：

```bash
# 数据库
DB_NAME=roamio_production
DB_USER=roamio_user
DB_PASSWORD=your_password
DB_HOST=your_host
DB_PORT=3306

# Redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

# 腾讯云 COS
TENCENT_COS_SECRET_ID=your_secret_id
TENCENT_COS_SECRET_KEY=your_secret_key
TENCENT_COS_BUCKET=your_bucket
TENCENT_COS_REGION=ap-guangzhou

# QQ OAuth
QQ_APP_ID=your_app_id
QQ_APP_KEY=your_app_key
QQ_REDIRECT_URI=https://roamio.cn/settings/qq/receive_code

# Ralendar OAuth
RALENDAR_OAUTH_CLIENT_ID=your_client_id
RALENDAR_OAUTH_CLIENT_SECRET=your_client_secret
RALENDAR_OAUTH_REDIRECT_URI=https://roamio.cn/auth/ralendar/callback

# AI 服务
AI_GENERATION_ENABLED=True
QWEN_API_KEY=your_api_key
QWEN_MODEL=qwen-plus

# 邮件服务
USE_REAL_EMAIL=1
EMAIL_HOST=smtp.qq.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_password
```

---

## 📂 项目结构

```
roamio/
├── roamio/                      # Django 配置
│   ├── settings.py              # 项目设置
│   ├── urls.py                  # 主路由
│   ├── api_docs_config.py       # ⭐ API 文档配置
│   └── wsgi.py                  # WSGI 入口
│
├── backend/                     # ⭐ 后端业务模块
│   ├── models/                  # 数据模型
│   │   ├── trip.py              # 旅程模型
│   │   ├── comment.py           # 评论模型
│   │   ├── user_profile.py      # 用户资料
│   │   ├── event.py             # 事件模型（Ralendar）
│   │   ├── ralendar_account.py  # Ralendar 账号绑定
│   │   └── social_auth.py       # 第三方登录
│   │
│   ├── api/                     # RESTful API
│   │   ├── viewsets/            # API ViewSet
│   │   │   ├── ai_viewset.py    # ⭐ AI 行程生成
│   │   │   ├── auth_viewset.py  # 认证（注册/登录/QQ）
│   │   │   ├── trip_viewset.py  # 旅程管理
│   │   │   ├── comment_viewset.py  # 评论管理
│   │   │   ├── event_viewset.py    # 事件管理
│   │   │   ├── ralendar_viewset.py # Ralendar 集成
│   │   │   └── ralendar_oauth_viewset.py  # Ralendar OAuth
│   │   ├── views/                # API 视图
│   │   │   └── ralendar_events.py  # Ralendar 事件操作
│   │   └── urls.py              # API 路由
│   │
│   ├── serializers/             # 序列化器
│   │   ├── ai_serializer.py     # AI 相关
│   │   ├── auth_serializer.py   # 认证相关
│   │   ├── trip_serializer.py   # 旅程相关
│   │   └── comment_serializer.py # 评论相关
│   │
│   ├── utils/                   # 工具函数
│   │   ├── ai/                  # ⭐ AI 服务
│   │   │   └── ai_service.py    # 通义千问集成
│   │   ├── auth/                # 认证工具
│   │   │   ├── qq_oauth.py      # QQ OAuth
│   │   │   └── rate_limit.py    # 频率限制
│   │   ├── external/            # 外部服务
│   │   │   ├── ralendar_client.py  # Ralendar API 客户端
│   │   │   └── email_service.py    # 邮件服务
│   │   ├── storage/             # 存储服务
│   │   │   └── tencent_cos.py   # 腾讯云 COS
│   │   └── email_service.py     # 邮件服务
│   │
│   └── static/                  # 静态资源
│       ├── images/              # 图片
│       ├── audios/              # 音频
│       └── videos/              # 视频
│
├── web/                         # Vue 3 前端
│   ├── src/
│   │   ├── views/               # 页面组件
│   │   │   ├── TripListView.vue      # 旅程列表
│   │   │   ├── TripDetailView.vue    # 旅程详情
│   │   │   ├── TripEditorView.vue    # 旅程编辑器
│   │   │   ├── MyTripsView.vue       # 我的旅程
│   │   │   ├── UserCenterView.vue    # 个人中心
│   │   │   └── auth/                 # 认证页面
│   │   │
│   │   ├── components/          # 可复用组件
│   │   │   ├── ai/              # ⭐ AI 组件
│   │   │   │   └── TripGenerator.vue  # AI 行程生成器
│   │   │   ├── calendar/        # 日历组件
│   │   │   │   └── CalendarSyncSelector.vue
│   │   │   ├── comments/        # 评论组件
│   │   │   │   ├── CommentForm.vue
│   │   │   │   └── CommentItem.vue
│   │   │   ├── events/          # 事件组件
│   │   │   │   ├── GlobalSidebar.vue  # Ralendar 侧边栏
│   │   │   │   └── EventItem.vue
│   │   │   ├── map/             # 地图组件
│   │   │   │   └── MapPicker.vue     # 地图选择器
│   │   │   ├── ralendar/        # Ralendar 组件
│   │   │   │   └── RalendarAccountManager.vue
│   │   │   └── trip/            # 旅程组件
│   │   │
│   │   ├── api/                 # API 封装
│   │   │   ├── ai.js            # AI API
│   │   │   ├── auth.js          # 认证 API
│   │   │   ├── ralendar.js      # Ralendar API
│   │   │   └── ralendarOAuth.js # Ralendar OAuth
│   │   │
│   │   ├── stores/              # Pinia 状态管理
│   │   │   └── user.js          # 用户状态
│   │   │
│   │   └── router/              # 路由配置
│   │       └── index.js
│   │
│   ├── public/                  # 公共资源
│   ├── dist/                    # ⭐ 构建产物（提交到 Git）
│   └── package.json
│
├── docs/                        # ⭐ 项目文档
│   ├── README.md                # 文档中心首页
│   ├── api/                     # API 相关文档
│   ├── architecture/           # 架构设计文档
│   ├── guides/                  # 开发指南
│   ├── summaries/              # 工作总结
│   ├── ecosystem/              # 生态系统文档
│   ├── integration/            # 集成文档
│   └── features/               # 功能文档
│
├── scripts/                     # 部署脚本
│   └── uwsgi.ini                # uWSGI 配置
│
├── cloud_settings/              # 云服务配置
│   ├── env.example              # 环境变量模板
│   ├── nginx_roamio.cn.conf     # Nginx 配置
│   └── uwsgi.ini                # uWSGI 配置
│
├── templates/                   # Django 模板
│   └── emails/                  # 邮件模板
│
└── requirements.txt             # Python 依赖
```

### 🎯 架构说明

**前后端分离**：
- 后端：Django REST Framework 提供 API
- 前端：Vue 3 SPA，由 Nginx 直接服务
- 通信：RESTful API + JWT 认证

**多端支持**：
- Web 端：`web/dist/` 构建产物
- 小程序端：规划中
- Android 端：Ralendar 项目（独立应用）

**文档管理**：
- 分类清晰：api / architecture / guides / summaries / ecosystem / integration
- 英文文件名 + 中文内容
- 完整的文档索引：`docs/README.md`

---

## 🎨 技术亮点

### 后端
- ✅ **RESTful API 设计** - 标准化接口，前后端分离
- ✅ **JWT 认证** - 无状态的用户认证
- ✅ **OAuth 2.0** - QQ、Ralendar 第三方登录集成
- ✅ **Redis 缓存** - 热点数据缓存，提升性能
- ✅ **邮件服务** - SMTP 邮件发送（QQ 邮箱）
- ✅ **限流机制** - 防止恶意请求
- ✅ **腾讯云 COS** - 对象存储，图片/视频上传
- ✅ **AI 集成** - 通义千问大模型，智能行程生成
- ✅ **MySQL 生产数据库** - 腾讯云 CDB，稳定可靠

### 前端
- ✅ **Vue 3 Composition API** - 现代化组件开发
- ✅ **Pinia 状态管理** - 轻量级、类型安全
- ✅ **Vue Router** - 单页应用路由
- ✅ **响应式设计** - Bootstrap 5，适配移动端和 PC 端
- ✅ **懒加载优化** - 图片/视频按需加载
- ✅ **组件化开发** - 可复用组件库
- ✅ **地图集成** - 百度地图、高德地图选择器

### AI 功能
- ✅ **通义千问集成** - 使用 qwen-plus 模型
- ✅ **JSON 格式输出** - 结构化数据，易于处理
- ✅ **智能提示词** - 优化的 Prompt 工程
- ✅ **错误处理** - 完善的错误处理和重试机制
- ✅ **频率限制** - 防止滥用，保护资源

### 部署与运维
- ✅ **生产环境部署** - 真实用户使用中
- ✅ **Nginx 反向代理** - 高性能 Web 服务器
- ✅ **uWSGI 应用服务器** - 稳定的 Python 应用运行环境
- ✅ **腾讯云 CDN** - 静态资源全球加速
- ✅ **日志管理** - 完善的日志记录与错误追踪
- ✅ **域名备案** - roamio.cn（ICP 备案 + 公安备案）

### 性能优化
- ✅ **图片流量优化 95%** - 从 1.9 MB 降至几十 KB
- ✅ **懒加载** - 图片/视频按需加载
- ✅ **SVG 内联** - 默认头像使用 SVG，避免重复请求
- ✅ **Redis 缓存** - 减少数据库查询
- ✅ **CDN 加速** - 静态资源分发

---

## 🎓 项目定位

### 技术层面
本项目是一个**真实部署在生产环境**的完整 Web 应用：
- ✅ **非玩具项目** - 真实用户使用，真实数据
- ✅ **完整技术栈** - 前端 + 后端 + 数据库 + 云服务 + 部署
- ✅ **工程化实践** - 代码规范、版本控制、完善文档体系
- ✅ **性能优化** - 图片流量优化 95%，Redis 缓存，CDN 加速
- ✅ **问题解决能力** - Docker 容器删除后 48 小时内完整重建
- ✅ **AI 集成** - 大模型应用，智能行程生成
- ✅ **生态系统** - 与 Ralendar 等产品深度集成

**技术水平**: 在大三学生中处于 **TOP 10-15%**，已达到**初级工程师**水平。

### 产品层面
本项目不仅仅是一个技术练手项目，更是一个**有清晰愿景的产品**：
- 🎯 **从旅行到体验** - 从单一场景扩展到多场景
- 🚀 **探索创新** - AI 智能规划、场景化支付、AI 智能管家等前瞻性功能
- 💡 **商业潜力** - 清晰的商业模式和发展路径
- 📈 **可持续增长** - 网络效应 + 数据积累
- 🤝 **生态合作** - 与 Ralendar 等产品形成完整生态

**产品愿景**: 从旅行记录开始，逐步扩展到巡演、马拉松、学习等场景，最终成为一个跨场景的体验管理平台。

详见：**[商业计划书](docs/BUSINESS_PLAN.md)** | **[项目水平评估](docs/PROJECT_VALUE_AND_LEVELS.md)**

---

## 🏆 项目成就

### 技术成就
- ✅ 独立完成前后端完整开发
- ✅ Docker 容器删除后 48 小时内完整重建
- ✅ 图片流量优化 95%，解决性能瓶颈
- ✅ AI 功能集成，智能行程生成
- ✅ Ralendar OAuth 集成，日历同步
- ✅ 完善的文档体系（20+ 篇技术文档）
- ✅ 真实生产环境部署经验

### 项目亮点
- 🌟 **真实项目** - 不是 Demo，而是真实用户在用
- 🌟 **完整技术栈** - 涵盖前后端、部署、优化全流程
- 🌟 **AI 驱动** - 大模型应用，智能行程生成
- 🌟 **生态集成** - 与 Ralendar 深度集成，形成完整生态
- 🌟 **问题解决** - 从 502 错误到邮件发送，一步步解决真实问题
- 🌟 **性能优化** - 从理论到实践，真正的性能提升
- 🌟 **产品思维** - 不仅仅是写代码，更关注用户体验和商业价值

---

## 📄 开源协议

本项目采用 MIT 协议开源。

---

## 🙏 鸣谢

**技术栈**:
- **Django** - 强大的 Python Web 框架
- **Vue.js** - 渐进式 JavaScript 框架
- **Bootstrap** - 优秀的 CSS 框架
- **Django REST Framework** - 强大的 API 开发工具
- **通义千问** - 阿里云大语言模型

**云服务**:
- **腾讯云** - COS 对象存储、CDN 加速、MySQL 数据库
- **阿里云** - 通义千问 AI 服务
- **Redis** - 高性能缓存数据库

**合作伙伴**:
- **Ralendar** - 日历助手，生态系统合作伙伴

**感谢所有贡献者和支持者！** ❤️

---

## 📞 联系方式

- **项目地址**: https://github.com/ppshuX/roamio
- **在线演示**: https://roamio.cn/
- **问题反馈**: [GitHub Issues](https://github.com/ppshuX/roamio/issues)
- **邮箱**: 联系请通过 GitHub Issues

---

## 💪 为什么选择 Roamio？

**对用户**：
- 📝 结构化记录旅程，不再是朋友圈的碎片
- 🤖 AI 智能生成行程，5分钟完成规划
- 📅 一键同步到日历，不错过任何行程
- 🌍 分享精彩体验，与他人互动交流
- 📸 支持图片/视频，记录每一个美好瞬间

**对开发者**：
- 🛠️ 完整技术栈，真实生产环境
- 📚 详细文档体系，从 0 到 1 的完整经验
- 💡 性能优化实践，值得学习和参考
- 🚀 清晰的发展路线，可以持续学习
- 🤖 AI 集成示例，大模型应用参考

**对投资人**：
- 📈 清晰的商业模式和发展规划
- 💰 巨大的市场空间（体验经济）
- 🎯 从旅行到多场景的扩展潜力
- 🤝 生态系统布局，形成竞争壁垒

---

**让 Roamio 陪你探索世界的每一个角落！** 🌍✨

**从记录旅行开始，走向体验经济的未来！** 🚀

**Built with ❤️ by the Roamio Team**
