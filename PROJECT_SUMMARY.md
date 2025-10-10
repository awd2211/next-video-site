# 项目概览

## 📋 项目信息

**项目名称**: VideoSite - 视频流媒体平台
**位置**: `/home/eric/video`
**状态**: ✅ 初始开发完成
**提交数**: 4 个
**源代码文件**: 62+ 个

## 🎯 项目目标

创建一个功能完整的视频流媒体平台，支持：
- 各个国家的电视剧和电影
- 用户端浏览和观看
- 强大的后台管理系统

## 📦 项目结构

```
video/
├── backend/                    # Python FastAPI 后端
│   ├── app/
│   │   ├── models/            # 数据库模型 (8 个文件)
│   │   ├── schemas/           # Pydantic schemas (4 个文件)
│   │   ├── api/               # 用户端 API (5 个文件)
│   │   ├── admin/             # 后台管理 API (7 个文件)
│   │   ├── utils/             # 工具函数
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 数据库连接
│   │   └── main.py            # 应用入口
│   ├── requirements.txt       # Python 依赖
│   ├── Dockerfile
│   └── .env.example           # 环境变量示例
│
├── frontend/                   # React 用户端前端
│   ├── src/
│   │   ├── components/        # 可复用组件 (5 个)
│   │   │   ├── VideoPlayer/   # YouTube 风格播放器
│   │   │   ├── VideoCard/     # 视频卡片
│   │   │   ├── Header/        # 头部导航
│   │   │   ├── Footer/        # 页脚
│   │   │   └── Layout/        # 布局
│   │   ├── pages/             # 页面组件 (7 个)
│   │   ├── services/          # API 服务
│   │   └── types/             # TypeScript 类型定义
│   ├── package.json           # 使用 pnpm
│   └── Dockerfile
│
├── admin-frontend/            # React 后台管理前端
│   ├── src/
│   │   ├── layouts/           # 布局组件
│   │   ├── pages/             # 管理页面 (7+ 个)
│   │   │   ├── Dashboard/     # 数据看板
│   │   │   ├── Videos/        # 视频管理
│   │   │   ├── Users/         # 用户管理
│   │   │   ├── Comments/      # 评论审核
│   │   │   └── Statistics/    # 统计分析
│   │   └── services/          # API 服务
│   ├── package.json           # 使用 pnpm + Ant Design
│   └── Dockerfile
│
├── docker-compose.yml         # 完整服务编排
├── docker-compose.dev.yml     # 开发环境基础设施
├── Makefile                   # 开发命令
├── README.md                  # 完整文档
├── QUICKSTART.md              # 快速启动指南
└── DEV_SETUP.md               # 开发环境设置
```

## 🚀 技术栈

### 后端
- **FastAPI** - 现代异步 Python Web 框架
- **PostgreSQL 16** - 主数据库
- **SQLAlchemy 2.0** - 异步 ORM
- **Alembic** - 数据库迁移
- **Redis** - 缓存
- **JWT** - 身份认证
- **MinIO** - 对象存储
- **Celery** - 异步任务（配置完成，待实现）

### 前端
- **React 18** + **TypeScript**
- **Vite** - 超快构建工具
- **TailwindCSS** - 实用优先的 CSS 框架
- **TanStack Query** - 数据获取和缓存
- **Video.js** - 专业视频播放器
- **React Router** - 路由
- **pnpm** - 包管理器

### 后台管理
- **React 18** + **TypeScript**
- **Ant Design** - 企业级 UI 组件库
- **Ant Design Charts** - 数据可视化
- **Vite**
- **pnpm**

## 📊 数据库设计

### 核心表（20+ 张）

**用户相关**:
- `users` - 普通用户
- `admin_users` - 管理员用户
- `roles` - 角色
- `permissions` - 权限
- `role_permissions` - 角色权限关联

**视频相关**:
- `videos` - 视频主表
- `categories` - 分类
- `countries` - 国家/地区
- `tags` - 标签
- `actors` - 演员
- `directors` - 导演
- `video_categories` - 视频分类关联
- `video_tags` - 视频标签关联
- `video_actors` - 视频演员关联
- `video_directors` - 视频导演关联

**互动相关**:
- `comments` - 评论
- `ratings` - 评分
- `favorites` - 收藏
- `watch_history` - 观看历史

**运营相关**:
- `banners` - 轮播图
- `recommendations` - 推荐位
- `announcements` - 公告
- `reports` - 举报

**系统相关**:
- `operation_logs` - 操作日志

## ✨ 核心功能

### 用户端功能
✅ 视频浏览（分页、筛选、排序）
✅ 高级搜索
✅ 类似 YouTube 的视频播放器
  - 键盘快捷键支持
  - 播放速度控制
  - 全屏/画中画
  - 进度条预览
✅ 用户认证（注册、登录、JWT）
✅ 多级分类和标签
✅ 评分和评论系统
✅ 收藏和观看历史
✅ 多国家/地区支持
✅ 响应式设计

### 后台管理功能
✅ **数据统计看板**
  - 总用户数、视频数、评论数、观看数
  - 实时统计

✅ **视频管理**
  - 完整的 CRUD 操作
  - 批量操作支持
  - 状态管理（草稿/发布/归档）
  - 高级筛选和搜索
  - 分类、标签、演员、导演关联

✅ **用户管理**
  - 用户列表查看
  - 用户详情
  - 封禁/解封

✅ **内容审核**
  - 评论审核（待审核/通过/拒绝）
  - 举报处理

✅ **运营工具**
  - 轮播图管理
  - 推荐位管理
  - 公告管理

✅ **操作日志**
  - 完整的操作记录
  - 审计追踪

