# 🏗️ Roamio 项目结构分析

> **更新时间**: 2025-11-17  
> **项目状态**: 生产环境运行中（域名：roamio.cn）

---

## 📁 项目目录结构

```
roamio/
├── backend/                    # Django 后端应用（核心业务逻辑）
│   ├── api/                   # RESTful API
│   │   ├── viewsets/         # ViewSet（处理 API 请求）
│   │   │   ├── auth_viewset.py       # 认证（注册/登录/QQ登录）
│   │   │   ├── user_viewset.py       # 用户管理
│   │   │   ├── trip_viewset.py       # 旅行管理
│   │   │   ├── trip_plan_viewset.py  # 旅行计划
│   │   │   ├── comment_viewset.py    # 评论管理
│   │   │   ├── event_viewset.py      # 事件管理（Ralendar 集成）
│   │   │   └── ralendar_viewset.py   # Ralendar 集成 API
│   │   └── urls.py           # API 路由配置
│   │
│   ├── models/               # 数据模型
│   │   ├── user_profile.py   # 用户资料（头像/等级/标签）
│   │   ├── trip.py           # 旅行（标题/描述/封面）
│   │   ├── comment.py        # 评论（文字/图片/视频）
│   │   ├── event.py          # 事件（日程/提醒）
│   │   ├── social_auth.py    # 第三方登录（QQ/微信）
│   │   ├── email_verification.py  # 邮箱验证码
│   │   └── site_stat.py      # 网站统计
│   │
│   ├── serializers/          # 数据序列化器
│   │   ├── auth_serializer.py      # 认证相关
│   │   ├── user_serializer.py      # 用户相关
│   │   ├── trip_serializer.py      # 旅行列表
│   │   ├── trip_detail_serializer.py  # 旅行详情
│   │   ├── comment_serializer.py   # 评论相关
│   │   └── event_serializer.py     # 事件相关
│   │
│   ├── utils/                # 工具函数
│   │   ├── qq_oauth.py       # QQ OAuth 2.0 登录
│   │   ├── email_service.py  # 邮件发送（验证码）
│   │   ├── tencent_cos.py    # 腾讯云 COS 对象存储
│   │   ├── file_upload_handler.py  # 文件上传处理
│   │   ├── avatar_downloader.py    # QQ 头像下载
│   │   ├── rate_limit.py     # 频率限制（防刷）
│   │   ├── trip_utils.py     # 旅行工具函数
│   │   └── ralendar_client.py  # Ralendar API 客户端
│   │
│   ├── management/commands/  # Django 管理命令
│   │   ├── cleanup_users.py  # 清理未验证用户
│   │   └── fix_missing_slugs.py  # 修复缺失的 slug
│   │
│   ├── static/               # 后端静态资源
│   │   ├── images/          # 图片（logo/默认头像）
│   │   ├── audios/          # 音频（背景音乐）
│   │   └── videos/          # 视频
│   │
│   └── migrations/           # 数据库迁移文件
│
├── web/                       # Vue.js 前端应用
│   ├── src/
│   │   ├── views/           # 页面组件
│   │   │   ├── HomePage.vue        # 首页
│   │   │   ├── TripDetailPage.vue  # 旅行详情
│   │   │   ├── UserCenter.vue      # 个人中心
│   │   │   ├── LoginPage.vue       # 登录页
│   │   │   ├── RegisterPage.vue    # 注册页
│   │   │   └── events/             # Ralendar 事件页面
│   │   │
│   │   ├── components/      # 可复用组件
│   │   │   ├── GlobalSidebar.vue   # 全局侧边栏
│   │   │   ├── TripCard.vue        # 旅行卡片
│   │   │   ├── CommentItem.vue     # 评论项
│   │   │   ├── RalendarSettingsModal.vue  # Ralendar 设置弹窗
│   │   │   └── events/             # Ralendar 事件组件
│   │   │
│   │   ├── api/             # API 请求封装
│   │   │   ├── auth.js      # 认证 API
│   │   │   ├── user.js      # 用户 API
│   │   │   ├── trip.js      # 旅行 API
│   │   │   ├── comment.js   # 评论 API
│   │   │   ├── event.js     # 事件 API
│   │   │   └── ralendar.js  # Ralendar API
│   │   │
│   │   ├── stores/          # Pinia 状态管理
│   │   │   ├── user.js      # 用户状态
│   │   │   └── ralendar.js  # Ralendar 状态
│   │   │
│   │   ├── router/          # Vue Router 路由
│   │   │   └── index.js
│   │   │
│   │   └── config/          # 配置文件
│   │       ├── api.js       # API 基础配置
│   │       └── ralendar.js  # Ralendar 配置
│   │
│   ├── dist/                # 构建输出（已提交到 Git）
│   │   ├── index.html
│   │   ├── assets/          # CSS/JS 打包文件
│   │   ├── images/
│   │   └── music/
│   │
│   └── public/              # 公共资源（不经过 Webpack）
│       ├── index.html
│       ├── favicon.png
│       └── logo_Roamio.png
│
├── roamio/                   # Django 项目配置
│   ├── settings.py          # 核心配置（数据库/COS/邮件/QQ OAuth）
│   ├── urls.py              # 主路由
│   ├── wsgi.py              # WSGI 入口
│   └── api_docs_config.py   # API 文档配置
│
├── cloud_settings/           # 云服务器配置
│   └── uwsgi.ini            # uWSGI 配置
│
├── scripts/                  # 部署脚本
│   └── uwsgi.ini            # uWSGI 配置（备份）
│
├── templates/                # Django 模板
│   └── emails/
│       └── verification_code.html  # 验证码邮件模板
│
├── docs/                     # 项目文档
│   ├── README.md            # 文档总览
│   ├── api/                 # API 文档
│   │   ├── ECOSYSTEM_API_DOCUMENTATION.md  # 生态系统 API
│   │   ├── RALENDAR_API_CONFIG.md          # Ralendar API 配置
│   │   └── API_STANDARDS.md                # API 规范
│   │
│   ├── architecture/        # 架构文档
│   │   ├── ARCHITECTURE_ANALYSIS.md  # 架构分析
│   │   └── PROJECT_EVALUATION.md     # 项目评估
│   │
│   ├── ecosystem/           # 生态系统文档
│   │   ├── ECOSYSTEM_OVERVIEW.md           # 生态概览
│   │   ├── RALENDAR_INTEGRATION_GUIDE.md   # Ralendar 集成指南
│   │   ├── ROAMIO_DATABASE_INFO_FOR_RALENDAR.md  # 数据库信息
│   │   ├── RDS_SETUP_COMPLETE.md           # RDS 配置完成
│   │   ├── BUSINESS_PLAN.md                # 商业计划
│   │   ├── ROAMIO_V2_TECHNICAL_PLAN.md     # V2 技术规划
│   │   └── FUSION_IMPLEMENTATION_GUIDE.md  # 融合实现指南
│   │
│   ├── features/            # 功能文档
│   │   └── FLOATING_RALENDAR_BUTTON.md  # 浮动按钮
│   │
│   ├── guides/              # 使用指南
│   │   ├── TRIP_SHARING_GUIDE.md           # 旅行分享指南
│   │   ├── TENCENT_COS_SETUP.md            # COS 配置指南
│   │   └── STATIC_RESOURCES_DEPLOYMENT.md  # 静态资源部署
│   │
│   └── summaries/           # 项目总结
│       └── PROJECT_STATUS.md  # 项目状态
│
├── manage.py                 # Django 管理脚本
├── requirements.txt          # Python 依赖
├── package.json              # Node.js 依赖（前端）
├── env.example               # 环境变量示例
├── README.md                 # 项目说明
└── db.sqlite3                # SQLite 数据库（本地开发）

```

