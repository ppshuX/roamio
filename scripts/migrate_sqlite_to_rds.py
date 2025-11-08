#!/usr/bin/env python
"""
Roamio SQLite 到 RDS MySQL 数据迁移脚本
执行时间：2025-11-08
"""

import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roamio.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

def main():
    print("=" * 60)
    print("🚀 Roamio 数据库迁移工具")
    print("=" * 60)
    print()
    
    # 步骤 1：检查当前数据库配置
    print("📊 步骤 1：检查数据库配置")
    print(f"   数据库引擎: {connection.settings_dict['ENGINE']}")
    print(f"   数据库名称: {connection.settings_dict['NAME']}")
    print(f"   数据库主机: {connection.settings_dict.get('HOST', 'N/A')}")
    print()
    
    # 步骤 2：确认迁移
    response = input("⚠️  确认要迁移数据吗？这将覆盖 RDS 中的现有数据！(yes/no): ")
    if response.lower() != 'yes':
        print("❌ 迁移已取消")
        return
    print()
    
    # 步骤 3：运行 Django 迁移
    print("📦 步骤 2：运行 Django 迁移（创建表结构）")
    try:
        call_command('migrate', '--noinput')
        print("   ✅ 迁移成功！")
    except Exception as e:
        print(f"   ❌ 迁移失败: {e}")
        return
    print()
    
    # 步骤 4：导出 SQLite 数据
    print("💾 步骤 3：导出 SQLite 数据")
    print("   请手动执行以下命令：")
    print()
    print("   # 1. 备份当前 settings.py")
    print("   cp roamio/settings.py roamio/settings.py.backup")
    print()
    print("   # 2. 临时切换回 SQLite 配置")
    print("   # 编辑 roamio/settings.py，将 DATABASES 改回 SQLite")
    print()
    print("   # 3. 导出数据")
    print("   python manage.py dumpdata --natural-foreign --natural-primary \\")
    print("       --exclude auth.permission --exclude contenttypes \\")
    print("       --indent 2 > data_backup.json")
    print()
    print("   # 4. 恢复 RDS 配置")
    print("   cp roamio/settings.py.backup roamio/settings.py")
    print()
    print("   # 5. 导入数据到 RDS")
    print("   python manage.py loaddata data_backup.json")
    print()
    
    print("=" * 60)
    print("✅ 迁移指南已显示！")
    print("=" * 60)

if __name__ == '__main__':
    main()

