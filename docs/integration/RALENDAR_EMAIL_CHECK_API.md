# 📮 Ralendar 邮箱占用检查接口规范

> **背景**：Roamio 需要在注册 / 更改邮箱阶段，确定目标邮箱是否已经在 Ralendar 侧被其他账号使用，以避免同一邮箱被不同人占用、导致行程同步混乱。

本规范说明了 Ralendar 需要实现的 HTTP 接口，Roamio 将调用该接口完成邮箱可用性检查。

---

## 1. 接口概览

| 项目 | 说明 |
| --- | --- |
| **Method** | `POST` |
| **URL** | `/fusion/users/check-email/` |
| **Auth** | 建议校验 Roamio 发起方（可通过服务端白名单 / 预共享 Token） |
| **Body** | JSON，包含 `email` |
| **Timeout** | 3s（Roamio 端默认超时） |

### 1.1 请求体

```json
{
  "email": "user@example.com"
}
```

> - `email`：必填，不区分大小写。Ralendar 需自行做格式验证。

### 1.2 返回体

#### 场景 A：邮箱不存在

```json
{
  "exists": false
}
```

#### 场景 B：邮箱已被占用

```json
{
  "exists": true,
  "provider": "qq",
  "match_type": "unionid",
  "owner": {
    "email": "user@example.com",
    "unionid": "UNIONID_xxx",
    "openid": "OPENID_xxx",
    "user_id": 12345,
    "nickname": "Ralendar 用户昵称"
  }
}
```

字段说明：

| 字段 | 说明 |
| --- | --- |
| `exists` | `true/false`，表示邮箱是否在 Ralendar 侧存在 |
| `provider` | 可选，标记占用邮箱的登录方式（如 `qq`、`acwing` 等） |
| `match_type` | 可选，说明匹配依据（如 `unionid`、`email`） |
| `owner` | 可选，关于占用该邮箱的 Ralendar 账号信息 |
| `owner.unionid/openid` | **强烈建议返回**。Roamio 可以据此判断是否与当前 QQ 用户为同一人 |
| `owner.user_id` | 可选，Ralendar 内部用户 ID，便于排查问题 |

> **说明**：当 `owner.unionid` 与 Roamio 当前用户的 QQ `unionid` 一致时，Roamio 会视为同一用户，允许继续绑定/修改邮箱。

### 1.3 错误返回

| HTTP Code | 情况 | 建议返回 |
| --- | --- | --- |
| `400` | 请求体缺失 / 参数非法 | `{"error": "invalid_email"}` |
| `401/403` | 身份认证失败 | `{"error": "unauthorized"}` |
| `500` | 服务故障 | `{"error": "server_error"}` |

Roamio 在收到异常时会记录告警，并退化为“仅本地检查”逻辑。

---

## 2. Roamio 调用行为

- **注册**：发送验证码 / 注册前，会调用该接口。若返回 `exists=true` 且 `owner.unionid` 不匹配，将阻止注册并提示“请使用 QQ 登录”。
- **更改邮箱**：用户输入新邮箱后，Roamio 会调用该接口。若邮箱被其他 Ralendar 账号使用，则拒绝修改。
- **同一个 QQ 用户**：如果 `owner.unionid` 与当前用户相同，Roamio 会视为合法（允许更新，以便同步最新邮箱）。
- **AcWing 账号**：若 Ralendar 返回 `provider=acwing` 且无 `unionid`，Roamio 会认为邮箱被“其他人”使用，并要求更换邮箱。

---

## 3. 调试建议

1. 提供测试环境地址/密钥，便于 Roamio 集成测试。
2. 日志中至少记录：`email`、`exists`、`owner.unionid`、`owner.user_id`，便于快速追踪问题。
3. 若未来支持“统一用户中心”，该接口仍然是重要的防御机制，可保留作为双保险。

---

## 4. 版本规划

| 阶段 | Roamio 侧状态 | Ralendar 需求 | 说明 |
| --- | --- | --- | --- |
| v1 | 已上线邮箱检查 API (`/api/v1/auth/check-email/`) | 实现本规范接口 | 无需额外改动 |
| v2 | 统一用户中心 | 接口可保留（optional） | 作为 fallback |

---

如需进一步技术对接，请联系 Roamio 团队：`dev@roamio.cn`

