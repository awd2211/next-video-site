# 🎬 VideoSite - 现代化视频流媒体平台

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)

**功能完善、生产就绪的全栈视频流媒体平台**

[功能特性](#-功能特性) • [在线演示](#-在线演示) • [快速开始](#-快速开始) • [技术文档](#-技术文档) • [参与贡献](#-参与贡献)

</div>

---

## 📖 项目概述

VideoSite 是一个使用现代化 Web 技术构建的全面、开源的视频流媒体平台。它提供了视频托管、转码、流媒体传输和用户互动的完整解决方案，类似于 YouTube 或 Bilibili 等流行的视频平台。

### ✨ 核心亮点

- 🎥 **完整视频管道**: 上传、转码(H.264/H.265/AV1)、存储和流媒体播放
- 🚀 **高性能架构**: 优化的数据库查询、Redis 缓存、无限滚动加载
- 🎨 **现代化 UI/UX**: 暗黑/明亮主题、懒加载、搜索自动完成、视频预览
- 📱 **响应式设计**: 移动端优先的设计理念，专用移动播放器
- 🔐 **企业级安全**: JWT 认证、请求限流、IP 黑名单
- 💬 **丰富互动功能**: 评论、评分、弹幕、收藏夹
- 📊 **管理员仪表板**: 功能全面的管理界面和数据分析
- 🌍 **国际化支持**: 多语言支持架构

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
- **弹幕系统**: 实时弹幕评论(B站风格)
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

- **Docker** 和 **Docker Compose** (推荐)
- 或手动安装:
  - Python 3.11+
  - Node.js 18+
  - PostgreSQL 16+
  - Redis 7+
  - pnpm

### 🐳 Docker 部署 (推荐)

```bash
# 克隆仓库
git clone https://github.com/awd2211/next-video-site.git
cd next-video-site

# 使用 Docker Compose 启动所有服务
docker-compose up -d

# 初始化数据库
docker-compose exec backend alembic upgrade head

# 创建管理员账户 (可选)
docker-compose exec backend python scripts/create_admin.py
```

**访问应用:**
- 用户前端: http://localhost:3000
- 管理后台: http://localhost:3001
- API 文档: http://localhost:8000/api/docs

### 🛠️ 手动开发环境搭建

#### 1. 基础设施启动

```bash
# 启动 PostgreSQL、Redis 和 MinIO
make infra-up

# 或手动使用 Docker Compose
docker-compose -f docker-compose.dev.yml up -d
```

#### 2. 后端设置

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
cp .env.example .env
# 编辑 .env 文件配置你的环境

# 运行数据库迁移
alembic upgrade head

# 启动后端服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. 前端设置

```bash
cd frontend

# 安装依赖
pnpm install

# 启动开发服务器
pnpm run dev
```

#### 4. 管理后台设置

```bash
cd admin-frontend

# 安装依赖
pnpm install

# 启动开发服务器
pnpm run dev
```

### 📝 配置说明

在 `backend` 目录下创建 `.env` 文件:

```env
# 数据库配置
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/videosite
DATABASE_URL_SYNC=postgresql://user:password@localhost:5432/videosite

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# MinIO / S3 配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=videos

# 安全配置
SECRET_KEY=你的密钥-生产环境请修改
JWT_SECRET_KEY=你的JWT密钥
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# SMTP 邮件配置 (可选，用于邮件功能)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password
```

---

## 📚 技术文档

### 项目结构

```
video/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/            # API 端点
│   │   ├── admin/          # 管理端点
│   │   ├── models/         # SQLAlchemy 模型
│   │   ├── schemas/        # Pydantic 模式
│   │   ├── utils/          # 工具函数(认证、缓存等)
│   │   └── middleware/     # 自定义中间件
│   ├── alembic/            # 数据库迁移
│   └── tests/              # 单元测试
│
├── frontend/               # 用户前端 React 应用
│   ├── src/
│   │   ├── components/    # 可复用组件
│   │   ├── pages/         # 页面组件
│   │   ├── services/      # API 服务
│   │   ├── contexts/      # React 上下文
│   │   └── hooks/         # 自定义钩子
│   └── public/            # 静态资源
│
├── admin-frontend/        # 管理后台
│   └── src/
│       ├── pages/         # 管理页面
│       └── services/      # 管理 API 服务
│
├── docs/                  # 额外文档
│   ├── features/          # 功能文档
│   ├── guides/            # 开发指南
│   └── api/               # API 文档
│
└── docker-compose.yml     # Docker 编排
```

### 核心文档

- 📖 [开发指南](CLAUDE.md) - 全面的开发文档
- 🎯 [功能展示](FEATURE_SHOWCASE.md) - 所有已实现的功能
- 🔧 [API 文档](http://localhost:8000/api/docs) - 交互式 API 文档
- 📊 [数据库设计](docs/features/video-transcoding/database-schema.md)
- 🚀 [部署指南](docs/guides/quick-start.md)

---

## 🎮 使用示例

### 创建视频上传

```python
# 后端 API 示例
from app.services.video import VideoService

video = await VideoService.create_video(
    title="我的精彩视频",
    description="演示视频",
    file=uploaded_file,
    user_id=current_user.id
)
```

### 获取带筛选的视频列表

```typescript
// 前端示例
import { videoService } from '@/services/videoService'

const videos = await videoService.getVideos({
  page: 1,
  page_size: 20,
  category_id: 5,
  sort_by: 'created_at',
  year: 2024
})
```

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
