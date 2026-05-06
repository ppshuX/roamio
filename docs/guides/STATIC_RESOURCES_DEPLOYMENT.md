# 📦 公共静态资源部署指南

> **版本**: v1.0.0  
> **更新日期**: 2025-11-07  
> **适用项目**: Roamio 生态系统

---

## 🎯 设计理念

将公共资源（Logo、图标、音乐等）统一放在 `backend/static/` 目录，供所有生态产品共享使用。

### **优势**

1. ✅ **统一管理** - 所有公共资源在一个地方
2. ✅ **跨项目共享** - Roamio、Ralendar、Rote 等都可以使用
3. ✅ **版本控制** - 资源更新时，所有项目自动同步
4. ✅ **减少冗余** - 避免在每个项目中重复存储

---

## 📂 目录结构

```
backend/static/
├── images/                      # 公共图片
│   ├── logo_Roamio.png         # Roamio Logo
│   ├── logo_Ralendar.png       # Ralendar Logo（未来）
│   ├── qq_login.png            # QQ 登录图标
│   ├── qq_logo.png             # QQ Logo
│   ├── default_avatar.png      # 默认头像
│   └── favicon.png             # 网站图标
├── audios/                      # 公共音乐
│   ├── rain.mp3                # 雨声
│   ├── road.mp3                # 路途
│   └── windy.mp3               # 风声
└── videos/                      # 公共视频（未来）
    └── (待添加)
```

---

## 🔧 Django 配置

### settings.py

```python
# Static files (CSS, JavaScript, Images)
# 
# 前后端分离架构：
# - 前端静态文件: backend/web_dist/ (由 Vite 构建，Nginx 直接访问)
# - Django Admin 静态文件: staticfiles/ (由 collectstatic 收集)
# - 公共资源: backend/static/ (跨项目共享，由 Nginx 直接访问)

STATIC_URL = '/admin-static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# ⭐ 公共静态资源目录（跨项目共享）
# 这些资源会被提交到 Git，供 Roamio、Ralendar 等所有生态产品使用
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'backend/static'),  # 公共资源：images, audios, videos
    os.path.join(BASE_DIR, 'backend', 'web_dist'),  # Vite 前端构建输出
]
```

---

## 🌐 Nginx 配置

### 方案 A：直接访问（推荐）⭐

```nginx
server {
    listen 443 ssl;
    server_name roamio.cn;
    
    # SSL 证书
    ssl_certificate /etc/letsencrypt/live/roamio.cn/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/roamio.cn/privkey.pem;
    
    # ==================== 前端静态文件 ====================
    location / {
        root /home/acs/roamio/backend/web_dist;
        try_files $uri $uri/ /index.html;
        
        # 缓存策略
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
    
    # ==================== 公共静态资源 ⭐ ====================
    # 供所有生态产品使用的公共资源
    location /static/ {
        alias /home/acs/roamio/backend/static/;
        
        # 长期缓存（资源不常变）
        expires 30d;
        add_header Cache-Control "public, immutable";
        
        # CORS 配置（允许跨域访问）
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, OPTIONS";
        add_header Access-Control-Allow-Headers "Origin, Content-Type, Accept";
        
        # 安全头
        add_header X-Content-Type-Options "nosniff";
    }
    
    # ==================== Django Admin 静态文件 ====================
    location /admin-static/ {
        alias /home/acs/roamio/staticfiles/;
        expires 7d;
    }
    
    # ==================== API 接口 ====================
    location /api/ {
        include uwsgi_params;
        uwsgi_pass 127.0.0.1:8000;
        uwsgi_read_timeout 300;
        
        # 传递真实 IP
        uwsgi_param HTTP_X_FORWARDED_FOR $proxy_add_x_forwarded_for;
        uwsgi_param HTTP_X_REAL_IP $remote_addr;
    }
    
    # ==================== 媒体文件（用户上传）====================
    location /media/ {
        alias /home/acs/roamio/media/;
        expires 7d;
    }
}
```

### 方案 B：通过 Django 服务（不推荐）

```nginx
# 不推荐：会增加 Django 负担
location /static/ {
    include uwsgi_params;
    uwsgi_pass 127.0.0.1:8000;
}
```

---

## 🔗 访问路径

### **前端引用**

```javascript
// Vue 组件中
<img src="/static/images/logo_Roamio.png" alt="Roamio Logo">
<audio src="/static/audios/rain.mp3"></audio>

// JavaScript 中
const logoUrl = '/static/images/logo_Roamio.png'
const musicUrl = '/static/audios/rain.mp3'
```

### **后端引用**

```python
# Django 模型中
def get_avatar_url(self):
    if self.avatar:
        return self.avatar
    else:
        return '/static/images/default_avatar.png'

# 邮件模板中
<img src="https://roamio.cn/static/images/logo_Roamio.png">
```

### **Ralendar 引用（未来）**

```kotlin
// Android Kotlin 中
val logoUrl = "https://roamio.cn/static/images/logo_Roamio.png"
val ralendarLogoUrl = "https://roamio.cn/static/images/logo_Ralendar.png"

// 使用 Glide 加载
Glide.with(context)
    .load(logoUrl)
    .into(imageView)
```

