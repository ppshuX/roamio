#!/bin/bash
# 修复 Django Admin 静态文件显示问题

echo "=========================================="
echo "修复 Django Admin 静态文件"
echo "=========================================="

# 1. 进入项目目录
cd ~/roamio || { echo "项目目录不存在"; exit 1; }

# 2. 激活虚拟环境
source venv/bin/activate || { echo "虚拟环境激活失败"; exit 1; }

# 3. 收集静态文件（Django Admin 的 CSS/JS）
echo "正在收集静态文件..."
python manage.py collectstatic --noinput --clear

# 4. 设置权限（让 Nginx 可以访问）
echo "设置静态文件权限..."
sudo chown -R www-data:www-data ~/roamio/staticfiles
sudo chmod -R 755 ~/roamio/staticfiles

# 5. 检查 Nginx 配置
echo ""
echo "=========================================="
echo "检查 Nginx 配置"
echo "=========================================="

NGINX_CONF="/etc/nginx/sites-available/roamio"

# 检查是否存在 admin-static 配置
if grep -q "location /admin-static/" "$NGINX_CONF"; then
    echo "✅ Nginx 已配置 /admin-static/ 路由"
else
    echo "⚠️ Nginx 缺少 /admin-static/ 配置，正在添加..."
    
    # 备份原配置
    sudo cp "$NGINX_CONF" "${NGINX_CONF}.backup.$(date +%Y%m%d_%H%M%S)"
    
    # 在 server 块中添加 admin-static 配置（在 location / 之前）
    sudo sed -i '/location \/ {/i \    # Django Admin 静态文件\n    location /admin-static/ {\n        alias /home/ubuntu/roamio/staticfiles/;\n        expires 30d;\n        add_header Cache-Control "public, immutable";\n    }\n' "$NGINX_CONF"
    
    echo "✅ 已添加 Nginx 配置"
fi

# 6. 测试 Nginx 配置
echo ""
echo "测试 Nginx 配置..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx 配置测试通过"
    
    # 7. 重新加载 Nginx
    echo "重新加载 Nginx..."
    sudo systemctl reload nginx
    
    echo ""
    echo "=========================================="
    echo "✅ 修复完成！"
    echo "=========================================="
    echo ""
    echo "请刷新浏览器访问 https://roamio.cn/admin/"
    echo ""
else
    echo "❌ Nginx 配置测试失败，请手动检查"
    exit 1
fi

# 8. 显示收集的静态文件统计
echo ""
echo "静态文件统计："
echo "总大小: $(du -sh ~/roamio/staticfiles | cut -f1)"
echo "文件数量: $(find ~/roamio/staticfiles -type f | wc -l)"
echo ""
echo "Django Admin 静态文件:"
ls -lh ~/roamio/staticfiles/admin/ 2>/dev/null || echo "未找到 admin 目录"

