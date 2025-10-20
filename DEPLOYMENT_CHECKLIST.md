# 🚀 VideoSite 生产部署检查清单

本文档提供生产环境部署的完整检查清单，包含新增的支付订阅系统和季度管理功能。

---

## 📋 部署前准备

### 1. 环境变量配置

#### 后端 `.env.production`

```bash
# 复制模板
cp backend/.env.production.template backend/.env.production

# 必需配置项
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/videosite
DATABASE_URL_SYNC=postgresql://user:password@host:5432/videosite
SECRET_KEY=[生成32字符随机字符串]
JWT_SECRET_KEY=[生成32字符随机字符串]
REDIS_URL=redis://redis:6379/0

# MinIO 对象存储
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=[生产访问密钥]
MINIO_SECRET_KEY=[生产密钥]
MINIO_PUBLIC_URL=https://cdn.yourdomain.com

# SMTP 邮件服务
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@yourdomain.com
SMTP_PASSWORD=[应用专用密码]
SMTP_FROM=noreply@yourdomain.com

# CORS 配置
CORS_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com

# Sentry 错误追踪
SENTRY_DSN=[Sentry项目DSN]
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1

# 支付网关配置（关键！）
STRIPE_SECRET_KEY=sk_live_[生产密钥]
STRIPE_PUBLISHABLE_KEY=pk_live_[生产密钥]
STRIPE_WEBHOOK_SECRET=whsec_[Webhook签名密钥]

PAYPAL_CLIENT_ID=[生产Client ID]
PAYPAL_CLIENT_SECRET=[生产Secret]
PAYPAL_ENVIRONMENT=live

ALIPAY_APP_ID=[支付宝应用ID]
ALIPAY_PRIVATE_KEY=[RSA私钥]
ALIPAY_PUBLIC_KEY=[支付宝公钥]
ALIPAY_GATEWAY_URL=https://openapi.alipay.com/gateway.do
```

#### 前端环境变量

**Admin Frontend `.env.production`:**
```bash
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_WS_URL=wss://api.yourdomain.com
```

**User Frontend `.env.production`:**
```bash
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_[生产密钥]
```

---

### 2. 支付网关配置

#### Stripe 配置步骤

1. **创建生产环境产品**
   - 登录 [Stripe Dashboard](https://dashboard.stripe.com/)
   - Products → Create Product
   - 为每个订阅计划创建对应的 Price

2. **配置 Webhook**
   - Developers → Webhooks → Add Endpoint
   - Endpoint URL: `https://api.yourdomain.com/api/v1/webhooks/stripe`
   - 选择事件：
     - `payment_intent.succeeded`
     - `payment_intent.payment_failed`
     - `customer.subscription.created`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
   - 复制 Webhook 签名密钥到 `.env.production`

3. **测试 Webhook**
   ```bash
   stripe listen --forward-to https://api.yourdomain.com/api/v1/webhooks/stripe
   stripe trigger payment_intent.succeeded
   ```

#### PayPal 配置步骤

1. 切换到生产模式
2. 配置 Webhook URL: `https://api.yourdomain.com/api/v1/webhooks/paypal`
3. 验证 Webhook 事件接收

#### Alipay 配置步骤

1. 上传应用公钥到支付宝开放平台
2. 下载支付宝公钥
3. 配置异步通知URL: `https://api.yourdomain.com/api/v1/webhooks/alipay`

---

### 3. 数据库迁移

```bash
# 1. 备份生产数据库（重要！）
pg_dump -h localhost -U videosite -d videosite > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. 运行迁移
cd backend
source venv/bin/activate
alembic upgrade head

# 3. 验证迁移
python -c "
from app.database import AsyncSessionLocal
from app.models import *
import asyncio

async def check():
    async with AsyncSessionLocal() as db:
        # 检查支付表
        from sqlalchemy import select
        result = await db.execute(select(SubscriptionPlan).limit(1))
        print('✅ SubscriptionPlan table exists')

        result = await db.execute(select(Season).limit(1))
        print('✅ Season table exists')

asyncio.run(check())
"
```

---

### 4. 初始化生产数据

```bash
cd backend
source venv/bin/activate

# 1. 创建超级管理员
python << EOF
from app.database import SessionLocal
from app.models.user import AdminUser
from app.utils.security import get_password_hash
import asyncio

async def create_admin():
    async with SessionLocal() as db:
        admin = AdminUser(
            email='admin@yourdomain.com',
            username='admin',
            hashed_password=get_password_hash('[安全密码]'),
            full_name='Super Admin',
            is_active=True,
            is_superadmin=True
        )
        db.add(admin)
        await db.commit()
        print('✅ Admin user created')

asyncio.run(create_admin())
EOF

# 2. 导入订阅计划
python scripts/seed_payment_data.py --production

# 3. 配置系统设置
# 通过 Admin Panel 手动配置
```

---

## 🔐 安全检查清单

### 应用安全

- [ ] 所有密钥使用强随机生成（32+字符）
- [ ] `.env` 文件不被git追踪
- [ ] CORS 配置仅允许生产域名
- [ ] Rate Limiting 已启用
- [ ] SQL 注入防护已测试
- [ ] XSS 防护已启用（CSP Headers）
- [ ] CSRF 保护已配置
- [ ] 密码哈希使用 bcrypt
- [ ] JWT Token 过期时间合理（15分钟）
- [ ] Refresh Token 安全存储

### 支付安全

- [ ] 使用 HTTPS（TLS 1.2+）
- [ ] Stripe/PayPal 使用生产密钥
- [ ] Webhook 签名验证已实现
- [ ] 支付金额验证在后端
- [ ] 敏感信息不记录到日志
- [ ] PCI DSS合规（如适用）
- [ ] 支付失败重试机制
- [ ] 退款流程已测试

### 数据安全

- [ ] 数据库加密传输
- [ ] 定期备份策略（每日）
- [ ] 备份加密存储
- [ ] 用户数据脱敏（日志/Sentry）
- [ ] GDPR 合规检查

### 基础设施安全

- [ ] SSH密钥登录，禁用密码
- [ ] 防火墙仅开放必要端口
- [ ] 系统自动安全更新
- [ ] Docker镜像定期扫描
- [ ] MinIO访问策略最小权限

---

## 📦 Docker 部署

### 1. 构建镜像

```bash
# Backend
cd backend
docker build -t videosite-backend:latest .

# Admin Frontend
cd admin-frontend
docker build -t videosite-admin:latest .

# User Frontend
cd frontend
docker build -t videosite-frontend:latest .
```

### 2. 推送到镜像仓库

```bash
docker tag videosite-backend:latest registry.yourdomain.com/videosite-backend:v1.0.0
docker push registry.yourdomain.com/videosite-backend:v1.0.0

# 同样推送其他镜像
```

### 3. 使用 docker-compose 部署

```bash
# 使用生产配置
docker-compose -f docker-compose.yml up -d

# 检查服务状态
docker-compose ps
docker-compose logs -f backend
```

---

## 🌐 Nginx 配置

```nginx
# /etc/nginx/sites-available/videosite

# Admin Panel
server {
    listen 443 ssl http2;
    server_name admin.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/admin.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/admin.yourdomain.com/privkey.pem;

    location / {
        root /var/www/admin-frontend/dist;
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache";
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# User Frontend
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        root /var/www/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}

# API Server
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    # 增加超时时间（文件上传）
    client_max_body_size 1000M;
    proxy_connect_timeout 600s;
    proxy_send_timeout 600s;
    proxy_read_timeout 600s;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 📊 监控配置

### 1. Sentry 错误追踪

```python
# backend/app/main.py
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.SENTRY_ENVIRONMENT,
    traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
    profiles_sample_rate=0.1,
)

