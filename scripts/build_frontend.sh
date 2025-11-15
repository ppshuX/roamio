#!/bin/bash

# 前端构建脚本
# 使用方法：./scripts/build_frontend.sh

set -e

echo "🚀 开始构建前端..."
echo ""

# 进入前端目录
cd web

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    npm install
    echo ""
fi

# 构建前端
echo "🔨 构建前端..."
npm run build

echo ""
echo "✅ 构建完成！"
echo ""
echo "📋 构建结果："
ls -la dist/
echo ""
echo "🔄 下一步："
echo "   1. 检查构建结果："
echo "      ls -la web/dist/"
echo ""
echo "   2. 如果使用 nginx，复制到静态目录："
echo "      # 根据实际情况调整路径"
echo "      cp -r web/dist/* /path/to/nginx/static/"
echo ""
echo "   3. 或者重启 nginx："
echo "      sudo systemctl reload nginx"
echo ""

