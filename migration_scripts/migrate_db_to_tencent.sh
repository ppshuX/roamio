#!/bin/bash
# ========================================
# Roamio 数据库迁移脚本
# 从阿里云 RDS 迁移到腾讯云 MySQL
# 日期：2025-11-13
# ========================================

set -e  # 遇到错误立即停止

echo "========================================="
echo "🔄 Roamio 数据库迁移开始"
echo "========================================="
echo ""

# ==================== 配置信息 ====================
# 阿里云数据库（源）
SOURCE_HOST="rm-wz91m3g4wa6io3dfi8o.mysql.rds.aliyuncs.com"
SOURCE_USER="roamio_user"
SOURCE_PASS="Roamio@2025!Pass"
SOURCE_DB="roamio_production"

# 腾讯云数据库（目标）
TARGET_HOST="gz-cdb-k9ylziyr.sql.tencentcdb.com"  # 外网地址（用于迁移）
TARGET_USER="roamio_user"
TARGET_PASS="Roamio@2025!Pass"
TARGET_DB="roamio_production"

# 备份文件
BACKUP_FILE="aliyun_backup_$(date +%Y%m%d_%H%M%S).sql"
BACKUP_DIR="$HOME/roamio_backups"

# ==================== 步骤 1：创建备份目录 ====================
echo "📁 步骤 1：创建备份目录"
mkdir -p "$BACKUP_DIR"
cd "$BACKUP_DIR"
echo "✅ 备份目录：$BACKUP_DIR"
echo ""

# ==================== 步骤 2：备份阿里云数据库 ====================
echo "💾 步骤 2：备份阿里云数据库"
echo "正在导出数据..."

mysqldump -h "$SOURCE_HOST" \
  -u "$SOURCE_USER" \
  -p"$SOURCE_PASS" \
  --databases "$SOURCE_DB" \
  --single-transaction \
  --routines \
  --triggers \
  --events \
  --set-gtid-purged=OFF \
  > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(ls -lh "$BACKUP_FILE" | awk '{print $5}')
    echo "✅ 备份成功：$BACKUP_FILE（大小：$BACKUP_SIZE）"
else
    echo "❌ 备份失败！请检查阿里云数据库连接"
    exit 1
fi
echo ""

# ==================== 步骤 3：验证备份文件 ====================
echo "🔍 步骤 3：验证备份文件"
if [ ! -s "$BACKUP_FILE" ]; then
    echo "❌ 备份文件为空！"
    exit 1
fi

# 检查备份文件中的关键信息
echo "备份文件包含的表："
grep "CREATE TABLE" "$BACKUP_FILE" | head -10
echo ""

# ==================== 步骤 4：测试腾讯云数据库连接 ====================
echo "🔌 步骤 4：测试腾讯云数据库连接"
mysql -h "$TARGET_HOST" \
  -P 3306 \
  -u "$TARGET_USER" \
  -p"$TARGET_PASS" \
  -e "SELECT VERSION();" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ 腾讯云数据库连接成功"
else
    echo "❌ 腾讯云数据库连接失败！请检查："
    echo "   - 外网地址是否正确"
    echo "   - 账号密码是否正确"
    echo "   - 安全组是否允许本机IP访问"
    exit 1
fi
echo ""

# ==================== 步骤 5：检查腾讯云数据库是否为空 ====================
echo "🔍 步骤 5：检查目标数据库状态"
EXISTING_TABLES=$(mysql -h "$TARGET_HOST" \
  -P 3306 \
  -u "$TARGET_USER" \
  -p"$TARGET_PASS" \
  -e "USE $TARGET_DB; SHOW TABLES;" 2>/dev/null | wc -l)

if [ "$EXISTING_TABLES" -gt 1 ]; then
    echo "⚠️  警告：目标数据库已存在 $((EXISTING_TABLES - 1)) 个表"
    echo "是否继续导入？这会覆盖现有数据。(yes/no)"
    read -r CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        echo "❌ 用户取消操作"
        exit 0
    fi
else
    echo "✅ 目标数据库为空，可以安全导入"
fi
echo ""

# ==================== 步骤 6：导入数据到腾讯云 ====================
echo "📥 步骤 6：导入数据到腾讯云 MySQL"
echo "正在导入数据（可能需要 5-10 分钟）..."

mysql -h "$TARGET_HOST" \
  -P 3306 \
  -u "$TARGET_USER" \
  -p"$TARGET_PASS" \
  < "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ 数据导入成功"
else
    echo "❌ 数据导入失败！"
    echo "备份文件仍在：$BACKUP_DIR/$BACKUP_FILE"
    echo "可以手动重试"
    exit 1
fi
echo ""

# ==================== 步骤 7：验证数据完整性 ====================
echo "✅ 步骤 7：验证数据完整性"

# 统计用户数
USER_COUNT=$(mysql -h "$TARGET_HOST" \
  -P 3306 \
  -u "$TARGET_USER" \
  -p"$TARGET_PASS" \
  -e "USE $TARGET_DB; SELECT COUNT(*) FROM auth_user;" 2>/dev/null | tail -1)

# 统计旅行数
TRIP_COUNT=$(mysql -h "$TARGET_HOST" \
  -P 3306 \
  -u "$TARGET_USER" \
  -p"$TARGET_PASS" \
  -e "USE $TARGET_DB; SELECT COUNT(*) FROM backend_trip;" 2>/dev/null | tail -1)

# 统计评论数
COMMENT_COUNT=$(mysql -h "$TARGET_HOST" \
  -P 3306 \
  -u "$TARGET_USER" \
  -p"$TARGET_PASS" \
  -e "USE $TARGET_DB; SELECT COUNT(*) FROM backend_comment;" 2>/dev/null | tail -1)

echo "数据统计："
echo "  - 用户数：$USER_COUNT"
echo "  - 旅行数：$TRIP_COUNT"
echo "  - 评论数：$COMMENT_COUNT"
echo ""

# ==================== 完成 ====================
echo "========================================="
echo "🎉 数据库迁移完成！"
echo "========================================="
echo ""
echo "📋 下一步操作："
echo "1. 修改 settings.py 中的数据库配置"
echo "2. 使用内网地址：172.16.0.11"
echo "3. Git 提交并推送"
echo "4. 服务器上 git pull + 重启 uWSGI"
echo "5. 测试网站功能"
echo ""
echo "💾 备份文件保存在："
echo "   $BACKUP_DIR/$BACKUP_FILE"
echo ""
echo "🔙 如需回滚，修改 settings.py 改回阿里云地址即可"
echo ""

