#!/bin/bash
# Roamio 导出脚本（在阿里云上执行）

set -e  # 遇到错误立即退出

echo "====================================="
echo "🚀 Roamio 迁移导出脚本"
echo "====================================="
echo ""

# 配置
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/tmp/roamio_migration_${DATE}"
TARGET_SERVER="YOUR_TARGET_SERVER_IP"  # 目标服务器IP（腾讯云）

mkdir -p ${BACKUP_DIR}
cd ${BACKUP_DIR}

echo "📦 步骤1: 导出Docker镜像..."
docker ps
echo ""
read -p "请输入Roamio Web容器名称: " WEB_CONTAINER
read -p "请输入Roamio DB容器名称（如果有，没有则回车跳过）: " DB_CONTAINER

# 导出Web容器
echo "导出Web容器镜像..."
docker commit ${WEB_CONTAINER} roamio:migration-${DATE}
docker save roamio:migration-${DATE} -o roamio_web.tar
echo "✅ Web镜像导出完成: roamio_web.tar ($(du -h roamio_web.tar | cut -f1))"

# 导出DB容器（如果有）
if [ ! -z "$DB_CONTAINER" ]; then
    echo "导出DB容器镜像..."
    docker commit ${DB_CONTAINER} roamio-db:migration-${DATE}
    docker save roamio-db:migration-${DATE} -o roamio_db.tar
    echo "✅ DB镜像导出完成: roamio_db.tar ($(du -h roamio_db.tar | cut -f1))"
fi

echo ""
echo "💾 步骤2: 备份数据库..."
if [ ! -z "$DB_CONTAINER" ]; then
    echo "请选择数据库类型: 1) MySQL  2) PostgreSQL  3) 跳过"
    read -p "选择: " DB_TYPE
    
    if [ "$DB_TYPE" == "1" ]; then
        read -p "数据库名称: " DB_NAME
        docker exec ${DB_CONTAINER} mysqldump -u root -p ${DB_NAME} > roamio_db_backup.sql
        echo "✅ MySQL备份完成"
    elif [ "$DB_TYPE" == "2" ]; then
        read -p "数据库名称: " DB_NAME
        docker exec ${DB_CONTAINER} pg_dump -U postgres ${DB_NAME} > roamio_db_backup.sql
        echo "✅ PostgreSQL备份完成"
    fi
fi

echo ""
echo "📁 步骤3: 备份配置文件..."
if [ -d ~/roamio ]; then
    tar -czf roamio_config.tar.gz -C ~ roamio/cloud_settings roamio/.env 2>/dev/null || echo "⚠️  部分配置文件不存在，已跳过"
    echo "✅ 配置文件备份完成"
fi

echo ""
echo "📤 步骤4: 传输文件到腾讯云..."
echo "文件列表："
ls -lh ${BACKUP_DIR}
echo ""

read -p "是否立即传输到腾讯云 ${TARGET_SERVER}? (y/n): " TRANSFER
if [ "$TRANSFER" == "y" ]; then
    echo "开始传输..."
    scp ${BACKUP_DIR}/*.tar root@${TARGET_SERVER}:/tmp/
    if [ -f roamio_db_backup.sql ]; then
        scp ${BACKUP_DIR}/roamio_db_backup.sql root@${TARGET_SERVER}:/tmp/
    fi
    if [ -f roamio_config.tar.gz ]; then
        scp ${BACKUP_DIR}/roamio_config.tar.gz root@${TARGET_SERVER}:/tmp/
    fi
    echo "✅ 传输完成"
else
    echo "手动传输命令："
    echo "scp ${BACKUP_DIR}/* root@${TARGET_SERVER}:/tmp/"
fi

echo ""
echo "====================================="
echo "✅ 导出完成！"
echo "====================================="
echo "备份位置: ${BACKUP_DIR}"
echo ""
echo "⏭️  下一步："
echo "1. 在腾讯云上运行 import_roamio.sh"
echo "2. 验证服务正常后，更新DNS解析"
echo ""

