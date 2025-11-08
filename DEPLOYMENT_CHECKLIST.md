# 🚀 Roamio v2.0 部署检查清单

## 📋 云服务器部署步骤

### 1. 拉取最新代码
```bash
cd ~/roamio
git pull
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 运行数据库迁移
```bash
python3 manage.py migrate
```

### 4. 收集静态文件（如果需要）
```bash
python3 manage.py collectstatic --noinput
```

### 5. 重启 uWSGI
```bash
pkill -f uwsgi
bash scripts/start_uwsgi.sh
```

### 6. 检查服务状态
```bash
# 检查 uWSGI 进程
ps aux | grep uwsgi

# 检查日志
tail -f django_errors.log
```

---

## 🔍 功能检查清单

### ✅ 桌面端（>768px）

- [ ] 旅行编辑页面右侧显示"旅行事项"边栏
- [ ] 可以添加、编辑、删除事项
- [ ] 未登录时显示登录提示
- [ ] 已登录时显示事项列表
- [ ] 空状态显示正确

### ✅ 移动端（≤768px）

- [ ] 旅行编辑页面右下角显示**紫色圆形悬浮按钮**
- [ ] 按钮上有 Ralendar logo
- [ ] 有事项时显示数量徽章
- [ ] 可以拖拽按钮到任意位置
- [ ] 拖拽时底部出现垃圾桶
- [ ] 拖到垃圾桶可以隐藏按钮
- [ ] 点击按钮弹出底部面板
- [ ] 面板显示事项列表
- [ ] 可以在面板中添加、编辑、删除事项

---

## 🐛 常见问题排查

### 问题 1：移动端看不到悬浮按钮

**可能原因：**
1. 浏览器缓存了旧版本
2. 屏幕宽度 > 768px（不算移动端）
3. 不在编辑模式（需要在编辑页面）
4. 按钮被隐藏了（拖到垃圾桶）

**解决方案：**
```bash
# 1. 强制刷新浏览器
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (Mac)

# 2. 清除 localStorage
打开浏览器控制台 (F12)
执行: localStorage.removeItem('ralendar_button_visible')
执行: localStorage.removeItem('ralendar_button_position')

# 3. 检查屏幕宽度
打开浏览器控制台 (F12)
执行: window.innerWidth
确保 <= 768

# 4. 使用浏览器开发者工具的移动设备模拟
F12 → 点击设备切换图标 → 选择手机设备
```

### 问题 2：502 Bad Gateway

**可能原因：**
- uWSGI 没有运行
- 缺少依赖包

**解决方案：**
```bash
# 检查 uWSGI 状态
ps aux | grep uwsgi

# 重启 uWSGI
pkill -f uwsgi
bash scripts/start_uwsgi.sh

# 检查依赖
pip install -r requirements.txt
```

### 问题 3：数据库迁移错误

**可能原因：**
- 旧的迁移文件冲突

**解决方案：**
```bash
# 查看迁移状态
python3 manage.py showmigrations

# 如果有冲突，假迁移
python3 manage.py migrate backend 0018 --fake
```

### 问题 4：静态文件 404

**可能原因：**
- Nginx 配置不正确
- 静态文件路径错误

**解决方案：**
```bash
# 检查 Nginx 配置
cat /etc/nginx/sites-enabled/roamio

# 确保有以下配置：
location /static/ {
    alias /home/acs/roamio/backend/static/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}

# 重启 Nginx
sudo systemctl restart nginx
```

---

## 📱 移动端测试步骤

### 方法 1：使用浏览器开发者工具

1. 打开 Chrome/Edge 浏览器
2. 按 F12 打开开发者工具
3. 点击"切换设备工具栏"图标（或按 Ctrl+Shift+M）
4. 选择一个手机设备（如 iPhone 12 Pro）
5. 访问旅行编辑页面
6. 应该能看到右下角的紫色圆形按钮

### 方法 2：使用真实手机

1. 用手机浏览器访问网站
2. 登录账号
3. 进入任意旅行的编辑页面
4. 应该能看到右下角的紫色圆形按钮

### 测试交互

- ✅ 长按按钮可以拖拽
- ✅ 拖拽时底部出现垃圾桶
- ✅ 拖到垃圾桶松手，按钮消失
- ✅ 点击按钮弹出底部面板
- ✅ 面板可以滚动查看事项
- ✅ 可以添加新事项
- ✅ 可以编辑/删除事项

---

## 🎨 视觉检查

### 悬浮按钮样式

- **形状**：圆形
- **大小**：60×60 px
- **颜色**：渐变紫色 (#667eea → #764ba2)
- **图标**：Ralendar logo (40×40 px)
- **阴影**：柔和的紫色阴影
- **徽章**：红色圆形，显示事项数量

### 底部面板样式

- **位置**：从底部滑入
- **高度**：最高 80vh
- **圆角**：顶部圆角 20px
- **头部**：紫色渐变背景，白色文字
- **内容**：白色背景，可滚动

---

## 📊 性能检查

### 加载速度

```bash
# 检查静态文件大小
du -sh backend/static/

# 检查构建后的文件
du -sh web/dist/
```

### 响应时间

- 页面加载：< 2s
- API 响应：< 500ms
- 拖拽流畅度：60 FPS

---

## ✅ 最终确认

- [ ] 代码已推送到 GitHub
- [ ] 云服务器已拉取最新代码
- [ ] 数据库迁移成功
- [ ] uWSGI 正常运行
- [ ] 桌面端功能正常
- [ ] 移动端悬浮按钮显示
- [ ] 拖拽功能正常
- [ ] 事项管理功能正常
- [ ] 无 JavaScript 错误
- [ ] 无 502/404 错误

---

## 📞 需要帮助？

如果遇到问题，请提供以下信息：

1. **浏览器类型和版本**
2. **屏幕宽度**（执行 `window.innerWidth`）
3. **控制台错误信息**（F12 → Console）
4. **网络请求状态**（F12 → Network）
5. **截图或录屏**

---

**最后更新**: 2025-11-08  
**版本**: Roamio v2.0  
**状态**: ✅ 已完成开发

