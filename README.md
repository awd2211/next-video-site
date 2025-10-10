# VideoSite - 视频流媒体平台

一个功能完整的视频流媒体平台，支持各个国家的电视剧和电影。包含用户端和强大的后台管理系统。

## 技术栈

### 后端
- **FastAPI** - 现代化的 Python Web 框架
- **PostgreSQL** - 主数据库
- **SQLAlchemy** - ORM
- **Redis** - 缓存和会话管理
- **JWT** - 身份认证
- **MinIO** - 对象存储
- **Celery** - 异步任务队列

### 前端（用户端）
- **React 18** + **TypeScript**
- **Vite** - 构建工具
- **TailwindCSS** - 样式框架
- **TanStack Query** - 数据获取和缓存
- **Video.js** - 类似 YouTube 的视频播放器
- **React Router** - 路由管理

### 前端（后台管理）
- **React 18** + **TypeScript**
- **Ant Design** - UI 组件库
- **Ant Design Charts** - 数据可视化
- **Vite** - 构建工具

## 📖 完整技术文档

> **新增**: 专业的技术文档已迁移到 [`docs/`](./docs/) 目录

**快速链接**:
- [📚 文档索引](./docs/README.md) - 查看所有文档
- [🎬 视频转码系统](./docs/features/video-transcoding/) - 2K/4K + 并行转码 + GPU加速
- [🆕 视频悬停预览](./docs/features/video-transcoding/hover-preview.md) - YouTube/Netflix风格预览
- [🛠️ 开发环境配置](./docs/guides/dev-setup.md) - 快速搭建开发环境
- [📊 开发进度](./docs/status/progress.md) - 当前95%完成度

---

## 核心功能

### 用户端功能
- ✅ 视频浏览和搜索 (5维度高级搜索)
- ✅ 类似 YouTube 的视频播放器（支持键盘快捷键）
- ✅ **视频悬停预览** - 🆕 鼠标hover自动播放预览
- ✅ 智能推荐系统 (协同过滤 + 内容过滤)
- ✅ 用户注册和登录
- ✅ 视频分类和标签
- ✅ 评分和评论系统
- ✅ 收藏和观看历史
- ✅ 多国家/地区内容支持
- ✅ 响应式设计

### 后台管理功能
- ✅ 数据统计看板
- ✅ 视频管理（CRUD、批量操作）
- ✅ **视频转码系统** - 🆕 支持2K/4K + 并行转码 + GPU加速
- ✅ 用户管理（查看、封禁）
- ✅ 评论审核
- ✅ 内容分类管理
- ✅ 演员/导演管理
- ✅ 运营工具（轮播图、推荐位、公告）
- ✅ 操作日志
- ✅ 权限管理（RBAC）

## 项目结构

```
video/
├── backend/                    # Python 后端
│   ├── app/
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── api/               # 用户端 API
│   │   ├── admin/             # 后台管理 API
│   │   ├── utils/             # 工具函数
│   │   ├── config.py          # 配置
│   │   ├── database.py        # 数据库连接
│   │   └── main.py            # 应用入口
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/                   # React 用户端
│   ├── src/
│   │   ├── components/        # 组件
│   │   │   ├── VideoPlayer/   # 视频播放器
│   │   │   ├── VideoCard/     # 视频卡片
│   │   │   ├── Header/        # 头部
│   │   │   └── Footer/        # 底部
│   │   ├── pages/             # 页面
│   │   ├── services/          # API 服务
│   │   └── types/             # TypeScript 类型
│   ├── package.json
│   └── Dockerfile
│
├── admin-frontend/            # React 后台管理
│   ├── src/
│   │   ├── layouts/           # 布局
│   │   ├── pages/             # 页面
│   │   └── services/          # API 服务
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml         # Docker 编排
└── README.md
```

## 快速开始

### 使用 Docker（推荐）

1. **克隆项目并进入目录**
```bash
cd /home/eric/video
```

2. **创建环境变量文件**
```bash
cp backend/.env.example backend/.env
# 编辑 backend/.env 根据需要修改配置
```

3. **启动所有服务**
```bash
docker-compose up -d
```

4. **运行数据库迁移**
```bash
docker-compose exec backend alembic upgrade head
```

5. **访问应用**
- 用户端: http://localhost:3000
- 后台管理: http://localhost:3001
- API 文档: http://localhost:8000/api/docs
- MinIO 控制台: http://localhost:9001

### 手动安装

#### 后端设置

