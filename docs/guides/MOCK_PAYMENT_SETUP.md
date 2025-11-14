# 🎭 模拟支付配置指南（个人开发者推荐）

> **适用于**：个人开发者学习项目，无需企业认证，可立即使用！

---

## ✅ 为什么使用模拟支付？

### 个人开发者的限制
- ❌ **支付宝**：需要企业或个体工商户认证
- ❌ **微信支付**：需要企业认证
- ❌ **Ping++ 等聚合平台**：需要企业认证才能配置支付渠道

### 模拟支付的优势
- ✅ **无需认证**：不需要任何企业资质
- ✅ **立即可用**：代码已支持，无需配置
- ✅ **完整测试**：可以测试完整的支付流程
- ✅ **学习友好**：重点在学习商业模式和技术实现

---

## 🚀 如何使用模拟支付

### 方法一：完全不配置（推荐）

**不配置任何支付相关环境变量**，代码会自动使用模拟支付：

```python
# 代码会自动检测
if not self.enabled:
    # 使用模拟支付
    return {
        'id': f'mock_charge_{order_id}',
        'mock': True,
        # ...
    }
```

**配置**：
```env
# 不配置任何 PINGPP_* 或 ALIPAY_* 环境变量
# 代码会自动使用模拟支付
```

### 方法二：显式启用模拟支付

如果你想明确标识使用模拟支付：

```env
# 模拟支付配置
PAYMENT_MOCK_MODE=True
```

---

## 📋 模拟支付流程

### 1. 创建订单

```python
from backend.utils.external.pingpp_client import pingpp_client

# 创建支付订单（模拟）
result = pingpp_client.create_charge(
    order_id='ORDER_20250101_001',
    amount=0.1,  # 0.1元
    subject='测试订单',
    body='这是测试订单',
    user=request.user,
    payment_method='alipay'  # 或 'wx'
)

# 模拟支付立即返回
print(result)
# {
#     'id': 'mock_charge_ORDER_20250101_001',
#     'mock': True,
#     'paid': False,  # 需要前端触发"支付成功"
#     ...
# }
```

### 2. 前端处理（模拟支付）

```javascript
// 模拟支付页面
async function handleMockPayment(orderId) {
    // 显示"模拟支付"界面
    const confirmed = confirm('这是模拟支付，点击"确定"完成支付（仅用于测试）');
    
    if (confirmed) {
        // 调用后端 API，标记订单为已支付
        const response = await fetch(`/api/payment/mock-pay/${orderId}/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            // 支付成功，跳转到成功页面
            window.location.href = '/payment/success/';
        }
    }
}
```

### 3. 后端处理（模拟支付）

```python
# backend/api/viewsets/payment_viewset.py

@action(detail=True, methods=['post'], url_path='mock-pay')
def mock_pay(self, request, pk=None):
    """模拟支付接口（仅用于测试）"""
    order = self.get_object()
    
    if order.status != 'pending':
        return Response({'error': '订单状态不正确'}, status=400)
    
    # 标记订单为已支付（模拟）
    order.mark_as_paid(
        transaction_id=f'MOCK_{order.order_sn}',
        payment_channel='mock'
    )
    
    return Response({
        'code': 200,
        'message': '模拟支付成功',
        'data': {
            'order_sn': order.order_sn,
            'status': order.status
        }
    })
```

---

## 🎯 完整的模拟支付流程

```
用户创建订单
    ↓
前端显示"模拟支付"按钮
    ↓
用户点击"支付"（模拟）
    ↓
前端调用 /api/payment/orders/{id}/mock-pay/
    ↓
后端标记订单为已支付
    ↓
返回成功，跳转到成功页面
    ↓
订单完成！
```

---

## 💡 前端 UI 建议

### 模拟支付按钮

```vue
<template>
  <div class="payment-mock">
    <h3>🎭 模拟支付（仅用于测试）</h3>
    <p>这是模拟支付，不需要真实支付</p>
    <button @click="handleMockPay" class="btn btn-primary">
      完成支付（模拟）
    </button>
  </div>
</template>
```

### 支付成功提示

```vue
<template>
  <div class="payment-success">
    <h2>✅ 支付成功（模拟）</h2>
    <p>订单号：{{ order.order_sn }}</p>
    <p>金额：¥{{ order.amount }}</p>
    <button @click="goToTrip">查看我的旅行</button>
  </div>
</template>
```

---

## 📝 注意事项

### 开发环境
- ✅ **完全使用模拟支付**：不需要配置任何支付渠道
- ✅ **测试完整流程**：创建订单 → 支付 → 完成
- ✅ **学习技术实现**：重点在理解支付流程和业务逻辑

### 生产环境
- ⚠️ **如果上线真实项目**：需要注册企业或个体工商户
- ⚠️ **配置真实支付**：支付宝/微信/Ping++ 等
- ⚠️ **移除模拟支付**：或仅限管理员使用

---

## 🔒 安全建议

### 模拟支付限制

```python
# 仅在开发环境或测试环境启用模拟支付
if settings.DEBUG or os.getenv('PAYMENT_MOCK_MODE') == 'True':
    # 允许模拟支付
    pass
else:
    # 生产环境禁用模拟支付
    return Response({'error': '模拟支付仅限开发环境'}, status=403)
```

### 管理员限制

```python
# 仅管理员可以使用模拟支付
if not request.user.is_staff:
    return Response({'error': '权限不足'}, status=403)
```

---

## 🎓 学习重点

使用模拟支付，你可以：

1. **理解支付流程**：
   - 创建订单 → 支付 → 回调 → 完成
   
2. **实现业务逻辑**：
   - 权限检查（会员系统）
   - 订单管理
   - 支付状态更新

3. **前端交互**：
   - 支付页面
   - 成功/失败提示
   - 订单查询

4. **数据库设计**：
   - 订单表
   - 会员表
   - 支付记录表

---

## 🚀 快速开始

### 1. 确保代码已支持模拟支付

检查 `backend/utils/external/pingpp_client.py`：
```python
if not self.enabled:
    # 模拟支付逻辑
    return {...}
```

### 2. 不配置任何支付环境变量

```env
# 不配置 PINGPP_* 或 ALIPAY_* 
# 代码会自动使用模拟支付
```

### 3. 测试支付流程

```bash
# 创建测试订单
curl -X POST http://localhost:8000/api/payment/orders/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"amount": 0.1, "subject": "测试订单"}'

# 模拟支付
curl -X POST http://localhost:8000/api/payment/orders/{id}/mock-pay/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📚 参考代码

- `backend/utils/external/pingpp_client.py`：支付客户端（支持模拟）
- `backend/models/payment.py`：订单模型
- `backend/api/viewsets/payment_viewset.py`：支付 API（待实现）

---

**模拟支付配置完成！可以开始测试支付功能了！** 🎉

