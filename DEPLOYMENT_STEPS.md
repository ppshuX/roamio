# 🚀 公共静态资源部署步骤

> **重要**: 这是本地部署说明，**不要提交到 Git**

---

## 📋 部署步骤

### 1. 重新构建前端

```bash
cd ~/roamio/web
npm run build
```

### 2. 更新 Nginx 配置

```bash
# 备份当前配置
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup

# 编辑 Nginx 配置
sudo vim /etc/nginx/nginx.conf
```

**在第 130 行后面添加以下内容**（在 `/admin-static` 配置之后，`/wss` 配置之前）：

```nginx
        # ============================================================
        # ⭐ 公共静态资源（新增）
        # 供 Roamio 生态所有产品使用的公共资源
        # ============================================================
        location /static/ {
            alias /home/acs/roamio/backend/static/;
            
            # 长期缓存（30天，资源不常变）
            expires 30d;
            add_header Cache-Control "public, immutable";
            
            # CORS 配置（允许跨域访问，供 Ralendar 等使用）
            add_header Access-Control-Allow-Origin *;
            add_header Access-Control-Allow-Methods "GET, OPTIONS";
            add_header Access-Control-Allow-Headers "Origin, Content-Type, Accept";
            
            # 安全头
            add_header X-Content-Type-Options "nosniff";
            
            # 关闭访问日志（减少 I/O）
            access_log off;
        }
```

### 3. 测试 Nginx 配置

```bash
# 测试配置是否正确
sudo nginx -t
```

**如果显示 `syntax is ok` 和 `test is successful`，继续下一步。**

### 4. 重启 Nginx

```bash
sudo systemctl reload nginx
```

### 5. 验证资源可访问

```bash
# 测试图片
curl -I https://app7508.acapp.acwing.com.cn/static/images/logo_Roamio.png

# 测试音乐
curl -I https://app7508.acapp.acwing.com.cn/static/audios/rain.mp3

# 应该返回 200 OK
```

### 6. 浏览器测试

访问以下 URL，确保资源正常显示：

- https://app7508.acapp.acwing.com.cn/static/images/logo_Roamio.png
- https://app7508.acapp.acwing.com.cn/static/images/qq_login.png
- https://app7508.acapp.acwing.com.cn/static/images/default_avatar.png
- https://app7508.acapp.acwing.com.cn/static/audios/rain.mp3

### 7. 测试前端功能

- ✅ 登录页面：QQ 登录图标显示正常
- ✅ 注册页面：QQ 登录图标显示正常
- ✅ 用户中心：默认头像显示正常
- ✅ 旅行详情：背景音乐播放正常
- ✅ 编辑器：音乐选择正常

---

## ⚠️ 如果遇到 404 错误

### 检查文件是否存在

```bash
ls -lh ~/roamio/backend/static/images/
ls -lh ~/roamio/backend/static/audios/
```

### 检查 Nginx 配置

```bash
# 查看 Nginx 配置
sudo nginx -T | grep -A 10 "location /static/"

# 确认 alias 路径正确
# 应该是：alias /home/acs/roamio/backend/static/;
```

### 检查文件权限

```bash
# 确保 Nginx 可以读取文件
sudo chmod -R 755 ~/roamio/backend/static/
```

---

## 🔄 回滚方案

如果出现问题，可以快速回滚：

```bash
# 恢复备份的 Nginx 配置
sudo cp /etc/nginx/nginx.conf.backup /etc/nginx/nginx.conf

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl reload nginx
```

---

## ✅ 部署完成检查清单

- [ ] 前端重新构建（`npm run build`）
- [ ] Nginx 配置已更新
- [ ] Nginx 配置测试通过（`nginx -t`）
- [ ] Nginx 已重启
- [ ] 图片资源可访问（`/static/images/`）
- [ ] 音乐资源可访问（`/static/audios/`）
- [ ] QQ 登录图标显示正常
- [ ] 默认头像显示正常
- [ ] 背景音乐播放正常

---

**部署完成后，删除此文件！**

```bash
rm ~/roamio/DEPLOYMENT_STEPS.md
```

