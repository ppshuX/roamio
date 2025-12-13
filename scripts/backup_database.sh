#!/bin/bash
# 腾讯云 MySQL 数据库备份脚本
# 使用方法: ./backup_database.sh
# 
# 配置说明：
# 从环境变量读取数据库配置，如果没有设置则使用默认值
# 建议在服务器上创建 ~/.roamio_db_config 文件并设置环境变量

set -e

# 从环境变量读取配置（如果存在配置文件则加载）
if [ -f ~/.roamio_db_config ]; then
    source ~/.roamio_db_config
fi

# 配置信息（从环境变量读取，如果没有则提示错误）
DB_HOST="${DB_HOST:-}"
DB_PORT="${DB_PORT:-}"
DB_NAME="${DB_NAME:-roamio_production}"
DB_USER="${DB_USER:-}"
DB_PASSWORD="${DB_PASSWORD:-}"

# 检查必要的配置
if [ -z "$DB_HOST" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
    echo "❌ 错误: 缺少数据库配置信息"
    echo ""
    echo "请设置环境变量或创建 ~/.roamio_db_config 文件："
    echo "  export DB_HOST='your-db-host'"
    echo "  export DB_PORT='your-db-port'"
    echo "  export DB_USER='your-db-user'"
    echo "  export DB_PASSWORD='your-db-password'"
    echo ""
    echo "或者创建 ~/.roamio_db_config 文件："
    echo "  DB_HOST='your-db-host'"
    echo "  DB_PORT='your-db-port'"
    echo "  DB_USER='your-db-user'"
    echo "  DB_PASSWORD='your-db-password'"
    exit 1
fi

# 备份目录
BACKUP_DIR="/backup/roamio_db"
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
    --no-tablespaces \
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

