# 🔄 Roamio & Ralendar 服务器迁移方案

## 📋 迁移背景

**问题**：`roamio.cn` 域名备案在腾讯云（81.71.138.122），但实际运行在阿里云（47.121.137.60），违反工信部备案规定。

**解决方案**：服务器对调
- ✅ 利用Docker容器化优势，快速迁移
- ✅ 保持现有备案号有效
- ✅ 避免重新备案的长时间等待

---

## 🎯 迁移目标

### 现状
```
阿里云 47.121.137.60  →  Roamio (roamio.cn)
腾讯云 81.71.138.122  →  Ralendar (app7626.acapp.acwing.com.cn)
```

### 迁移后
```
阿里云 47.121.137.60  →  Ralendar (app7626.acapp.acwing.com.cn)
腾讯云 81.71.138.122  →  Roamio (roamio.cn) ✅ 符合备案要求
```

---

## 📦 迁移准备清单

### 1. 确认服务器配置

**阿里云 (47.121.137.60)**
- [ ] 操作系统版本
- [ ] Docker 版本
- [ ] 磁盘空间（至少10GB可用）
- [ ] 内存（建议2GB+）

**腾讯云 (81.71.138.122)**
- [ ] 操作系统版本
- [ ] Docker 版本
- [ ] 磁盘空间（至少10GB可用）
- [ ] 内存（建议2GB+）

### 2. 备份数据

**Roamio**
```bash
# 备份数据库
docker exec roamio-db mysqldump -u root -p roamio_production > roamio_backup_$(date +%Y%m%d).sql

# 备份媒体文件
tar -czf roamio_media_$(date +%Y%m%d).tar.gz ~/roamio/media

# 备份配置文件
tar -czf roamio_config_$(date +%Y%m%d).tar.gz ~/roamio/cloud_settings
```

**Ralendar**
```bash
# 备份数据库
docker exec ralendar-db pg_dump -U postgres ralendar_db > ralendar_backup_$(date +%Y%m%d).sql

# 备份媒体文件（如果有）
tar -czf ralendar_media_$(date +%Y%m%d).tar.gz ~/ralendar/media

# 备份配置文件
tar -czf ralendar_config_$(date +%Y%m%d).tar.gz ~/ralendar/config
```

---

## 🚀 迁移步骤

### Phase 1: 导出Docker镜像（10分钟）

#### 在阿里云上（Roamio）

```bash
# 1. 查看当前运行的容器
docker ps

# 2. 导出Roamio镜像
docker commit roamio-web roamio:migration-$(date +%Y%m%d)
docker save roamio:migration-$(date +%Y%m%d) -o roamio_image.tar

# 3. 导出数据库容器（如果有单独的DB容器）
docker commit roamio-db roamio-db:migration-$(date +%Y%m%d)
docker save roamio-db:migration-$(date +%Y%m%d) -o roamio_db.tar

# 4. 查看文件大小
ls -lh roamio*.tar

# 5. 上传到临时存储（方式1：使用阿里云OSS）
# 或者直接通过scp传输到腾讯云（方式2）
scp roamio_image.tar root@81.71.138.122:/tmp/
scp roamio_db.tar root@81.71.138.122:/tmp/
scp roamio_backup_*.sql root@81.71.138.122:/tmp/
```

#### 在腾讯云上（Ralendar）

```bash
# 1. 查看当前运行的容器
docker ps

# 2. 导出Ralendar镜像
docker commit ralendar-web ralendar:migration-$(date +%Y%m%d)
docker save ralendar:migration-$(date +%Y%m%d) -o ralendar_image.tar

# 3. 导出数据库容器
docker commit ralendar-db ralendar-db:migration-$(date +%Y%m%d)
docker save ralendar-db:migration-$(date +%Y%m%d) -o ralendar_db.tar

# 4. 上传到阿里云
scp ralendar_image.tar root@47.121.137.60:/tmp/
scp ralendar_db.tar root@47.121.137.60:/tmp/
scp ralendar_backup_*.sql root@47.121.137.60:/tmp/
```

