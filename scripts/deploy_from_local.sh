#!/bin/bash
# ============================================================
# 本地构建并部署到服务器
# ============================================================
# 
# 使用方法：
# 1. 配置服务器信息（修改下面的变量）
# 2. chmod +x scripts/deploy_from_local.sh
# 3. ./scripts/deploy_from_local.sh
#
# ============================================================

set -e  # 遇到错误立即退出

# ============================================================
# 配置区域（根据你的服务器修改）
# ============================================================
SERVER_USER="acs"
SERVER_HOST="your-server-ip-or-domain"  # 修改为你的服务器 IP 或域名
SERVER_PATH="/home/acs/roamio/web/dist"

# ============================================================
# 1. 构建前端
# ============================================================
echo ""
echo "🔨 [1/3] 构建前端..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd web

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    npm install
fi

# 构建
echo "🔨 开始构建..."
npm run build

if [ ! -d "dist" ]; then
    echo "❌ 构建失败：dist 目录不存在"
    exit 1
fi

echo "✅ 构建完成！"
cd ..

# ============================================================
# 2. 上传到服务器
# ============================================================
echo ""
echo "📤 [2/3] 上传到服务器..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查是否安装了 rsync
if command -v rsync &> /dev/null; then
    echo "使用 rsync 上传（增量同步）..."
    rsync -avz --delete \
        --exclude='*.map' \
        web/dist/ ${SERVER_USER}@${SERVER_HOST}:${SERVER_PATH}/
else
    echo "⚠️  未安装 rsync，使用 scp 上传（全量）..."
    echo "建议安装 rsync 以提高上传速度：brew install rsync (macOS) 或 apt install rsync (Linux)"
    
    # 打包
    cd web/dist
    tar -czf ../dist.tar.gz *
    cd ../..
    
    # 上传
    scp web/dist.tar.gz ${SERVER_USER}@${SERVER_HOST}:${SERVER_PATH}/../
    
    # 解压
    ssh ${SERVER_USER}@${SERVER_HOST} << EOF
cd ${SERVER_PATH}/..
rm -rf dist/*
tar -xzf dist.tar.gz -C dist/
rm dist.tar.gz
EOF
    
    # 清理本地临时文件
    rm web/dist.tar.gz
fi

echo "✅ 上传完成！"

# ============================================================
# 3. 验证部署
# ============================================================
echo ""
echo "🧪 [3/3] 验证部署..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查服务器上的文件
echo "检查服务器文件..."
ssh ${SERVER_USER}@${SERVER_HOST} << EOF
echo "📁 文件列表："
ls -lh ${SERVER_PATH}/
echo ""
echo "📊 磁盘使用："
du -sh ${SERVER_PATH}/
EOF

# ============================================================
# 完成
# ============================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 部署完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 部署信息："
echo "  - 前端文件: ${SERVER_PATH}/"
echo "  - 服务器: ${SERVER_USER}@${SERVER_HOST}"
echo ""
echo "🌐 访问地址："
echo "  - https://app7508.acapp.acwing.com.cn"
echo ""
echo "🧪 测试建议："
echo "  1. 访问网站，检查首页是否正常"
echo "  2. 硬刷新（Ctrl + Shift + R）清除缓存"
echo "  3. 检查浏览器控制台是否有错误"
echo "  4. 测试主要功能（登录、旅行列表等）"
echo ""