---

## 🎯 核心功能模块

### 1️⃣ **用户系统**
- **注册/登录**: 邮箱验证码注册，用户名/邮箱登录
- **QQ 一键登录**: OAuth 2.0，自动获取头像和昵称
- **用户资料**: 头像、等级、标签、简介
- **邮箱验证**: 验证码发送（QQ 邮箱 SMTP）

### 2️⃣ **旅行系统**
- **旅行管理**: 创建、编辑、删除旅行
- **旅行详情**: 标题、描述、封面、作者、统计
- **旅行计划**: 行程安排、景点、交通
- **旅行分享**: 公开/私密，分享链接

### 3️⃣ **评论系统**
- **多媒体评论**: 文字、图片、视频
- **嵌套评论**: 支持回复（父子关系）
- **点赞功能**: 评论点赞统计
- **实时更新**: 评论列表实时刷新

### 4️⃣ **事件系统（Ralendar 集成）**
- **事件管理**: 创建、编辑、删除事件
- **日程提醒**: 时间、地点、描述
- **与旅行关联**: 事件绑定到旅行
- **跨应用同步**: 与 Ralendar 应用数据共享

### 5️⃣ **文件存储**
- **腾讯云 COS**: 对象存储（图片/视频/音频）
- **自动压缩**: 图片压缩（1920px 宽度限制）
- **头像处理**: 裁剪为 300x300 正方形
- **CDN 加速**: 全球加速访问

### 6️⃣ **安全与性能**
- **JWT 认证**: 无状态身份验证
- **频率限制**: 防止恶意刷接口
- **CORS 配置**: 跨域资源共享
- **SQL 注入防护**: Django ORM 自动防护
- **XSS 防护**: 前端输入过滤