app = SentryAsgiMiddleware(app)
```

### 2. 日志配置

```python
# 配置日志轮转
LOGGING_CONFIG = {
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10,
        }
    }
}
```

### 3. 性能监控

- [ ] 设置 APM（如 New Relic, Datadog）
- [ ] 配置数据库慢查询日志
- [ ] 设置 Redis 性能监控
- [ ] 配置资源使用告警

---

## 🧪 生产测试清单

### 冒烟测试（部署后立即执行）

- [ ] 主页可访问
- [ ] 管理后台可登录
- [ ] API 健康检查通过 `/api/health`
- [ ] 数据库连接正常
- [ ] Redis 连接正常
- [ ] MinIO 连接正常

### 支付系统测试

- [ ] 订阅计划列表加载
- [ ] 测试支付流程（小额测试）
- [ ] Webhook 接收正常
- [ ] 订阅激活成功
- [ ] 发票生成正确
- [ ] 优惠券可用

### 关键功能测试

- [ ] 用户注册/登录
- [ ] 视频上传/播放
- [ ] 评论功能
- [ ] 搜索功能
- [ ] 季度/剧集管理
- [ ] 多语言切换

---

## 🔄 备份与恢复

### 自动备份脚本

```bash
#!/bin/bash
# /opt/videosite/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backups/videosite

# 1. 数据库备份
pg_dump -h localhost -U videosite -d videosite | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# 2. MinIO 数据备份
mc mirror minio/videos $BACKUP_DIR/minio_$DATE/

# 3. 上传到云存储（如 S3）
aws s3 sync $BACKUP_DIR s3://videosite-backups/

# 4. 清理30天前的备份
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

### 设置 Cron 任务

```bash
# 每天凌晨2点执行备份
0 2 * * * /opt/videosite/backup.sh >> /var/log/videosite-backup.log 2>&1
```

---

## 🚨 故障恢复计划

### 数据库恢复

```bash
# 从备份恢复
gunzip < backup_20250119_020000.sql.gz | psql -h localhost -U videosite -d videosite
```

### 回滚部署

```bash
# 回滚到上一个版本
docker-compose down
docker-compose up -d registry.yourdomain.com/videosite-backend:v0.9.9
```

---

## ✅ 最终部署检查清单

### 部署前

- [ ] 代码已合并到 main 分支
- [ ] 所有测试通过
- [ ] 数据库备份已完成
- [ ] 环境变量已配置
- [ ] SSL 证书有效
- [ ] DNS 记录正确

### 部署中

- [ ] 数据库迁移成功
- [ ] Docker 容器启动正常
- [ ] Nginx 配置已重载
- [ ] 冒烟测试通过

### 部署后

- [ ] 监控系统正常
- [ ] 错误率在正常范围
- [ ] 性能指标正常
- [ ] 支付功能正常
- [ ] 用户反馈收集

---

## 📞 紧急联系

- **技术负责人:** [姓名] - [电话]
- **数据库管理员:** [姓名] - [电话]
- **支付平台支持:**
  - Stripe: https://support.stripe.com
  - PayPal: https://www.paypal.com/support
  - Alipay: https://open.alipay.com

---

**部署成功！** 🎉

记得监控系统运行状况，收集用户反馈并持续改进！
