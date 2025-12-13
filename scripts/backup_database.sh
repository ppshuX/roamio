#!/bin/bash
# 腾讯云 MySQL 数据库备份脚本
# 使用方法: ./backup_database.sh

set -e

# 配置信息（从 settings.py 获取）
DB_HOST="gz-cdb-k9ylziyr.sql.tencentcdb.com"
DB_PORT="23768"
DB_NAME="roamio_production"
DB_USER="roamio_user"
DB_PASSWORD="Roamio@2025!Pass"

# 备份目录（使用用户目录，避免权限问题）
BACKUP_DIR="${HOME}/backup/roamio_db"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/roamio_backup_${DATE}.sql"

# 创建备份目录
mkdir -p ${BACKUP_DIR}

echo "====================================="
echo "🗄️  Roamio 数据库备份脚本"
echo "====================================="
echo "数据库: ${DB_NAME}"
echo "主机: ${DB_HOST}:${DB_PORT}"
echo "备份文件: ${BACKUP_FILE}"
echo ""

# 执行备份
echo "⏳ 正在备份数据库..."
mysqldump -h ${DB_HOST} -P ${DB_PORT} -u ${DB_USER} -p${DB_PASSWORD} \
    --single-transaction \
    --routines \
    --triggers \
    --events \
    ${DB_NAME} > ${BACKUP_FILE}

# 压缩备份文件
echo "📦 正在压缩备份文件..."
gzip ${BACKUP_FILE}
BACKUP_FILE_GZ="${BACKUP_FILE}.gz"

# 显示备份文件信息
BACKUP_SIZE=$(du -h ${BACKUP_FILE_GZ} | cut -f1)
echo ""
echo "✅ 备份完成！"
echo "备份文件: ${BACKUP_FILE_GZ}"
echo "文件大小: ${BACKUP_SIZE}"
echo ""

# 清理旧备份（保留最近7天的备份）
echo "🧹 清理7天前的旧备份..."
find ${BACKUP_DIR} -name "roamio_backup_*.sql.gz" -mtime +7 -delete
echo "✅ 清理完成"
echo ""

# 列出当前备份
echo "📋 当前备份列表："
ls -lh ${BACKUP_DIR}/roamio_backup_*.sql.gz 2>/dev/null || echo "暂无备份文件"
echo ""

echo "====================================="
echo "✅ 备份任务完成！"
echo "====================================="