---

## 🔧 技术栈

### **后端**
- **框架**: Django 4.2 + Django REST Framework
- **数据库**: MySQL 8.0（Aliyun RDS）
- **认证**: JWT（simplejwt）
- **存储**: 腾讯云 COS
- **邮件**: QQ 邮箱 SMTP
- **部署**: uWSGI + Nginx

### **前端**
- **框架**: Vue 3 + Vue Router + Pinia
- **UI**: Bootstrap 5 + 自定义样式
- **HTTP**: Axios
- **构建**: Webpack（Vue CLI）

### **第三方服务**
- **QQ 互联**: OAuth 2.0 登录
- **腾讯云 COS**: 对象存储
- **阿里云 RDS**: MySQL 数据库
- **QQ 邮箱**: SMTP 邮件服务

---

## 📊 数据库设计

### **核心表**

| 表名 | 说明 | 关键字段 |
|------|------|---------|
| `auth_user` | 用户表 | `username`, `email`, `password` |
| `backend_userprofile` | 用户资料 | `avatar`, `level`, `tags`, `bio` |
| `backend_trip` | 旅行表 | `title`, `description`, `cover`, `author` |
| `backend_comment` | 评论表 | `content`, `image`, `video`, `user`, `trip` |
| `backend_tripevent` | 事件表 | `title`, `start_time`, `end_time`, `trip` |
| `backend_socialaccount` | 第三方登录 | `provider`, `uid`, `unionid`, `avatar_url` |
| `backend_emailverificationcode` | 验证码 | `email`, `code`, `verification_type` |

### **关系**
- `UserProfile` ↔ `User` (1:1)
- `Trip` ↔ `User` (N:1)
- `Comment` ↔ `User` (N:1)
- `Comment` ↔ `Trip` (N:1)
- `TripEvent` ↔ `Trip` (N:1)
- `SocialAccount` ↔ `User` (N:1)

---

## 🚀 部署架构

```
用户浏览器
    ↓
Nginx (反向代理)
    ↓
uWSGI (WSGI 服务器)
    ↓
Django (后端应用)
    ↓
    ├── Aliyun RDS MySQL (数据库)
    ├── Tencent COS (文件存储)
    ├── QQ 互联 (OAuth)
    └── QQ 邮箱 (SMTP)
```

---

## 🎨 前端路由

| 路径 | 组件 | 说明 |
|------|------|------|
| `/` | `HomePage` | 首页（旅行列表） |
| `/trip/:slug` | `TripDetailPage` | 旅行详情 |
| `/user/center` | `UserCenter` | 个人中心 |
| `/login` | `LoginPage` | 登录页 |
| `/register` | `RegisterPage` | 注册页 |
| `/events` | `EventListPage` | 事件列表 |
| `/events/:id` | `EventDetailPage` | 事件详情 |

---

## 🔗 API 端点

### **认证相关** (`/api/v1/auth/`)
- `POST /register/` - 注册
- `POST /login/` - 登录
- `POST /logout/` - 登出
- `GET /me/` - 获取当前用户
- `POST /send_verification_code/` - 发送验证码
- `POST /verify_code/` - 验证验证码
- `GET /qq_login_url/` - 获取 QQ 登录 URL
- `POST /qq_callback/` - QQ 登录回调
- `POST /qq_bind/` - 绑定 QQ
- `POST /qq_bind_existing/` - 为已有账号绑定 QQ
- `DELETE /qq_unbind/` - 解绑 QQ
- `POST /reset_password/` - 重置密码

### **用户相关** (`/api/v1/users/`)
- `GET /{id}/` - 获取用户信息
- `PUT /{id}/` - 更新用户信息
- `POST /{id}/upload_avatar/` - 上传头像
- `GET /{id}/stats/` - 用户统计

### **旅行相关** (`/api/v1/trips/`)
- `GET /` - 旅行列表
- `POST /` - 创建旅行
- `GET /{slug}/` - 旅行详情
- `PUT /{slug}/` - 更新旅行
- `DELETE /{slug}/` - 删除旅行
- `GET /{slug}/stats/` - 旅行统计

### **评论相关** (`/api/v1/comments/`)
- `GET /` - 评论列表
- `POST /` - 创建评论
- `DELETE /{id}/` - 删除评论
- `POST /{id}/like/` - 点赞评论

### **事件相关** (`/api/v1/events/`)
- `GET /` - 事件列表
- `POST /` - 创建事件
- `GET /{id}/` - 事件详情
- `PUT /{id}/` - 更新事件
- `DELETE /{id}/` - 删除事件

### **Ralendar 集成** (`/api/v1/ralendar/`)
- `GET /sync/` - 同步 Ralendar 数据
- `POST /webhook/` - Ralendar Webhook

