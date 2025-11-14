# Ralendar 邮箱占用检查接口文档

> **集成对接**：Roamio ↔ Ralendar 邮箱可用性验证

---

## 📡 接口信息

| 项目 | 说明 |
| --- | --- |
| **Method** | `POST` |
| **URL** | `/api/fusion/users/check-email/` |
| **Auth** | 不需要认证（AllowAny） |
| **超时** | 建议 3s |
| **实现文件** | `backend/api/views/integration/fusion.py` |

---

## 📥 请求格式

### Headers

```http
Content-Type: application/json
```

### Body

```json
{
  "email": "user@example.com"
}
```

### 参数说明

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `email` | string | ✅ | 待检查的邮箱（不区分大小写，会自动转为小写） |

---

## 📤 响应格式

### 场景 A：邮箱不存在（可用）

**HTTP 200 OK**

```json
{
  "exists": false
}
```

---

### 场景 B：邮箱已被 QQ 用户占用

**HTTP 200 OK**

```json
{
  "exists": true,
  "provider": "qq",
  "match_type": "unionid",
  "owner": {
    "email": "user@example.com",
    "unionid": "UID_XXXXXXXXXXXXXXXXXXXXXXXX",
    "openid": "OPENID_XXXXXXXXXXXXXXXX",
    "user_id": 12345,
    "nickname": "Ralendar QQ用户"
  }
}
```

**字段说明：**

| 字段 | 说明 |
| --- | --- |
| `exists` | 是否存在：`true` |
| `provider` | 登录方式：`qq` / `acwing` / `email` |
| `match_type` | 匹配方式：`unionid` / `openid` / `email` |
| `owner.email` | 占用该邮箱的用户邮箱 |
| `owner.unionid` | **QQ UnionID**（Roamio 用于判断是否同一用户） |
| `owner.openid` | QQ OpenID |
| `owner.user_id` | Ralendar 内部用户 ID |
| `owner.nickname` | 用户昵称 |

---

### 场景 C：邮箱被 AcWing 用户占用

**HTTP 200 OK**

```json
{
  "exists": true,
  "provider": "acwing",
  "match_type": "openid",
  "owner": {
    "email": "user@example.com",
    "unionid": "",
    "openid": "ACWING_OPENID_XXX",
    "user_id": 67890,
    "nickname": "Ralendar AcWing用户"
  }
}
```

> **注意**：AcWing 用户没有 `unionid`，字段为空字符串。

---

### 场景 D：邮箱被普通注册用户占用

**HTTP 200 OK**

```json
{
  "exists": true,
  "provider": "email",
  "match_type": "email",
  "owner": {
    "email": "user@example.com",
    "unionid": "",
    "openid": "",
    "user_id": 11111,
    "nickname": "Ralendar普通用户"
  }
}
```

---

## ⚠️ 错误响应

### 400 Bad Request - 邮箱格式错误

```json
{
  "error": "invalid_email",
  "message": "邮箱格式不正确"
}
```

### 400 Bad Request - 邮箱为空

```json
{
  "error": "invalid_email",
  "message": "邮箱不能为空"
}
```

### 500 Internal Server Error - 服务器错误

```json
{
  "error": "server_error",
  "message": "服务器内部错误"
}
```

---

## 🧪 测试用例

### 测试脚本（Python）

```python
import requests

API_URL = "https://app7626.acapp.acwing.com.cn/api/fusion/users/check-email/"

# 测试 1：邮箱不存在
def test_email_not_exists():
    response = requests.post(API_URL, json={
        "email": "nonexistent_user_12345@example.com"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["exists"] == False
    print("✅ 测试通过：邮箱不存在")

# 测试 2：邮箱已被占用
def test_email_exists():
    response = requests.post(API_URL, json={
        "email": "existing_user@example.com"  # 替换为实际存在的邮箱
    })
    assert response.status_code == 200
    data = response.json()
    assert data["exists"] == True
    assert "owner" in data
    assert "unionid" in data["owner"]
    print(f"✅ 测试通过：邮箱已被占用 (Provider: {data['provider']})")

# 测试 3：邮箱格式错误
def test_invalid_email():
    response = requests.post(API_URL, json={
        "email": "invalid-email-format"
    })
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "invalid_email"
    print("✅ 测试通过：邮箱格式错误")

# 测试 4：空邮箱
def test_empty_email():
    response = requests.post(API_URL, json={
        "email": ""
    })
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "invalid_email"
    print("✅ 测试通过：空邮箱")

if __name__ == "__main__":
    test_email_not_exists()
    test_invalid_email()
    test_empty_email()
    # test_email_exists()  # 需要替换真实邮箱后测试
    print("\n🎉 所有测试通过！")
```

