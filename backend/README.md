# Backend - VideoSite API

FastAPI 后端服务，提供完整的视频流媒体平台 REST API。

## 📋 技术栈

- **框架**: FastAPI 0.109+
- **Python**: 3.11+
- **数据库**: PostgreSQL 16 (异步 asyncpg)
- **ORM**: SQLAlchemy 2.0 (异步)
- **缓存**: Redis 7
- **对象存储**: MinIO (S3 兼容)
- **认证**: JWT (python-jose)
- **迁移工具**: Alembic
- **测试**: pytest + pytest-asyncio
- **代码格式化**: Black + isort

## 📁 项目结构

```
backend/
├── app/
│   ├── api/                    # 用户 API 端点
│   │   ├── auth.py            # 认证 (登录/注册/刷新令牌)
│   │   ├── videos.py          # 视频操作 (列表/详情/上传)
│   │   ├── comments.py        # 评论系统
│   │   ├── categories.py      # 分类管理
│   │   ├── search.py          # 搜索功能
│   │   └── websocket.py       # WebSocket 通知
│   │
│   ├── admin/                 # 管理 API 端点
│   │   ├── auth.py            # 管理员认证
│   │   ├── videos.py          # 视频管理
│   │   ├── users.py           # 用户管理
│   │   ├── comments.py        # 评论审核
│   │   ├── stats.py           # 统计分析
│   │   ├── logs.py            # 操作日志
│   │   ├── ai_config.py       # AI 配置管理
│   │   └── system_health.py   # 系统健康监控
│   │
│   ├── models/                # SQLAlchemy 模型
│   │   ├── user.py            # User, AdminUser
│   │   ├── video.py           # Video
│   │   ├── comment.py         # Comment
│   │   ├── category.py        # Category, Country, Tag
│   │   ├── notification.py    # AdminNotification
│   │   └── ...
│   │
│   ├── schemas/               # Pydantic 验证模式
│   │   ├── user.py
│   │   ├── video.py
│   │   ├── comment.py
│   │   └── ...
│   │
│   ├── utils/                 # 工具函数
│   │   ├── security.py        # JWT 认证、密码哈希
│   │   ├── dependencies.py    # FastAPI 依赖注入
│   │   ├── cache.py           # Redis 缓存管理
│   │   ├── minio_client.py    # MinIO 对象存储客户端
│   │   ├── logging_utils.py   # 日志记录
│   │   └── admin_notification_service.py  # 管理员通知
│   │
│   ├── middleware/            # 自定义中间件
│   │   ├── security_headers.py         # 安全头部
│   │   ├── performance_monitor.py      # 性能监控
│   │   ├── request_id.py               # 请求 ID 追踪
│   │   ├── operation_log.py            # 操作日志
│   │   └── ...
│   │
│   ├── main.py               # FastAPI 应用入口
│   ├── config.py             # 配置管理 (Pydantic Settings)
│   └── database.py           # 数据库连接和会话管理
│
├── alembic/                  # 数据库迁移
│   ├── versions/             # 迁移脚本
│   └── env.py                # Alembic 配置
│
├── tests/                    # 单元测试
│   ├── conftest.py           # pytest 配置和 fixtures
│   ├── test_auth.py
│   ├── test_videos.py
│   └── ...
│
├── requirements.txt          # Python 依赖
├── .env.example             # 环境变量示例
└── alembic.ini              # Alembic 配置文件
```

## 🚀 快速开始

### 环境要求

- Python 3.11+
- PostgreSQL 16+
- Redis 7+
- MinIO (或 S3 兼容存储)

### 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件，配置数据库、Redis、MinIO 等
```

### 数据库初始化

```bash
# 运行迁移
alembic upgrade head

# 创建管理员账户（可选）
python -c "
from app.database import SessionLocal
from app.models.user import AdminUser
from app.utils.security import get_password_hash
db = SessionLocal()
admin = AdminUser(
    email='admin@example.com',
    username='admin',
    hashed_password=get_password_hash('admin123'),
    full_name='Admin',
    is_active=True,
    is_superadmin=True
)
db.add(admin)
db.commit()
print('Admin created: admin@example.com / admin123')
"
```

### 启动服务

```bash
# 开发模式（热重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用 Make 命令（从项目根目录）
cd .. && make backend-run
```

访问：

- **API 文档**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **健康检查**: http://localhost:8000/health

## 🛠️ 开发指南

### 数据库迁移

```bash
# 创建新迁移
alembic revision --autogenerate -m "描述你的修改"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1

# 查看迁移历史
alembic history

# 查看当前版本
alembic current
```

### 代码格式化

```bash
# 格式化代码
black app/ tests/
isort app/ tests/