---

## 🔐 环境变量

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com

# 数据库
DB_ENGINE=django.db.backends.mysql
DB_NAME=roamio_production
DB_USER=roamio_user
DB_PASSWORD=your-password
DB_HOST=rm-xxx.mysql.rds.aliyuncs.com
DB_PORT=3306

# 腾讯云 COS
TENCENT_COS_SECRET_ID=your-secret-id
TENCENT_COS_SECRET_KEY=your-secret-key
TENCENT_COS_REGION=ap-guangzhou
TENCENT_COS_BUCKET=roamio-media-1326824138

# QQ 互联
QQ_APP_ID=your-app-id
QQ_APP_KEY=your-app-key
QQ_REDIRECT_URI=https://yourdomain.com/auth/qq/callback

# 邮件
EMAIL_HOST=smtp.qq.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@qq.com
EMAIL_HOST_PASSWORD=your-smtp-password
EMAIL_USE_TLS=True
```

---

## 📈 项目复杂度分析

### **复杂度等级**: ⭐⭐⭐⭐ (中高)

### **复杂点**:
1. ✅ **微服务架构**: Roamio + Ralendar 双应用集成
2. ✅ **多种认证方式**: 邮箱注册 + QQ OAuth
3. ✅ **文件存储**: COS 对象存储 + 图片压缩
4. ✅ **数据库迁移**: SQLite → MySQL RDS
5. ✅ **前后端分离**: Vue SPA + Django REST API
6. ✅ **多媒体处理**: 图片/视频上传、压缩、裁剪

### **简化建议**:
1. 🔹 **合并冗余代码**: 部分 ViewSet 可以合并
2. 🔹 **统一错误处理**: 创建全局异常处理器
3. 🔹 **API 版本管理**: 为未来升级预留版本号
4. 🔹 **日志系统**: 使用 Django logging 替代 print
5. 🔹 **缓存优化**: 使用 Redis 缓存热点数据
6. 🔹 **测试覆盖**: 增加单元测试和集成测试

---

## 🎯 未来优化方向

### **短期（1-2 周）**
- [ ] 添加 Redis 缓存
- [ ] 完善错误日志
- [ ] 增加单元测试
- [ ] API 文档自动生成（Swagger）

### **中期（1-2 月）**
- [ ] 消息队列（Celery + Redis）
- [ ] 全文搜索（Elasticsearch）
- [ ] 数据分析面板
- [ ] 移动端适配优化

### **长期（3-6 月）**
- [ ] 微服务拆分（用户服务/旅行服务/事件服务）
- [ ] 容器化部署（Docker + Kubernetes）
- [ ] CI/CD 自动化部署
- [ ] 国际化（i18n）

---

## 📝 维护建议

### **日常维护**
- ✅ 定期备份数据库（每天自动备份）
- ✅ 监控服务器资源（CPU/内存/磁盘）
- ✅ 查看错误日志（`logs/uwsgi.log`）
- ✅ 更新依赖包（安全补丁）

### **代码规范**
- ✅ 遵循 PEP 8（Python）
- ✅ 遵循 Vue 风格指南
- ✅ 使用有意义的变量名
- ✅ 添加必要的注释
- ✅ 提交前运行 linter

### **Git 工作流**
- ✅ `master` 分支：生产环境
- ✅ `dev` 分支：开发环境（建议创建）
- ✅ `feature/*` 分支：新功能开发
- ✅ `hotfix/*` 分支：紧急修复

---

## 🆘 常见问题

### **Q1: 如何添加新的 API 端点？**
1. 在 `backend/api/viewsets/` 创建或修改 ViewSet
2. 在 `backend/api/urls.py` 注册路由
3. 在前端 `web/src/api/` 添加 API 调用函数

### **Q2: 如何修改数据库模型？**
1. 修改 `backend/models/` 中的模型
2. 运行 `python manage.py makemigrations`
3. 运行 `python manage.py migrate`
4. 在服务器上同步执行

### **Q3: 如何部署新版本？**
```bash
# 本地
git add .
git commit -m "feat: your feature"
git push

# 服务器
cd ~/roamio
git pull
pkill -9 -f uwsgi
nohup uwsgi --ini cloud_settings/uwsgi.ini > logs/uwsgi.log 2>&1 &
```

### **Q4: 如何查看错误日志？**
```bash
# 服务器
tail -100 logs/uwsgi.log
tail -100 logs/uwsgi.log | grep ERROR
```

---

## 📞 联系方式

- **项目地址**: https://github.com/ppshuX/roamio
- **生产环境**: http://47.121.137.60
- **开发者**: ppshu

---

**最后更新**: 2025-11-17  
**文档版本**: v1.0

