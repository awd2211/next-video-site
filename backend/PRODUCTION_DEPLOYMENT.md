# Production Deployment Guide

This guide covers deploying the VideoSite payment and subscription system to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Payment Gateway Configuration](#payment-gateway-configuration)
4. [Database Setup](#database-setup)
5. [Security Checklist](#security-checklist)
6. [SSL/HTTPS Configuration](#ssl-https-configuration)
7. [Email Configuration](#email-configuration)
8. [Monitoring and Logging](#monitoring-and-logging)
9. [Backup and Recovery](#backup-and-recovery)
10. [Deployment Procedures](#deployment-procedures)
11. [Post-Deployment Testing](#post-deployment-testing)

---

## Prerequisites

Before deploying to production, ensure you have:

- [ ] Domain name with DNS configured
- [ ] SSL certificate (Let's Encrypt, DigiCert, etc.)
- [ ] Production database server (PostgreSQL 14+)
- [ ] Redis server for caching
- [ ] MinIO or S3 for object storage
- [ ] SMTP server for email notifications
- [ ] Production accounts for payment gateways (Stripe, PayPal, Alipay)
- [ ] Server with adequate resources (4+ CPU cores, 8GB+ RAM recommended)

---

## Environment Configuration

### 1. Create Production `.env` File

**Location:** `/home/eric/video/backend/.env.production`

```bash
# Application Settings
DEBUG=False
ENVIRONMENT=production
SECRET_KEY=<GENERATE_STRONG_RANDOM_KEY_64_CHARS>
JWT_SECRET_KEY=<GENERATE_STRONG_RANDOM_KEY_64_CHARS>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# CORS - Your frontend domains
CORS_ORIGINS=["https://videosite.com","https://www.videosite.com","https://admin.videosite.com"]

# Database - Use SSL connection
DATABASE_URL=postgresql+asyncpg://username:password@db-host:5432/videosite?ssl=require
DATABASE_URL_SYNC=postgresql://username:password@db-host:5432/videosite?sslmode=require

# Database Pool Settings (for production load)
DB_POOL_SIZE=30
DB_MAX_OVERFLOW=60
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# Redis - Use password and SSL if available
REDIS_URL=rediss://username:password@redis-host:6379/0

# MinIO / S3
MINIO_ENDPOINT=s3.amazonaws.com  # Or your MinIO endpoint
MINIO_ACCESS_KEY=<YOUR_ACCESS_KEY>
MINIO_SECRET_KEY=<YOUR_SECRET_KEY>
MINIO_BUCKET=videosite-videos-prod
MINIO_SECURE=True
MINIO_PUBLIC_URL=https://cdn.videosite.com  # Use CDN for better performance

# === PAYMENT GATEWAYS (PRODUCTION) ===

# Stripe - LIVE MODE
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxxxxxxxxxxx  # NOT sk_test_
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxxxxxxxxxxxxxxxxxx  # NOT pk_test_
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxx

# PayPal - LIVE MODE
PAYPAL_CLIENT_ID=<YOUR_LIVE_CLIENT_ID>
PAYPAL_CLIENT_SECRET=<YOUR_LIVE_CLIENT_SECRET>
PAYPAL_ENVIRONMENT=live  # NOT sandbox

# Alipay - PRODUCTION
ALIPAY_APP_ID=<YOUR_APP_ID>
ALIPAY_PRIVATE_KEY=<YOUR_PRIVATE_KEY>
ALIPAY_PUBLIC_KEY=<ALIPAY_PUBLIC_KEY>
ALIPAY_GATEWAY_URL=https://openapi.alipay.com/gateway.do  # NOT alipaydev.com

# Email Settings - Production SMTP
SMTP_HOST=smtp.sendgrid.net  # Or your SMTP provider
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<YOUR_SMTP_PASSWORD>
SMTP_FROM_EMAIL=noreply@videosite.com
SMTP_FROM_NAME=VideoSite
SMTP_USE_TLS=True

# Admin Notifications
ADMIN_NOTIFICATION_EMAIL=admin@videosite.com
ADMIN_NOTIFICATION_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL  # Optional

# Security Headers
ENABLE_SECURITY_HEADERS=True
HSTS_MAX_AGE=31536000
CSP_POLICY=default-src 'self'; script-src 'self' https://js.stripe.com; frame-src https://js.stripe.com;

# Rate Limiting (adjust based on your needs)
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/videosite/app.log
ENABLE_SQL_LOGGING=False  # Only enable for debugging production issues

# Performance Monitoring
SLOW_API_THRESHOLD_MS=1000
SLOW_QUERY_THRESHOLD_MS=500
ENABLE_PERFORMANCE_MONITORING=True
```

### 2. Generate Secure Keys

```bash
# Generate SECRET_KEY and JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(64))"
# Run twice for two different keys
```

### 3. Environment-Specific Settings

Create a settings loader that switches based on environment:

```python
# app/config.py - Add environment detection
import os

class Settings(BaseSettings):
    ENVIRONMENT: str = Field(default="development")

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    class Config:
        env_file = f".env.{os.getenv('ENVIRONMENT', 'development')}"
        env_file_encoding = 'utf-8'
```

---

## Payment Gateway Configuration

### Stripe Production Setup

1. **Switch to Live Mode** in Stripe Dashboard
   - Go to https://dashboard.stripe.com
   - Toggle from "Test mode" to "Live mode" (top right)

2. **Get Live API Keys**
   - Navigate to Developers → API keys
   - Copy "Publishable key" (starts with `pk_live_`)
   - Reveal and copy "Secret key" (starts with `sk_live_`)
   - Add to `.env.production`

3. **Configure Webhooks**
   - Go to Developers → Webhooks
   - Click "Add endpoint"
   - Endpoint URL: `https://api.videosite.com/api/v1/webhooks/stripe`
   - Select events:
     - `payment_intent.succeeded`
     - `payment_intent.payment_failed`
     - `charge.refunded`
     - `customer.subscription.created`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
   - Copy webhook signing secret (starts with `whsec_`)
   - Add to `.env.production` as `STRIPE_WEBHOOK_SECRET`

4. **Test Webhook Delivery**
   ```bash
   # Use Stripe CLI to test
   stripe listen --forward-to https://api.videosite.com/api/v1/webhooks/stripe
   stripe trigger payment_intent.succeeded
   ```

5. **Enable Required Payment Methods**
   - Go to Settings → Payment methods
   - Enable: Credit cards, Apple Pay, Google Pay
   - Configure 3D Secure for fraud prevention

### PayPal Production Setup

1. **Switch to Live Credentials**
   - Go to https://developer.paypal.com
   - Navigate to "My Apps & Credentials"
   - Switch to "Live" tab
   - Create new app or use existing

2. **Get Live Credentials**
   - Copy "Client ID"
   - Copy "Secret"
   - Add to `.env.production`
   - Set `PAYPAL_ENVIRONMENT=live`

3. **Configure Webhooks**
   - In your PayPal app settings, go to "Webhooks"
   - Add webhook: `https://api.videosite.com/api/v1/webhooks/paypal`
   - Subscribe to events:
     - `PAYMENT.CAPTURE.COMPLETED`
     - `PAYMENT.CAPTURE.DENIED`
     - `PAYMENT.CAPTURE.REFUNDED`

4. **Production Testing**
   - Use PayPal's live sandbox first
   - Test with small real transactions ($0.01)
   - Verify webhook delivery

### Alipay Production Setup

1. **Complete Business Verification**
   - Alipay requires business verification for live access
   - Submit business documents at https://open.alipay.com

2. **Get Production Keys**
   - Download Alipay's official key generation tool
   - Generate RSA2048 key pair
   - Upload public key to Alipay dashboard
   - Save private key securely

3. **Configure Application**
   - Set gateway URL to: `https://openapi.alipay.com/gateway.do`
   - NOT `alipaydev.com` (that's sandbox)
   - Add to `.env.production`

4. **Set up Return URLs**
   - Return URL: `https://videosite.com/payment/return`
   - Notify URL: `https://api.videosite.com/api/v1/webhooks/alipay`

---

## Database Setup

### 1. Production Database Server

```bash
# Install PostgreSQL 14+ on production server
sudo apt update
sudo apt install postgresql-14 postgresql-contrib-14

# Configure PostgreSQL for production
sudo nano /etc/postgresql/14/main/postgresql.conf
```

**Recommended Settings:**
```conf
# Connections
max_connections = 200
shared_buffers = 2GB        # 25% of RAM
effective_cache_size = 6GB  # 75% of RAM
work_mem = 16MB
maintenance_work_mem = 512MB

# WAL
wal_buffers = 16MB
checkpoint_completion_target = 0.9
checkpoint_timeout = 10min

# Performance
random_page_cost = 1.1  # For SSD
effective_io_concurrency = 200

# Logging
log_destination = 'stderr'
logging_collector = on
log_directory = '/var/log/postgresql'
log_filename = 'postgresql-%Y-%m-%d.log'
log_rotation_age = 1d
log_min_duration_statement = 1000  # Log slow queries > 1s
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

### 2. Create Production Database

```bash
# Create database user
sudo -u postgres createuser -P videosite_prod
# Enter strong password

# Create database
sudo -u postgres createdb -O videosite_prod videosite_prod

# Enable required extensions
sudo -u postgres psql videosite_prod << EOF
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  # For text search
EOF
```

### 3. Run Migrations

```bash
cd /home/eric/video/backend

# Activate virtual environment
source venv/bin/activate

# Set environment
export ENVIRONMENT=production

# Run migrations
alembic upgrade head

# Verify tables created
alembic current
```

### 4. Create Initial Data

```bash
# Run seed script
python scripts/seed_payment_data.py

# Create admin user
python scripts/create_admin_user.py
```

### 5. Database Backups

Set up automated backups:

```bash
# Create backup script
sudo nano /usr/local/bin/backup_videosite_db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/postgresql/videosite"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="videosite_prod"

mkdir -p $BACKUP_DIR

# Backup with compression
pg_dump -U videosite_prod -Fc $DB_NAME > $BACKUP_DIR/videosite_$DATE.dump

# Keep only last 30 days
find $BACKUP_DIR -name "videosite_*.dump" -mtime +30 -delete

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/videosite_$DATE.dump s3://videosite-backups/database/
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup_videosite_db.sh

# Add to crontab (daily at 2 AM)
echo "0 2 * * * /usr/local/bin/backup_videosite_db.sh" | sudo crontab -
```

---

## Security Checklist

### Application Security

- [ ] **Secrets Management**
  - Never commit `.env` files to git
  - Use environment variables or secret managers (AWS Secrets Manager, HashiCorp Vault)
  - Rotate keys regularly (every 90 days)

- [ ] **Database Security**
  - Use strong passwords (20+ characters)
  - Enable SSL/TLS for database connections
  - Restrict database access by IP whitelist
  - Disable remote root login
  - Regular security updates

- [ ] **API Security**
  - Enable CORS only for trusted domains
  - Implement rate limiting (already configured)
  - Use HTTPS only (redirect HTTP → HTTPS)
  - Enable security headers (CSP, HSTS, X-Frame-Options)
  - Validate all inputs (Pydantic handles this)

- [ ] **Authentication**
  - Use strong JWT secrets (64+ characters)
  - Short access token expiry (15-60 minutes)
  - Implement token refresh rotation
  - Enable 2FA for admin accounts
  - Monitor failed login attempts

- [ ] **Payment Security**
  - Never store credit card details (use Stripe)
  - PCI DSS compliance via payment providers
  - Validate webhook signatures
  - Use HTTPS for all payment endpoints
  - Log all payment transactions

- [ ] **File Upload Security**
  - Validate file types and sizes
  - Scan uploads for malware
  - Use signed URLs for MinIO
  - Set proper CORS on storage buckets

### Infrastructure Security

- [ ] **Firewall Configuration**
  ```bash
  # Allow only necessary ports
  sudo ufw allow 80/tcp    # HTTP (redirect to HTTPS)
  sudo ufw allow 443/tcp   # HTTPS
  sudo ufw allow 22/tcp    # SSH (from specific IPs only)
  sudo ufw enable
  ```

- [ ] **SSH Hardening**
  ```bash
  # Disable password authentication
  sudo nano /etc/ssh/sshd_config
  # Set: PasswordAuthentication no
  # Set: PermitRootLogin no
  sudo systemctl restart sshd
  ```

- [ ] **Regular Updates**
  ```bash
  # Enable automatic security updates
  sudo apt install unattended-upgrades
  sudo dpkg-reconfigure -plow unattended-upgrades
  ```

---

## SSL/HTTPS Configuration

### Option 1: Nginx + Let's Encrypt (Recommended)

```bash
# Install Nginx and Certbot
sudo apt install nginx certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d api.videosite.com

# Configure Nginx
sudo nano /etc/nginx/sites-available/videosite
```

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.videosite.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name api.videosite.com;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/api.videosite.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.videosite.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy to FastAPI
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Increase upload size for video uploads
    client_max_body_size 5000M;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/videosite /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Auto-renew SSL certificates
sudo crontab -e
# Add: 0 3 * * * certbot renew --quiet
```

### Option 2: CloudFlare (Easiest)

1. Add your domain to CloudFlare
2. Enable "Full (Strict)" SSL mode
3. CloudFlare handles SSL certificate automatically
4. Enable "Always Use HTTPS"
5. Configure origin certificates for backend

---

## Email Configuration

### Production SMTP Setup

**Recommended Providers:**
- SendGrid (99,000 free emails/month)
- Amazon SES (62,000 free emails/month)
- Mailgun (5,000 free emails/month)
- Postmark (100 free emails/month)

### SendGrid Example

```bash
# Install SendGrid SDK
pip install sendgrid

# Add to .env.production
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxx
SMTP_FROM_EMAIL=noreply@videosite.com
SMTP_FROM_NAME=VideoSite
SMTP_USE_TLS=True
```

### Email Templates

Ensure email templates work across email clients:

```bash
# Test email rendering
python -c "
from app.services.email_notification_service import EmailNotificationService
from app.models.user import User
from app.models.subscription import UserSubscription, SubscriptionPlan

# Create test objects and send email
# Verify it looks good in Gmail, Outlook, Apple Mail
"
```

### SPF and DKIM Configuration

Add DNS records to prevent emails from going to spam:

```
TXT record for videosite.com:
v=spf1 include:sendgrid.net ~all

DKIM record (get from SendGrid):
s1._domainkey.videosite.com → [CNAME from SendGrid]
```

---

## Monitoring and Logging

### 1. Application Logging

```python
# app/config.py - Production logging
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "json": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/videosite/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10,
            "formatter": "json",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"],
    },
}
```

### 2. Monitoring Tools

**Option A: Prometheus + Grafana**

```bash
# Install prometheus-fastapi-instrumentator
pip install prometheus-fastapi-instrumentator

# Add to main.py
from prometheus_fastapi_instrumentator import Instrumentator

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)
```

**Option B: Sentry for Error Tracking**

```bash
# Install Sentry
pip install sentry-sdk[fastapi]

# Add to main.py
import sentry_sdk

sentry_sdk.init(
    dsn="https://xxxxx@sentry.io/xxxxx",
    environment="production",
    traces_sample_rate=0.1,  # 10% of transactions
)
```

### 3. Health Check Endpoint

Already implemented at `/health` - monitor it:

```bash
# Create health check script
cat > /usr/local/bin/check_videosite_health.sh << 'EOF'
#!/bin/bash
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://api.videosite.com/health)
if [ $RESPONSE -ne 200 ]; then
    echo "Health check failed! HTTP $RESPONSE"
    # Send alert (email, Slack, PagerDuty, etc.)
    curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
      -H 'Content-Type: application/json' \
      -d "{\"text\":\"🚨 VideoSite API health check failed: HTTP $RESPONSE\"}"
fi
EOF

chmod +x /usr/local/bin/check_videosite_health.sh

# Run every 5 minutes
echo "*/5 * * * * /usr/local/bin/check_videosite_health.sh" | crontab -
```

### 4. Database Monitoring

```sql
-- Monitor slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 20;

-- Monitor connection pool
SELECT count(*) FROM pg_stat_activity WHERE datname = 'videosite_prod';
```

### 5. Payment Monitoring

Monitor payment success rates:

```python
# Create monitoring endpoint (admin only)
@router.get("/admin/payments/health")
async def payment_health(db: AsyncSession = Depends(get_db)):
    last_hour = datetime.now() - timedelta(hours=1)

    payments = await db.execute(
        select(Payment).where(Payment.created_at >= last_hour)
    )
    payments = list(payments.scalars().all())

    total = len(payments)
    succeeded = len([p for p in payments if p.status == PaymentStatus.SUCCEEDED])
    failed = len([p for p in payments if p.status == PaymentStatus.FAILED])

    success_rate = (succeeded / total * 100) if total > 0 else 100

    # Alert if success rate < 95%
    if success_rate < 95:
        # Send alert to admin
        pass

    return {
        "total_payments_last_hour": total,
        "succeeded": succeeded,
        "failed": failed,
        "success_rate": round(success_rate, 2),
    }
```

---

## Backup and Recovery

### 1. Database Backups

Already covered in [Database Setup](#database-setup) section.

**Test Recovery:**
```bash
# Restore from backup
pg_restore -U videosite_prod -d videosite_prod_restore /var/backups/postgresql/videosite/videosite_20250119.dump

# Verify data integrity
psql -U videosite_prod videosite_prod_restore -c "SELECT COUNT(*) FROM users;"
```

### 2. File Storage Backups

```bash
# Backup MinIO/S3 buckets
aws s3 sync s3://videosite-videos-prod s3://videosite-videos-backup --storage-class GLACIER

# Or use MinIO mirror
mc mirror minio/videosite-videos-prod minio-backup/videosite-videos-backup
```

### 3. Application Code Backups

```bash
# Use Git tags for releases
git tag -a v1.0.0 -m "Production release 1.0.0"
git push origin v1.0.0

# Backup repository to multiple remotes
git remote add backup git@backup-server:videosite.git
git push backup main --tags
```

### 4. Configuration Backups

```bash
# Backup .env files (encrypted)
gpg --symmetric --cipher-algo AES256 .env.production
aws s3 cp .env.production.gpg s3://videosite-secrets/
```

---

## Deployment Procedures

### Initial Deployment

```bash
# 1. Clone repository on production server
cd /var/www
git clone https://github.com/yourorg/videosite.git
cd videosite/backend

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment file
cp .env.production .env
# Edit with production values
nano .env

# 5. Run database migrations
export ENVIRONMENT=production
alembic upgrade head

# 6. Seed initial data
python scripts/seed_payment_data.py

# 7. Create systemd service
sudo nano /etc/systemd/system/videosite.service
```

```ini
[Unit]
Description=VideoSite API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/videosite/backend
Environment="PATH=/var/www/videosite/backend/venv/bin"
Environment="ENVIRONMENT=production"
ExecStart=/var/www/videosite/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

```bash
# 8. Start service
sudo systemctl daemon-reload
sudo systemctl enable videosite
sudo systemctl start videosite
sudo systemctl status videosite

# 9. Check logs
sudo journalctl -u videosite -f
```

### Updates and Rollback

```bash
# Deploy new version
cd /var/www/videosite/backend
git fetch origin
git checkout v1.1.0  # Use specific tag

# Backup current database
pg_dump -U videosite_prod -Fc videosite_prod > /var/backups/pre-v1.1.0.dump

# Run migrations
source venv/bin/activate
alembic upgrade head

# Restart service
sudo systemctl restart videosite

# Monitor logs
sudo journalctl -u videosite -f

# If issues occur, rollback:
git checkout v1.0.0
alembic downgrade <previous_revision>
sudo systemctl restart videosite
```

### Zero-Downtime Deployment (Blue-Green)

```bash
# Run two instances behind load balancer
# Deploy to instance 1
# Remove instance 1 from load balancer
# Update instance 1
# Add instance 1 back
# Repeat for instance 2
```

---

## Post-Deployment Testing

### 1. Health Checks

```bash
# API health
curl https://api.videosite.com/health

# Database connectivity
curl https://api.videosite.com/health/db

# Redis connectivity
curl https://api.videosite.com/health/cache

# MinIO connectivity
curl https://api.videosite.com/health/storage
```

### 2. Payment Flow Testing

```bash
# Test with minimal amount
curl -X POST https://api.videosite.com/api/v1/payments/intent \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 0.50,
    "currency": "usd",
    "provider": "stripe"
  }'
```

**Manual Testing Checklist:**
- [ ] Create subscription with Stripe (use live card with small amount)
- [ ] Verify payment confirmation email received
- [ ] Check payment recorded in database
- [ ] Test auto-renewal (set short period)
- [ ] Cancel subscription
- [ ] Verify cancellation email
- [ ] Test refund process
- [ ] Verify webhook delivery for all providers
- [ ] Test coupon application
- [ ] Download invoice PDF
- [ ] Test tax calculation for different regions

### 3. Load Testing

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test API performance
ab -n 1000 -c 10 https://api.videosite.com/api/v1/videos

# Monitor during load test
watch -n 1 'ps aux | grep uvicorn'
watch -n 1 'netstat -an | grep :8000 | wc -l'
```

### 4. Security Scanning

```bash
# SSL test
curl https://www.ssllabs.com/ssltest/analyze.html?d=api.videosite.com

# Check for common vulnerabilities
nmap -sV api.videosite.com

# Scan for outdated dependencies
pip list --outdated
```

### 5. Monitoring Validation

- [ ] Verify logs are being written to `/var/log/videosite/`
- [ ] Check Sentry is receiving errors (trigger test error)
- [ ] Confirm Prometheus metrics available at `/metrics`
- [ ] Test alert notifications (trigger health check failure)
- [ ] Verify database backups are running
- [ ] Check S3/MinIO file uploads work

---

## Production Maintenance

### Regular Tasks

**Daily:**
- Monitor error logs for critical issues
- Check payment success rates
- Review failed payment notifications

**Weekly:**
- Review performance metrics
- Check disk space usage
- Update dependencies if security patches available
- Review admin operation logs

**Monthly:**
- Review and rotate logs
- Analyze subscription churn metrics
- Update SSL certificates if needed
- Review and optimize slow queries
- Security audit

### Emergency Procedures

**If Payment Processing Fails:**
1. Check payment provider status pages
2. Verify webhook secrets haven't changed
3. Check database connectivity
4. Review recent error logs
5. Switch to backup payment provider if needed

**If Database Connection Issues:**
1. Check connection pool stats
2. Verify database server is running
3. Check network connectivity
4. Review recent slow queries
5. Restart database if necessary

**If High Memory Usage:**
1. Check for memory leaks: `ps aux | grep uvicorn`
2. Review recent changes
3. Restart uvicorn workers
4. Scale horizontally if needed

---

## Performance Optimization

### 1. Database Indexing

```sql
-- Optimize payment queries
CREATE INDEX CONCURRENTLY idx_payments_user_created ON payments(user_id, created_at DESC);
CREATE INDEX CONCURRENTLY idx_payments_status ON payments(status);
CREATE INDEX CONCURRENTLY idx_subscriptions_status ON user_subscriptions(status);
CREATE INDEX CONCURRENTLY idx_subscriptions_user_active ON user_subscriptions(user_id, status) WHERE status = 'active';
```

### 2. Redis Caching

Already implemented, but verify cache hit rates:

```python
# Monitor cache effectiveness
from app.utils.cache import get_redis

client = await get_redis()
info = await client.info("stats")
hits = info.get("keyspace_hits", 0)
misses = info.get("keyspace_misses", 0)
hit_rate = hits / (hits + misses) * 100 if (hits + misses) > 0 else 0

# Aim for > 80% hit rate
```

### 3. CDN for Static Assets

- Use CloudFlare or CloudFront for MinIO/S3
- Cache videos, images, PDFs
- Reduce backend load

### 4. Database Connection Pooling

Already configured in `app/database.py`. Monitor pool usage:

```python
from app.database import get_pool_status

status = get_pool_status()
# Keep checked_out < pool_size + max_overflow
```

---

## Compliance and Legal

### PCI DSS Compliance

Since you're using Stripe, PayPal, and Alipay:
- [ ] Never store credit card numbers
- [ ] Use HTTPS for all payment pages
- [ ] Implement strong access control
- [ ] Monitor and log access to payment data
- [ ] Regularly update and patch systems

Stripe, PayPal, and Alipay handle PCI compliance for you.

### GDPR Compliance (if serving EU users)

- [ ] Implement data export for users
- [ ] Implement data deletion ("right to be forgotten")
- [ ] Add privacy policy and terms of service
- [ ] Get explicit consent for data processing
- [ ] Implement cookie consent banner

### Data Retention

```python
# Script to delete old data
# Run monthly via cron

# Delete payment records older than 7 years (financial records)
DELETE FROM payments WHERE created_at < NOW() - INTERVAL '7 years';

# Anonymize cancelled subscriptions older than 1 year
UPDATE user_subscriptions
SET billing_email = 'anonymized@deleted.com',
    billing_name = 'Deleted User'
WHERE status = 'canceled'
  AND canceled_at < NOW() - INTERVAL '1 year';
```

---

## Troubleshooting

### Common Issues

**Issue: High Database Load**
```bash
# Check active connections
psql -U videosite_prod videosite_prod -c "SELECT count(*) FROM pg_stat_activity;"

# Check slow queries
psql -U videosite_prod videosite_prod -c "
SELECT query, state, wait_event_type, wait_event
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY query_start;
"

# Solution: Increase connection pool or optimize queries
```

**Issue: Redis Connection Errors**
```bash
# Check Redis status
redis-cli ping

# Check memory usage
redis-cli info memory

# Solution: Increase maxmemory or clear old cache
redis-cli FLUSHDB
```

**Issue: Payment Webhook Not Received**
```bash
# Check webhook logs in Stripe Dashboard
# Verify webhook URL is accessible
curl -X POST https://api.videosite.com/api/v1/webhooks/stripe

# Check webhook secret matches
# Check firewall allows Stripe IPs
```

---

## Support and Resources

### Payment Provider Documentation

- **Stripe:** https://stripe.com/docs/api
- **PayPal:** https://developer.paypal.com/docs/api/overview/
- **Alipay:** https://global.alipay.com/docs/ac/global/overview

### Monitoring

- **Sentry:** https://docs.sentry.io/
- **Prometheus:** https://prometheus.io/docs/
- **Grafana:** https://grafana.com/docs/

### Support Channels

- Application errors: Check `/var/log/videosite/app.log`
- Payment issues: Check provider dashboards
- Database issues: Check PostgreSQL logs
- Emergency: Contact system administrator

---

## Checklist for Go-Live

Use this checklist before launching to production:

### Pre-Launch
- [ ] All environment variables set in `.env.production`
- [ ] Database migrations completed
- [ ] SSL certificate installed and configured
- [ ] Payment gateways switched to live mode
- [ ] Webhook endpoints configured and tested
- [ ] Email sending configured and tested
- [ ] Domain DNS configured correctly
- [ ] Backups configured and tested
- [ ] Monitoring and alerting set up
- [ ] Load testing completed
- [ ] Security audit completed
- [ ] Legal pages ready (terms, privacy)

### Launch Day
- [ ] Deploy application
- [ ] Verify health checks pass
- [ ] Test complete payment flow
- [ ] Monitor error logs
- [ ] Monitor payment processing
- [ ] Verify emails are sending
- [ ] Check webhook delivery

### Post-Launch (Week 1)
- [ ] Daily error log review
- [ ] Monitor payment success rates
- [ ] Check backup completion
- [ ] Review performance metrics
- [ ] Address any issues immediately

---

**Last Updated:** 2025-01-19
**Version:** 1.0.0

For questions or issues, contact: admin@videosite.com
