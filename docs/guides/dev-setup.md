# 开发环境设置指南

本指南用于设置本地开发环境，不使用完整的 Docker Compose。

## 前置要求

- Python 3.11+
- Node.js 20+
- pnpm
- Docker (仅用于运行 PostgreSQL, Redis, MinIO)

## 快速开始

### 1. 启动基础设施服务

使用 Docker 只运行数据库和缓存服务：

```bash
# 使用 Makefile
make infra-up

# 或直接使用 docker-compose
docker-compose -f docker-compose.dev.yml up -d
```

这将启动：
- PostgreSQL (localhost:5432)
- Redis (localhost:6379)
- MinIO (localhost:9000, 控制台: localhost:9001)

### 2. 设置后端

#### 安装依赖

```bash
# 使用 Makefile
make backend-install

# 或手动操作
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 配置环境变量

```bash
cd backend
cp .env.example .env
```

`.env` 文件内容（默认配置已经可用）：
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/videosite
DATABASE_URL_SYNC=postgresql://postgres:postgres@localhost:5432/videosite
REDIS_URL=redis://localhost:6379/0
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production
```

#### 初始化数据库

```bash
# 使用 Makefile
make db-init

# 或手动操作
cd backend
source venv/bin/activate
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

#### 运行后端服务器

```bash
# 使用 Makefile (在新终端)
make backend-run

# 或手动操作
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 API 文档: http://localhost:8000/api/docs

### 3. 设置用户端前端

在新终端：

```bash
# 使用 Makefile
make frontend-install
make frontend-run

# 或手动操作
cd frontend
pnpm install
pnpm run dev
```

访问: http://localhost:3000

### 4. 设置后台管理前端

在新终端：

```bash
# 使用 Makefile
make admin-install
make admin-run

# 或手动操作
cd admin-frontend
pnpm install
pnpm run dev
```

访问: http://localhost:3001

## Makefile 命令

我们提供了 Makefile 简化开发流程：

```bash
# 查看所有命令
make help

# 基础设施
make infra-up          # 启动 PostgreSQL, Redis, MinIO
make infra-down        # 停止基础设施

# 后端
make backend-install   # 安装 Python 依赖
make backend-run       # 运行后端
make db-init          # 初始化数据库
make db-migrate MSG="your message"  # 创建迁移
make db-upgrade       # 执行迁移

# 前端
make frontend-install  # 安装前端依赖
make frontend-run      # 运行前端

# 后台管理
make admin-install     # 安装后台前端依赖
make admin-run         # 运行后台前端

# 组合命令
make all-install      # 安装所有依赖
make dev             # 启动基础设施（然后需手动启动其他服务）
make clean           # 清理所有 Docker 容器和数据
```

## 典型开发工作流

### 首次设置

```bash
# 1. 启动基础设施
make infra-up

# 2. 安装所有依赖
make all-install

# 3. 初始化数据库
make db-init

# 4. 在 3 个终端分别运行：
# 终端 1
make backend-run

# 终端 2
make frontend-run

# 终端 3
make admin-run
```

### 日常开发

```bash
# 确保基础设施运行
docker-compose -f docker-compose.dev.yml ps

# 如果没运行，启动它
make infra-up

# 然后在不同终端启动需要的服务
make backend-run    # 终端 1
make frontend-run   # 终端 2
make admin-run      # 终端 3
```

### 数据库更改

```bash
# 修改模型后
make db-migrate MSG="Add new field to video model"
make db-upgrade
```

## 创建初始管理员账户

```bash
cd backend
source venv/bin/activate

python << EOF
from app.database import SessionLocal
from app.models.user import AdminUser
from app.utils.security import get_password_hash

db = SessionLocal()
admin = AdminUser(
    email='admin@videosite.com',
    username='admin',
    hashed_password=get_password_hash('admin123'),
    full_name='Super Admin',
    is_active=True,
    is_superadmin=True
)
db.add(admin)
db.commit()
db.close()
print('Admin user created!')
print('Username: admin')
print('Password: admin123')
EOF
```

## 创建测试数据

### 创建测试用户

```bash
cd backend
source venv/bin/activate

python << EOF
from app.database import SessionLocal
from app.models.user import User
from app.utils.security import get_password_hash

db = SessionLocal()
user = User(
    email='test@example.com',
    username='testuser',
    hashed_password=get_password_hash('password123'),
    full_name='Test User',
    is_active=True,
    is_verified=True
)
db.add(user)
db.commit()
db.close()
print('Test user created!')
print('Email: test@example.com')
print('Password: password123')
EOF
```

## 故障排查

### PostgreSQL 连接失败

检查 PostgreSQL 是否运行：
```bash
docker-compose -f docker-compose.dev.yml ps postgres
```

重启 PostgreSQL：
```bash
docker-compose -f docker-compose.dev.yml restart postgres
```

### 端口被占用

检查端口占用：
```bash
# Linux/Mac
lsof -i :8000  # 后端
lsof -i :3000  # 前端
lsof -i :3001  # 后台管理

# 或使用 netstat
netstat -tlnp | grep 8000
```

### Python 虚拟环境问题

```bash
# 删除并重新创建
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### pnpm 依赖问题

```bash
# 清理并重新安装
cd frontend  # 或 admin-frontend
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

## 开发工具推荐

### VS Code 扩展

- Python (Microsoft)
- Pylance
- ES7+ React/Redux/React-Native snippets
- TypeScript Vue Plugin (Volar)
- Tailwind CSS IntelliSense
- Thunder Client (API 测试)

### 数据库工具

- pgAdmin 4
- DBeaver
- TablePlus

### API 测试

- Thunder Client (VS Code 扩展)
- Postman
- Insomnia
- 或直接使用 http://localhost:8000/api/docs (Swagger UI)

## 性能优化提示

### 后端

- 使用 `uvicorn --reload` 进行热重载
- 查看 SQL 查询: 在 `.env` 中设置 `DEBUG=True`
- 使用 Alembic 生成迁移时检查生成的 SQL

### 前端

- Vite 已经提供了很快的 HMR
- 使用浏览器 DevTools 的 React Developer Tools
- 检查网络请求和性能

## 下一步

- 阅读 [README.md](README.md) 了解完整功能
- 查看 [QUICKSTART.md](QUICKSTART.md) 了解 Docker 部署
- 开始开发你的功能！

Happy coding! 🚀
