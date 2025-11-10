# 🔐 Roamio 安全检查清单

## ⚠️ 重要提醒

**永远不要将敏感信息提交到 Git 仓库！**

---

## 🔑 敏感信息清单

### 1. API Keys / 密钥
- ❌ **通义千问 API Key**: `QWEN_API_KEY`
- ❌ **腾讯云 COS 密钥**: `TENCENT_COS_SECRET_ID`, `TENCENT_COS_SECRET_KEY`
- ❌ **QQ OAuth 密钥**: `QQ_APP_KEY`
- ❌ **Django Secret Key**: `SECRET_KEY`

### 2. 邮箱凭证
- ❌ **邮箱密码/授权码**: `EMAIL_HOST_PASSWORD`
- ❌ **邮箱账号**: `EMAIL_HOST_USER`

### 3. 数据库凭证
- ❌ **Redis 密码**: `REDIS_PASSWORD`
- ❌ **MySQL 密码**: `DB_PASSWORD`

### 4. 其他敏感信息
- ❌ **服务器 IP 地址**
- ❌ **域名管理密码**
- ❌ **SSL 证书私钥**

---

## ✅ 安全实践

### 1. 使用环境变量
```python
# ✅ 正确做法
import os
api_key = os.getenv('QWEN_API_KEY')

# ❌ 错误做法
api_key = "sk-0b9ac4fb62f640e2aeb473f1cc30d34e"
```

### 2. 使用 .env 文件
```bash
# .env 文件（不提交到 Git）
QWEN_API_KEY=sk-真实的密钥
EMAIL_HOST_PASSWORD=真实的密码

# env.example 文件（可以提交）
QWEN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
EMAIL_HOST_PASSWORD=你的邮箱授权码
```

### 3. 配置 .gitignore
```bash
# 确保以下文件/目录在 .gitignore 中
.env
*.env
cloud_settings/.env
*.log
*.pid
__pycache__/
*.pyc
node_modules/
```

### 4. 文档中的示例
```markdown
# ✅ 正确：使用占位符
QWEN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

# ✅ 正确：使用脱敏
API Key: sk-****************************d34e

# ❌ 错误：暴露完整密钥
QWEN_API_KEY=sk-0b9ac4fb62f640e2aeb473f1cc30d34e
```

---

## 🔍 定期检查

### 检查命令
```bash
# 1. 搜索可能泄露的 API Key
grep -r "sk-0b9ac4fb" .
grep -r "AKID64qPk3EC" .

# 2. 搜索邮箱密码
grep -r "MWhM934vyBrYQGVU" .

# 3. 搜索 QQ OAuth 密钥
grep -r "OddPvLYXHo69wTYO" .

# 4. 检查 Git 历史（如果已提交）
git log -p | grep -i "api_key\|password\|secret"
```

### 如果已经泄露
1. **立即撤销密钥**
   - 阿里云百炼：删除旧 API Key，创建新的
   - 邮箱：修改授权码
   - 腾讯云：禁用旧密钥，创建新的

2. **清理 Git 历史**（如果已提交）
   ```bash
   # 使用 BFG Repo-Cleaner 或 git filter-branch
   # ⚠️ 谨慎操作，可能破坏历史记录
   ```

3. **更新所有配置**
   - 服务器 `.env` 文件
   - 本地开发环境
   - CI/CD 配置

---

## 📋 提交前检查清单

在每次 `git commit` 前，检查：

- [ ] 没有硬编码的 API Key
- [ ] 没有硬编码的密码
- [ ] `.env` 文件没有被添加
- [ ] 日志文件没有被添加
- [ ] 敏感配置已使用占位符
- [ ] 文档中的示例已脱敏

### 使用 Git Hooks
创建 `.git/hooks/pre-commit`：
```bash
#!/bin/bash

# 检查是否有敏感信息
if git diff --cached | grep -i "sk-0b9ac4fb\|MWhM934vyBrYQGVU\|OddPvLYXHo69wTYO"; then
    echo "❌ 错误：检测到敏感信息！"
    echo "请移除敏感信息后再提交。"
    exit 1
fi

echo "✅ 安全检查通过"
exit 0
```

---

## 🎯 团队规范

### 1. 新成员入职
- 提供 `.env.example` 模板
- 指导如何获取真实密钥
- 强调安全意识

### 2. 密钥管理
- 使用密钥管理工具（如 1Password、LastPass）
- 定期轮换密钥
- 最小权限原则

### 3. 代码审查
- Review 时检查敏感信息
- 使用自动化工具扫描
- 建立安全检查流程

---

## 🚨 应急响应

### 如果发现泄露
1. **立即行动**（5分钟内）
   - 撤销/禁用泄露的密钥
   - 通知团队成员

2. **评估影响**（30分钟内）
   - 检查是否被滥用
   - 查看 API 调用日志
   - 检查账户余额

3. **清理和恢复**（1小时内）
   - 生成新密钥
   - 更新所有配置
   - 清理 Git 历史

4. **总结和改进**（1天内）
   - 分析泄露原因
   - 改进安全流程
   - 团队培训

---

## 📚 参考资源

### 工具
- [git-secrets](https://github.com/awslabs/git-secrets) - 防止提交敏感信息
- [truffleHog](https://github.com/trufflesecurity/trufflehog) - 扫描 Git 历史
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/) - 清理 Git 历史

### 最佳实践
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [阿里云安全最佳实践](https://help.aliyun.com/document_detail/102600.html)

---

## ✅ 当前状态

### 已修复的泄露
- [x] `docs/AI_DEPLOYMENT_CHECKLIST.md` - 已脱敏 (2025-11-10)
- [x] `cloud_settings/env.example` - 已使用占位符 (2025-11-10)

### 待办事项
- [ ] 创建 Git pre-commit hook
- [ ] 配置自动化安全扫描
- [ ] 团队安全培训

---

*最后更新: 2025-11-10*  
*维护者: Roamio 开发团队*

**记住：安全无小事，预防胜于补救！** 🔐

