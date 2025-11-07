# 🌍 Roamio 生态 - 统一 API 规范

> **版本**: v1.0.0  
> **更新日期**: 2025-11-07  
> **适用范围**: Roamio 主平台 + 所有子产品（Ralendar, Rote, Rapture 等）

---

## 📋 目录

1. [设计原则](#设计原则)
2. [URL 规范](#url-规范)
3. [请求规范](#请求规范)
4. [响应规范](#响应规范)
5. [认证规范](#认证规范)
6. [错误码规范](#错误码规范)
7. [版本管理](#版本管理)
8. [命名规范](#命名规范)

---

## 🎯 设计原则

### 1. RESTful 风格
- 使用标准 HTTP 方法（GET, POST, PUT, PATCH, DELETE）
- 资源用名词表示，操作用 HTTP 方法表示
- URL 层级清晰，语义明确

### 2. 统一性
- 所有子产品遵循相同的 API 规范
- 错误码、响应格式统一
- 认证方式统一（JWT）

### 3. 可扩展性
- 支持版本管理（v1, v2...）
- 支持分页、过滤、排序
- 支持国际化

### 4. 安全性
- 敏感数据加密传输（HTTPS）
- JWT Token 认证
- 权限控制

---

## 🔗 URL 规范

### 基础格式

```
https://{domain}/api/{version}/{module}/{resource}/{action}
```

### 示例

```bash
# Roamio 主平台
https://app7508.acapp.acwing.com.cn/api/v1/trips/123/
https://app7508.acapp.acwing.com.cn/api/v1/users/456/profile/

# Ralendar（未来）
https://app7508.acapp.acwing.com.cn/api/v1/ralendar/events/
https://app7508.acapp.acwing.com.cn/api/v1/ralendar/calendars/

# Rote（未来）
https://app7508.acapp.acwing.com.cn/api/v1/rote/notes/
```

### 命名规则

| 规则 | 说明 | 示例 |
|------|------|------|
| 小写字母 | 所有 URL 使用小写 | `/api/v1/users/` ✅<br>`/api/v1/Users/` ❌ |
| 复数形式 | 资源名使用复数 | `/api/v1/trips/` ✅<br>`/api/v1/trip/` ❌ |
| 连字符 | 多个单词用 `-` 连接 | `/api/v1/trip-plans/` ✅<br>`/api/v1/trip_plans/` ❌ |
| 无动词 | URL 中不包含动词 | `/api/v1/users/123/` ✅<br>`/api/v1/get-user/123/` ❌ |

### HTTP 方法映射

| 方法 | 操作 | URL 示例 | 说明 |
|------|------|----------|------|
| GET | 查询 | `GET /api/v1/trips/` | 获取列表 |
| GET | 查询 | `GET /api/v1/trips/123/` | 获取详情 |
| POST | 创建 | `POST /api/v1/trips/` | 创建资源 |
| PUT | 完整更新 | `PUT /api/v1/trips/123/` | 完整更新 |
| PATCH | 部分更新 | `PATCH /api/v1/trips/123/` | 部分更新 |
| DELETE | 删除 | `DELETE /api/v1/trips/123/` | 删除资源 |

---

## 📤 请求规范

### 请求头

```http
Content-Type: application/json
Authorization: Bearer <access_token>
Accept-Language: zh-CN
```

### 请求体（JSON）

```json
{
  "title": "云南7日游",
  "start_date": "2025-12-01",
  "end_date": "2025-12-07",
  "description": "探索彩云之南"
}
```

### 查询参数

#### 分页

```bash
GET /api/v1/trips/?page=1&page_size=20
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | int | 1 | 页码（从1开始） |
| page_size | int | 20 | 每页数量 |

#### 过滤

```bash
GET /api/v1/trips/?status=published&author=123
```

#### 搜索

```bash
GET /api/v1/trips/?search=云南
```

#### 排序

```bash
GET /api/v1/trips/?ordering=-created_at
```

- 升序：`ordering=created_at`
- 降序：`ordering=-created_at`
- 多字段：`ordering=-created_at,title`

---

## 📥 响应规范

### 成功响应

#### 列表查询（带分页）

```json
{
  "count": 100,
  "next": "https://app7508.acapp.acwing.com.cn/api/v1/trips/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "云南7日游",
      "created_at": "2025-11-07 10:00:00"
    }
  ]
}
```

#### 详情查询

```json
{
  "id": 1,
  "title": "云南7日游",
  "start_date": "2025-12-01",
  "end_date": "2025-12-07",
  "description": "探索彩云之南",
  "created_at": "2025-11-07 10:00:00",
  "updated_at": "2025-11-07 12:00:00"
}
```

#### 创建/更新成功

```json
{
  "id": 1,
  "title": "云南7日游",
  "message": "创建成功"
}
```

#### 删除成功

```json
{
  "message": "删除成功"
}
```

### HTTP 状态码

| 状态码 | 说明 | 使用场景 |
|--------|------|----------|
| 200 | OK | 查询、更新成功 |
| 201 | Created | 创建成功 |
| 204 | No Content | 删除成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证 |
| 403 | Forbidden | 无权限 |
| 404 | Not Found | 资源不存在 |
| 500 | Internal Server Error | 服务器错误 |

---

## 🔐 认证规范

### JWT Token 认证

#### 1. 获取 Token

**请求**：
```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "username": "user123",
  "password": "password123"
}
```

**响应**：
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com"
  }
}
```

#### 2. 使用 Token

在请求头中添加：

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

#### 3. 刷新 Token

**请求**：
```http
POST /api/v1/auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**响应**：
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Token 有效期

| Token 类型 | 有效期 | 说明 |
|-----------|--------|------|
| Access Token | 1 天 | 用于 API 调用 |
| Refresh Token | 7 天 | 用于刷新 Access Token |

---

## ⚠️ 错误码规范

### 错误响应格式

```json
{
  "error": "错误类型",
  "message": "详细错误信息",
  "code": "ERROR_CODE",
  "details": {
    "field": "具体字段错误"
  }
}
```

### 统一错误码

#### 认证相关（1xxx）

| 错误码 | 说明 | HTTP 状态码 |
|--------|------|-------------|
| 1001 | 未登录 | 401 |
| 1002 | Token 过期 | 401 |
| 1003 | Token 无效 | 401 |
| 1004 | 用户名或密码错误 | 400 |
| 1005 | 账号已被禁用 | 403 |

#### 权限相关（2xxx）

| 错误码 | 说明 | HTTP 状态码 |
|--------|------|-------------|
| 2001 | 无权限访问 | 403 |
| 2002 | 无权限编辑 | 403 |
| 2003 | 无权限删除 | 403 |

#### 资源相关（3xxx）

| 错误码 | 说明 | HTTP 状态码 |
|--------|------|-------------|
| 3001 | 资源不存在 | 404 |
| 3002 | 资源已存在 | 400 |
| 3003 | 资源已被删除 | 410 |

#### 参数相关（4xxx）

| 错误码 | 说明 | HTTP 状态码 |
|--------|------|-------------|
| 4001 | 参数缺失 | 400 |
| 4002 | 参数格式错误 | 400 |
| 4003 | 参数值超出范围 | 400 |

#### 业务相关（5xxx）

| 错误码 | 说明 | HTTP 状态码 |
|--------|------|-------------|
| 5001 | 操作失败 | 400 |
| 5002 | 重复操作 | 400 |
| 5003 | 操作冲突 | 409 |

#### 系统相关（9xxx）

| 错误码 | 说明 | HTTP 状态码 |
|--------|------|-------------|
| 9001 | 服务器内部错误 | 500 |
| 9002 | 服务暂时不可用 | 503 |
| 9003 | 数据库错误 | 500 |

### 错误示例

```json
{
  "error": "ValidationError",
  "message": "参数验证失败",
  "code": "4002",
  "details": {
    "title": ["标题不能为空"],
    "start_date": ["日期格式错误"]
  }
}
```

---

## 📌 版本管理

### URL 版本控制

```bash
# v1 版本（当前）
https://app7508.acapp.acwing.com.cn/api/v1/trips/

# v2 版本（未来）
https://app7508.acapp.acwing.com.cn/api/v2/trips/
```

### 版本兼容性

- **向后兼容**：新版本应尽量兼容旧版本
- **废弃通知**：废弃的 API 应提前通知（至少 3 个月）
- **文档标注**：在文档中明确标注版本信息

### 废弃 API 响应头

```http
Warning: 299 - "This API version is deprecated and will be removed on 2026-01-01"
```

---

## 📝 命名规范

### 字段命名

#### 通用字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | int | 主键ID |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |
| deleted_at | datetime | 软删除时间 |
| is_deleted | boolean | 是否删除 |

#### 用户相关

| 字段名 | 类型 | 说明 |
|--------|------|------|
| username | string | 用户名 |
| email | string | 邮箱 |
| avatar | string | 头像URL |
| avatar_url | string | 头像完整URL |

#### 内容相关

| 字段名 | 类型 | 说明 |
|--------|------|------|
| title | string | 标题 |
| content | string | 内容 |
| description | string | 描述 |
| cover | string | 封面图 |
| status | string | 状态 |

### 状态值命名

```python
# 发布状态
STATUS_DRAFT = 'draft'          # 草稿
STATUS_PUBLISHED = 'published'  # 已发布
STATUS_ARCHIVED = 'archived'    # 已归档

# 审核状态
REVIEW_PENDING = 'pending'      # 待审核
REVIEW_APPROVED = 'approved'    # 已通过
REVIEW_REJECTED = 'rejected'    # 已拒绝
```

---

## 🔗 模块划分

### Roamio 主平台

```
/api/v1/auth/          # 认证模块
/api/v1/users/         # 用户模块
/api/v1/trips/         # 旅行模块
/api/v1/comments/      # 评论模块
/api/v1/stats/         # 统计模块
```

### Ralendar（日历）

```
/api/v1/ralendar/calendars/      # 日历管理
/api/v1/ralendar/events/         # 事件管理
/api/v1/ralendar/subscriptions/  # 订阅管理
/api/v1/ralendar/reminders/      # 提醒管理
```

### Rote（笔记）

```
/api/v1/rote/notes/              # 笔记管理
/api/v1/rote/notebooks/          # 笔记本管理
/api/v1/rote/tags/               # 标签管理
```

### Rapture（照片）

```
/api/v1/rapture/albums/          # 相册管理
/api/v1/rapture/photos/          # 照片管理
/api/v1/rapture/tags/            # 标签管理
```

---

## 🌐 国际化

### 请求头

```http
Accept-Language: zh-CN
```

### 支持语言

| 语言代码 | 语言 |
|---------|------|
| zh-CN | 简体中文 |
| zh-TW | 繁体中文 |
| en-US | 英语 |
| ja-JP | 日语 |

---

## 📚 API 文档

### 访问地址

- **Swagger UI**（交互式）: https://app7508.acapp.acwing.com.cn/api/docs/
- **ReDoc**（美观）: https://app7508.acapp.acwing.com.cn/api/redoc/
- **OpenAPI Schema**（JSON）: https://app7508.acapp.acwing.com.cn/api/schema/

### 文档规范

每个 API 应包含：

1. **接口描述**：功能说明
2. **请求示例**：完整的请求示例
3. **响应示例**：成功和失败的响应示例
4. **参数说明**：每个参数的类型、是否必填、默认值
5. **错误码**：可能返回的错误码

---

## ✅ 检查清单

在发布新 API 前，请确认：

- [ ] 遵循 RESTful 风格
- [ ] URL 命名符合规范
- [ ] 使用标准 HTTP 方法和状态码
- [ ] 响应格式统一
- [ ] 错误处理完善
- [ ] 添加认证和权限控制
- [ ] 编写 API 文档
- [ ] 添加单元测试
- [ ] 性能测试通过
- [ ] 安全审查通过

---

## 📞 联系方式

如有疑问或建议，请联系：

- **邮箱**: 2064747320@qq.com
- **GitHub**: [Roamio 项目](https://github.com/your-repo/roamio)

---

**最后更新**: 2025-11-07  
**维护者**: Roamio Team

