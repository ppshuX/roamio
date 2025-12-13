# 从腾讯云 MySQL 迁移到华为云 RDS 指南

## 📋 迁移概述

**当前配置：**
- 云服务商：腾讯云 MySQL
- 实例ID：`cdb-k9ylziyr`
- 地址：`gz-cdb-k9ylziyr.sql.tencentcdb.com:23768`
- 数据库：`roamio_production`
- 到期时间：2025-12-08

**目标配置：**
- 云服务商：华为云 RDS for MySQL
- 需要创建新的 RDS 实例

---

## ✅ 迁移可行性

**完全可行！** 原因：
1. ✅ 项目使用标准 MySQL，不依赖云服务商特定功能
2. ✅ Django 的 MySQL 驱动兼容所有 MySQL 服务
3. ✅ 只需要修改连接配置
4. ✅ 数据可以完整迁移

---

## 📝 迁移步骤

### 第一步：在华为云创建 RDS 实例

1. **登录华为云控制台**
   - 访问：https://console.huaweicloud.com/
   - 进入：云数据库 RDS

2. **创建 MySQL 实例**
   - 选择：MySQL 8.0（推荐）或 MySQL 5.7
   - 地域：选择与服务器相同的地域（如：华南-广州）
   - 规格：根据数据量选择（建议至少 2核4GB）
   - 存储：SSD 云盘，建议 100GB 起步
   - 网络：选择与服务器相同的 VPC

3. **配置数据库**
   ```sql
   -- 创建数据库
   CREATE DATABASE roamio_production CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   
   -- 创建用户（请使用强密码）
   CREATE USER 'roamio_user'@'%' IDENTIFIED BY 'your_strong_password_here';
   GRANT ALL PRIVILEGES ON roamio_production.* TO 'roamio_user'@'%';
   FLUSH PRIVILEGES;
   ```

4. **配置安全组**
   - 开放端口：3306（内网）或自定义外网端口
   - 允许服务器 IP 访问

---

### 第二步：备份腾讯云数据

在服务器上执行：

```bash
cd ~/roamio
./scripts/backup_database.sh
```

备份文件位置：`~/backup/roamio_db/roamio_backup_YYYYMMDD_HHMMSS.sql.gz`

---

### 第三步：迁移数据到华为云

```bash
# 1. 解压备份文件
gunzip ~/backup/roamio_db/roamio_backup_最新日期.sql.gz

# 2. 导入到华为云 RDS
mysql -h <华为云RDS地址> -P <端口> -u roamio_user -p \
      roamio_production < ~/backup/roamio_db/roamio_backup_最新日期.sql

# 示例：
# mysql -h rds-xxx.rds.huaweicloud.com -P 3306 -u roamio_user -p \
#       roamio_production < ~/backup/roamio_db/roamio_backup_20251208_020000.sql
```

---

### 第四步：更新 Django 配置

修改 `roamio/settings.py`：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'roamio_production',
        'USER': 'roamio_user',
        'PASSWORD': 'your_strong_password_here',  # ⚠️ 请使用强密码
        'HOST': '<华为云RDS地址>',  # ⭐ 华为云 RDS 地址
        'PORT': '<端口>',  # 通常是 3306
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}
```

---

### 第五步：测试连接

```bash
# 在服务器上测试
cd ~/roamio
python manage.py dbshell

# 如果连接成功，执行：
SHOW TABLES;
# 应该能看到所有表

# 退出
exit
```

---

### 第六步：重启服务

```bash
# 重启 uWSGI
pkill -9 uwsgi
cd ~/roamio
uwsgi --ini scripts/uwsgi.ini --daemonize /tmp/uwsgi.log

# 检查服务状态
tail -f /tmp/uwsgi.log
```

---

### 第七步：验证功能

1. 访问网站：https://roamio.cn
2. 测试登录、注册
3. 测试创建旅行、评论
4. 检查数据是否正确

---

## 💰 成本对比

### 腾讯云 MySQL
- 高可用版-通用型
- 价格：根据规格（通常 ¥200-500/月）

### 华为云 RDS
- 价格通常比腾讯云便宜 20-30%
- 新用户可能有优惠
- 建议选择：通用型或高可用型

**省钱建议：**
- 选择按需付费（按小时计费）
- 选择合适规格（不要过度配置）
- 使用优惠券

---

## ⚠️ 注意事项

1. **数据迁移时间**
   - 小数据量（<1GB）：几分钟
   - 中等数据量（1-10GB）：10-30分钟
   - 大数据量（>10GB）：可能需要1小时以上

2. **服务中断时间**
   - 建议在低峰期（如凌晨）进行迁移
   - 迁移期间服务会短暂中断（5-10分钟）

3. **回滚方案**
   - 保留腾讯云数据库到迁移验证完成
   - 如果迁移失败，可以快速切回

4. **DNS/网络**
   - 确保服务器能访问华为云 RDS
   - 如果使用内网，确保在同一 VPC

---

## 🔄 迁移检查清单

- [ ] 在华为云创建 RDS 实例
- [ ] 创建数据库和用户
- [ ] 配置安全组规则
- [ ] 备份腾讯云数据
- [ ] 导入数据到华为云
- [ ] 更新 `settings.py` 配置
- [ ] 测试数据库连接
- [ ] 重启服务
- [ ] 验证所有功能
- [ ] 确认数据完整性
- [ ] 取消腾讯云自动续费

---

## 📞 需要帮助？

如果在迁移过程中遇到问题：
1. 检查网络连接
2. 检查安全组规则
3. 查看 Django 日志：`tail -f /tmp/uwsgi.log`
4. 查看数据库日志（华为云控制台）

---

## 🎯 迁移后优化

迁移成功后，可以：
1. 更新备份脚本（修改华为云地址）
2. 设置华为云自动备份
3. 配置监控告警
4. 优化数据库性能参数

