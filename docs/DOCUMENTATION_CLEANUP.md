# 📚 文档清理与整理计划

**目的**：整理冗余文档，优化文档结构

---

## 📋 当前文档分类

### ✅ 保留（核心文档）
1. **`ROAMIO_V2_LAUNCH_SUMMARY.md`** - v2.0 上线总结 ⭐⭐⭐⭐⭐
2. **`README.md`** - 项目说明
3. **`docs/README.md`** - 文档索引
4. **`docs/PROJECT_STRUCTURE.md`** - 项目结构
5. **`docs/DEBUG_CLEANUP_PLAN.md`** - 调试清理计划

### ✅ 保留（部署相关）
6. **`cloud_settings/nginx_roamio.cn.conf`** - Nginx 配置
7. **`cloud_settings/uwsgi.ini`** - uWSGI 配置
8. **`cloud_settings/env.example`** - 环境变量示例
9. **`cloud_settings/SSL_CERTIFICATE_TROUBLESHOOTING.md`** - SSL 排查指南
10. **`cloud_settings/POST_MIGRATION_CHECKLIST.md`** - 迁移后检查清单

### ✅ 保留（API 文档）
11. **`docs/api/ECOSYSTEM_API_DOCUMENTATION.md`** - API 完整文档

### ✅ 保留（安全）
12. **`docs/SECURITY_CHECKLIST.md`** - 安全检查清单

---

## 🗑️ 建议归档/删除（已完成的迁移文档）

### 服务器迁移（已完成）
- **`SERVER_MIGRATION_GUIDE.md`** → 移到 `docs/archived/`
- **`RALENDAR_TEAM_NOTICE.md`** → 移到 `docs/archived/`
- **`migration_scripts/export_roamio.sh`** → 保留（可复用）
- **`migration_scripts/import_roamio.sh`** → 保留（可复用）

### 数据库迁移（已完成）
- **`cloud_settings/DATABASE_MIGRATION_TO_TENCENT.md`** → 移到 `docs/archived/`
- **`cloud_settings/QUICK_DB_MIGRATION_STEPS.md`** → 移到 `docs/archived/`
- **`cloud_settings/DOMAIN_MIGRATION_GUIDE.md`** → 移到 `docs/archived/`

### 私有信息（不应提交）
- **`cloud_settings/MIGRATION_PRIVATE_INFO.md`** → 已在 .gitignore（保留本地）

---

## 📝 可能冗余的文档（需要合并）

### AI 相关文档（7个，内容可能重复）
1. `docs/AI_DEPLOYMENT_CHECKLIST.md`
2. `docs/AI_INTEGRATION_MILESTONE.md`
3. `docs/AI_MVP_DEPLOYMENT.md`
4. `docs/AI_MVP_SUMMARY.md`
5. `docs/AI_PHASE2_RAG_PLAN.md` → 未来计划
6. `docs/AI_ROADMAP.md` → 未来计划
7. `docs/AI_TRIP_PLANNER.md`

**建议**：
- 保留 `AI_INTEGRATION_MILESTONE.md`（里程碑记录）
- 保留 `AI_ROADMAP.md`（未来规划）
- 其他合并到 `docs/features/AI_FEATURE.md`

### Ralendar 相关文档（6个）
1. `docs/RALENDAR_COLLABORATION_PLAN.md`
2. `docs/REPLY_TO_RALENDAR_20251110.md`
3. `docs/ecosystem/ROAMIO_DATABASE_INFO_FOR_RALENDAR.md` → **已过期**（数据库已迁移）
4. `docs/ecosystem/ROAMIO_INTEGRATION_REPORT.md`
5. `docs/ecosystem/ROAMIO_RESPONSE_TO_RALENDAR.md`
6. `docs/features/RALENDAR_INTEGRATION.md`

**建议**：
- 更新 `ROAMIO_DATABASE_INFO_FOR_RALENDAR.md`（数据库地址已变）
- 合并其他文档到 `docs/ecosystem/RALENDAR_INTEGRATION.md`

### 重构完成文档（已过期）
- `docs/REFACTOR_COMPLETE_SUMMARY.md` → 移到 `docs/archived/`
- `docs/UTILS_REFACTOR_COMPLETED.md` → 移到 `docs/archived/`
- `docs/BACKEND_UTILS_REFACTOR.md` → 移到 `docs/archived/`

---

## 🎯 清理执行计划

### 立即删除
- [x] `test_ai_debug.py` - 调试脚本

### 本周归档（移到 docs/archived/）
- [ ] 已完成的迁移文档（5个）
- [ ] 已完成的重构文档（3个）

### 下周合并
- [ ] AI 相关文档合并（保留 2-3 个核心）
- [ ] Ralendar 文档合并（保留 2 个核心）

---

## 📂 优化后的文档结构

```
roamio/
├── ROAMIO_V2_LAUNCH_SUMMARY.md     # v2.0 上线总结 ⭐
├── README.md                        # 项目说明
├── docs/
│   ├── README.md                    # 文档索引
│   ├── PROJECT_STRUCTURE.md         # 项目结构
│   ├── DEBUG_CLEANUP_PLAN.md        # 调试清理计划
│   ├── SECURITY_CHECKLIST.md        # 安全检查
│   ├── api/
│   │   └── ECOSYSTEM_API_DOCUMENTATION.md  # API 文档
│   ├── features/
│   │   ├── AI_FEATURE.md            # AI 功能（合并后）
│   │   └── RALENDAR_INTEGRATION.md  # Ralendar 集成
│   ├── guides/
│   │   ├── DEPLOYMENT_GUIDE.md      # 部署指南
│   │   └── ...
│   ├── ecosystem/
│   │   └── RALENDAR_DATABASE.md     # Ralendar 数据库信息（更新后）
│   └── archived/                    # 已完成的历史文档
│       ├── SERVER_MIGRATION_GUIDE.md
│       ├── DATABASE_MIGRATION_TO_TENCENT.md
│       └── ...
├── cloud_settings/
│   ├── nginx_roamio.cn.conf
│   ├── uwsgi.ini
│   ├── env.example
│   └── ...（部署配置）
└── migration_scripts/               # 可复用的迁移脚本
    ├── export_roamio.sh
    └── import_roamio.sh
```

---

**此清理计划将在稳定期逐步执行。**

