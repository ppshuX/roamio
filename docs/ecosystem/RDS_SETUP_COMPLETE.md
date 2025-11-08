# ✅ Roamio RDS 数据库配置完成

> **配置日期**: 2025-11-08  
> **数据库类型**: 阿里云 RDS MySQL  
> **状态**: ✅ 已完成初始化

---

## 🎉 **配置摘要**

### 已完成的工作

1. ✅ **创建阿里云 RDS 实例**
   - 实例 ID: `rm-wz91m3g4wa6io3dfi`
   - 区域: 华南1（深圳）
   - 规格: 2核 4GB 50GB
   - 类型: 包年包月（2个月免费试用）

2. ✅ **配置网络访问**
   - 内网地址: `rm-wz91m3g4wa6io3dfi.mysql.rds.aliyuncs.com:3306`
   - 外网地址: `rm-wz91m3g4wa6io3dfi8o.mysql.rds.aliyuncs.com:3306`
   - 白名单: 已添加 Roamio 和 Ralendar 服务器 IP

3. ✅ **创建数据库和用户**
   - 数据库: `roamio_production`
   - 高权限账号: `Roamio2025`
   - Roamio 用户: `roamio_user` (完整权限)
   - Ralendar 用户: `ralendar_user` (读写权限)

4. ✅ **创建迁移文档和脚本**
   - SQL 初始化脚本: `scripts/init_rds_database.sql`
   - 迁移指南: `docs/RDS_MIGRATION_GUIDE.md`
   - 配置脚本: `scripts/configure_rds.sh`
   - 数据迁移脚本: `scripts/migrate_sqlite_to_rds.py`

---

## 📊 **连接信息**

### Roamio 使用

```python
# roamio/settings.py
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

### Ralendar 使用

```bash
# .env
DB_TYPE=mysql
DB_HOST=rm-wz91m3g4wa6io3dfi8o.mysql.rds.aliyuncs.com
DB_PORT=3306
DB_NAME=roamio_production
DB_USER=ralendar_user
DB_PASSWORD=Ralendar@2025!Pass
```

---

## 🚀 **下一步操作**

### 在 Roamio 服务器上执行

```bash
# 1. 安装 MySQL 驱动
pip install mysqlclient

# 2. 更新 settings.py（使用上面的配置）
vim roamio/settings.py

# 3. 运行数据库迁移
python manage.py migrate

# 4. 导出 SQLite 数据（如果需要）
python manage.py dumpdata \
    --natural-foreign \
    --natural-primary \
    --exclude auth.permission \
    --exclude contenttypes \
    --indent 2 > data_backup.json

# 5. 导入数据到 RDS
python manage.py loaddata data_backup.json

# 6. 创建超级用户（如果需要）
python manage.py createsuperuser

# 7. 重启服务
sudo systemctl restart uwsgi
```

---

## 🔐 **账号权限说明**

### 1. Roamio2025 (高权限账号)
- **用途**: 数据库管理、创建用户、修改结构
- **权限**: 完整数据库管理权限
- **密码**: `Abcdefg1234567@`

### 2. roamio_user (Roamio 应用账号)
- **用途**: Roamio 应用日常使用
- **权限**: `roamio_production` 数据库的所有操作
- **密码**: `Roamio@2025!Pass`

### 3. ralendar_user (Ralendar 应用账号)
- **用途**: Ralendar 应用访问 Roamio 数据
- **权限**: `roamio_production` 数据库的 SELECT, INSERT, UPDATE, DELETE
- **密码**: `Ralendar@2025!Pass`

---

## 📋 **数据库表结构**

Roamio 数据库包含以下主要表：

### 用户相关
- `auth_user` - Django 用户表
- `trips_userprofile` - 用户扩展信息
- `trips_socialaccount` - 社交账号绑定（包含 UnionID）
- `trips_emailverification` - 邮箱验证

### 旅行相关
- `trips_trip` - 旅行记录
- `trips_comment` - 评论

### 系统相关
- `trips_sitestat` - 网站统计

---

## 🔄 **数据同步策略**

### Roamio → Ralendar
- **用户数据**: 通过 QQ UnionID 关联
- **旅行事项**: Ralendar 可读取 Roamio 的旅行数据
- **提醒功能**: Ralendar 可为 Roamio 的旅行添加提醒

### Ralendar → Roamio
- **日历事件**: Ralendar 的事件可同步到 Roamio
- **提醒通知**: 共享提醒系统

---

## 🛡️ **安全建议**

1. ✅ **定期备份**
   - 使用 `scripts/backup_rds.sh` 每天自动备份
   - 保留最近 7 天的备份

2. ✅ **密码管理**
   - 定期更换数据库密码
   - 不要在代码中硬编码密码
   - 使用环境变量或配置文件

3. ✅ **访问控制**
   - 白名单只包含必要的 IP
   - 定期审查访问日志

4. ✅ **监控告警**
   - 配置 RDS 监控告警
   - 关注 CPU、内存、连接数

---

## 📞 **联系信息**

### Roamio 服务器
- **IP**: 47.121.137.60
- **域名**: app7508.acapp.acwing.com.cn

### Ralendar 服务器
- **IP**: 81.71.138.122

### RDS 实例
- **控制台**: [阿里云 RDS 控制台](https://rdsnext.console.aliyun.com/)
- **实例 ID**: rm-wz91m3g4wa6io3dfi

---

## 📚 **相关文档**

- [RDS 迁移指南](../RDS_MIGRATION_GUIDE.md)
- [Roamio 数据库信息](./ROAMIO_DATABASE_INFO_FOR_RALENDAR.md)
- [阿里云 RDS 文档](https://help.aliyun.com/product/26090.html)

---

## ✅ **检查清单**

- [x] RDS 实例已创建
- [x] 网络访问已配置
- [x] 白名单已设置
- [x] 数据库已创建
- [x] 用户已创建
- [x] 权限已授予
- [x] 连接测试成功
- [x] 文档已创建
- [ ] Roamio 已迁移到 RDS
- [ ] 数据已导入
- [ ] Ralendar 已配置连接
- [ ] 功能测试通过

---

**恭喜！RDS 数据库配置完成！** 🎉

现在可以开始迁移 Roamio 的数据了！

