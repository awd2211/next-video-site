# 支付与订阅系统实施指南

## 📋 系统概述

本视频平台已实现完整的订阅和支付系统，支持多种支付方式、优惠券、自动续费、发票管理等功能。

## 🏗️ 架构组成

### 后端 (FastAPI)
- **6个数据表**: subscription_plans, user_subscriptions, payments, payment_methods, coupons, invoices
- **4个核心服务**: SubscriptionService, PaymentService, InvoiceService, CouponService
- **66个API端点**: 31个用户端 + 35个管理端
- **3个支付网关**: Stripe, PayPal, Alipay

### 前端 (React + TypeScript)
- **4个API服务模块**: subscription.ts, payment.ts, coupon.ts, invoice.ts
- **3个用户页面**: Subscription, Checkout, AccountSubscription
- **完整国际化**: 英文 + 中文翻译

## 🚀 快速开始

### 1. 数据库初始化

```bash
cd backend
source venv/bin/activate

# 应用数据库迁移
alembic upgrade head

# 创建初始数据
python scripts/seed_payment_data.py
```

这将创建:
- 7个订阅套餐 (月度/季度/年度/终身)
- 5个测试优惠券
- 管理员账户 (admin@videosite.com / admin123)

### 2. 配置支付网关

在 `backend/.env` 文件中添加:

```bash
# Stripe配置
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# PayPal配置
PAYPAL_CLIENT_ID=xxxxx
PAYPAL_CLIENT_SECRET=xxxxx
PAYPAL_ENVIRONMENT=sandbox  # 或 live

# Alipay配置
ALIPAY_APP_ID=xxxxx
ALIPAY_PRIVATE_KEY=xxxxx
ALIPAY_PUBLIC_KEY=xxxxx
ALIPAY_GATEWAY_URL=https://openapi.alipaydev.com/gateway.do
```

### 3. 启动服务

```bash
# 后端 (端口 8000)
cd backend
uvicorn app.main:app --reload

# 前端 (端口 5173)
cd frontend
pnpm run dev
```

## 📍 访问路径

### 用户端
- 订阅套餐: http://localhost:5173/subscription
- 支付结账: http://localhost:5173/checkout
- 订阅管理: http://localhost:5173/account/subscription

### API文档
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 💳 初始数据

### 订阅套餐

| 套餐名称 | 计费周期 | 价格 (USD) | 画质 | 并发流 | 下载 |
|---------|---------|-----------|------|--------|------|
| Basic Monthly | 月度 | $9.99 | 720p | 1 | ❌ |
| Premium Monthly | 月度 | $19.99 | 1080p | 2 | ✅ |
| Ultimate Monthly | 月度 | $29.99 | 4K | 4 | ✅ |
| Premium Quarterly | 季度 | $53.97 | 1080p | 2 | ✅ |
| Premium Yearly | 年度 | $191.90 | 1080p | 2 | ✅ |
| Ultimate Yearly | 年度 | $287.90 | 4K | 4 | ✅ |
| Lifetime Premium | 终身 | $499.99 | 1080p | 2 | ✅ |

### 测试优惠券

| 代码 | 类型 | 折扣 | 最大使用次数 | 有效期 |
|------|------|------|------------|--------|
| WELCOME20 | 百分比 | 20% | 1000 | 90天 |
| SPRING10 | 固定金额 | $10 | 500 | 30天 |
| VIP30 | 百分比 | 30% | 100 | 180天 |
| TEST99 | 百分比 | 99% | 10 | 365天 |

## 🔧 配置Webhook

### Stripe Webhook
1. 登录 Stripe Dashboard
2. 进入 Developers > Webhooks
3. 添加端点: `https://your-domain.com/api/v1/webhooks/stripe`
4. 选择事件:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. 复制 Webhook 签名密钥到 `.env`

### PayPal Webhook
1. 登录 PayPal Developer Dashboard
2. 选择应用 > Webhooks
3. 添加 Webhook: `https://your-domain.com/api/v1/webhooks/paypal`
4. 选择事件:
   - `PAYMENT.CAPTURE.COMPLETED`
   - `PAYMENT.CAPTURE.DENIED`
   - `BILLING.SUBSCRIPTION.ACTIVATED`
   - `BILLING.SUBSCRIPTION.CANCELLED`

### Alipay Webhook
- 在支付宝商户平台配置异步通知地址
- URL: `https://your-domain.com/api/v1/webhooks/alipay`

## 📊 管理功能

### 管理员登录
- 邮箱: admin@videosite.com
- 密码: admin123

