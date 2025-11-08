#!/bin/bash
# ==========================================
# Roamio RDS 迁移部署脚本
# ==========================================
# 在服务器上执行此脚本完成数据库迁移
# ==========================================

set -e

echo "=========================================="
echo "🚀 Roamio RDS 迁移部署"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 步骤 1：检查当前目录
echo -e "${BLUE}📂 步骤 1：检查当前目录${NC}"
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ 错误：请在 roamio 项目根目录下执行此脚本${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 当前目录正确${NC}"
echo ""

# 步骤 2：备份 SQLite 数据库
echo -e "${BLUE}💾 步骤 2：备份 SQLite 数据库${NC}"
if [ -f "db.sqlite3" ]; then
    BACKUP_FILE="db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)"
    cp db.sqlite3 "$BACKUP_FILE"
    echo -e "${GREEN}✅ 已备份到: $BACKUP_FILE${NC}"
else
    echo -e "${YELLOW}⚠️  db.sqlite3 不存在，跳过备份${NC}"
fi
echo ""

# 步骤 3：安装系统依赖
echo -e "${BLUE}📦 步骤 3：安装系统依赖${NC}"
echo "正在安装 MySQL 客户端和开发库..."
sudo apt update
sudo apt install -y mysql-client libmysqlclient-dev pkg-config python3-dev build-essential
echo -e "${GREEN}✅ 系统依赖已安装${NC}"
echo ""

# 步骤 4：安装 Python MySQL 驱动（使用国内镜像）
echo -e "${BLUE}📦 步骤 4：安装 Python MySQL 驱动${NC}"
echo "使用清华镜像源..."
pip3 install mysqlclient -i https://pypi.tuna.tsinghua.edu.cn/simple --timeout 120 || \
pip3 install mysqlclient -i https://mirrors.aliyun.com/pypi/simple/ --timeout 120 || \
pip3 install mysqlclient -i https://pypi.douban.com/simple --timeout 120

# 验证安装
if python3 -c "import MySQLdb" 2>/dev/null; then
    echo -e "${GREEN}✅ mysqlclient 已安装${NC}"
else
    echo -e "${RED}❌ mysqlclient 安装失败${NC}"
    exit 1
fi
echo ""

# 步骤 5：测试 RDS 连接
echo -e "${BLUE}🔌 步骤 5：测试 RDS 连接${NC}"
if mysql -h rm-wz91m3g4wa6io3dfi8o.mysql.rds.aliyuncs.com \
         -P 3306 \
         -u roamio_user \
         -p'Roamio@2025!Pass' \
         -e "SELECT 1;" roamio_production &> /dev/null; then
    echo -e "${GREEN}✅ RDS 连接成功！${NC}"
else
    echo -e "${RED}❌ RDS 连接失败！${NC}"
    echo "请检查："
    echo "1. 白名单是否包含服务器 IP"
    echo "2. 网络是否畅通"
    exit 1
fi
echo ""

# 步骤 6：运行数据库迁移
echo -e "${BLUE}🔄 步骤 6：运行数据库迁移${NC}"
echo "正在创建表结构..."
python3 manage.py migrate
echo -e "${GREEN}✅ 数据库迁移完成${NC}"
echo ""

# 步骤 7：导出 SQLite 数据（如果存在）
echo -e "${BLUE}💾 步骤 7：导出 SQLite 数据${NC}"
if [ -f "db.sqlite3" ]; then
    echo "正在导出数据..."
    
    # 临时切换回 SQLite
    if [ -f "roamio/settings.py.rds" ]; then
        cp roamio/settings.py roamio/settings.py.rds
    fi
    
    # 创建临时 SQLite 配置
    python3 << 'EOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roamio.settings')

# 临时修改数据库配置
from django.conf import settings
settings.DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

django.setup()
from django.core.management import call_command
call_command('dumpdata', 
    '--natural-foreign', 
    '--natural-primary',
    '--exclude', 'auth.permission',
    '--exclude', 'contenttypes',
    '--indent', '2',
    output='data_backup.json')
print("✅ 数据导出完成: data_backup.json")
EOF
    
    echo -e "${GREEN}✅ SQLite 数据已导出${NC}"
else
    echo -e "${YELLOW}⚠️  db.sqlite3 不存在，跳过数据导出${NC}"
fi
echo ""

# 步骤 8：导入数据到 RDS
echo -e "${BLUE}📥 步骤 8：导入数据到 RDS${NC}"
if [ -f "data_backup.json" ]; then
    echo "正在导入数据..."
    python3 manage.py loaddata data_backup.json
    echo -e "${GREEN}✅ 数据已导入到 RDS${NC}"
else
    echo -e "${YELLOW}⚠️  data_backup.json 不存在，跳过数据导入${NC}"
fi
echo ""

# 步骤 9：验证数据
echo -e "${BLUE}✅ 步骤 9：验证数据${NC}"
python3 << 'EOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roamio.settings')
django.setup()

from django.contrib.auth.models import User
from trips.models import Trip, Comment

print(f"用户数量: {User.objects.count()}")
print(f"旅行数量: {Trip.objects.count()}")
print(f"评论数量: {Comment.objects.count()}")
EOF
echo -e "${GREEN}✅ 数据验证完成${NC}"
echo ""

# 步骤 10：重启服务
echo -e "${BLUE}🔄 步骤 10：重启服务${NC}"
echo "正在重启 uWSGI..."
if [ -f "/etc/systemd/system/uwsgi.service" ]; then
    sudo systemctl restart uwsgi
    echo -e "${GREEN}✅ uWSGI 已重启${NC}"
else
    echo -e "${YELLOW}⚠️  未找到 uWSGI 服务，请手动重启${NC}"
fi
echo ""

# 完成
echo "=========================================="
echo -e "${GREEN}🎉 RDS 迁移完成！${NC}"
echo "=========================================="
echo ""
echo "📋 迁移摘要："
echo "  - SQLite 数据已备份"
echo "  - RDS 表结构已创建"
echo "  - 数据已导入到 RDS"
echo "  - 服务已重启"
echo ""
echo "🔍 下一步："
echo "  1. 访问应用测试功能"
echo "  2. 检查日志: tail -f logs/uwsgi.log"
echo "  3. 如有问题，可恢复 SQLite: cp $BACKUP_FILE db.sqlite3"
echo ""