### cURL 测试

```bash
# 测试邮箱不存在
curl -X POST https://app7626.acapp.acwing.com.cn/api/fusion/users/check-email/ \
  -H "Content-Type: application/json" \
  -d '{"email": "nonexistent@example.com"}'

# 测试邮箱已存在
curl -X POST https://app7626.acapp.acwing.com.cn/api/fusion/users/check-email/ \
  -H "Content-Type: application/json" \
  -d '{"email": "existing_user@example.com"}'
```

---

## 🔒 安全建议

1. **频率限制**：建议在 Nginx 或 Django Middleware 添加频率限制（如每 IP 每分钟 60 次）

2. **日志记录**：所有请求已记录到 Django logger，格式为：

   ```
   [Email Check] 检查邮箱: user@example.com
   [Email Check] ✅ 邮箱可用: user@example.com
   [Email Check] ❌ 邮箱已被占用: user@example.com (User ID: 123)
   ```

3. **服务端白名单（可选）**：可在视图中添加 IP 白名单或共享 Token 验证

---

## 🔗 Roamio 集成说明

### Roamio 调用时机

1. **用户注册**：输入邮箱后、发送验证码前

2. **更改邮箱**：输入新邮箱后、保存前

### Roamio 业务逻辑

```python
# Roamio 端示例代码
def check_email_before_register(email, current_user_unionid):
    response = requests.post(
        "https://app7626.acapp.acwing.com.cn/api/fusion/users/check-email/",
        json={"email": email},
        timeout=3
    )
    
    if response.status_code != 200:
        # 接口异常，降级为仅本地检查
        return check_local_email(email)
    
    data = response.json()
    
    if not data["exists"]:
        # 邮箱可用
        return True
    
    # 邮箱已被占用
    owner_unionid = data["owner"]["unionid"]
    
    if owner_unionid and owner_unionid == current_user_unionid:
        # 同一个 QQ 用户，允许继续
        return True
    else:
        # 不同用户，阻止注册
        raise Exception(f"该邮箱已被使用，请使用 QQ 登录或更换邮箱")
```

---

## 📝 实现细节

### 用户匹配优先级

1. **QQ 用户**（优先级最高）：返回 `unionid` 和 `openid`

2. **AcWing 用户**：返回 `openid`（`unionid` 为空）

3. **普通邮箱用户**：`unionid` 和 `openid` 均为空

### 数据库查询

```python
# 1. 通过邮箱查找用户
user = User.objects.get(email=email)

# 2. 尝试关联 QQ 信息
qq_user = QQUser.objects.get(user=user)  # 优先级最高

# 3. 尝试关联 AcWing 信息
acwing_user = AcWingUser.objects.get(user=user)

# 4. 普通用户（无第三方绑定）
```

---

## 🚀 部署清单

- [x] 视图函数实现：`backend/api/views/integration/fusion.py`
- [x] 路由配置：`backend/api/url_patterns/fusion.py`
- [x] 视图导出：`backend/api/views/__init__.py`
- [ ] 数据库迁移（如需）：无需新建表
- [ ] Nginx 配置频率限制（可选）
- [ ] 监控告警配置（可选）

---

## 📞 联系方式

如有技术问题，请联系：

- **Ralendar Team**: dev@ralendar.example.com
- **Roamio Team**: dev@roamio.cn

**最后更新**：2025-11-14
