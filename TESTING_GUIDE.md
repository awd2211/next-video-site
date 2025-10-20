# 🧪 VideoSite 功能测试指南

本指南帮助您在开发环境中测试新增的支付订阅系统和季度管理功能。

## 📋 测试前准备

### 1. 启动基础设施
```bash
# 确认 PostgreSQL, Redis, MinIO 正在运行
docker ps | grep -E "postgres|redis|minio"

# 如果未运行，启动它们
cd /home/eric/video
docker-compose -f docker-compose.dev.yml up -d
```

### 2. 运行数据库迁移
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

### 3. 初始化测试数据
```bash
# 创建管理员账户（如果还没有）
python scripts/init_data.py

# 可选：导入支付系统测试数据
python scripts/seed_payment_data.py
```

### 4. 启动后端服务
```bash
# Terminal 1
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 启动前端服务
```bash
# Terminal 2 - Admin Frontend
cd admin-frontend
pnpm run dev  # 运行在 http://localhost:5173 (proxies to :3001)

# Terminal 3 - User Frontend
cd frontend
pnpm run dev  # 运行在 http://localhost:5173 (proxies to :3000)
```

---

## 🧪 功能测试清单

### A. 支付订阅系统测试

#### A1. 订阅计划管理（Admin）

**前置条件：**
- 管理员账号登录 admin-frontend

**测试步骤：**
1. 导航到 「💳 Payment」→「Subscription Plans」
2. 验证页面显示订阅计划列表
3. 点击「创建订阅计划」按钮
4. 填写表单：
   - Name (EN): Premium Monthly
   - Name (ZH): 高级月度套餐
   - Billing Period: Monthly
   - Price (USD): 9.99
   - Max Video Quality: 1080p
   - Max Concurrent Streams: 2
   - Features: [勾选] Allow Downloads, Ads Free
5. 提交表单
6. 验证新计划出现在列表中

**TODO(human): 在此实现订阅计划删除测试**
```
步骤：
1. 选择刚创建的测试计划
2. 点击删除按钮
3. 确认删除
4. 验证计划已从列表中移除

预期结果：
- [ ] 删除成功
- [ ] 列表已更新
- [ ] 显示成功提示
```

#### A2. 优惠券管理（Admin）

**测试步骤：**
1. 导航到 「💳 Payment」→「Coupons」
2. 点击「创建优惠券」
3. 填写：
   - Code: TEST20
   - Description: 测试优惠券
   - Discount Type: Percentage
   - Discount Value: 20
   - Valid From: 2025-01-01
   - Status: Active
4. 提交并验证创建成功

**TODO(human): 实现优惠券验证测试**
```
测试优惠券验证逻辑：
1. 创建一个有最低消费要求的优惠券（Min Purchase: $50）
2. 尝试在订阅 $9.99 套餐时使用
3. 应该显示错误：「不符合最低消费要求」

预期结果：
- [ ] 验证逻辑正确
- [ ] 错误信息清晰
- [ ] UI 反馈友好
```

#### A3. 支付记录查看（Admin）

**测试步骤：**
1. 导航到 「💳 Payment」→「Payments」
2. 查看支付记录列表
3. 使用筛选器（按状态、日期）
4. 验证排序功能
5. 导出 CSV（如果已实现）

---

### B. 季度/剧集管理测试

#### B1. 创建电视剧季度（Admin）

**前置条件：**
- 已有一个电视剧类型的 Series

**测试步骤：**
1. 导航到「Series」→ 选择一个电视剧
2. 点击「Seasons」标签
3. 点击「创建季度」
4. 填写：
   - Season Number: 1
   - Title: 第一季：凛冬将至
   - Status: Draft
   - VIP Required: 否
5. 提交并验证

**TODO(human): 实现剧集添加测试**
```
在刚创建的季度下添加剧集：
1. 进入 Season 详情页
2. 点击「添加剧集」
3. 填写剧集信息：
   - Episode Number: 1
   - Title: 第一集
   - Video ID: [选择一个视频]
   - Is Free: 是
4. 提交

