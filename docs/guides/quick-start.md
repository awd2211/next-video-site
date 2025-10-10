# 快速启动指南

## 前置要求

- Docker 和 Docker Compose
- Git
- (可选) pnpm - 如果想本地开发前端

## 一键启动（推荐）

### 1. 配置环境变量

```bash
cp backend/.env.example backend/.env
```

编辑 `backend/.env` 文件，至少修改以下内容：
```env
SECRET_KEY=your-random-secret-key-here
JWT_SECRET_KEY=your-random-jwt-secret-key-here
```

### 2. 启动所有服务

```bash
docker-compose up -d
```

这将启动：
- PostgreSQL 数据库（端口 5432）
- Redis（端口 6379）
- MinIO 对象存储（端口 9000, 9001）
- 后端 API（端口 8000）
- 用户端前端（端口 3000）
- 后台管理前端（端口 3001）

### 3. 初始化数据库

首次启动需要运行数据库迁移：

```bash
# 创建数据库迁移
docker-compose exec backend alembic revision --autogenerate -m "Initial migration"

# 执行迁移
docker-compose exec backend alembic upgrade head
```

### 4. 创建超级管理员（可选）

进入后端容器创建管理员用户：

```bash
docker-compose exec backend python -c "
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
print('Admin user created!')
"
```

默认管理员账号：
- 用户名: `admin`
- 密码: `admin123`

### 5. 访问应用

- **用户端**: http://localhost:3000
- **后台管理**: http://localhost:3001
- **API 文档**: http://localhost:8000/api/docs
- **MinIO 控制台**: http://localhost:9001 (minioadmin/minioadmin)

## 本地开发（不使用 Docker）

### 后端

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 运行迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload
```

### 前端

```bash
cd frontend

# 安装依赖
pnpm install

# 启动开发服务器
pnpm run dev
```

### 后台管理

```bash
cd admin-frontend

# 安装依赖
pnpm install

# 启动开发服务器
pnpm run dev
```

## 常用命令

### 查看服务日志
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f admin_frontend
```

### 停止服务
```bash
docker-compose down
```

### 重启服务
```bash
docker-compose restart
```

### 清理所有数据（小心！）
```bash
docker-compose down -v
```

## 数据库管理

### 创建新的迁移
```bash
docker-compose exec backend alembic revision --autogenerate -m "Your message"
```

### 执行迁移
```bash
docker-compose exec backend alembic upgrade head
```

### 回滚迁移
```bash
docker-compose exec backend alembic downgrade -1
```

### 查看迁移历史
```bash
docker-compose exec backend alembic history
```

## 测试数据

### 创建测试用户

```bash
docker-compose exec backend python -c "
from app.database import SessionLocal
from app.models.user import User
from app.utils.security import get_password_hash

db = SessionLocal()
user = User(
    email='test@example.com',
    username='testuser',
    hashed_password=get_password_hash('password123'),
    full_name='Test User',
    is_active=True
)
db.add(user)
db.commit()
print('Test user created!')
"
```

### 创建测试视频

可以通过后台管理界面添加视频，或者使用 API：

```bash
curl -X POST "http://localhost:8000/api/v1/admin/videos" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Movie",
    "video_type": "movie",
    "status": "published",
    "description": "This is a test movie",
    "release_year": 2024
  }'
```

## 故障排查

### 端口冲突
如果端口已被占用，编辑 `docker-compose.yml` 修改端口映射：
```yaml
ports:
  - "8001:8000"  # 将 8000 改为 8001
```

### 数据库连接错误
确保 PostgreSQL 服务已启动：
```bash
docker-compose ps postgres
```

### 前端无法连接后端
检查代理配置在 `frontend/vite.config.ts` 和 `admin-frontend/vite.config.ts`

## 生产环境部署

1. **修改所有密钥和密码**
2. **配置 Nginx 反向代理**
3. **启用 HTTPS**
4. **配置专业的对象存储（AWS S3/阿里云 OSS）**
5. **设置数据库备份**
6. **配置 CDN**
7. **监控和日志**

详见 [README.md](README.md) 的部署章节。

## 下一步

- 阅读完整 [README.md](README.md) 了解所有功能
- 浏览 [API 文档](http://localhost:8000/api/docs)
- 开始添加视频内容！

## 需要帮助？

- 查看日志: `docker-compose logs`
- 检查服务状态: `docker-compose ps`
- 重启服务: `docker-compose restart`

祝你使用愉快！🎬
