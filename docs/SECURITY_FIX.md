# 🔒 安全修复：移除 Git 历史中的敏感信息

## ⚠️ 重要提醒

**发现的问题：**
- 数据库密码等敏感信息被提交到了 Git 仓库
- 这些信息在 Git 历史中仍然存在

**已完成的修复：**
- ✅ 移除了脚本中的硬编码密码
- ✅ 改为从环境变量读取配置
- ✅ 更新了 `.gitignore` 忽略配置文件
- ✅ 创建了配置示例文件

**仍需处理：**
- ⚠️ Git 历史中仍然包含敏感信息
- ⚠️ 需要清理 Git 历史（如果仓库是公开的，建议立即处理）

---

## 🛠️ 清理 Git 历史中的敏感信息

### 方法1：使用 git filter-branch（推荐）

```bash
# 警告：这会重写 Git 历史，需要强制推送
# 如果仓库是共享的，需要通知所有协作者

# 1. 备份仓库
cd ~
cp -r roamio roamio_backup

# 2. 清理历史中的敏感信息
cd roamio
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch scripts/backup_database.sh" \
  --prune-empty --tag-name-filter cat -- --all

# 3. 强制推送（危险操作！）
git push origin --force --all
git push origin --force --tags
```

### 方法2：使用 BFG Repo-Cleaner（更简单）

```bash
# 1. 下载 BFG
# https://rtyley.github.io/bfg-repo-cleaner/

# 2. 清理敏感信息
java -jar bfg.jar --replace-text passwords.txt

# 3. 清理和推送
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
```

### 方法3：如果仓库是私有的

如果仓库是私有的，可以：
1. 立即修改数据库密码（最重要！）
2. 清理历史（可选，但建议执行）

---

## 🔐 立即行动：修改数据库密码

**最重要！** 即使清理了 Git 历史，密码可能已经泄露：

1. **立即修改腾讯云 MySQL 密码**
   - 登录腾讯云控制台
   - 进入数据库实例
   - 修改密码

2. **更新所有配置文件**
   - 服务器上的 `~/.roamio_db_config`
   - Django 的 `settings.py`（如果也在 Git 中）
   - 其他使用该密码的地方

---

## 📋 检查清单

- [ ] 修改数据库密码（最重要！）
- [ ] 更新服务器上的配置文件
- [ ] 清理 Git 历史（如果仓库是公开的）
- [ ] 通知团队成员（如果有）
- [ ] 检查其他可能泄露的地方

---

## 💡 预防措施

1. **使用环境变量**：所有敏感信息都从环境变量读取
2. **使用 .gitignore**：确保配置文件不被提交
3. **使用 GitHub Secrets**：如果使用 CI/CD
4. **定期审查**：使用工具扫描仓库中的敏感信息

---

## 📞 需要帮助？

如果遇到问题：
1. 先修改数据库密码（最重要）
2. 然后考虑清理 Git 历史
3. 如果仓库是公开的，建议设为私有或清理历史

