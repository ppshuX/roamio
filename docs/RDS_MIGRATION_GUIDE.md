# 🚀 Roamio SQLite 到 RDS MySQL 迁移指南

> **迁移日期**: 2025-11-08  
> **目标数据库**: 阿里云 RDS MySQL  
> **实例 ID**: rm-wz91m3g4wa6io3dfi

---

## 📋 迁移前准备

### 1. 安装 MySQL 客户端和 Python 驱动

```bash
# 在服务器上安装 MySQL 客户端
sudo apt update
sudo apt install mysql-client -y

# 安装 Python MySQL 驱动
pip install mysqlclient
# 或者
pip install pymysql
```

### 2. 备份现有 SQLite 数据库

```bash
cd /home/ubuntu/roamio
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)
```

---

## 🔧 步骤 1：更新 Django 配置

### 1.1 备份 settings.py

```bash
cp roamio/settings.py roamio/settings.py.sqlite.backup
```

### 1.2 修改 settings.py

编辑 `roamio/settings.py`，找到 `DATABASES` 配置：

```python
# 原配置（SQLite）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

替换为：

```python
# 新配置（RDS MySQL）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'roamio_production',
        'USER': 'roamio_user',
        'PASSWORD': 'Roamio@2025!Pass',
        'HOST': 'rm-wz91m3g4wa6io3dfi8o.mysql.rds.aliyuncs.com',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}
```

### 1.3 测试连接

```bash
python manage.py check
```

---

## 📦 步骤 2：运行数据库迁移

### 2.1 创建表结构

```bash
python manage.py migrate
```

### 2.2 创建超级用户（可选）

```bash
python manage.py createsuperuser
```

---

## 💾 步骤 3：迁移数据

### 方法 1：使用 Django dumpdata/loaddata（推荐）

#### 3.1 导出 SQLite 数据

```bash
# 临时切换回 SQLite 配置
cp roamio/settings.py.sqlite.backup roamio/settings.py

# 导出数据
python manage.py dumpdata \
    --natural-foreign \
    --natural-primary \
    --exclude auth.permission \
    --exclude contenttypes \
    --indent 2 > data_backup.json

# 检查导出的数据
ls -lh data_backup.json
```

#### 3.2 导入到 RDS

```bash
# 恢复 RDS 配置
cp roamio/settings.py.sqlite.backup roamio/settings.py
# 然后手动修改为 RDS 配置

# 导入数据
python manage.py loaddata data_backup.json
```

### 方法 2：使用 MySQL 工具（高级）

```bash
# 1. 将 SQLite 转换为 SQL 文件
sqlite3 db.sqlite3 .dump > sqlite_dump.sql

# 2. 转换 SQL 语法（SQLite -> MySQL）
# 需要手动处理一些语法差异

# 3. 导入到 MySQL
mysql -h rm-wz91m3g4wa6io3dfi8o.mysql.rds.aliyuncs.com \
      -P 3306 \
      -u roamio_user \
      -p'Roamio@2025!Pass' \
      roamio_production < sqlite_dump.sql
```

---

## ✅ 步骤 4：验证迁移

### 4.1 检查数据

```bash
# 启动 Django shell
python manage.py shell

# 检查用户数量
from django.contrib.auth.models import User
print(f"用户数量: {User.objects.count()}")

# 检查旅行数量
from trips.models import Trip
print(f"旅行数量: {Trip.objects.count()}")

# 检查评论数量
from trips.models import Comment
print(f"评论数量: {Comment.objects.count()}")
```

### 4.2 测试应用

```bash
# 启动开发服务器
python manage.py runserver 0.0.0.0:8000

# 访问应用并测试：
# - 用户登录
# - 创建旅行
# - 发表评论
# - 上传图片
```

---

## 🔄 步骤 5：更新服务器配置

### 5.1 更新 uWSGI 配置

如果使用 uWSGI，确保环境变量正确：

```ini
# scripts/uwsgi.ini
[uwsgi]
# ... 其他配置 ...

# 确保 Python 路径正确
pythonpath = /home/ubuntu/roamio
```

### 5.2 重启服务

```bash
# 重启 uWSGI
sudo systemctl restart uwsgi

# 或者使用脚本
./scripts/start_uwsgi.sh
```

---

## 🎯 步骤 6：配置自动备份

### 6.1 创建备份脚本

```bash
#!/bin/bash
# scripts/backup_rds.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/ubuntu/roamio_backups"
mkdir -p $BACKUP_DIR

# 备份数据库
mysqldump -h rm-wz91m3g4wa6io3dfi8o.mysql.rds.aliyuncs.com \
          -P 3306 \
          -u roamio_user \
          -p'Roamio@2025!Pass' \
          roamio_production \
          | gzip > $BACKUP_DIR/roamio_$DATE.sql.gz

# 保留最近 7 天的备份
find $BACKUP_DIR -name "roamio_*.sql.gz" -mtime +7 -delete

echo "✅ 备份完成: roamio_$DATE.sql.gz"
```

### 6.2 设置定时任务

```bash
# 编辑 crontab
crontab -e

# 添加每天凌晨 2 点自动备份
0 2 * * * /home/ubuntu/roamio/scripts/backup_rds.sh >> /home/ubuntu/roamio/logs/backup.log 2>&1
```

---

## 📊 数据库连接信息汇总

```bash
# RDS 连接信息
DB_HOST=rm-wz91m3g4wa6io3dfi8o.mysql.rds.aliyuncs.com
DB_PORT=3306
DB_NAME=roamio_production
DB_USER=roamio_user
DB_PASSWORD=Roamio@2025!Pass

# 管理账号
ADMIN_USER=Roamio2025
ADMIN_PASSWORD=Abcdefg1234567@

# Ralendar 账号
RALENDAR_USER=ralendar_user
RALENDAR_PASSWORD=Ralendar@2025!Pass
```

---

## ⚠️ 常见问题

### 问题 1：连接超时

```bash
# 检查白名单配置
# 确保服务器 IP 已添加到 RDS 白名单
```

### 问题 2：字符集问题

```python
# 确保 Django 配置中指定了 utf8mb4
'OPTIONS': {
    'charset': 'utf8mb4',
}
```

### 问题 3：权限不足

```sql
-- 使用高权限账号授予权限
GRANT ALL PRIVILEGES ON roamio_production.* TO 'roamio_user'@'%';
FLUSH PRIVILEGES;
```

---

## 🎉 迁移完成检查清单

- [ ] MySQL 客户端已安装
- [ ] Python MySQL 驱动已安装
- [ ] SQLite 数据已备份
- [ ] settings.py 已更新为 RDS 配置
- [ ] 数据库迁移已运行（`python manage.py migrate`）
- [ ] 数据已导入到 RDS
- [ ] 应用功能测试通过
- [ ] uWSGI/服务已重启
- [ ] 自动备份脚本已配置
- [ ] 文档已更新

---

## 📞 支持

如有问题，请参考：
- [阿里云 RDS 文档](https://help.aliyun.com/product/26090.html)
- [Django 数据库配置](https://docs.djangoproject.com/en/stable/ref/databases/)
- Roamio 项目文档：`docs/ecosystem/ROAMIO_DATABASE_INFO_FOR_RALENDAR.md`

---

**祝迁移顺利！** 🚀