### 管理端API端点

**订阅套餐管理** (`/api/v1/admin/subscription-plans`)
- GET / - 列出所有套餐
- POST / - 创建新套餐
- PATCH /{id} - 更新套餐
- DELETE /{id} - 删除套餐
- POST /{id}/activate - 激活套餐
- POST /{id}/deactivate - 停用套餐

**用户订阅管理** (`/api/v1/admin/subscriptions`)
- GET / - 列出所有订阅
- GET /stats/overview - 获取统计(MRR, 流失率)
- POST /{id}/cancel - 取消订阅
- POST /{id}/renew - 手动续费

**支付管理** (`/api/v1/admin/payments`)
- GET / - 列出所有支付
- GET /stats/overview - 支付统计
- POST /{id}/refund - 退款处理

**优惠券管理** (`/api/v1/admin/coupons`)
- GET / - 列出所有优惠券
- POST / - 创建优惠券
- PATCH /{id} - 更新优惠券
- GET /{id}/statistics - 使用统计

**发票管理** (`/api/v1/admin/invoices`)
- GET / - 列出所有发票
- GET /stats/financial - 财务统计
- POST /{id}/mark-paid - 标记已支付

## 🎨 前端集成

### 页面组件

1. **订阅页面** (`/src/pages/Subscription.tsx`)
   - 展示所有可用套餐
   - 计费周期切换
   - 节省百分比计算
   - 响应式设计

2. **结账页面** (`/src/pages/Checkout.tsx`)
   - 套餐详情确认
   - 优惠券验证
   - 支付方式选择
   - 自动续费选项

3. **订阅管理** (`/src/pages/AccountSubscription.tsx`)
   - 当前订阅状态
   - 自动续费开关
   - 取消订阅
   - 支付历史和发票

### API服务

所有前端API调用已封装在 `/src/services/` 中:
- `subscription.ts` - 订阅相关
- `payment.ts` - 支付相关
- `coupon.ts` - 优惠券相关
- `invoice.ts` - 发票相关

## 🔐 安全考虑

1. **支付信息安全**
   - 不存储完整信用卡号
   - 使用 Stripe.js/PayPal SDK 处理敏感数据
   - 所有通信使用 HTTPS

2. **Webhook验证**
   - Stripe: 验证签名头
   - PayPal: 验证 webhook ID
   - Alipay: 验证签名

3. **权限控制**
   - 用户只能访问自己的订阅和支付
   - 管理端需要 admin 权限
   - Superadmin 有额外权限

## 📈 业务指标

系统自动计算以下指标:

- **MRR** (Monthly Recurring Revenue): 月度经常性收入
- **Churn Rate**: 流失率
- **Conversion Rate**: 转化率
- **ARPU** (Average Revenue Per User): 平均用户收入
- **LTV** (Lifetime Value): 用户生命周期价值

可在管理端查看: GET `/api/v1/admin/subscriptions/stats/overview`

## 🧪 测试

### 测试支付

使用 Stripe 测试卡号:
- 成功: `4242 4242 4242 4242`
- 失败: `4000 0000 0000 0002`
- 3D Secure: `4000 0027 6000 3184`

任意有效的未来日期和 CVC 即可。

### 测试优惠券

使用种子数据中的优惠券代码:
- `TEST99` - 99% 折扣
- `WELCOME20` - 20% 折扣
- `SPRING10` - $10 折扣

## 🚨 故障排查

### 支付失败
1. 检查支付网关配置
2. 查看 webhook 日志
3. 确认 API 密钥有效
4. 检查网络连接

### 订阅未激活
1. 确认支付成功
2. 检查 webhook 是否触发
3. 查看数据库订阅状态
4. 检查服务器日志

### 优惠券无效
1. 确认优惠券代码正确
2. 检查有效期
3. 验证使用次数限制
4. 确认适用套餐

## 📝 待办事项

- [ ] 集成 Stripe Elements (信用卡表单)
- [ ] 添加更多支付提供商 (微信支付、Apple Pay)
- [ ] 实现订阅升级/降级逻辑
- [ ] 添加退款自动化处理
- [ ] 实现发票PDF生成
- [ ] 添加电子邮件通知
- [ ] 实现计费警告系统
- [ ] 添加税收计算

## 📞 支持

如有问题,请查看:
- API文档: http://localhost:8000/api/docs
- 日志文件: `backend/logs/`
- 数据库状态: `backend/alembic/versions/`

---

**版本**: 1.0.0
**更新日期**: 2025-10-19
**作者**: Claude Code (Anthropic)