预期结果：
- [ ] 剧集创建成功
- [ ] 显示在季度剧集列表中
- [ ] 季度的 total_episodes 数量更新
```

#### B2. 批量发布季度（Admin）

**测试步骤：**
1. 在 Seasons 列表中选择多个草稿状态的季度
2. 点击「批量发布」按钮
3. 确认操作
4. 验证所有选中季度状态变为「已发布」

---

### C. 多语言支持测试

#### C1. 语言切换测试

**测试步骤：**
1. 在 Admin Frontend 右上角点击语言切换器
2. 依次切换到各种语言：
   - 英文 (en-US)
   - 简体中文 (zh-CN)
   - 德语 (de-DE)
   - 法语 (fr-FR)
   - 日语 (ja-JP)
   - 繁体中文 (zh-TW)
3. 验证每种语言下：
   - 菜单翻译正确
   - 页面内容翻译完整
   - 支付模块术语准确

**预期结果：**
- [ ] 所有语言切换流畅
- [ ] 无缺失翻译
- [ ] 格式显示正常

---

## 🔍 API 端点测试

### 使用 Swagger UI 测试

访问：http://localhost:8000/api/docs

#### 支付系统 API

**Admin - Subscription Plans:**
- GET `/api/v1/admin/subscription-plans` - 获取计划列表
- POST `/api/v1/admin/subscription-plans` - 创建计划
- PUT `/api/v1/admin/subscription-plans/{id}` - 更新计划
- DELETE `/api/v1/admin/subscription-plans/{id}` - 删除计划

**Admin - Payments:**
- GET `/api/v1/admin/payments` - 获取支付记录
- GET `/api/v1/admin/payments/statistics` - 支付统计

**Admin - Coupons:**
- GET `/api/v1/admin/coupons` - 优惠券列表
- POST `/api/v1/admin/coupons` - 创建优惠券
- POST `/api/v1/admin/coupons/validate` - 验证优惠券

**TODO(human): 测试以下 API 并记录结果**
```
测试 Subscription Statistics API:
GET /api/v1/admin/subscriptions/statistics

预期响应应包含：
- active_subscriptions: 数量
- monthly_recurring_revenue: MRR 金额
- churn_rate: 流失率
- average_revenue_per_user: ARPU

在下方记录实际响应：
[在此粘贴 JSON 响应]

验证项：
- [ ] 所有字段都存在
- [ ] 数值类型正确
- [ ] 计算逻辑准确
```

#### 季度/剧集 API

**Admin - Seasons:**
- GET `/api/v1/admin/series/{series_id}/seasons` - 获取季度列表
- POST `/api/v1/admin/series/{series_id}/seasons` - 创建季度
- PUT `/api/v1/admin/seasons/{id}` - 更新季度
- DELETE `/api/v1/admin/seasons/{id}` - 删除季度
- POST `/api/v1/admin/seasons/batch-publish` - 批量发布

**Admin - Episodes:**
- GET `/api/v1/admin/seasons/{season_id}/episodes` - 获取剧集列表
- POST `/api/v1/admin/seasons/{season_id}/episodes` - 创建剧集
- PUT `/api/v1/admin/episodes/{id}/markers` - 设置片头片尾标记

---

## 🐛 常见问题排查

### 后端启动失败
```bash
# 检查数据库连接
psql -h localhost -p 5434 -U videosite -d videosite -c "SELECT 1;"

# 检查 Redis 连接
redis-cli -h localhost -p 6381 ping

# 查看后端日志
tail -f backend/logs/app.log
```

### 前端构建错误
```bash
# 清理并重新安装
cd admin-frontend
rm -rf node_modules pnpm-lock.yaml
pnpm install

# 类型检查
pnpm run type-check
```

### 数据库迁移问题
```bash
# 查看迁移历史
cd backend
alembic history

# 回滚一个迁移
alembic downgrade -1

# 强制升级到最新
alembic upgrade head
```

---

## ✅ 测试完成检查清单

- [ ] 所有基础设施服务正常运行
- [ ] 数据库迁移成功
- [ ] 后端服务启动无错误
- [ ] 前端服务启动无错误
- [ ] 管理员可以登录
- [ ] 支付计划 CRUD 功能正常
- [ ] 优惠券管理功能正常
- [ ] 季度管理功能正常
- [ ] 剧集管理功能正常
- [ ] 多语言切换正常
- [ ] API 端点响应正确
- [ ] 无控制台错误
- [ ] 用户体验流畅

---

## 📝 测试报告模板

完成测试后，请填写此模板：

```markdown
# 测试报告

**测试日期:** [日期]
**测试人员:** [姓名]
**测试环境:** 开发环境

## 功能测试结果

### 支付订阅系统
- 订阅计划管理: ✅ / ❌
- 优惠券管理: ✅ / ❌
- 支付记录: ✅ / ❌
- 发现的问题: [列出问题]

### 季度/剧集管理
- 季度 CRUD: ✅ / ❌
- 剧集 CRUD: ✅ / ❌
- 批量操作: ✅ / ❌
- 发现的问题: [列出问题]

### 多语言支持
- 语言切换: ✅ / ❌
- 翻译完整性: ✅ / ❌
- 发现的问题: [列出问题]

## 性能观察
- 页面加载时间: [记录]
- API 响应时间: [记录]
- 内存使用: [记录]

## 建议改进
1. [改进建议 1]
2. [改进建议 2]
3. [改进建议 3]
```

---

**祝测试顺利！** 🎉

如有问题，请参考 `/home/eric/video/PAYMENT_SYSTEM_GUIDE.md` 获取详细的系统架构说明。
