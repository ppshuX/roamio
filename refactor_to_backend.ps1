# 重构脚本：trips → backend

Write-Host "开始重构..." -ForegroundColor Green

# 1. 创建数据库迁移
Write-Host "`n[1/3] 创建数据库迁移..." -ForegroundColor Yellow
python manage.py makemigrations backend

# 2. 应用迁移
Write-Host "`n[2/3] 应用迁移..." -ForegroundColor Yellow
python manage.py migrate

# 3. 测试
Write-Host "`n[3/3] 测试服务器..." -ForegroundColor Yellow
Write-Host "启动开发服务器测试（按 Ctrl+C 停止）..." -ForegroundColor Cyan
python manage.py runserver

Write-Host "`n✅ 完成！" -ForegroundColor Green

