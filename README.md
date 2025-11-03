# 🌍 Roamio - 智能旅行记录与分享平台

> **记录旅程，分享故事，让每一段体验都值得被铭记**

**从旅行开始，走向体验经济的未来** ✈️🌄✨

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2+-092E20.svg)](https://www.djangoproject.com/)
[![Vue](https://img.shields.io/badge/Vue-3.0+-4FC08D.svg)](https://vuejs.org/)

[在线演示](https://app7508.acapp.acwing.com.cn/) · [项目文档](docs/) · [问题反馈](https://github.com/ppshuX/roamio/issues)

---

## 🎯 项目简介

Roamio 是一个**真实部署在生产环境**的现代化旅行记录与分享平台，采用前后端分离架构。

**核心特色**：
- ✅ 结构化旅程记录（策划 → 实时更新 → 回忆）
- ✅ 丰富的社交互动（评论、图片、视频、点赞）
- ✅ 性能优化实践（图片流量节省 95%）
- ✅ 完整的技术栈（Django + Vue 3 + Redis + 腾讯云）

**未来愿景**：从旅行扩展到巡演、马拉松、学习等多种场景，最终成为一个跨场景的体验记录与分享平台，并探索场景化支付等创新功能。

详见：**[商业计划书](docs/BUSINESS_PLAN.md)**

---

## 📚 项目文档

**商业与规划**：
- 💼 **[商业计划书 - 精简版](docs/BUSINESS_PLAN_EXECUTIVE_SUMMARY.md)** - 适合投资人/老师（推荐阅读）
- 📋 **[商业计划书 - 完整版](docs/BUSINESS_PLAN.md)** - 完整思考和长期愿景
- 🗺️ **[项目发展计划](docs/DEVELOPMENT_ROADMAP.md)** - 内部使用，校准方向和进度

**技术与运维**：
- 🚀 **[性能优化指南](docs/PERFORMANCE_OPTIMIZATION.md)** - 流量优化、懒加载、图片压缩
- 🐳 **[Docker 重建完整指南](docs/DOCKER_REBUILD_COMPLETE_GUIDE.md)** - 生产环境部署经验
- 📊 **[项目价值与水平分析](docs/PROJECT_VALUE_AND_LEVELS.md)** - 技术评估、求职亮点
- 📝 **[Docker 重建历程](docs/DOCKER_REBUILD_JOURNEY.md)** - 踩坑记录与解决方案

---

## 🌟 核心功能

### ✈️ 旅程管理
- **创建旅程** - 设置标题、描述、封面图片
- **唯一链接分享** - 每个旅程有独立的 slug 链接
- **旅程列表** - 浏览所有公开旅程
- **旅程详情** - 完整展示旅程信息和互动内容

### 💬 社交互动
- **发布评论** - 支持文字、图片、视频
- **嵌套回复** - 二级评论系统
- **点赞功能** - 为评论点赞
- **实时更新** - 旅程进行中实时发布动态

### 👤 用户系统
- **邮箱注册登录** - 邮箱验证码注册
- **QQ 快捷登录** - OAuth 2.0 第三方登录
- **个人主页** - 用户资料、头像上传
- **旅程管理** - 查看自己创建的旅程

### 🚀 性能优化
- **图片懒加载** - 减少首屏加载时间
- **视频懒加载** - 优化网络流量
- **图片压缩** - 腾讯云 COS 图片处理
- **Redis 缓存** - 热点数据缓存
- **CDN 加速** - 静态资源全球加速

**优化成果**：图片流量从 1.9 MB（116 次请求）优化到仅 **几十 KB**，节省约 **95%** 流量！

---

## 🔮 未来规划

### 短期（0-6 个月）
- [ ] **地图集成** - 腾讯地图 API，地点标注
- [ ] **行程规划工具** - 拖拽式时间线编辑器
- [ ] **预算管理** - 旅行预算计算与跟踪
- [ ] **AI 助手** - 接入腾讯混元大模型，智能规划建议
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

详见：**[商业计划书](docs/BUSINESS_PLAN.md)**

---

## 🛠️ 技术栈

**后端**:
- Django 4.2 + Django REST Framework
- Redis 6.0（缓存）
- SQLite（开发）/ MySQL（生产）
- uWSGI + Nginx

**前端**:
- Vue 3 + Vue Router + Pinia
- Bootstrap 5
- Axios（HTTP 请求）

**云服务**:
- 腾讯云 COS（对象存储）
- 腾讯云 CDN（内容分发）
- QQ OAuth 2.0（第三方登录）

**部署**:
- Linux（Ubuntu/Debian）
- Nginx（反向代理）
- uWSGI（WSGI 服务器）

---

## 🚀 快速开始

### 本地开发

```bash
# 1. 克隆项目
git clone https://github.com/ppshuX/roamio.git
cd roamio

# 2. 后端设置
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver  # 运行在 http://127.0.0.1:8000/

# 3. 前端设置（新终端）
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
uwsgi --ini scripts/uwsgi.ini --daemonize uwsgi.log
sudo systemctl restart nginx
```

详细部署指南：**[Docker 重建完整指南](docs/DOCKER_REBUILD_COMPLETE_GUIDE.md)**

---

## 📂 项目结构

```
roamio/
├── roamio/              # Django 配置
│   ├── settings.py      # 项目设置
│   ├── urls.py          # 主路由
│   └── wsgi.py          # WSGI 入口
├── trips/               # 主应用
│   ├── models/          # 数据模型
│   │   ├── trip.py      # 旅程模型
│   │   ├── comment.py   # 评论模型
│   │   └── user_profile.py  # 用户资料
│   ├── api/             # RESTful API
│   │   └── viewsets/    # API ViewSet
│   ├── serializers/     # 序列化器
│   ├── utils/           # 工具函数
│   │   ├── email_service.py  # 邮件服务
│   │   ├── qq_oauth.py       # QQ 登录
│   │   └── rate_limit.py     # 限流
│   └── views/           # 视图函数
├── web/                 # Vue 3 前端
│   ├── src/
│   │   ├── views/       # 页面组件
│   │   ├── components/  # 可复用组件
│   │   ├── api/         # API 封装
│   │   ├── stores/      # Pinia 状态管理
│   │   └── router/      # 路由配置
│   └── package.json
├── media/               # 用户上传文件（腾讯云 COS）
├── static/              # 静态文件
├── docs/                # 项目文档
├── scripts/             # 部署脚本
│   └── uwsgi.ini        # uWSGI 配置
└── requirements.txt     # Python 依赖
```

---

## 🎨 技术亮点

### 后端
- ✅ **RESTful API 设计** - 标准化接口，前后端分离
- ✅ **JWT 认证** - 无状态的用户认证
- ✅ **OAuth 2.0** - QQ 第三方登录集成
- ✅ **Redis 缓存** - 热点数据缓存，提升性能
- ✅ **邮件服务** - SMTP 邮件发送（QQ 邮箱）
- ✅ **限流机制** - 防止恶意请求
- ✅ **腾讯云 COS** - 对象存储，图片/视频上传

### 前端
- ✅ **Vue 3 Composition API** - 现代化组件开发
- ✅ **Pinia 状态管理** - 轻量级、类型安全
- ✅ **Vue Router** - 单页应用路由
- ✅ **响应式设计** - Bootstrap 5，适配移动端和 PC 端
- ✅ **懒加载优化** - 图片/视频按需加载
- ✅ **组件化开发** - 可复用组件库

### 部署与运维
- ✅ **Docker 容器化** - 经历过容器删除后完整重建的考验
- ✅ **Nginx 反向代理** - 高性能 Web 服务器
- ✅ **uWSGI 应用服务器** - 稳定的 Python 应用运行环境
- ✅ **腾讯云 CDN** - 静态资源全球加速
- ✅ **日志管理** - 完善的日志记录与错误追踪

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

**技术水平**: 在大三学生中处于 **TOP 10-15%**，已达到**初级工程师**水平。

### 产品层面
本项目不仅仅是一个技术练手项目，更是一个**有清晰愿景的产品**：
- 🎯 **从旅行到体验** - 从单一场景扩展到多场景
- 🚀 **探索创新** - 场景化支付、AI 智能管家等前瞻性功能
- 💡 **商业潜力** - 清晰的商业模式和发展路径
- 📈 **可持续增长** - 网络效应 + 数据积累

**产品愿景**: 从旅行记录开始，逐步扩展到巡演、马拉松、学习等场景，最终成为一个跨场景的体验管理平台。

详见：**[商业计划书](docs/BUSINESS_PLAN.md)** | **[项目水平评估](docs/PROJECT_VALUE_AND_LEVELS.md)**

---

## 🏆 项目成就

### 技术成就
- ✅ 独立完成前后端完整开发
- ✅ Docker 容器删除后 48 小时内完整重建
- ✅ 图片流量优化 95%，解决性能瓶颈
- ✅ 完善的文档体系（10+ 篇技术文档）
- ✅ 真实生产环境部署经验

### 项目亮点
- 🌟 **真实项目** - 不是 Demo，而是真实用户在用
- 🌟 **完整技术栈** - 涵盖前后端、部署、优化全流程
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

**云服务**:
- **腾讯云** - COS 对象存储、CDN 加速
- **Redis** - 高性能缓存数据库

**感谢所有贡献者和支持者！** ❤️

---

## 📞 联系方式

- **项目地址**: https://github.com/ppshuX/roamio
- **在线演示**: https://app7508.acapp.acwing.com.cn/
- **问题反馈**: [GitHub Issues](https://github.com/ppshuX/roamio/issues)
- **邮箱**: 联系请通过 GitHub Issues

---

## 💪 为什么选择 Roamio？

**对用户**：
- 📝 结构化记录旅程，不再是朋友圈的碎片
- 🌍 分享精彩体验，与他人互动交流
- 📸 支持图片/视频，记录每一个美好瞬间

**对开发者**：
- 🛠️ 完整技术栈，真实生产环境
- 📚 详细文档体系，从 0 到 1 的完整经验
- 💡 性能优化实践，值得学习和参考
- 🚀 清晰的发展路线，可以持续学习

**对投资人**：
- 📈 清晰的商业模式和发展规划
- 💰 巨大的市场空间（体验经济）
- 🎯 从旅行到多场景的扩展潜力

---

**让 Roamio 陪你探索世界的每一个角落！** 🌍✨

**从记录旅行开始，走向体验经济的未来！** 🚀

**Built with ❤️ by the Roamio Team**