---

### Phase 2: 停止现有服务（5分钟）

⚠️ **注意**：这会导致服务短暂不可用（预计20-30分钟）

**建议时间**：凌晨2:00-3:00（访问量最低）

#### 在阿里云上
```bash
# 停止Roamio服务
docker-compose down

# 或者
docker stop roamio-web roamio-db
```

#### 在腾讯云上
```bash
# 停止Ralendar服务
docker-compose down

# 或者
docker stop ralendar-web ralendar-db
```

---

### Phase 3: 加载镜像并启动（15分钟）

#### 在腾讯云上启动Roamio

```bash
# 1. 加载镜像
cd /tmp
docker load -i roamio_image.tar
docker load -i roamio_db.tar

# 2. 创建工作目录
mkdir -p ~/roamio
cd ~/roamio

# 3. 上传或复制以下文件到这里：
#    - docker-compose.yml
#    - .env
#    - nginx配置
#    - SSL证书

# 4. 恢复数据库（如果需要）
docker run -d --name roamio-db roamio-db:migration-YYYYMMDD
# 等待数据库启动
sleep 10
docker exec -i roamio-db mysql -u root -p < /tmp/roamio_backup_*.sql

# 5. 启动服务
docker-compose up -d

# 6. 查看日志
docker-compose logs -f
```

#### 在阿里云上启动Ralendar

```bash
# 1. 加载镜像
cd /tmp
docker load -i ralendar_image.tar
docker load -i ralendar_db.tar

# 2. 创建工作目录
mkdir -p ~/ralendar
cd ~/ralendar

# 3. 上传配置文件

# 4. 恢复数据库
docker run -d --name ralendar-db ralendar-db:migration-YYYYMMDD
sleep 10
docker exec -i ralendar-db psql -U postgres ralendar_db < /tmp/ralendar_backup_*.sql

# 5. 启动服务
docker-compose up -d

# 6. 查看日志
docker-compose logs -f
```

---

### Phase 4: 更新DNS解析（5分钟）

#### 修改DNS记录

**roamio.cn**
```
类型: A
主机记录: @
记录值: 81.71.138.122  (从 47.121.137.60 改为腾讯云IP)
TTL: 600 (10分钟)
```

**app7626.acapp.acwing.com.cn**
```
类型: A
主机记录: app7626
记录值: 47.121.137.60  (从 81.71.138.122 改为阿里云IP)
TTL: 600
```

⚠️ **DNS生效时间**：10分钟 - 2小时（取决于运营商缓存）

---

### Phase 5: 配置Nginx和SSL（10分钟）

#### 在腾讯云上（Roamio）

```bash
# 1. 配置Nginx for roamio.cn
cat > /etc/nginx/sites-available/roamio.cn.conf << 'EOF'
server {
    listen 80;
    server_name roamio.cn www.roamio.cn;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name roamio.cn www.roamio.cn;

    ssl_certificate /etc/nginx/ssl/roamio.cn.crt;
    ssl_certificate_key /etc/nginx/ssl/roamio.cn.key;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/acs/roamio/staticfiles/;
    }

    location /media/ {
        alias /home/acs/roamio/media/;
    }
}
EOF

# 2. 启用配置
ln -s /etc/nginx/sites-available/roamio.cn.conf /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

#### 在阿里云上（Ralendar）

```bash
# 配置Nginx for app7626.acapp.acwing.com.cn
# (类似的配置)
```

---

## ✅ 验证清单

### 功能测试

**Roamio (roamio.cn - 腾讯云)**
- [ ] 网站可以访问（https://roamio.cn）
- [ ] 用户可以登录
- [ ] 旅行列表正常显示
- [ ] 可以创建新旅行
- [ ] 图片和媒体文件正常加载
- [ ] 评论功能正常
- [ ] Ralendar集成正常
- [ ] 天气查询正常
- [ ] 备案号正确显示

**Ralendar (app7626... - 阿里云)**
- [ ] API可以访问
- [ ] 事件创建/编辑/删除正常
- [ ] 与Roamio的集成正常
- [ ] 数据同步正常

### 性能测试

```bash
# 测试响应时间
curl -w "\nTotal time: %{time_total}s\n" https://roamio.cn

