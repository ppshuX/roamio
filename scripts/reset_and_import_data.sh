#!/bin/bash
# ==========================================
# 重置 RDS 数据库并导入数据
# ==========================================
# 用于解决数据导入时的主键冲突问题
# ==========================================

set -e

echo "=========================================="
echo "🔄 重置 RDS 数据库并导入数据"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 数据库连接信息
DB_HOST="rm-wz91m3g4wa6io3dfi8o.mysql.rds.aliyuncs.com"
DB_PORT="3306"
DB_USER="roamio_user"
DB_PASS="Roamio@2025!Pass"
DB_NAME="roamio_production"

# 步骤 1：确认操作
echo -e "${YELLOW}⚠️  警告：此操作将清空 RDS 数据库中的所有数据！${NC}"
echo ""
read -p "确认要继续吗？(yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${RED}❌ 操作已取消${NC}"
    exit 0
fi
echo ""

# 步骤 2：删除所有表（保留结构）
echo -e "${BLUE}🗑️  步骤 1：清空数据库表${NC}"
echo "正在删除所有数据..."

mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" << 'EOF'
SET FOREIGN_KEY_CHECKS = 0;

-- 删除所有表的数据
TRUNCATE TABLE auth_user;
TRUNCATE TABLE auth_group;
TRUNCATE TABLE auth_permission;
TRUNCATE TABLE django_content_type;
TRUNCATE TABLE django_session;
TRUNCATE TABLE django_admin_log;
TRUNCATE TABLE backend_userprofile;
TRUNCATE TABLE backend_socialaccount;
TRUNCATE TABLE backend_emailverification;
TRUNCATE TABLE backend_trip;
TRUNCATE TABLE backend_comment;
TRUNCATE TABLE backend_sitestat;

SET FOREIGN_KEY_CHECKS = 1;
EOF

echo -e "${GREEN}✅ 数据库已清空${NC}"
echo ""

# 步骤 3：重新运行迁移（确保表结构正确）
echo -e "${BLUE}📦 步骤 2：重新运行数据库迁移${NC}"
python3 manage.py migrate --fake-initial
echo -e "${GREEN}✅ 迁移完成${NC}"
echo ""

# 步骤 4：导入数据
echo -e "${BLUE}📥 步骤 3：导入数据${NC}"
if [ -f "data_backup.json" ]; then
    echo "正在导入数据..."
    python3 manage.py loaddata data_backup.json
    echo -e "${GREEN}✅ 数据导入成功${NC}"
else
    echo -e "${RED}❌ 错误：data_backup.json 不存在${NC}"
    exit 1
fi
echo ""

# 步骤 5：验证数据
echo -e "${BLUE}✅ 步骤 4：验证数据${NC}"
python3 << 'EOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roamio.settings')
django.setup()

from django.contrib.auth.models import User
from backend.models import Trip, Comment, UserProfile

print(f"用户数量: {User.objects.count()}")
print(f"用户资料数量: {UserProfile.objects.count()}")
print(f"旅行数量: {Trip.objects.count()}")
print(f"评论数量: {Comment.objects.count()}")
EOF
echo -e "${GREEN}✅ 数据验证完成${NC}"
echo ""

# 完成
echo "=========================================="
echo -e "${GREEN}🎉 数据导入完成！${NC}"
echo "=========================================="

