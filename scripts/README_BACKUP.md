# 数据库备份说明

## ⚠️ 重要提醒

**腾讯云 MySQL 数据库即将到期：**
- 实例ID: `cdb-k9ylziyr`
- 到期时间: **2025-12-08 16:18:00**
- 预计停服时间: **2025-12-15 16:18:00**

**请务必在到期前：**
1. ✅ **立即备份数据库**（使用下面的脚本）
2. ✅ **续费数据库**（前往腾讯云控制台）
3. ✅ **设置自动续费**（避免再次忘记）

---

## 📋 备份脚本使用说明

### 1. 手动备份

在服务器上执行：

```bash
cd ~/roamio
./scripts/backup_database.sh
```

备份文件将保存在：`/backup/roamio_db/roamio_backup_YYYYMMDD_HHMMSS.sql.gz`

### 2. 设置自动备份

设置每天凌晨2点自动备份：

```bash
cd ~/roamio
./scripts/setup_auto_backup.sh
```

### 3. 恢复数据库

如果需要恢复备份：

```bash
# 解压备份文件
gunzip /backup/roamio_db/roamio_backup_20251208_020000.sql.gz

# 恢复数据库
mysql -h gz-cdb-k9ylziyr.sql.tencentcdb.com -P 23768 \
      -u roamio_user -p \
      roamio_production < /backup/roamio_db/roamio_backup_20251208_020000.sql
```

---

## 🔧 数据库配置信息

- **主机**: `gz-cdb-k9ylziyr.sql.tencentcdb.com`
- **端口**: `23768`
- **数据库名**: `roamio_production`
- **用户名**: `roamio_user`
- **密码**: `Roamio@2025!Pass`（在 settings.py 中配置）

---

## 📦 备份文件管理

- 备份文件会自动压缩（.sql.gz 格式）
- 自动保留最近7天的备份
- 旧备份会自动清理

---

## 🚨 紧急情况处理

如果数据库已经停服，但你有备份文件：

1. **购买新的 MySQL 实例**（腾讯云控制台）
2. **创建数据库**：
   ```sql
   CREATE DATABASE roamio_production CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. **恢复备份**（使用上面的恢复命令）
4. **更新 settings.py 中的数据库配置**

---

## 💡 建议

1. **立即执行一次手动备份**，确保数据安全
2. **设置自动备份**，每天自动备份
3. **前往腾讯云控制台续费**，避免服务中断
4. **设置自动续费**，避免再次忘记

---

## 📞 联系方式

- 腾讯云客服：95716
- 腾讯云控制台：https://console.cloud.tencent.com/

