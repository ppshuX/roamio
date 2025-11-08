-- ==========================================
-- Roamio RDS MySQL 数据库初始化脚本
-- ==========================================
-- 阿里云 RDS 实例：rm-wz91m3g4wa6io3dfi8o.mysql.rds.aliyuncs.com
-- 执行时间：2025-11-08
-- ==========================================

-- 1. 创建生产数据库
CREATE DATABASE IF NOT EXISTS roamio_production 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 2. 创建 Roamio 专用用户
CREATE USER IF NOT EXISTS 'roamio_user'@'%' IDENTIFIED BY 'Roamio@2025!Pass';

-- 3. 创建 Ralendar 专用用户
CREATE USER IF NOT EXISTS 'ralendar_user'@'%' IDENTIFIED BY 'Ralendar@2025!Pass';

-- 4. 授予 Roamio 用户完整权限
GRANT ALL PRIVILEGES ON roamio_production.* TO 'roamio_user'@'%';

-- 5. 授予 Ralendar 用户读写权限（不包括结构修改）
GRANT SELECT, INSERT, UPDATE, DELETE ON roamio_production.* TO 'ralendar_user'@'%';

-- 6. 刷新权限
FLUSH PRIVILEGES;

-- 7. 验证用户创建
SELECT User, Host FROM mysql.user WHERE User IN ('roamio_user', 'ralendar_user');

-- 8. 显示数据库
SHOW DATABASES;

-- ==========================================
-- 执行完成！
-- ==========================================
-- 下一步：
-- 1. 在本地执行此脚本连接 RDS
-- 2. 配置 Roamio 的 settings.py 使用新数据库
-- 3. 运行 Django 迁移
-- 4. 导入现有 SQLite 数据
-- ==========================================

