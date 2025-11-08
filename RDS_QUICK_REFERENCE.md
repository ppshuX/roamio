# 🚀 Roamio RDS 快速参考

## 📊 连接信息

```bash
# RDS 实例
HOST=rm-wz91m3g4wa6io3dfi8o.mysql.rds.aliyuncs.com
PORT=3306
DATABASE=roamio_production

# Roamio 账号
USER=roamio_user
PASS=Roamio@2025!Pass

# Ralendar 账号
USER=ralendar_user
PASS=Ralendar@2025!Pass

# 管理员账号
ADMIN=Roamio2025
ADMIN_PASS=Abcdefg1234567@
```

---

## 🔧 常用命令

### 连接数据库
```bash
mysql -h rm-wz91m3g4wa6io3dfi8o.mysql.rds.aliyuncs.com \
      -P 3306 \
      -u roamio_user \
      -p'Roamio@2025!Pass' \
      roamio_production
```

### Django 配置
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'roamio_production',
        'USER': 'roamio_user',
        'PASSWORD': 'Roamio@2025!Pass',
        'HOST': 'rm-wz91m3g4wa6io3dfi8o.mysql.rds.aliyuncs.com',
        'PORT': '3306',
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}
```

### 数据迁移
```bash
# 1. 安装驱动
pip install mysqlclient

# 2. 运行迁移
python manage.py migrate

# 3. 导出 SQLite
python manage.py dumpdata --exclude contenttypes --indent 2 > backup.json

# 4. 导入 RDS
python manage.py loaddata backup.json
```

---

## 📚 文档

- **完整指南**: `docs/RDS_MIGRATION_GUIDE.md`
- **配置完成**: `docs/ecosystem/RDS_SETUP_COMPLETE.md`
- **Ralendar 信息**: `docs/ecosystem/ROAMIO_DATABASE_INFO_FOR_RALENDAR.md`

---

## 🆘 故障排查

### 连接失败
1. 检查白名单是否包含你的 IP
2. 检查用户名密码是否正确
3. 测试网络: `ping rm-wz91m3g4wa6io3dfi8o.mysql.rds.aliyuncs.com`

### 权限不足
```sql
-- 使用管理员账号授权
GRANT ALL PRIVILEGES ON roamio_production.* TO 'roamio_user'@'%';
FLUSH PRIVILEGES;
```

---

**快速参考完成！** 🎉