# 测试SSL
openssl s_client -connect roamio.cn:443 -servername roamio.cn

# 测试API
curl -X GET https://roamio.cn/api/v1/trips/
```

---

## 🔙 回滚方案

如果迁移失败，立即执行回滚：

### 快速回滚（5分钟内）

```bash
# 1. 恢复DNS到原来的IP
roamio.cn → 47.121.137.60 (阿里云)
app7626... → 81.71.138.122 (腾讯云)

# 2. 在原服务器重启服务
# 阿里云
cd ~/roamio
docker-compose up -d

# 腾讯云
cd ~/ralendar
docker-compose up -d
```

---

## 📊 迁移时间表

| 阶段 | 时间 | 负责人 | 状态 |
|------|------|--------|------|
| 备份数据 | 30分钟 | 双方 | ⏳ 待执行 |
| 导出镜像 | 10分钟 | 双方 | ⏳ 待执行 |
| 传输文件 | 20分钟 | 双方 | ⏳ 待执行 |
| 停止服务 | 5分钟 | 双方 | ⏳ 待执行 |
| 加载&启动 | 15分钟 | 双方 | ⏳ 待执行 |
| DNS更新 | 5分钟 | Roamio | ⏳ 待执行 |
| 验证测试 | 30分钟 | 双方 | ⏳ 待执行 |
| **总计** | **约2小时** | | |

---

## 📞 联系方式

**Roamio团队**
- 负责人：吕文潇
- 服务器：腾讯云 81.71.138.122 (目标)
- 域名：roamio.cn
- 备案号：滇ICP备2025073012号-1

**Ralendar团队**
- 负责人：[待填写]
- 服务器：阿里云 47.121.137.60 (目标)
- 域名：app7626.acapp.acwing.com.cn

---

## 🎯 迁移建议时间

**推荐时间**：2025年11月14日（周四）凌晨 02:00 - 04:00
- ✅ 访问量最低
- ✅ 有充足时间处理意外情况
- ✅ 工作日白天可以持续监控

**备选时间**：周末凌晨（11月16日 02:00）

---

## ⚠️ 注意事项

1. **提前通知用户**：在网站首页发布维护公告
2. **保持通讯畅通**：迁移期间双方保持在线沟通
3. **准备回滚**：确保可以在5分钟内回滚到原状态
4. **监控日志**：迁移后持续24小时监控系统日志
5. **备案更新**：迁移完成后，如需要可以更新备案信息中的接入商

---

## 📝 迁移后续工作

1. **更新文档**：更新项目README中的服务器信息
2. **监控告警**：配置新服务器的监控和告警
3. **性能优化**：观察新环境下的性能表现
4. **清理旧数据**：确认稳定后，清理原服务器上的数据

---

## 🤝 协作建议

1. **同步时间**：两边同时开始操作
2. **实时沟通**：使用微信/钉钉保持联系
3. **分工明确**：
   - Roamio团队：负责腾讯云上的Roamio部署
   - Ralendar团队：负责阿里云上的Ralendar部署
4. **互相支持**：遇到问题及时互相协助

---

## 📚 附录

### A. Docker Compose 模板

详见项目中的 `docker-compose.yml` 文件

### B. 常见问题排查

**Q: Docker容器无法启动？**
```bash
# 查看日志
docker logs container_name

# 检查端口占用
netstat -tlnp | grep 8000
```

**Q: 数据库连接失败？**
```bash
# 检查数据库容器状态
docker ps | grep db

# 进入容器检查
docker exec -it db_container bash
```

**Q: Nginx配置错误？**
```bash
# 测试配置
nginx -t

# 查看错误日志
tail -f /var/log/nginx/error.log
```

---

**创建日期**：2025-11-13  
**版本**：v1.0  
**状态**：待执行

---

🚀 **Let's make this migration smooth and successful!**

