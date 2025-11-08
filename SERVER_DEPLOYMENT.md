# 🚀 Roamio 服务器部署指南 - RDS 迁移

> **服务器**: 47.121.137.60  
> **用户**: acs  
> **项目路径**: ~/roamio

---

## 📋 快速部署（一键执行）

### 方法 1：自动部署脚本（推荐）

```bash
# 1. SSH 登录服务器
ssh acs@47.121.137.60

# 2. 进入项目目录
cd ~/roamio

# 3. 拉取最新代码
git pull

# 4. 给脚本添加执行权限
chmod +x scripts/deploy_rds_migration.sh

# 5. 执行自动部署脚本
./scripts/deploy_rds_migration.sh
```

**这个脚本会自动完成：**
- ✅ 备份 SQLite 数据库
- ✅ 安装系统依赖（MySQL 客户端）
- ✅ 安装 Python MySQL 驱动（使用国内镜像）
- ✅ 测试 RDS 连接
- ✅ 运行数据库迁移
- ✅ 导出 SQLite 数据
- ✅ 导入数据到 RDS
- ✅ 验证数据
- ✅ 重启 uWSGI 服务

---

## 📋 手动部署（分步执行）

如果自动脚本失败，可以手动执行：

### 步骤 1：拉取代码

```bash
cd ~/roamio
git pull
```

### 步骤 2：安装系统依赖

```bash
sudo apt update
sudo apt install -y mysql-client libmysqlclient-dev pkg-config python3-dev build-essential
```

### 步骤 3：安装 Python MySQL 驱动（解决超时问题）

```bash
# 使用清华镜像源
pip3 install mysqlclient -i https://pypi.tuna.tsinghua.edu.cn/simple --timeout 120

# 如果清华源失败，尝试阿里云
pip3 install mysqlclient -i https://mirrors.aliyun.com/pypi/simple/ --timeout 120

# 如果还失败，尝试豆瓣
pip3 install mysqlclient -i https://pypi.douban.com/simple --timeout 120
```

**或者使用脚本：**

```bash
chmod +x scripts/install_mysqlclient.sh
./scripts/install_mysqlclient.sh
```

### 步骤 4：测试 RDS 连接

```bash
mysql -h rm-wz91m3g4wa6io3dfi8o.mysql.rds.aliyuncs.com \
      -P 3306 \
      -u roamio_user \
      -p'Roamio@2025!Pass' \
      roamio_production
```

如果连接成功，输入 `exit` 退出。

### 步骤 5：备份 SQLite 数据库

```bash
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)
```

### 步骤 6：运行数据库迁移

```bash
python3 manage.py migrate
```

### 步骤 7：导出 SQLite 数据（可选）

如果需要迁移现有数据：

```bash
# 导出数据
python3 manage.py dumpdata \
    --natural-foreign \
    --natural-primary \
    --exclude auth.permission \
    --exclude contenttypes \
    --indent 2 > data_backup.json

# 导入到 RDS
python3 manage.py loaddata data_backup.json
```

### 步骤 8：创建超级用户（可选）

```bash
python3 manage.py createsuperuser
```

### 步骤 9：重启服务

```bash
sudo systemctl restart uwsgi
```

### 步骤 10：验证部署

```bash
# 检查服务状态
sudo systemctl status uwsgi

# 查看日志
tail -f logs/uwsgi.log

# 测试 API
curl http://localhost:8000/api/v1/health/
```

---

## 🔍 故障排查

### 问题 1：pip 安装超时

**错误信息：**
```
socket.timeout: The read operation timed out
ReadTimeoutError: HTTPSConnectionPool(host='files.pythonhosted.org', port=443): Read timed out.
```

**解决方案：**
```bash
# 使用国内镜像源
pip3 install mysqlclient -i https://pypi.tuna.tsinghua.edu.cn/simple --timeout 120
```

### 问题 2：RDS 连接失败

**错误信息：**
```
ERROR 2003 (HY000): Can't connect to MySQL server
```

**解决方案：**
1. 检查白名单是否包含服务器 IP
2. 检查网络连接：`ping rm-wz91m3g4wa6io3dfi8o.mysql.rds.aliyuncs.com`
3. 检查防火墙：`sudo ufw status`

### 问题 3：权限不足

**错误信息：**
```
ERROR 1045 (28000): Access denied for user
```

**解决方案：**
检查用户名和密码是否正确：
```bash
# 用户名：roamio_user
# 密码：Roamio@2025!Pass
```

### 问题 4：数据库迁移失败

**错误信息：**
```
django.db.utils.OperationalError
```

**解决方案：**
```bash
# 检查数据库连接
python3 manage.py check

# 查看详细错误
python3 manage.py migrate --verbosity 3
```

---

## 📊 验证部署

### 1. 检查数据库数据

```bash
python3 manage.py shell
```

```python
from django.contrib.auth.models import User
from trips.models import Trip, Comment

print(f"用户数量: {User.objects.count()}")
print(f"旅行数量: {Trip.objects.count()}")
print(f"评论数量: {Comment.objects.count()}")
```

### 2. 测试 API

```bash
# 健康检查
curl http://localhost:8000/api/v1/health/

# 获取旅行列表
curl http://localhost:8000/api/v1/trips/
```

### 3. 访问应用

浏览器访问：`http://app7508.acapp.acwing.com.cn`

---

## 🔄 回滚方案

如果迁移失败，可以回滚到 SQLite：

```bash
# 1. 恢复 settings.py
git checkout roamio/settings.py

# 2. 恢复 SQLite 数据库
cp db.sqlite3.backup.YYYYMMDD_HHMMSS db.sqlite3

# 3. 重启服务
sudo systemctl restart uwsgi
```

---

## 📞 支持

如有问题，请参考：
- **完整迁移指南**: `docs/RDS_MIGRATION_GUIDE.md`
- **配置完成文档**: `docs/ecosystem/RDS_SETUP_COMPLETE.md`
- **快速参考**: `RDS_QUICK_REFERENCE.md`

---

## ✅ 部署检查清单

- [ ] 代码已拉取（`git pull`）
- [ ] 系统依赖已安装（MySQL 客户端）
- [ ] Python 驱动已安装（mysqlclient）
- [ ] RDS 连接测试成功
- [ ] SQLite 数据已备份
- [ ] 数据库迁移已运行
- [ ] 数据已导入（如果需要）
- [ ] 服务已重启
- [ ] 应用功能测试通过
- [ ] 日志无错误

---

**祝部署顺利！** 🎉

