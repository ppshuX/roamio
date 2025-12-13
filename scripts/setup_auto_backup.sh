#!/bin/bash
# 设置自动备份（添加到 crontab）
# 使用方法: ./setup_auto_backup.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_SCRIPT="${SCRIPT_DIR}/backup_database.sh"

echo "====================================="
echo "⏰ 设置 Roamio 数据库自动备份"
echo "====================================="
echo ""

# 检查备份脚本是否存在
if [ ! -f "${BACKUP_SCRIPT}" ]; then
    echo "❌ 错误: 找不到备份脚本 ${BACKUP_SCRIPT}"
    exit 1
fi

# 确保备份脚本可执行
chmod +x ${BACKUP_SCRIPT}

# 添加 crontab 任务（每天凌晨2点备份）
CRON_JOB="0 2 * * * ${BACKUP_SCRIPT} >> /var/log/roamio_backup.log 2>&1"

# 检查是否已存在
if crontab -l 2>/dev/null | grep -q "${BACKUP_SCRIPT}"; then
    echo "⚠️  自动备份任务已存在"
    echo "当前 crontab 任务："
    crontab -l | grep "${BACKUP_SCRIPT}"
else
    # 添加新的 crontab 任务
    (crontab -l 2>/dev/null; echo "${CRON_JOB}") | crontab -
    echo "✅ 自动备份任务已添加"
    echo "备份时间: 每天凌晨 2:00"
fi

echo ""
echo "📋 当前所有 crontab 任务："
crontab -l
echo ""
echo "====================================="
echo "✅ 设置完成！"
echo "====================================="
echo ""
echo "💡 提示："
echo "1. 备份文件保存在: /backup/roamio_db/"
echo "2. 备份日志保存在: /var/log/roamio_backup.log"
echo "3. 自动保留最近7天的备份"
echo ""

