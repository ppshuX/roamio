#!/usr/bin/env python3
"""
清空 RDS 数据库并导入 SQLite 数据
解决主键冲突问题
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
    print("🔄 清空 RDS 数据库并导入数据")
    print("=" * 60)
    print()
    
    # 确认操作
    print("⚠️  警告：此操作将清空 RDS 数据库中的所有数据！")
    response = input("确认要继续吗？(yes/no): ")
    if response.lower() != 'yes':
        print("❌ 操作已取消")
        return
    print()
    
    # 步骤 1：禁用外键检查并清空所有表
    print("🗑️  步骤 1：清空数据库表")
    with connection.cursor() as cursor:
        # 禁用外键检查
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        # 获取所有表
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'roamio_production'
            AND table_name NOT LIKE 'django_migrations';
        """)
        tables = cursor.fetchall()
        
        # 清空所有表
        for (table_name,) in tables:
            print(f"   清空表: {table_name}")
            cursor.execute(f"TRUNCATE TABLE `{table_name}`;")
        
        # 启用外键检查
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    
    print("✅ 数据库已清空")
    print()
    
    # 步骤 2：重新运行迁移
    print("📦 步骤 2：重新运行数据库迁移")
    call_command('migrate', '--fake-initial', '--noinput')
    print("✅ 迁移完成")
    print()
    
    # 步骤 3：导入数据
    print("📥 步骤 3：导入数据")
    if not os.path.exists('data_backup.json'):
        print("❌ 错误：data_backup.json 不存在")
        return
    
    try:
        call_command('loaddata', 'data_backup.json')
        print("✅ 数据导入成功")
    except Exception as e:
        print(f"❌ 数据导入失败: {e}")
        return
    print()
    
    # 步骤 4：验证数据
    print("✅ 步骤 4：验证数据")
    from django.contrib.auth.models import User
    from backend.models import Trip, Comment, UserProfile
    
    print(f"   用户数量: {User.objects.count()}")
    print(f"   用户资料数量: {UserProfile.objects.count()}")
    print(f"   旅行数量: {Trip.objects.count()}")
    print(f"   评论数量: {Comment.objects.count()}")
    print()
    
    print("=" * 60)
    print("🎉 数据导入完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()

