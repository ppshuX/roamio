"""
AI 服务调试脚本
"""
import os
import sys
import django
import time

# 设置 Django 环境
sys.path.insert(0, '/home/acs/roamio')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roamio.settings')
django.setup()

print("=" * 60)
print("AI 服务调试测试")
print("=" * 60)

# 测试 1: 导入
print("\n[1] 测试导入...")
start = time.time()
from backend.utils.ai import TripPlannerAI
print(f"   导入耗时: {time.time() - start:.2f}秒")

# 测试 2: 初始化
print("\n[2] 测试初始化...")
start = time.time()
ai = TripPlannerAI()
print(f"   初始化耗时: {time.time() - start:.2f}秒")
print(f"   AI 启用: {ai.enabled}")
print(f"   模型: {ai.model}")
print(f"   API Key: {ai.api_key[:15]}..." if ai.api_key else "   API Key: None")

# 测试 3: 构建提示词
print("\n[3] 测试构建提示词...")
start = time.time()
system_prompt = ai._build_system_prompt({'days': 3, 'budget_level': 'medium'})
user_prompt = ai._build_user_prompt("推荐北京3日游", {'days': 3}, None)
print(f"   构建提示词耗时: {time.time() - start:.2f}秒")
print(f"   系统提示词长度: {len(system_prompt)} 字符")
print(f"   用户提示词长度: {len(user_prompt)} 字符")

# 测试 4: API 调用
print("\n[4] 测试 API 调用...")
print("   发送请求...")
start = time.time()

try:
    result = ai.generate_trip_plan("推荐北京3日游", {'days': 3})
    elapsed = time.time() - start
    
    print(f"   ✅ 成功!")
    print(f"   耗时: {elapsed:.2f}秒")
    print(f"   消耗 tokens: {ai.tokens_used}")
    print(f"   行程标题: {result['trip_title']}")
    print(f"   天数: {len(result['days_detail'])}")
    
except Exception as e:
    elapsed = time.time() - start
    print(f"   ❌ 失败!")
    print(f"   耗时: {elapsed:.2f}秒")
    print(f"   错误: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)

