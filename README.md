# 🎬 VideoSite - 企业级视频流媒体平台

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)

**功能完善、生产就绪的全栈视频流媒体解决方案**

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [开发指南](#-开发指南) • [技术架构](#-系统架构) • [贡献指南](#-参与贡献)

</div>

---

## 📖 项目概述

VideoSite 是一个基于现代化技术栈构建的开源视频流媒体平台，提供从视频上传、转码、存储到播放的完整解决方案。适用于构建类似 YouTube、Bilibili 的视频网站，支持弹幕、评论、收藏等丰富的社交互动功能。

### ✨ 核心亮点

- 🎥 **完整视频解决方案**: 多格式上传、自动转码、HLS/DASH 自适应流媒体
- 🚀 **高性能架构**: 异步处理、多层缓存、数据库连接池优化
- 🎨 **现代化界面**: 深色/浅色主题、响应式设计、流畅动画
- 🔐 **企业级安全**: JWT 认证、RBAC 权限、请求限流、操作审计
- 💬 **社交互动**: 实时弹幕、嵌套评论、评分系统、收藏夹
- 📊 **强大管理后台**: 可视化数据分析、批量操作、系统监控、AI 管理
- 🌍 **国际化支持**: 中英文双语、可扩展的 i18n 架构
- 🐳 **容器化部署**: Docker Compose 一键部署，开箱即用

---

## 🎯 功能特性

### 🎬 视频管理

- **多格式支持**: MP4、MKV、AVI、MOV 等主流格式
- **自适应流媒体**: 支持 HLS/DASH 多码率自适应
- **AV1 编码**: 支持新一代编解码器，更优的压缩率
- **GPU 加速**: NVIDIA NVENC 硬件加速转码
- **缩略图生成**: 自动生成封面图和预览帧
- **字幕支持**: 多语言字幕上传和显示

### 👥 用户功能

- **身份认证**: 安全的 JWT 令牌登录/注册
- **视频互动**: 点赞、收藏、评论、评分
- **观看历史**: 自动记录播放进度，断点续播
- **收藏夹**: 自定义文件夹组织视频
- **个性化推荐**: AI 驱动的内容推荐
- **系列剧集**: 追剧功能，连续播放
- **搜索功能**: 全文搜索，自动完成和高级筛选

### 🎮 互动功能

- **弹幕系统**: 实时弹幕评论(B 站风格)
- **评分系统**: 5 星评分，显示平均分
- **评论主题**: 支持嵌套评论和审核
- **社交分享**: 分享视频到社交媒体平台
- **实时通知**: WebSocket 实时通知推送

### ⚙️ 管理后台

- **数据仪表板**: 统计数据、图表、用户分析
- **内容审核**: 审查视频、评论、用户
- **用户管理**: 封禁、权限管理
- **系统设置**: 配置全站参数
- **操作日志**: 所有管理操作的审计记录
- **IP 黑名单**: 屏蔽恶意 IP 和 IP 段
- **批量操作**: 批量管理视频和用户

### 🔧 技术特性

- **数据库优化**: 复合索引、查询优化
- **多层缓存**: Redis + 浏览器多层缓存策略
- **请求限流**: 智能限流防止滥用
- **图片处理**: 自动压缩和 WebP 转换
- **CDN 就绪**: MinIO 对象存储集成
- **Docker 支持**: 容器化部署
- **API 文档**: 自动生成 OpenAPI/Swagger 文档

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                       客户端层                               │
├──────────────────┬──────────────────┬──────────────────────┤
│   用户前端       │   管理后台        │   移动应用 (PWA)      │
│  (React + TS)    │  (React + Ant)   │                      │
└────────┬─────────┴────────┬─────────┴──────────────────────┘
         │                  │
         └──────────┬───────┘
                    │
         ┌──────────▼──────────┐
         │   API 网关           │
         │   (FastAPI)          │
         └──────────┬──────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
┌───▼────┐    ┌────▼────┐    ┌────▼────┐
│PostgreSQL│   │  Redis  │    │  MinIO  │
│  数据库  │   │  缓存   │    │  存储   │
└──────────┘   └─────────┘    └─────────┘
```

### 技术栈

#### 后端

- **框架**: FastAPI (Python 3.11+)
- **数据库**: PostgreSQL 16 + asyncpg
- **缓存**: Redis 7 + 连接池
- **存储**: MinIO (S3 兼容对象存储)
- **ORM**: SQLAlchemy 2.0 (异步)
- **迁移工具**: Alembic
- **认证**: JWT (python-jose)
- **任务队列**: Celery + Redis

#### 前端

- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **样式**: TailwindCSS
- **状态管理**: TanStack Query (React Query)
- **路由**: React Router v6
- **视频播放器**: Video.js + HLS 支持
- **图标**: Lucide React

#### 管理后台

- **框架**: React 18 + TypeScript
- **UI 库**: Ant Design 5
- **图表**: Ant Design Charts
- **表单处理**: Ant Design Form

#### 运维部署

- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx (可选)
- **监控**: 内置操作日志
- **CI/CD**: GitHub Actions

---

## 🚀 快速开始

### 环境要求

**推荐方式 (Docker):**

- Docker 20.10+
- Docker Compose 2.0+

**手动安装:**

- Python 3.11+
- Node.js 18+
- pnpm 8+
- PostgreSQL 16+
- Redis 7+
- MinIO (或 S3 兼容存储)

### 🐳 Docker 部署 (推荐)

```bash
# 1. 克隆仓库
git clone https://github.com/awd2211/next-video-site.git
cd next-video-site

# 2. 启动所有服务
docker-compose up -d

# 3. 初始化数据库
docker-compose exec backend alembic upgrade head

# 4. 创建管理员账户
docker-compose exec backend python -c "
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

**✅ 访问应用:**

- 🌐 用户前端: http://localhost:3000
- 🛠️ 管理后台: http://localhost:3001
- 📡 API 文档: http://localhost:8000/api/docs
- 📦 MinIO 控制台: http://localhost:9003

---

### 🛠️ 开发环境搭建 (使用 Make)

**查看所有可用命令:**

```bash
make help
```

#### 步骤 1: 启动基础设施

```bash
# 启动 PostgreSQL (端口 5434)、Redis (端口 6381)、MinIO (端口 9002/9003)
make infra-up

# 安装所有依赖 (后端 + 前端 + 管理后台)
make all-install

# 初始化数据库
make db-init
```

#### 步骤 2: 启动服务 (需要 3 个终端)

```bash
# 终端 1: 启动后端 (http://localhost:8000)
make backend-run

# 终端 2: 启动用户前端 (http://localhost:5173 代理到 3000)
make frontend-run

# 终端 3: 启动管理后台 (http://localhost:5173 代理到 3001)
make admin-run
```

#### 常用 Make 命令

```bash
# 数据库操作
make db-migrate MSG="添加新字段"    # 创建数据库迁移
make db-upgrade                    # 应用迁移
make db-downgrade                  # 回滚一个迁移

# 代码格式化
make format                        # 格式化所有代码
make format-backend                # 格式化后端代码 (Black + isort)
make format-check                  # 检查格式化

# 基础设施管理
make infra-up                      # 启动基础设施
make infra-down                    # 停止基础设施
make clean                         # 清理所有容器和卷
```

#### 手动启动（不使用 Make）

<details>
<summary>展开查看详细步骤</summary>

**后端:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # 编辑配置
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**前端:**

```bash
cd frontend
pnpm install
pnpm run dev  # 访问 http://localhost:5173
```

**管理后台:**

```bash
cd admin-frontend
pnpm install
pnpm run dev  # 访问 http://localhost:5173
```

</details>

### 📝 环境配置

在 `backend` 目录下创建 `.env` 文件（参考 `.env.example`）:

```env
# 数据库配置 (开发环境使用端口 5434)
DATABASE_URL=postgresql+asyncpg://videosite:videosite@localhost:5434/videosite
DATABASE_URL_SYNC=postgresql://videosite:videosite@localhost:5434/videosite

# Redis 配置 (开发环境使用端口 6381)
REDIS_URL=redis://localhost:6381/0

# MinIO 配置 (开发环境使用端口 9002)
MINIO_ENDPOINT=localhost:9002
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=videos
MINIO_PUBLIC_URL=http://localhost:9002  # 用于生成文件 URL

# 安全配置 (生产环境必须修改)
SECRET_KEY=change-this-in-production-$(openssl rand -hex 32)
JWT_SECRET_KEY=change-this-in-production-$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# 应用配置
DEBUG=True  # 生产环境设置为 False
PROJECT_NAME=VideoSite
API_V1_STR=/api/v1

# SMTP 邮件配置 (可选)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@videosite.com
```

**注意事项:**

- 开发环境的端口已映射避免冲突 (5434/6381/9002)
- 生产环境请使用强随机密钥
- MinIO 需要先创建 `videos` bucket

---

## 📚 项目结构

```
video/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/               # 用户 API 端点
│   │   │   ├── auth.py        # 认证相关
│   │   │   ├── videos.py      # 视频操作
│   │   │   ├── comments.py    # 评论系统
│   │   │   └── websocket.py   # WebSocket 通知
│   │   ├── admin/             # 管理 API 端点
│   │   │   ├── videos.py      # 视频管理
│   │   │   ├── users.py       # 用户管理
│   │   │   ├── stats.py       # 统计分析
│   │   │   └── system_health.py  # 系统监控
│   │   ├── models/            # SQLAlchemy ORM 模型
│   │   ├── schemas/           # Pydantic 验证模式
│   │   ├── utils/             # 工具函数
│   │   │   ├── security.py    # JWT 认证
│   │   │   ├── cache.py       # Redis 缓存
│   │   │   ├── minio_client.py  # 对象存储
│   │   │   └── logging_utils.py  # 日志记录
│   │   ├── middleware/        # 自定义中间件
│   │   ├── main.py            # FastAPI 应用入口
│   │   ├── config.py          # 配置管理
│   │   └── database.py        # 数据库连接
│   ├── alembic/               # 数据库迁移
│   └── tests/                 # 单元测试
│
├── frontend/                  # 用户前端 (React 18 + TypeScript)
│   └── src/
│       ├── components/        # 可复用组件
│       │   ├── VideoPlayer/   # 视频播放器
│       │   ├── VideoCard/     # 视频卡片
│       │   └── Layout/        # 布局组件
│       ├── pages/             # 页面组件
│       ├── services/          # API 服务
│       ├── contexts/          # React 上下文
│       ├── hooks/             # 自定义 Hooks
│       └── i18n/              # 国际化
│
├── admin-frontend/            # 管理后台 (React 18 + Ant Design)
│   └── src/
│       ├── pages/             # 管理页面
│       │   ├── Dashboard/     # 数据仪表板
│       │   ├── Videos/        # 视频管理
│       │   ├── Users/         # 用户管理
│       │   └── SystemHealth/  # 系统健康
│       ├── services/          # 管理 API
│       └── i18n/              # 国际化
│
├── docker-compose.yml         # 生产环境编排
├── docker-compose.dev.yml     # 开发环境编排
├── Makefile                   # 开发命令集
├── CLAUDE.md                  # 开发指南
└── CHANGELOG.md               # 变更日志
```

## 📖 开发指南

### 核心文档

- 📘 **[CLAUDE.md](CLAUDE.md)** - 完整的开发文档，包含架构说明、开发工作流、最佳实践
- 📝 **[CHANGELOG.md](CHANGELOG.md)** - 版本变更记录
- 🔧 **[API 文档](http://localhost:8000/api/docs)** - 自动生成的 Swagger UI 交互式文档
- 🤝 **[CONTRIBUTING.md](CONTRIBUTING.md)** - 贡献指南和代码规范

### 关键概念

**认证系统:**

- JWT 令牌 (access token + refresh token)
- 用户认证: `get_current_user()` 依赖注入
- 管理员认证: `get_current_admin_user()` 依赖注入
- 超级管理员: `get_current_superadmin()` 权限检查

**数据库会话:**

- 异步 SQLAlchemy + asyncpg 驱动
- 连接池: 20 基础 + 40 溢出连接
- 使用 `get_db()` 依赖注入获取会话
- 自动提交/回滚事务

**缓存策略:**

- Redis 多层缓存
- 视频列表: 5-15 分钟 TTL
- 分类/国家: 1 小时 TTL
- 统计数据: 5 分钟 TTL
- 使用 `CacheManager` 类管理

**中间件栈 (按执行顺序):**

1. `SecurityHeadersMiddleware` - 安全头部
2. `PerformanceMonitorMiddleware` - 性能监控
3. `RequestIDMiddleware` - 请求 ID 追踪
4. `HTTPCacheMiddleware` - HTTP 缓存
5. `RequestSizeLimitMiddleware` - 请求大小限制
6. `CORSMiddleware` - 跨域处理
7. `GZipMiddleware` - 响应压缩
8. `OperationLogMiddleware` - 操作日志

---

## 🎮 API 使用示例

### 用户认证

```bash
# 注册用户
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"user","password":"password123"}'

# 登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"password123"}'
```

### 获取视频列表

```bash
# 获取视频列表（带分页和筛选）
curl http://localhost:8000/api/v1/videos?page=1&page_size=20&category_id=1&sort_by=views

# 搜索视频
curl http://localhost:8000/api/v1/videos/search?q=关键词&page=1
```

### 前端集成示例

```typescript
// 使用 TanStack Query 获取视频
import { useQuery } from '@tanstack/react-query';
import { videoService } from '@/services/videoService';

function VideoList() {
  const { data, isLoading } = useQuery({
    queryKey: ['videos', { page: 1, category_id: 5 }],
    queryFn: () => videoService.getVideos({ page: 1, category_id: 5 }),
  });

  if (isLoading) return <div>加载中...</div>;
  return (
    <div>
      {data.items.map((video) => (
        <VideoCard key={video.id} {...video} />
      ))}
    </div>
  );
}
```

---

## ❓ 常见问题

<details>
<summary><b>如何创建管理员账户？</b></summary>

使用上面 Docker 部署步骤中的 Python 脚本，或者手动在数据库中创建。管理员账户存储在 `admin_users` 表中。

</details>

<details>
<summary><b>MinIO 连接失败怎么办？</b></summary>

1. 检查 MinIO 服务是否运行: `docker ps | grep minio`
2. 确认端口映射正确: 开发环境使用 9002/9003
3. 检查 `.env` 中的 `MINIO_ENDPOINT` 配置
4. 访问 MinIO 控制台手动创建 `videos` bucket

</details>

<details>
<summary><b>数据库迁移失败？</b></summary>

```bash
# 查看当前迁移状态
cd backend && alembic current

# 查看迁移历史
alembic history

# 回滚到上一个版本
alembic downgrade -1

# 重新应用迁移
alembic upgrade head
```

</details>

<details>
<summary><b>前端请求出现 CORS 错误？</b></summary>

开发环境中，Vite 配置了代理转发到后端，应该不会有 CORS 问题。如果出现：

1. 确认后端已启动在 8000 端口
2. 检查 `frontend/vite.config.ts` 和 `admin-frontend/vite.config.ts` 中的代理配置
3. 确认后端 `CORS_ORIGINS` 环境变量包含前端地址

</details>

<details>
<summary><b>如何清空所有数据重新开始？</b></summary>

```bash
# 停止所有服务并清理卷
make clean

# 或手动操作
docker-compose -f docker-compose.dev.yml down -v

# 重新启动基础设施
make infra-up

# 重新初始化数据库
make db-init
```

</details>

<details>
<summary><b>生产环境部署建议？</b></summary>

1. 使用强随机密钥替换 `SECRET_KEY` 和 `JWT_SECRET_KEY`
2. 设置 `DEBUG=False`
3. 配置 Nginx 作为反向代理
4. 使用专业的对象存储服务 (AWS S3, 阿里云 OSS)
5. 配置 SSL/TLS 证书
6. 设置数据库备份策略
7. 配置日志收集和监控

</details>

---

## 🤝 参与贡献

我们欢迎社区的贡献！请阅读[贡献指南](CONTRIBUTING.md)开始参与。

### 如何贡献

1. **Fork** 本仓库
2. **创建**功能分支 (`git checkout -b feature/AmazingFeature`)
3. **提交**你的修改 (`git commit -m '添加某个很棒的功能'`)
4. **推送**到分支 (`git push origin feature/AmazingFeature`)
5. **打开** Pull Request

### 开发规范

- 遵循现有代码风格
- 为新功能编写测试
- 根据需要更新文档
- 使用约定式提交规范

---

## 🐛 Bug 报告 & 功能请求

请使用 [GitHub Issues](https://github.com/awd2211/next-video-site/issues) 报告 bug 或请求新功能。

**创建 issue 前请:**

- 检查是否已存在相同的 issue
- 提供详细的复现步骤
- 包含系统信息(操作系统、浏览器、版本)

---

## 📜 开源协议

本项目采用 **MIT 协议** - 详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- **FastAPI** - 现代化的 Python Web 框架
- **React** - 用户界面库
- **Video.js** - HTML5 视频播放器
- **Ant Design** - 企业级 UI 组件库
- **TailwindCSS** - 实用优先的 CSS 框架
- 所有在本项目中使用的开源库

---

## 📞 联系 & 支持

- **GitHub**: [@awd2211](https://github.com/awd2211)
- **Issues**: [项目 Issues](https://github.com/awd2211/next-video-site/issues)
- **讨论区**: [GitHub Discussions](https://github.com/awd2211/next-video-site/discussions)

---

## 🗺️ 开发路线图

- [ ] 移动原生应用 (iOS/Android)
- [ ] 直播支持 (RTMP/WebRTC)
- [ ] AI 驱动的内容审核
- [ ] 多 CDN 支持
- [ ] 高级数据分析仪表板
- [ ] 插件系统，支持扩展
- [ ] Elasticsearch 集成，高级搜索
- [ ] 多租户支持

---

## 📊 项目统计

![GitHub stars](https://img.shields.io/github/stars/awd2211/next-video-site?style=social)
![GitHub forks](https://img.shields.io/github/forks/awd2211/next-video-site?style=social)
![GitHub issues](https://img.shields.io/github/issues/awd2211/next-video-site)
![GitHub pull requests](https://img.shields.io/github/issues-pr/awd2211/next-video-site)

---

<div align="center">

**⭐ 如果觉得有帮助，请给项目点个 Star！**

用 ❤️ 制作 by VideoSite 团队

</div>