✅ **权限管理**
  - 基于角色的访问控制（RBAC）
  - 细粒度权限

## 🔌 API 端点

### 用户端 API (`/api/v1`)

**认证**:
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `POST /auth/refresh` - 刷新 token
- `GET /auth/me` - 获取当前用户

**视频**:
- `GET /videos` - 视频列表（支持分页、筛选、排序）
- `GET /videos/{id}` - 视频详情
- `GET /videos/trending` - 热门视频

**搜索**:
- `GET /search?q={query}` - 搜索视频

**分类**:
- `GET /categories` - 获取所有分类

**用户**:
- `GET /users/me` - 个人信息
- `PUT /users/me` - 更新个人信息

### 后台管理 API (`/api/v1/admin`)

**视频管理**:
- `GET /admin/videos` - 获取所有视频
- `POST /admin/videos` - 创建视频
- `GET /admin/videos/{id}` - 视频详情
- `PUT /admin/videos/{id}` - 更新视频
- `DELETE /admin/videos/{id}` - 删除视频
- `PUT /admin/videos/{id}/status` - 更新状态

**用户管理**:
- `GET /admin/users` - 用户列表
- `PUT /admin/users/{id}/ban` - 封禁用户

**评论审核**:
- `GET /admin/comments/pending` - 待审核评论
- `PUT /admin/comments/{id}/approve` - 通过评论

**统计数据**:
- `GET /admin/stats/overview` - 总览统计

**日志**:
- `GET /admin/logs/operations` - 操作日志

## 🎮 视频播放器功能

基于 Video.js 的专业播放器，提供类似 YouTube 的体验：

### 键盘快捷键
- **空格/K** - 播放/暂停
- **← →** - 后退/前进 5 秒
- **↑ ↓** - 增加/减少音量
- **F** - 全屏
- **M** - 静音
- **0-9** - 跳转到视频百分比

### 播放器特性
- 自适应视频质量
- 播放速度控制（0.25x - 2x）
- 画中画模式
- 字幕支持
- 音量控制
- 全屏模式
- 进度条

## 🐳 Docker 支持

### docker-compose.yml（完整部署）
包含所有服务：
- PostgreSQL
- Redis
- MinIO
- Backend API
- Frontend
- Admin Frontend

### docker-compose.dev.yml（开发环境）
仅包含基础设施：
- PostgreSQL
- Redis
- MinIO

适合本地开发时使用。

## 📝 快速开始

### 方式 1: 使用 Docker（完整部署）

```bash
# 配置环境变量
cp backend/.env.example backend/.env

# 启动所有服务
docker-compose up -d

# 初始化数据库
docker-compose exec backend alembic upgrade head

# 访问
# 用户端: http://localhost:3000
# 后台: http://localhost:3001
# API: http://localhost:8000/api/docs
```

### 方式 2: 本地开发（推荐）

```bash
# 1. 启动基础设施
make infra-up

# 2. 安装依赖
make all-install

# 3. 初始化数据库
make db-init

# 4. 在 3 个终端分别运行
make backend-run    # 终端 1
make frontend-run   # 终端 2
make admin-run      # 终端 3
```

详见：
- [QUICKSTART.md](QUICKSTART.md) - 快速启动
- [DEV_SETUP.md](DEV_SETUP.md) - 开发环境详细设置

## 📚 文档

- **README.md** - 完整项目文档
- **QUICKSTART.md** - 快速启动指南
- **DEV_SETUP.md** - 开发环境设置
- **PROJECT_SUMMARY.md** - 本文档（项目概览）

API 文档自动生成，访问: http://localhost:8000/api/docs

## 🔐 默认账号

### 管理员（需手动创建）
```bash
make backend-run
# 然后参考 DEV_SETUP.md 创建管理员
```

默认账号：
- 用户名: `admin`
- 密码: `admin123`

## 📈 项目统计

- **总文件数**: 70+ 个
- **代码文件**: 62+ 个
- **Python 文件**: 20+ 个
- **TypeScript/React 文件**: 40+ 个
- **数据库表**: 20+ 张
- **API 端点**: 30+ 个

## ⚡ 性能优化

### 已实现
- FastAPI 异步处理
- PostgreSQL 连接池
- Redis 缓存
- 前端代码分割
- Vite HMR（热模块替换）

### 待实现
- Elasticsearch 全文搜索
- CDN 静态资源加速
- 视频转码和多清晰度
- 数据库查询优化
- API 限流

## 🚧 待实现功能

基础已完成，以下是可扩展的功能：

- [ ] 视频转码和多清晰度支持
- [ ] Elasticsearch 全文搜索
- [ ] 实时弹幕系统
- [ ] VIP 会员系统
- [ ] 支付集成
- [ ] 社交分享
- [ ] 移动端 App
- [ ] 推荐算法
- [ ] 多语言支持（i18n）
- [ ] 视频上传功能
- [ ] 完整的评论功能
- [ ] 个人中心功能
- [ ] 通知系统
- [ ] 数据分析和报表

## 🎓 学习资源

- FastAPI 文档: https://fastapi.tiangolo.com
- React 文档: https://react.dev
- Ant Design: https://ant.design
- Video.js: https://videojs.com
- PostgreSQL: https://www.postgresql.org/docs

## 🤝 贡献

项目代码已提交到本地 Git 仓库。

要推送到远程仓库：
```bash
git remote add origin <你的仓库URL>
git push -u origin master
```

## 📄 许可证

MIT License

---

**项目创建时间**: 2024-10-09
**当前版本**: 1.0.0
**状态**: 开发完成，可以开始使用和扩展

🤖 Generated with [Claude Code](https://claude.com/claude-code)