1. **创建虚拟环境**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\\Scripts\\activate  # Windows
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件
```

4. **设置数据库**
```bash
# 确保 PostgreSQL 正在运行
alembic upgrade head
```

5. **启动后端**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端设置（用户端）

1. **安装依赖（使用 pnpm）**
```bash
cd frontend
pnpm install
```

2. **启动开发服务器**
```bash
pnpm run dev
```

访问: http://localhost:3000

#### 后台管理前端设置

1. **安装依赖（使用 pnpm）**
```bash
cd admin-frontend
pnpm install
```

2. **启动开发服务器**
```bash
pnpm run dev
```

访问: http://localhost:3001

## 视频播放器功能

播放器基于 Video.js，提供类似 YouTube 的体验：

### 键盘快捷键
- **空格/K** - 播放/暂停
- **← →** - 后退/前进 5 秒
- **↑ ↓** - 增加/减少音量
- **F** - 全屏
- **M** - 静音
- **0-9** - 跳转到视频的特定百分比

### 播放器特性
- 自适应视频质量
- 播放速度控制（0.25x - 2x）
- 画中画模式
- 字幕支持
- 进度条预览
- 音量控制
- 全屏模式

## 数据库模型

主要数据表：
- **users** - 用户表
- **admin_users** - 管理员用户
- **videos** - 视频表
- **categories** - 分类表
- **countries** - 国家/地区
- **actors/directors** - 演员/导演
- **comments** - 评论
- **ratings** - 评分
- **favorites** - 收藏
- **watch_history** - 观看历史
- **roles/permissions** - 角色权限
- **operation_logs** - 操作日志
- **banners** - 轮播图
- **recommendations** - 推荐位
- **announcements** - 公告

## API 端点

### 用户端 API (`/api/v1`)

#### 认证
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `POST /auth/refresh` - 刷新 token
- `GET /auth/me` - 获取当前用户信息

#### 视频
- `GET /videos` - 获取视频列表
- `GET /videos/{id}` - 获取视频详情
- `GET /videos/trending` - 热门视频
- `GET /search` - 搜索视频

#### 分类
- `GET /categories` - 获取所有分类

#### 用户
- `GET /users/me` - 获取个人信息
- `PUT /users/me` - 更新个人信息

### 后台管理 API (`/api/v1/admin`)

#### 视频管理
- `GET /admin/videos` - 获取所有视频
- `POST /admin/videos` - 创建视频
- `GET /admin/videos/{id}` - 获取视频详情
- `PUT /admin/videos/{id}` - 更新视频
- `DELETE /admin/videos/{id}` - 删除视频
- `PUT /admin/videos/{id}/status` - 更新视频状态

#### 用户管理
- `GET /admin/users` - 获取所有用户
- `PUT /admin/users/{id}/ban` - 封禁用户

#### 评论审核
- `GET /admin/comments/pending` - 待审核评论
- `PUT /admin/comments/{id}/approve` - 通过评论
- `PUT /admin/comments/{id}/reject` - 拒绝评论

#### 统计数据
- `GET /admin/stats/overview` - 总览统计

#### 日志
- `GET /admin/logs/operations` - 操作日志

## 环境变量说明

参考 `backend/.env.example`:

```env
# Application
APP_NAME=VideoSite
DEBUG=True
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/videosite
DATABASE_URL_SYNC=postgresql://user:pass@localhost:5432/videosite

# Redis
REDIS_URL=redis://localhost:6379/0

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

## 部署

### 生产环境部署建议

1. **使用环境变量管理敏感信息**
2. **配置 Nginx 作为反向代理**
3. **启用 HTTPS (Let's Encrypt)**
4. **使用专业的对象存储（AWS S3/阿里云 OSS）**
5. **配置 CDN 加速视频分发**
6. **设置数据库备份策略**
7. **启用日志监控和告警**

### 性能优化

- 使用 Redis 缓存热门数据
- 视频使用 CDN 分发
- 数据库查询优化和索引
- 异步任务处理（视频转码、统计计算）
- 前端资源压缩和懒加载

## 待实现功能

- [ ] 视频转码和多清晰度支持
- [ ] Elasticsearch 全文搜索
- [ ] 实时弹幕系统
- [ ] VIP 会员系统
- [ ] 支付集成
- [ ] 社交分享功能
- [ ] 移动端 App
- [ ] 推荐算法优化
- [ ] 多语言支持（i18n）

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 作者

VideoSite Team

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
