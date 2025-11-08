#!/usr/bin/env python3
"""
修复 data_backup.json 中的重复数据并导入
解决 UserProfile 重复的 user_id 问题
"""

import json
import os

def fix_duplicate_userprofiles(data):
    """修复重复的 UserProfile"""
    print("🔍 检查 UserProfile 重复...")
    
    # 找出所有 UserProfile
    profiles = [obj for obj in data if obj['model'] == 'backend.userprofile']
    other_data = [obj for obj in data if obj['model'] != 'backend.userprofile']
    
    print(f"   原始 UserProfile 数量: {len(profiles)}")
    
    # 按 user_id 去重，保留第一个
    seen_user_ids = set()
    unique_profiles = []
    duplicates = []
    
    for profile in profiles:
        user_id = profile['fields']['user']
        if user_id not in seen_user_ids:
            seen_user_ids.add(user_id)
            unique_profiles.append(profile)
        else:
            duplicates.append(profile)
            print(f"   ⚠️  发现重复: user_id={user_id}, pk={profile['pk']}")
    
    print(f"   去重后 UserProfile 数量: {len(unique_profiles)}")
    print(f"   删除重复数量: {len(duplicates)}")
    
    # 合并数据
    fixed_data = other_data + unique_profiles
    
    return fixed_data

def main():
    print("=" * 60)
    print("🔧 修复并导入数据")
    print("=" * 60)
    print()
    
    # 检查文件是否存在
    if not os.path.exists('data_backup.json'):
        print("❌ 错误：data_backup.json 不存在")
        return
    
    # 读取原始数据
    print("📖 读取 data_backup.json...")
    with open('data_backup.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"   总记录数: {len(data)}")
    print()
    
    # 备份原始文件
    print("💾 备份原始文件...")
    import shutil
    shutil.copy('data_backup.json', 'data_backup.json.original')
    print("   ✅ 已备份到: data_backup.json.original")
    print()
    
    # 修复重复数据
    fixed_data = fix_duplicate_userprofiles(data)
    print()
    
    # 保存修复后的数据
    print("💾 保存修复后的数据...")
    with open('data_backup_fixed.json', 'w', encoding='utf-8') as f:
        json.dump(fixed_data, f, ensure_ascii=False, indent=2)
    print("   ✅ 已保存到: data_backup_fixed.json")
    print()
    
    # 显示数据统计
    print("📊 数据统计:")
    models = {}
    for obj in fixed_data:
        model = obj['model']
        models[model] = models.get(model, 0) + 1
    
    for model, count in sorted(models.items()):
        print(f"   {model}: {count}")
    print()
    
    # 询问是否导入
    print("=" * 60)
    response = input("是否立即导入修复后的数据？(yes/no): ")
    if response.lower() != 'yes':
        print("❌ 已取消导入")
        print("💡 提示：可以手动运行: python3 manage.py loaddata data_backup_fixed.json")
        return
    print()
    
    # 导入数据
    print("📥 导入数据到 RDS...")
    import django
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roamio.settings')
    django.setup()
    
    from django.core.management import call_command
    
    try:
        call_command('loaddata', 'data_backup_fixed.json')
        print("✅ 数据导入成功！")
    except Exception as e:
        print(f"❌ 数据导入失败: {e}")
        return
    print()
    
    # 验证数据
    print("✅ 验证数据...")
    from django.contrib.auth.models import User
    from backend.models import Trip, Comment, UserProfile
    
    print(f"   用户数量: {User.objects.count()}")
    print(f"   用户资料数量: {UserProfile.objects.count()}")
    print(f"   旅行数量: {Trip.objects.count()}")
    print(f"   评论数量: {Comment.objects.count()}")
    print()
    
    print("=" * 60)
    print("🎉 数据修复并导入完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()

