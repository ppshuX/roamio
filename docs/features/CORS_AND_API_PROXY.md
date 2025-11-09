# 🌐 为什么前端不能直接调用 Ralendar API？CORS 与 API 代理详解

## 📋 目录

1. [问题现象](#问题现象)
2. [什么是 CORS](#什么是-cors)
3. [为什么会被 CORS 阻止](#为什么会被-cors-阻止)
4. [解决方案：后端代理](#解决方案后端代理)
5. [技术实现](#技术实现)
6. [优缺点对比](#优缺点对比)

---

## 🚨 问题现象

当 Roamio 前端直接调用 Ralendar API 时，浏览器控制台会出现以下错误：

```
Access to fetch at 'https://app7626.acapp.acwing.com.cn/api/v1/events/' 
from origin 'https://app7508.acapp.acwing.com.cn' 
has been blocked by CORS policy: 
Response to preflight request doesn't pass access control check: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

---

## 🔒 什么是 CORS？

**CORS (Cross-Origin Resource Sharing)** = 跨域资源共享

### 同源策略 (Same-Origin Policy)

浏览器的安全机制，规定：
- **只有相同源的网页才能互相访问资源**
- **源 (Origin)** = 协议 + 域名 + 端口

### 什么是"同源"？

| URL 1 | URL 2 | 是否同源 | 原因 |
|-------|-------|---------|------|
| `https://app7508.acapp.acwing.com.cn` | `https://app7508.acapp.acwing.com.cn/api/` | ✅ 同源 | 协议、域名、端口完全相同 |
| `https://app7508.acapp.acwing.com.cn` | `https://app7626.acapp.acwing.com.cn` | ❌ 跨域 | 域名不同 (7508 vs 7626) |
| `https://example.com` | `http://example.com` | ❌ 跨域 | 协议不同 (https vs http) |
| `https://example.com:443` | `https://example.com:8080` | ❌ 跨域 | 端口不同 (443 vs 8080) |

---

## 🚫 为什么会被 CORS 阻止？

### Roamio 和 Ralendar 的情况

```
Roamio 前端:  https://app7508.acapp.acwing.com.cn
Ralendar API: https://app7626.acapp.acwing.com.cn

域名不同 → 跨域请求 → 被 CORS 阻止 ❌
```

### CORS 的工作流程

1. **浏览器发送 Preflight 请求**（OPTIONS 方法）
   ```
   OPTIONS https://app7626.acapp.acwing.com.cn/api/v1/events/
   Origin: https://app7508.acapp.acwing.com.cn
   ```

2. **服务器需要返回允许的源**
   ```
   Access-Control-Allow-Origin: https://app7508.acapp.acwing.com.cn
   Access-Control-Allow-Methods: GET, POST, PUT, DELETE
   Access-Control-Allow-Headers: Authorization, Content-Type
   ```

3. **如果服务器没有返回这些头，浏览器会阻止请求** ❌

---

## ✅ 解决方案：后端代理

### 方案对比

| 方案 | 优点 | 缺点 | 是否可行 |
|------|------|------|---------|
| **方案 1：Ralendar 配置 CORS** | 简单，前端直接调用 | 需要 Ralendar 团队配置，安全风险 | ⚠️ 需要 Ralendar 配合 |
| **方案 2：Roamio 后端代理** | 完全控制，安全，灵活 | 增加后端代码 | ✅ **推荐方案** |
| **方案 3：JSONP** | 绕过 CORS | 只支持 GET，不安全 | ❌ 不推荐 |

### 为什么选择后端代理？

1. **不受 CORS 限制**：
   - 后端到后端的请求不受浏览器同源策略限制
   - 服务器之间可以自由通信

2. **安全性更高**：
   - 可以在代理层添加额外的验证
   - 可以隐藏敏感信息（如 API Key）
   - 可以统一处理认证逻辑

3. **灵活性更强**：
   - 可以修改请求/响应数据
   - 可以添加日志和监控
   - 可以实现缓存和限流

---

## 🛠️ 技术实现

### 架构图

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   浏览器     │         │   Roamio    │         │  Ralendar   │
│  (前端)     │ ──────> │   后端      │ ──────> │    API      │
│             │  同源✅  │  (代理)     │  跨域✅  │             │
└─────────────┘         └─────────────┘         └─────────────┘
     CORS 限制              不受 CORS 限制
```

### 前端代码

```javascript
// ❌ 错误：直接调用 Ralendar API（会被 CORS 阻止）
fetch('https://app7626.acapp.acwing.com.cn/api/v1/events/', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`
  }
})

// ✅ 正确：通过 Roamio 后端代理
fetch('/api/v1/ralendar/trips/events/', {  // ← 同源请求
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
```

### 后端代理代码

```python
# backend/api/viewsets/ralendar_viewset.py

class RalendarIntegrationViewSet(ViewSet):
    """Ralendar 集成 API（代理）"""
    
    @action(detail=False, methods=['get'], url_path='events')
    def list_events(self, request):
        """
        代理：获取事件列表
        
        前端调用：GET /api/v1/ralendar/trips/events/
        后端转发：GET https://app7626.acapp.acwing.com.cn/api/v1/fusion/events/
        """
        user_token = self.get_user_token(request)
        
        # 获取 UnionID
        social_account = SocialAccount.objects.filter(
            user=request.user,
            provider='qq'
        ).first()
        unionid = social_account.unionid if social_account else None
        
        # 调用 Ralendar API
        client = RalendarClient()
        result = client.list_events(user_token, unionid=unionid)
        
        # 返回给前端
        return Response({
            'results': result.get('events', []),
            'count': result.get('events_count', 0)
        })
```

### Ralendar API 客户端

```python
# backend/utils/ralendar_client.py

class RalendarClient:
    """Ralendar API 客户端"""
    
    def list_events(self, user_token, unionid=None):
        """调用 Ralendar Fusion API"""
        url = f"{self.base_url}/fusion/events/"
        headers = {
            'Authorization': f'Bearer {user_token}',
            'Content-Type': 'application/json'
        }
        params = {'unionid': unionid} if unionid else {}
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
```

---

## 📊 优缺点对比

### 方案 1：前端直接调用（被 CORS 阻止）

**优点**：
- ✅ 代码简单
- ✅ 减少后端负载

**缺点**：
- ❌ 被浏览器 CORS 策略阻止
- ❌ 需要 Ralendar 配置 CORS 白名单
- ❌ 安全性较低（Token 暴露在前端）
- ❌ 无法添加额外的业务逻辑

### 方案 2：后端代理（推荐）

**优点**：
- ✅ 不受 CORS 限制
- ✅ 安全性更高
- ✅ 可以添加日志、监控、缓存
- ✅ 可以统一处理认证（自动添加 UnionID/OpenID）
- ✅ 可以转换数据格式
- ✅ 完全控制，不依赖第三方配置

**缺点**：
- ⚠️ 增加后端代码量
- ⚠️ 增加一层网络请求（但延迟很小）

---

## 🔐 安全性考虑

### 为什么后端代理更安全？

1. **Token 不暴露给第三方**：
   - 前端只与 Roamio 后端通信
   - Roamio 后端再与 Ralendar 通信
   - 中间可以添加额外的验证

2. **可以隐藏敏感信息**：
   - API Key、Secret Key 等不暴露在前端
   - 可以在后端层面做权限控制

3. **防止恶意请求**：
   - 可以在代理层添加限流
   - 可以验证请求合法性
   - 可以记录审计日志

---

## 📝 完整的 API 代理列表

### Roamio 提供的代理接口

| 前端调用 | 后端转发 | 功能 |
|---------|---------|------|
| `GET /api/v1/ralendar/trips/events/` | `GET https://app7626.../fusion/events/` | 获取事件列表 |
| `POST /api/v1/ralendar/trips/events/create/` | `POST https://app7626.../fusion/events/batch/` | 创建事件 |
| `PUT /api/v1/ralendar/trips/events/{id}/` | `PUT https://app7626.../events/{id}/` | 更新事件 |
| `DELETE /api/v1/ralendar/trips/events/{id}/` | `DELETE https://app7626.../events/{id}/` | 删除事件 |

### 自动添加的字段

后端代理会自动添加：
- ✅ `unionid`：从 Roamio 数据库获取
- ✅ `openid`：从 Roamio 数据库获取
- ✅ `source_app: "roamio"`：标识来源

---

## 🎯 总结

### 为什么前端 fetch 不行？

1. **浏览器安全策略**：CORS 是浏览器强制执行的安全机制
2. **跨域限制**：Roamio (app7508) 和 Ralendar (app7626) 是不同的域
3. **Preflight 检查失败**：Ralendar 没有返回允许 Roamio 访问的 CORS 头

### 为什么要用后端代理？

1. **绕过 CORS**：服务器之间的通信不受浏览器限制
2. **更安全**：Token 和敏感信息不暴露
3. **更灵活**：可以添加业务逻辑、日志、监控
4. **统一管理**：所有 Ralendar API 调用都经过 Roamio 后端

### 类比

```
前端直接调用 = 你直接给陌生人打电话（被拒绝）
后端代理     = 你通过朋友转达（朋友帮你打电话）
```

---

## 🔗 相关文档

- [MDN: CORS](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/CORS)
- [Ralendar 集成文档](./RALENDAR_INTEGRATION.md)
- [集成测试指南](../ecosystem/INTEGRATION_TEST_GUIDE.md)

---

**最后更新：2025-11-09**

