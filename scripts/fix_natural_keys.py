#!/usr/bin/env python3
"""
修复 natural keys 问题
将 user_id 从用户名列表转换为实际的用户 ID
"""

import json
import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roamio.settings')
django.setup()

from django.contrib.auth.models import User

def main():
    print("=" * 60)
    print("🔧 修复 Natural Keys")
    print("=" * 60)
    print()
    
    # 读取数据
    print("📖 读取 data_backup_fixed.json...")
    with open('data_backup_fixed.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"   总记录数: {len(data)}")
    print()
    
    # 先导入用户，建立用户名到 ID 的映射
    print("👥 步骤 1：导入用户...")
    users = [obj for obj in data if obj['model'] == 'auth.user']
    print(f"   用户数量: {len(users)}")
    
    # 清空现有用户
    User.objects.all().delete()
    
    # 导入用户
    from django.core import serializers
    for user_data in users:
        user = serializers.deserialize('json', json.dumps([user_data])).__next__()
        user.save()
    
    print(f"   ✅ 已导入 {User.objects.count()} 个用户")
    print()
    
    # 建立用户名到 ID 的映射
    print("🗺️  步骤 2：建立用户名映射...")
    username_to_id = {}
    for user in User.objects.all():
        username_to_id[user.username] = user.id
        print(f"   {user.username} -> {user.id}")
    print()
    
    # 修复 UserProfile 的 user_id
    print("🔧 步骤 3：修复 UserProfile...")
    profiles = [obj for obj in data if obj['model'] == 'backend.userprofile']
    fixed_profiles = []
    
    for profile in profiles:
        user_id = profile['fields']['user']
        
        # 如果是列表，取第一个元素（用户名）
        if isinstance(user_id, list):
            username = user_id[0]
            # 转换为实际的用户 ID
            if username in username_to_id:
                profile['fields']['user'] = username_to_id[username]
                fixed_profiles.append(profile)
                print(f"   修复: {username} -> {username_to_id[username]}")
            else:
                print(f"   ⚠️  跳过: 找不到用户 {username}")
        else:
            # 已经是 ID，直接保留
            fixed_profiles.append(profile)
    
    print(f"   ✅ 修复了 {len(fixed_profiles)} 个用户资料")
    print()
    
    # 修复 Trip 的 author
    print("🔧 步骤 4：修复 Trip...")
    trips = [obj for obj in data if obj['model'] == 'backend.trip']
    fixed_trips = []
    
    for trip in trips:
        author = trip['fields'].get('author')
        if author and isinstance(author, list):
            username = author[0]
            if username in username_to_id:
                trip['fields']['author'] = username_to_id[username]
                fixed_trips.append(trip)
                print(f"   修复旅行: author={username} -> {username_to_id[username]}")
            else:
                print(f"   ⚠️  跳过旅行: 找不到作者 {username}")
        else:
            fixed_trips.append(trip)
    
    print(f"   ✅ 修复了 {len(fixed_trips)} 个旅行")
    print()
    
    # 修复 Comment 的 user
    print("🔧 步骤 5：修复 Comment...")
    comments = [obj for obj in data if obj['model'] == 'backend.comment']
    fixed_comments = []
    
    for comment in comments:
        user = comment['fields'].get('user')
        if user and isinstance(user, list):
            username = user[0]
            if username in username_to_id:
                comment['fields']['user'] = username_to_id[username]
                fixed_comments.append(comment)
            else:
                print(f"   ⚠️  跳过评论: 找不到用户 {username}")
        else:
            fixed_comments.append(comment)
    
    print(f"   ✅ 修复了 {len(fixed_comments)} 个评论")
    print()
    
    # 修复 SocialAccount 的 user
    print("🔧 步骤 6：修复 SocialAccount...")
    social_accounts = [obj for obj in data if obj['model'] == 'backend.socialaccount']
    fixed_social = []
    
    for account in social_accounts:
        user = account['fields'].get('user')
        if user and isinstance(user, list):
            username = user[0]
            if username in username_to_id:
                account['fields']['user'] = username_to_id[username]
                fixed_social.append(account)
                print(f"   修复社交账号: user={username} -> {username_to_id[username]}")
            else:
                print(f"   ⚠️  跳过社交账号: 找不到用户 {username}")
        else:
            fixed_social.append(account)
    
    print(f"   ✅ 修复了 {len(fixed_social)} 个社交账号")
    print()
    
    # 合并所有数据
    print("📦 步骤 7：合并数据...")
    other_data = [obj for obj in data if obj['model'] not in [
        'auth.user', 
        'backend.userprofile', 
        'backend.trip', 
        'backend.comment',
        'backend.socialaccount'
    ]]
    
    final_data = users + fixed_profiles + fixed_trips + fixed_comments + fixed_social + other_data
    print(f"   总记录数: {len(final_data)}")
    print()
    
    # 保存修复后的数据
    print("💾 步骤 8：保存修复后的数据...")
    with open('data_final.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    print("   ✅ 已保存到: data_final.json")
    print()
    
    # 询问是否导入
    print("=" * 60)
    response = input("是否立即导入修复后的数据？(yes/no): ")
    if response.lower() != 'yes':
        print("❌ 已取消导入")
        print("💡 提示：可以手动运行: python3 manage.py loaddata data_final.json")
        return
    print()
    
    # 导入数据
    print("📥 导入数据到 RDS...")
    from django.core.management import call_command
    
    try:
        call_command('loaddata', 'data_final.json')
        print("✅ 数据导入成功！")
    except Exception as e:
        print(f"❌ 数据导入失败: {e}")
        return
    print()
    
    # 验证数据
    print("✅ 验证数据...")
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