# 或使用 Make 命令（从项目根目录）
cd .. && make format-backend

# 检查格式化
cd .. && make format-check
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_auth.py

# 详细输出
pytest -v

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

### 添加新功能

1. **创建或修改模型** (`app/models/`)
2. **生成数据库迁移** (`alembic revision --autogenerate`)
3. **创建 Pydantic 模式** (`app/schemas/`)
4. **实现 API 端点** (`app/api/` 或 `app/admin/`)
5. **编写测试** (`tests/`)
6. **更新文档** (如需要)

## 🔑 核心概念

### 认证系统

- **JWT 令牌**: Access Token (30 分钟) + Refresh Token (7 天)
- **用户认证**: `get_current_user()` 依赖注入
- **管理员认证**: `get_current_admin_user()` 依赖注入
- **超级管理员**: `get_current_superadmin()` 权限检查

### 数据库会话

```python
from app.database import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def my_endpoint(db: AsyncSession = Depends(get_db)):
    # 使用 db 进行数据库操作
    result = await db.execute(select(Video))
    videos = result.scalars().all()
```

### 缓存使用

```python
from app.utils.cache import CacheManager

# 设置缓存
await CacheManager.set("key", value, ttl=300)

# 获取缓存
value = await CacheManager.get("key")

# 删除缓存
await CacheManager.delete("key")
```

### MinIO 文件上传

```python
from app.utils.minio_client import get_minio_client

minio_client = get_minio_client()
file_url = await minio_client.upload_file(
    file_data=file_content,
    file_name="video.mp4",
    content_type="video/mp4"
)
```

## 📊 中间件栈

请求处理顺序（自上而下）：

1. **SecurityHeadersMiddleware** - 添加安全头部 (CSP, HSTS, X-Frame-Options)
2. **PerformanceMonitorMiddleware** - 监控慢 API (>1 秒)
3. **RequestIDMiddleware** - 生成唯一请求 ID
4. **HTTPCacheMiddleware** - HTTP 缓存优化
5. **RequestSizeLimitMiddleware** - 限制请求大小 (10MB)
6. **CORSMiddleware** - 处理跨域请求
7. **GZipMiddleware** - 响应压缩
8. **OperationLogMiddleware** - 记录管理员操作

## 🔐 安全特性

- **JWT 认证**: 基于令牌的无状态认证
- **密码哈希**: bcrypt 加密存储
- **请求限流**: SlowAPI 防止滥用
- **SQL 注入防护**: SQLAlchemy ORM 参数化查询
- **XSS 防护**: 自动 HTML 转义
- **CSRF 保护**: SameSite Cookie 策略
- **安全头部**: CSP, HSTS, X-Content-Type-Options

## 📝 环境变量说明

| 变量名              | 说明               | 示例                                                      |
| ------------------- | ------------------ | --------------------------------------------------------- |
| `DATABASE_URL`      | 异步数据库连接     | `postgresql+asyncpg://user:pass@localhost:5434/videosite` |
| `DATABASE_URL_SYNC` | 同步连接 (Alembic) | `postgresql://user:pass@localhost:5434/videosite`         |
| `REDIS_URL`         | Redis 连接         | `redis://localhost:6381/0`                                |
| `MINIO_ENDPOINT`    | MinIO 端点         | `localhost:9002`                                          |
| `MINIO_ACCESS_KEY`  | MinIO 访问密钥     | `minioadmin`                                              |
| `MINIO_SECRET_KEY`  | MinIO 密钥         | `minioadmin`                                              |
| `SECRET_KEY`        | 应用密钥           | 随机生成                                                  |
| `JWT_SECRET_KEY`    | JWT 签名密钥       | 随机生成                                                  |
| `DEBUG`             | 调试模式           | `True` / `False`                                          |

## 🐛 调试技巧

### 查看 SQL 查询

在 `.env` 中设置 `DEBUG=True`，所有 SQL 查询会打印到控制台。

### 查看连接池状态

```python
from app.database import get_pool_status

status = get_pool_status()
print(f"Pool: {status}")
```

### 清空 Redis 缓存

```python
from app.utils.cache import get_redis

redis = await get_redis()
await redis.flushdb()
```

## 📚 相关文档

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 文档](https://docs.sqlalchemy.org/en/20/)
- [Alembic 文档](https://alembic.sqlalchemy.org/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [项目开发指南](../CLAUDE.md)

## 🤝 贡献指南

请参考项目根目录的 [CONTRIBUTING.md](../CONTRIBUTING.md)。

## 📄 许可证

MIT License - 详见 [LICENSE](../LICENSE)
