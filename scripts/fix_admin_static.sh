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

if [ $? -eq 0 ]; then
    echo "✅ 静态文件收集成功"
else
    echo "❌ 静态文件收集失败"
    exit 1
fi

# 4. 设置权限（让 Nginx 可以访问）
echo ""
echo "设置静态文件权限..."
# 根据实际用户修改（Nginx 通常使用 www-data 或 nginx 用户）
sudo chown -R acs:acs ~/roamio/staticfiles
sudo chmod -R 755 ~/roamio/staticfiles

echo "✅ 权限设置完成"

# 5. 显示收集的静态文件统计
echo ""
echo "=========================================="
echo "静态文件统计"
echo "=========================================="
echo "目录: ~/roamio/staticfiles"
echo "总大小: $(du -sh ~/roamio/staticfiles 2>/dev/null | cut -f1 || echo '未知')"
echo "文件数量: $(find ~/roamio/staticfiles -type f 2>/dev/null | wc -l || echo '0')"
echo ""

# 检查 admin 目录
if [ -d ~/roamio/staticfiles/admin ]; then
    echo "✅ Django Admin 静态文件目录存在"
    echo "Admin CSS 文件："
    ls -lh ~/roamio/staticfiles/admin/css/*.css 2>/dev/null | head -3
    echo "..."
else
    echo "❌ Django Admin 静态文件目录不存在！"
    echo "请检查 INSTALLED_APPS 中是否包含 'django.contrib.admin'"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ 修复完成！"
echo "=========================================="
echo ""
echo "Nginx 配置已存在（/admin-static → staticfiles/）"
echo "请刷新浏览器访问 https://roamio.cn/admin/"
echo ""

