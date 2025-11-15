# Ralendar OAuth 2.0 集成总结文档

> **文档版本**：v1.0  
> **完成日期**：2025-11-15  
> **状态**：✅ 已完成并测试通过

---

## 📋 目录

1. [项目概述](#项目概述)
2. [实现功能](#实现功能)
3. [技术架构](#技术架构)
4. [关键修改](#关键修改)
5. [配置说明](#配置说明)
6. [测试结果](#测试结果)
7. [文件清单](#文件清单)
8. [后续优化](#后续优化)

---

## 🎯 项目概述

本项目实现了 Roamio 与 Ralendar 之间的 OAuth 2.0 标准授权流程，允许用户通过安全的授权机制将 Roamio 账号与 Ralendar 账号绑定，实现旅行计划的日历同步功能。

### 核心目标

- ✅ 实现标准的 OAuth 2.0 Authorization Code Flow
- ✅ 支持一个 Roamio 账号绑定多个 Ralendar 账号
- ✅ 提供完整的账号管理功能（绑定、设置默认、解绑）
- ✅ 使用 OAuth Token 进行安全的 API 调用

---

## ✨ 实现功能

### 1. OAuth 授权流程

- **获取授权 URL**：用户点击"连接 Ralendar"后，系统生成授权 URL 并跳转
- **用户授权**：用户在 Ralendar 授权页面完成登录和授权
- **回调处理**：Ralendar 返回授权码，Roamio 后端处理回调
- **Token 交换**：使用授权码换取 access_token 和 refresh_token
- **用户信息获取**：使用 access_token 获取 Ralendar 用户信息
- **账号绑定**：将 Ralendar 账号信息保存到数据库

### 2. 账号管理功能

- **账号列表**：查看所有已绑定的 Ralendar 账号
- **默认账号**：设置默认使用的 Ralendar 账号
- **多账号支持**：支持绑定多个 Ralendar 账号
- **解绑功能**：解绑指定的 Ralendar 账号（包括撤销 Ralendar 端授权）

### 3. 集成点

- **个人中心**：在用户中心提供 Ralendar 账号管理界面
- **侧边栏**：在全局侧边栏显示未绑定账号时的连接提示
- **同步功能**：修改同步逻辑，使用 OAuth Token 调用 Ralendar API

---

## 🏗️ 技术架构

### 后端架构

```
┌─────────────────────────────────────────────────────────┐
│                  Roamio Backend (Django)                │
├─────────────────────────────────────────────────────────┤
│  RalendarOAuthViewSet                                  │
│  ├── authorize_url()     # 获取授权 URL                │
│  ├── callback()          # 处理 OAuth 回调             │
│  ├── accounts()          # 获取账号列表                │
│  ├── set_default()       # 设置默认账号                │
│  └── unbind()            # 解绑账号                    │
│                                                         │
│  RalendarAccount Model                                  │
│  ├── 存储 OAuth Token                                   │
│  ├── 存储用户信息                                       │
│  └── 管理账号状态                                       │
└─────────────────────────────────────────────────────────┘
                         │
                         │ OAuth 2.0 Flow
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Ralendar OAuth Server                      │
├─────────────────────────────────────────────────────────┤
│  /oauth/authorize    # 授权页面                         │
│  /oauth/token        # Token 交换                       │
│  /oauth/userinfo     # 用户信息                         │
│  /oauth/revoke       # 撤销授权                         │
└─────────────────────────────────────────────────────────┘
```

### 前端架构

```
┌─────────────────────────────────────────────────────────┐
│                 Vue.js Frontend                         │
├─────────────────────────────────────────────────────────┤
│  RalendarAccountManager.vue                             │
│  ├── 账号列表展示                                       │
│  ├── 连接/解绑操作                                      │
│  └── 默认账号设置                                       │
│                                                         │
│  RalendarCallback.vue                                   │
│  └── OAuth 回调处理                                     │
│                                                         │
│  GlobalSidebar.vue                                      │
│  └── 未绑定账号提示                                     │
│                                                         │
│  UserCenterView.vue                                     │
│  └── 集成账号管理组件                                   │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 关键修改

### 1. 数据库模型

**新增模型**：`RalendarAccount`

- 存储 Ralendar 用户的 OAuth Token
- 存储用户基本信息（用户名、邮箱、头像等）
- 支持多账号绑定和默认账号管理
- 包含 Token 过期时间检查和自动刷新机制

**关键字段**：
- `access_token`: OAuth Access Token
- `refresh_token`: OAuth Refresh Token
- `token_expires_at`: Token 过期时间
- `is_default`: 是否为默认账号
- `ralendar_user_id`: Ralendar 用户 ID（唯一标识）

### 2. API 端点

**新增 ViewSet**：`RalendarOAuthViewSet`

| 端点 | 方法 | 功能 | 权限 |
|------|------|------|------|
| `/ralendar-oauth/authorize-url/` | GET | 获取授权 URL | 已登录 |
| `/ralendar-oauth/callback/` | POST | 处理 OAuth 回调 | 公开 |
| `/ralendar-oauth/accounts/` | GET | 获取账号列表 | 已登录 |
| `/ralendar-oauth/{id}/set-default/` | POST | 设置默认账号 | 已登录 |
| `/ralendar-oauth/{id}/unbind/` | DELETE | 解绑账号 | 已登录 |

### 3. 同步逻辑修改

**修改文件**：`backend/api/viewsets/ralendar_viewset.py`

- 从使用 `unionid`/`openid`/`email` 改为使用 OAuth `access_token`
- 支持选择指定的 Ralendar 账号进行同步
- 自动检查 Token 是否过期，提示用户重新授权

### 4. URL 路径修复

**修复问题**：OAuth 端点 URL 配置错误

- ❌ 之前：`/api/oauth/token`、`/api/oauth/userinfo`
- ✅ 修复后：`/oauth/token`、`/oauth/userinfo`

---

## ⚙️ 配置说明

### 环境变量配置

在 `cloud_settings/.env` 文件中配置以下变量：

```bash
# Ralendar OAuth 配置
RALENDAR_OAUTH_CLIENT_ID=ralendar_client_CJjjv6N9prR6JpDGmWijgA
RALENDAR_OAUTH_CLIENT_SECRET=ZaEM6BTUqZ_KMPXq_Bh9ixlhRyBgG_YFc8cuRYbybms
RALENDAR_OAUTH_REDIRECT_URI=https://roamio.cn/auth/ralendar/callback

# Ralendar OAuth 端点（测试环境）
RALENDAR_OAUTH_AUTHORIZE_URL=https://app7626.acapp.acwing.com.cn/oauth/authorize
RALENDAR_OAUTH_TOKEN_URL=https://app7626.acapp.acwing.com.cn/oauth/token
RALENDAR_OAUTH_USERINFO_URL=https://app7626.acapp.acwing.com.cn/oauth/userinfo
```

### 前端路由配置

在 `web/src/router/index.js` 中新增路由：

```javascript
{
  path: '/auth/ralendar/callback',
  name: 'ralendar-callback',
  component: () => import('@/views/auth/RalendarCallback.vue'),
  meta: {
    title: 'Ralendar 授权回调',
    requiresAuth: false
  }
}
```

---

## ✅ 测试结果

### 测试环境

- **Roamio 后端**：Django 5.2
- **Roamio 前端**：Vue 3 + Vue Router
- **Ralendar OAuth Server**：app7626.acapp.acwing.com.cn
- **测试日期**：2025-11-15

### 测试用例

| 测试项 | 状态 | 备注 |
|--------|------|------|
| 获取授权 URL | ✅ 通过 | 正确生成授权链接 |
| 用户授权流程 | ✅ 通过 | 授权页面正常显示 |
| OAuth 回调处理 | ✅ 通过 | 成功接收授权码 |
| Token 交换 | ✅ 通过 | 成功获取 access_token |
| 用户信息获取 | ✅ 通过 | 成功获取用户信息 |
| 账号绑定 | ✅ 通过 | 数据正确保存到数据库 |
| 账号列表显示 | ✅ 通过 | 前端正确展示账号信息 |
| 设置默认账号 | ✅ 通过 | 默认账号逻辑正确 |
| 多账号绑定 | ✅ 通过 | 支持绑定多个账号 |
| 解绑账号 | ✅ 通过 | 成功解绑并撤销授权 |

### 已知问题

无已知问题。

---

## 📁 文件清单

### 后端文件

```
backend/
├── models/
│   ├── ralendar_account.py          # RalendarAccount 模型
│   └── __init__.py                   # 模型导出
├── api/
│   ├── viewsets/
│   │   ├── ralendar_oauth_viewset.py # OAuth ViewSet
│   │   └── ralendar_viewset.py       # 同步逻辑修改
│   ├── serializers/
│   │   └── ralendar_serializers.py   # RalendarAccount 序列化器
│   └── urls.py                       # 路由注册
└── migrations/
    └── 0009_ralendaraccount.py      # 数据库迁移
```

### 前端文件

```
web/src/
├── api/
│   └── ralendarOAuth.js              # OAuth API 服务
├── components/
│   ├── ralendar/
│   │   └── RalendarAccountManager.vue # 账号管理组件
│   └── events/
│       └── GlobalSidebar.vue          # 侧边栏修改
├── views/
│   ├── auth/
│   │   └── RalendarCallback.vue       # OAuth 回调页面
│   └── user-center/
│       └── UserCenterView.vue         # 个人中心集成
└── router/
    └── index.js                       # 路由配置
```

### 配置文件

```
roamio/
└── settings.py                        # OAuth 配置

cloud_settings/
└── env.example                        # 环境变量示例
```

### 文档文件

```
docs/integration/
├── RALENDAR_OAUTH_INTEGRATION_SPEC.md    # OAuth 集成规范
├── OAUTH_IMPLEMENTATION_PROGRESS.md      # 实现进度
├── OAUTH_SETUP_GUIDE.md                  # 设置指南
├── OAUTH_TEST_PLAN.md                    # 测试计划
└── OAUTH_IMPLEMENTATION_SUMMARY.md       # 本文档
```

---

## 🚀 后续优化

### 已规划功能

1. **Token 自动刷新**：实现 Token 过期前的自动刷新机制
2. **错误处理优化**：更友好的错误提示和恢复流程
3. **性能优化**：账号列表查询的性能优化
4. **日志完善**：添加更详细的操作日志记录

### 可扩展功能

1. **账号切换**：快速切换不同 Ralendar 账号进行同步
2. **同步历史**：记录同步历史，方便用户查看
3. **批量操作**：支持批量解绑或设置默认账号
4. **权限管理**：细化权限控制（只读、读写等）

---

## 📝 关键时间节点

- **2025-11-14**：开始实现 OAuth 2.0 集成
- **2025-11-14**：完成后端 OAuth ViewSet 实现
- **2025-11-14**：完成前端组件开发
- **2025-11-15**：修复 OAuth 端点 URL 配置问题
- **2025-11-15**：完成测试并成功连接 ✅

---

## 🙏 致谢

感谢 Ralendar 团队提供的 OAuth 2.0 服务器实现和详细的技术文档支持。

---

**文档维护者**：Roamio 开发团队  
**最后更新**：2025-11-15