---

## 🚀 部署步骤

### 1. 本地开发

```bash
# 确保资源已复制到 backend/static/
ls backend/static/images/
ls backend/static/audios/

# 运行 collectstatic（会将 backend/static/ 复制到 staticfiles/）
cd backend && python manage.py collectstatic --noinput
```

### 2. 服务器部署

```bash
cd ~/roamio

# 拉取最新代码
git pull

# 收集静态文件
cd backend && python3 manage.py collectstatic --noinput

# 重启服务
uwsgi --reload /tmp/roamio-uwsgi.pid
sudo systemctl reload nginx
```

### 3. 验证资源

```bash
# 检查文件是否存在
ls ~/roamio/backend/static/images/
ls ~/roamio/backend/static/audios/

# 测试访问
curl https://roamio.cn/static/images/logo_Roamio.png -I
curl https://roamio.cn/static/audios/rain.mp3 -I
```

---

## 📊 资源清单

### 当前资源

| 类型 | 文件名 | 大小 | 用途 |
|------|--------|------|------|
| 图片 | logo_Roamio.png | ~50KB | Roamio Logo |
| 图片 | qq_login.png | ~5KB | QQ 登录图标 |
| 图片 | qq_logo.png | ~10KB | QQ Logo |
| 图片 | default_avatar.png | ~20KB | 默认头像 |
| 图片 | favicon.png | ~5KB | 网站图标 |
| 音乐 | rain.mp3 | ~1MB | 雨声背景音乐 |
| 音乐 | road.mp3 | ~1MB | 路途背景音乐 |
| 音乐 | windy.mp3 | ~1MB | 风声背景音乐 |

**总计**: ~3.1MB

### 未来资源（规划）

| 类型 | 文件名 | 用途 |
|------|--------|------|
| 图片 | logo_Ralendar.png | Ralendar Logo |
| 图片 | logo_Rote.png | Rote Logo |
| 图片 | logo_Rapture.png | Rapture Logo |
| 视频 | intro.mp4 | 产品介绍视频 |

---

## ⚠️ 注意事项

### 1. .gitignore 配置

确保 `backend/static/` 会被提交：

```gitignore
# 排除 collectstatic 收集的文件
/staticfiles/

# 但保留后端公共资源（提交到 Git）
!backend/static/
```

### 2. 缓存策略

- **公共资源**：30 天缓存（不常变）
- **前端资源**：7 天缓存（可能更新）
- **API 响应**：不缓存

### 3. CORS 配置

如果 Ralendar 在不同域名，需要配置 CORS：

```nginx
add_header Access-Control-Allow-Origin *;
```

### 4. 资源更新

如果更新了公共资源：

```bash
# 1. 提交到 Git
git add backend/static/
git commit -m "update: logo_Roamio.png"
git push

# 2. 服务器拉取
cd ~/roamio
git pull

# 3. 构建前端 SPA 到 backend/web_dist/
cd frontend/web
npm install
npm run build
cd ../..

# 4. 重新收集 Django Admin 静态文件
cd backend && python3 manage.py collectstatic --noinput

# 5. 清除 CDN 缓存（如果使用了 CDN）
# 或等待缓存自动过期
```

---

## 🌍 跨项目使用示例

### Roamio Web

```vue
<!-- LoginView.vue -->
<img src="/static/images/qq_login.png" alt="QQ登录">
```

### Ralendar Android

```kotlin
// MainActivity.kt
val roamioLogoUrl = "https://roamio.cn/static/images/logo_Roamio.png"
val ralendarLogoUrl = "https://roamio.cn/static/images/logo_Ralendar.png"

Glide.with(this)
    .load(roamioLogoUrl)
    .into(binding.ivLogo)
```

### Rote Web（未来）

```html
<!-- index.html -->
<link rel="icon" href="https://roamio.cn/static/images/favicon.png">
```

---

## ✅ 检查清单

部署前确认：

- [ ] `backend/static/` 目录已创建
- [ ] `frontend/web` 已执行 `npm run build`
- [ ] `backend/web_dist/index.html` 已生成
- [ ] 公共资源已复制到对应目录
- [ ] Django `STATICFILES_DIRS` 已配置
- [ ] `.gitignore` 已更新
- [ ] 前端代码路径已更新
- [ ] 邮件模板路径已更新
- [ ] Nginx 配置已更新
- [ ] 测试所有资源可访问

部署后验证：

- [ ] 访问 `/static/images/logo_Roamio.png` 正常
- [ ] 访问 `/static/audios/rain.mp3` 正常
- [ ] QQ 登录图标显示正常
- [ ] 默认头像显示正常
- [ ] 背景音乐播放正常
- [ ] 邮件中的 Logo 显示正常

---

## 📞 联系方式

- **邮箱**: 2064747320@qq.com
- **项目地址**: https://github.com/ppshuX/roamio

---

**最后更新**: 2025-11-07  
**维护者**: Roamio Team

