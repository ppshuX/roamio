# 🌍 Roamio - 智能旅行规划平台

> **一个现代化的旅行规划与社区分享平台，采用前后端分离架构。**

**让每个旅行都成为难忘的回忆** ✈️🏖️🌄

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0+-092E20.svg)](https://www.djangoproject.com/)
[![Vue](https://img.shields.io/badge/Vue-3.0+-4FC08D.svg)](https://vuejs.org/)

[在线演示](https://app7508.acapp.acwing.com.cn/) · [完整文档](PROJECT_OVERVIEW.md) · [问题反馈](https://github.com/ppshuX/roamio/issues)

---

## 📚 项目文档

- 📖 **[完整项目说明](PROJECT_OVERVIEW.md)** - 技术架构、部署指南、开发经验（推荐阅读）
- 📊 **[项目价值与水平分析](docs/PROJECT_VALUE_AND_LEVELS.md)** - 技术评估、求职亮点
- 🐳 **[Docker 重建完整指南](docs/DOCKER_REBUILD_COMPLETE_GUIDE.md)** - 生产环境部署经验
- 📝 **[Docker 重建历程](docs/DOCKER_REBUILD_JOURNEY.md)** - 踩坑记录与解决方案

---

## 🌟 核心功能

### ✈️ 旅行规划
- **可视化行程编辑器** - 拖拽式行程设计
- **模块化组件** - 自由组合行程模块（进度条、亮点、预算等）
- **智能预算计算** - 实时费用估算
- **行程分享** - 公开或私密分享

### 🤖 AI助手（规划中）
- **智能推荐目的地** - 根据预算和偏好推荐
- **自动生成行程** - AI帮你规划每日安排
- **实时优化建议** - 检测行程问题并给出建议

### 👥 社区互动
- **旅行广场** - 浏览他人的精彩行程
- **评论与点赞** - 与旅行者互动交流
- **打卡分享** - 实际旅行后的照片分享
- **用户关注** - 关注喜欢的旅行达人

### 📱 现代化体验
- **前后端分离** - Vue 3 + Django REST Framework
- **响应式设计** - 完美适配移动端和PC端
- **实时预览** - 编辑行程时即时查看效果
- **RESTful API** - 标准化接口设计

---

## 🛠️ 技术栈

**后端**: Django 5 + Django REST Framework + JWT  
**前端**: Vue 3 + Vue Router + Pinia + Bootstrap 5  
**数据库**: SQLite (开发) / PostgreSQL (生产)  
**部署**: Nginx + uWSGI

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

---

## 📂 项目结构

```
roamio/
├── roamio/              # Django配置
├── trips/               # 主应用
│   ├── models/          # 数据模型
│   ├── api/             # RESTful API
│   ├── views/           # 视图函数
│   └── templates/       # Django模板
├── web/                 # Vue 3 前端
│   ├── src/
│   │   ├── views/       # 页面组件
│   │   ├── components/  # 可复用组件
│   │   ├── api/         # API封装
│   │   └── stores/      # Pinia状态管理
│   └── package.json
├── media/               # 用户上传文件
├── static/              # 静态文件
├── docs/                # 项目文档
└── requirements.txt     # Python依赖
```

---

## 🎨 特色功能

- ✅ **旅行树** - 可视化旅行展示
- ✅ **评论互动** - 图片/视频评论支持
- ✅ **智能压缩** - 自动压缩图片和视频
- ✅ **权限管理** - 精细的用户权限控制
- ✅ **响应式设计** - 完美适配移动端和PC端

---

## 📄 开源协议

本项目采用 MIT 协议开源。

---

## 🙏 鸣谢

- **Django** - 强大的Python Web框架
- **Vue.js** - 渐进式JavaScript框架
- **Bootstrap** - 优秀的CSS框架
- **DRF** - Django REST Framework
- **所有贡献者** - 感谢你们的支持！

---

## 📞 联系方式

- **项目地址**: https://github.com/ppshuX/roamio
- **在线演示**: https://app7508.acapp.acwing.com.cn/
- **问题反馈**: [GitHub Issues](https://github.com/ppshuX/roamio/issues)
- **邮箱**: 联系请通过 GitHub Issues

## 🎓 项目定位

本项目是一个**真实部署在生产环境**的完整 Web 应用，具有以下特点：

- ✅ **非玩具项目** - 真实用户使用，真实数据
- ✅ **完整技术栈** - 前端 + 后端 + 数据库 + 部署
- ✅ **工程化实践** - 代码规范、版本控制、文档体系
- ✅ **产品化思维** - 用户体验、交互设计、品牌一致性

**技术水平**: 在大三学生中处于 **TOP 10-15%**，已达到**初级工程师**水平。详见 [项目水平评估](docs/PROJECT_VALUE_AND_LEVELS.md)。

---

## 🗺️ 产品路线图

### 当前版本 v1.0 ✅
- ✅ 前后端分离架构（Vue 3 + Django REST Framework）
- ✅ 用户认证系统（JWT）
- ✅ 旅行树可视化展示
- ✅ 评论互动（图片/视频支持）
- ✅ 智能图片视频压缩
- ✅ 响应式设计（移动端/PC端）
- ✅ 旅行编辑器（基础版）

### v2.0 - 增强编辑器（进行中）
- [x] 基础旅行编辑器
- [x] 添加到旅行树功能
- [ ] 富文本编辑器
- [ ] 图片拖拽上传
- [ ] 实时协作编辑

### v3.0 - 社区功能（规划中）
- [ ] 旅行广场
- [ ] 用户关注系统
- [ ] 旅行收藏夹
- [ ] 筛选搜索

### v4.0 - AI助手（规划中）
- [ ] AI推荐目的地
- [ ] AI生成行程
- [ ] 智能预算计算
- [ ] 实时优化建议

详细规划请参考：**[阶段开发计划](docs/PHASE_PLAN.md)**

---

**让Roamio陪你探索世界的每一个角落！** 🌍✨

**Built with ❤️ by the Roamio Team**
