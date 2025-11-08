#!/usr/bin/env python3
"""临时脚本：添加 web/dist/ 到 Git"""
import subprocess
import os

# 获取脚本所在目录（项目根目录）
root_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(root_dir)

print(f"当前目录: {os.getcwd()}")
print(f"检查 web/dist/ 是否存在: {os.path.exists('web/dist')}")

# 添加 web/dist/ 到 Git
try:
    result = subprocess.run(
        ['git', 'add', 'web/dist/'],
        capture_output=True,
        text=True,
        check=True
    )
    print("✅ 成功添加 web/dist/ 到 Git")
    print(result.stdout)
except subprocess.CalledProcessError as e:
    print(f"❌ 添加失败: {e}")
    print(f"stdout: {e.stdout}")
    print(f"stderr: {e.stderr}")

# 查看状态
result = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True)
print("\n当前 Git 状态:")
print(result.stdout)

