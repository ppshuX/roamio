#!/bin/bash
# ==========================================
# Roamio RDS 配置脚本
# ==========================================
# 执行时间：2025-11-08
# 用途：快速配置 Roamio 使用 RDS MySQL
# ==========================================

set -e  # 遇到错误立即退出

echo "=========================================="
echo "🚀 Roamio RDS 配置工具"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 步骤 1：检查 MySQL 客户端
echo "📦 步骤 1：检查依赖..."
if ! command -v mysql &> /dev/null; then
    echo -e "${YELLOW}⚠️  MySQL 客户端未安装${NC}"
    echo "   正在安装..."
    sudo apt update
    sudo apt install mysql-client -y
    echo -e "${GREEN}✅ MySQL 客户端已安装${NC}"
else
    echo -e "${GREEN}✅ MySQL 客户端已安装${NC}"
fi
echo ""

# 步骤 2：检查 Python MySQL 驱动
echo "📦 步骤 2：检查 Python MySQL 驱动..."
if ! python -c "import MySQLdb" 2>/dev/null && ! python -c "import pymysql" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Python MySQL 驱动未安装${NC}"
    echo "   正在安装 mysqlclient..."
    pip install mysqlclient
    echo -e "${GREEN}✅ mysqlclient 已安装${NC}"
else
    echo -e "${GREEN}✅ Python MySQL 驱动已安装${NC}"
fi
echo ""

# 步骤 3：备份 settings.py
echo "💾 步骤 3：备份 settings.py..."
if [ -f "roamio/settings.py" ]; then
    BACKUP_FILE="roamio/settings.py.backup.$(date +%Y%m%d_%H%M%S)"
    cp roamio/settings.py "$BACKUP_FILE"
    echo -e "${GREEN}✅ 已备份到: $BACKUP_FILE${NC}"
else
    echo -e "${RED}❌ settings.py 不存在！${NC}"
    exit 1
fi
echo ""

# 步骤 4：测试 RDS 连接
echo "🔌 步骤 4：测试 RDS 连接..."
if mysql -h rm-wz91m3g4wa6io3dfi8o.mysql.rds.aliyuncs.com \
         -P 3306 \
         -u roamio_user \
         -p'Roamio@2025!Pass' \
         -e "SELECT 1;" roamio_production &> /dev/null; then
    echo -e "${GREEN}✅ RDS 连接成功！${NC}"
else
    echo -e "${RED}❌ RDS 连接失败！${NC}"
    echo "   请检查："
    echo "   1. 白名单是否包含服务器 IP"
    echo "   2. 用户名和密码是否正确"
    echo "   3. 网络是否畅通"
    exit 1
fi
echo ""

# 步骤 5：显示配置信息
echo "=========================================="
echo "📋 RDS 配置信息"
echo "=========================================="
echo "数据库主机: rm-wz91m3g4wa6io3dfi8o.mysql.rds.aliyuncs.com"
echo "数据库端口: 3306"
echo "数据库名称: roamio_production"
echo "用户名称: roamio_user"
echo "密码: Roamio@2025!Pass"
echo ""

# 步骤 6：提示下一步操作
echo "=========================================="
echo "📝 下一步操作"
echo "=========================================="
echo "1. 更新 roamio/settings.py 中的 DATABASES 配置"
echo "2. 运行: python manage.py migrate"
echo "3. 导出 SQLite 数据（如果需要）"
echo "4. 导入数据到 RDS"
echo "5. 测试应用功能"
echo ""
echo "详细步骤请参考: docs/RDS_MIGRATION_GUIDE.md"
echo ""
echo -e "${GREEN}✅ 配置检查完成！${NC}"
echo "=========================================="

