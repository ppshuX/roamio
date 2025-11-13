#!/bin/bash
# Roamio 导入脚本（在腾讯云上执行）

set -e  # 遇到错误立即退出

echo "====================================="
echo "🚀 Roamio 迁移导入脚本"
echo "====================================="
echo ""

# 配置
WORK_DIR=~/roamio
IMPORT_DIR="/tmp"

echo "📥 步骤1: 检查传输的文件..."
cd ${IMPORT_DIR}
ls -lh roamio*.tar* 2>/dev/null || echo "⚠️  未找到roamio文件"
echo ""

echo "🐳 步骤2: 加载Docker镜像..."
if [ -f roamio_web.tar ]; then
    echo "加载Web镜像..."
    docker load -i roamio_web.tar
    echo "✅ Web镜像加载完成"
else
    echo "❌ 错误: 未找到roamio_web.tar"
    exit 1
fi

if [ -f roamio_db.tar ]; then
    echo "加载DB镜像..."
    docker load -i roamio_db.tar
    echo "✅ DB镜像加载完成"
fi

echo ""
echo "📂 步骤3: 准备工作目录..."
mkdir -p ${WORK_DIR}
cd ${WORK_DIR}

# 解压配置文件
if [ -f ${IMPORT_DIR}/roamio_config.tar.gz ]; then
    tar -xzf ${IMPORT_DIR}/roamio_config.tar.gz -C ~
    echo "✅ 配置文件已恢复"
fi

echo ""
echo "⚙️  步骤4: 配置环境..."
echo "请确认以下文件存在:"
echo "  - docker-compose.yml"
echo "  - .env"
echo "  - cloud_settings/nginx配置"
echo "  - SSL证书"
echo ""
read -p "文件是否准备就绪? (y/n): " FILES_READY

if [ "$FILES_READY" != "y" ]; then
    echo "请先准备好配置文件，然后重新运行此脚本"
    exit 1
fi

echo ""
echo "🚀 步骤5: 启动服务..."
read -p "是否立即启动服务? (y/n): " START_SERVICE

if [ "$START_SERVICE" == "y" ]; then
    echo "停止旧服务（如果有）..."
    docker-compose down 2>/dev/null || true
    
    echo "启动新服务..."
    docker-compose up -d
    
    echo ""
    echo "等待服务启动..."
    sleep 10
    
    echo "📊 查看服务状态..."
    docker-compose ps
    
    echo ""
    echo "📝 查看日志（Ctrl+C退出）..."
    docker-compose logs --tail=50
fi

echo ""
echo "====================================="
echo "✅ 导入完成！"
echo "====================================="
echo ""
echo "⏭️  下一步验证："
echo "1. 检查服务运行状态: docker-compose ps"
echo "2. 查看日志: docker-compose logs -f"
echo "3. 测试本地访问: curl http://localhost:8000"
echo "4. 配置Nginx（如果还没配置）"
echo "5. 更新DNS: roamio.cn → $(curl -s ifconfig.me)"
echo ""

