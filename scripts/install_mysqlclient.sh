#!/bin/bash
# ==========================================
# 安装 mysqlclient 脚本（使用国内镜像）
# ==========================================

set -e

echo "=========================================="
echo "📦 安装 mysqlclient"
echo "=========================================="
echo ""

# 方法 1：使用清华镜像源（推荐）
echo "🚀 方法 1：使用清华镜像源..."
pip install mysqlclient -i https://pypi.tuna.tsinghua.edu.cn/simple --timeout 120

# 如果方法 1 失败，尝试方法 2
if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  方法 1 失败，尝试方法 2..."
    echo "🚀 方法 2：使用阿里云镜像源..."
    pip install mysqlclient -i https://mirrors.aliyun.com/pypi/simple/ --timeout 120
fi

# 如果方法 2 失败，尝试方法 3
if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  方法 2 失败，尝试方法 3..."
    echo "🚀 方法 3：使用豆瓣镜像源..."
    pip install mysqlclient -i https://pypi.douban.com/simple --timeout 120
fi

# 如果方法 3 失败，尝试方法 4
if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  方法 3 失败，尝试方法 4..."
    echo "🚀 方法 4：使用腾讯云镜像源..."
    pip install mysqlclient -i https://mirrors.cloud.tencent.com/pypi/simple --timeout 120
fi

# 验证安装
echo ""
echo "=========================================="
echo "✅ 验证安装"
echo "=========================================="
python3 -c "import MySQLdb; print('mysqlclient 版本:', MySQLdb.__version__)"

echo ""
echo "✅ 安装完成！"
echo "=========================================="

