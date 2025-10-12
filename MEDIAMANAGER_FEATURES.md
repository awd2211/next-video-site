# MediaManager 完整功能文档

## 📋 概述

MediaManager 是一个功能完整的企业级文件管理系统，采用 FastAPI + React + MinIO 技术栈，提供类似 Mega.io 的专业文件管理体验。

## 🎯 核心特性

### 1. 文件管理系统

#### 1.1 树形文件夹结构
- **无限层级嵌套**：支持任意深度的文件夹层级
- **路径管理**：自动维护完整路径信息
- **父子关系**：SQLAlchemy 自引用关系
- **面包屑导航**：完整路径显示和快速跳转

#### 1.2 文件操作
- **上传**
  - 分块上传（5MB/块）
  - 断点续传支持
  - 进度追踪
  - 拖拽上传
  - 批量上传
  
- **下载**
  - 单文件下载
  - **批量下载（服务器端ZIP生成）** ⭐
  - 分享链接下载
  - 进度显示

- **复制** ⭐
  - 单个文件复制
  - 批量复制
  - **递归文件夹复制**
  - MinIO 物理文件复制
  - 自动重命名（"副本"、"副本2"...）

- **移动**
  - 单个移动
  - 批量移动
  - 文件夹移动
  - 跨文件夹移动

- **删除**
  - 软删除机制
  - 批量删除
  - 文件夹递归删除
  - 回收站恢复

- **重命名**
  - 即时重命名
  - 冲突检测
  - 自动建议

### 2. 回收站系统 ⭐

#### 功能特性
- **软删除**：删除文件不立即物理删除
- **批量恢复**：一键恢复多个文件
- **永久删除**：从 MinIO 彻底删除文件
- **清空回收站**：批量永久删除所有项目
- **数量统计**：实时显示回收站文件数量
- **搜索筛选**：在回收站中搜索文件

#### API 端点
```
GET    /admin/media/deleted                 # 获取已删除文件列表
POST   /admin/media/batch/restore           # 批量恢复
DELETE /admin/media/batch/delete            # 永久删除
DELETE /admin/media/recycle-bin/clear       # 清空回收站
GET    /admin/media/recycle-bin/count       # 获取数量
```

### 3. 文件分享系统 ⭐⭐

#### 管理员功能
- **文件分享**：生成分享链接
- **文件夹分享** ⭐：分享整个文件夹
- **密码保护**：设置访问密码（bcrypt 加密）
- **过期时间**：设置链接有效期
- **访问限制**：
  - 最大访问次数
  - 最大下载次数
  - 允许/禁止下载
- **分享管理**：
  - 查看所有分享
  - 启用/禁用分享
  - 编辑分享设置
  - 删除分享链接
  - 查看统计数据

#### 公开访问 API（无需认证）⭐
```
GET /api/v1/share/{code}                    # 获取分享信息
GET /api/v1/share/{code}/folder-contents    # 浏览文件夹内容
GET /api/v1/share/{code}/download           # 下载文件
```

#### 特性
- 8 字符随机分享码
- 密码验证（bcrypt）
- 访问计数追踪
- 下载计数追踪
- 自动过期检查
- 访问限制检查

### 4. 版本历史系统 ⭐⭐

#### 核心功能
- **版本追踪**：自动记录每次文件更新
- **版本号管理**：自动递增版本号（v1, v2, v3...）
- **完整元数据**：保存文件所有属性
- **变更记录**：记录每次修改的说明
- **版本恢复**：一键回滚到任意历史版本
- **版本删除**：删除不需要的历史版本

#### API 端点
```
GET    /admin/media/{id}/versions                    # 查看版本列表
POST   /admin/media/{id}/versions                    # 上传新版本
POST   /admin/media/{id}/versions/{vid}/restore      # 恢复到指定版本
DELETE /admin/media/{id}/versions/{vid}              # 删除版本
```

#### 工作流程
1. **上传新版本**：当前文件变为 v1，新文件成为当前版本
2. **恢复版本**：当前版本保存为新版本，选中版本成为当前版本
3. **删除版本**：从数据库和 MinIO 删除历史版本

#### 版本信息
- 版本号
- 文件路径
- 文件大小
- MIME 类型
- 图片/视频属性（宽度、高度、时长）
- 变更说明
- 创建者
- 创建时间

### 5. 标签管理系统 ⭐

#### 功能
- **批量打标签**：为多个文件添加标签
- **标签建议**：智能推荐常用标签
- **标签搜索**：按标签筛选文件
- **标签编辑**：修改文件标签
- **标签统计**：查看标签使用情况

### 6. 搜索与筛选

#### 搜索功能
- 全文搜索（标题、文件名）
- 搜索历史（localStorage，最多 10 条）
- 搜索建议（模糊匹配）
- 实时搜索

#### 高级筛选
- 按媒体类型筛选（图片/视频）
- 按文件大小筛选
- 按上传时间筛选
- 按标签筛选
- 组合筛选

### 7. 批量操作

支持的批量操作：
- ✅ 批量移动
- ✅ 批量删除
- ✅ 批量下载（ZIP）
- ✅ 批量标签
- ✅ 批量复制 ⭐
- ✅ 批量恢复（从回收站）

### 8. 存储管理

#### MinIO 集成
- 对象存储
- 文件上传/下载
- 文件复制
- 文件删除
- 预签名 URL
- 文件存在性检查

#### 存储统计
- 总存储空间
- 已使用空间
- 文件数量统计
- 文件类型分布

## 🔧 技术实现

### 后端技术栈
- **框架**：FastAPI（异步）
- **数据库**：PostgreSQL + SQLAlchemy 2.0（异步）
- **对象存储**：MinIO
- **缓存**：Redis
- **认证**：JWT + bcrypt
- **迁移**：Alembic

### 前端技术栈
- **框架**：React 18 + TypeScript
- **UI 库**：Ant Design
- **状态管理**：React Hooks
- **路由**：React Router
- **HTTP 客户端**：Axios
- **国际化**：i18next

### 数据库模型

#### Media（媒体文件）
```python
- id: 主键
- title: 标题
- filename: 文件名
- file_path: MinIO 路径
- file_size: 文件大小
- mime_type: MIME 类型
- media_type: 媒体类型（image/video）
- status: 状态
- url: 访问 URL
- parent_id: 父文件夹 ID
- is_folder: 是否为文件夹
- path: 完整路径
- tags: 标签
- is_deleted: 软删除标记
- deleted_at: 删除时间
```

#### MediaShare（分享链接）
```python
- id: 主键
- media_id: 媒体文件 ID
- share_code: 分享码（8 字符）
- password: 访问密码（哈希）
- allow_download: 允许下载
- max_downloads: 最大下载次数
- download_count: 已下载次数
- max_views: 最大访问次数
- view_count: 已访问次数
- expires_at: 过期时间
- is_active: 是否启用
- created_by: 创建者
- note: 备注
```

#### MediaVersion（版本历史）
```python
- id: 主键
- media_id: 媒体文件 ID
- version_number: 版本号
- file_path: MinIO 路径
- file_size: 文件大小
- mime_type: MIME 类型
- url: 访问 URL
- width/height/duration: 媒体属性
- change_note: 变更说明
- created_by: 创建者
- created_at: 创建时间
```

#### UploadSession（上传会话）
```python
- id: 主键
- upload_id: 上传 ID（UUID）
- filename: 文件名
- file_size: 文件大小
- mime_type: MIME 类型
- chunk_size: 分块大小
- total_chunks: 总块数
- uploaded_chunks: 已上传块数
- temp_dir: 临时目录
- parent_id: 父文件夹 ID
- is_completed: 是否完成
- is_merged: 是否已合并
- expires_at: 过期时间
```

## 📊 API 统计

### 管理员 API（需要认证）

#### 媒体管理（18+ 端点）
```
GET    /admin/media                        # 文件列表
POST   /admin/media/folder                 # 创建文件夹
GET    /admin/media/tree                   # 文件夹树
GET    /admin/media/{id}                   # 文件详情
PUT    /admin/media/{id}                   # 更新文件
DELETE /admin/media/{id}                   # 删除文件
...
```

#### 批量操作（8 端点）
```
POST   /admin/media/batch/move             # 批量移动
DELETE /admin/media/batch/delete           # 批量删除
POST   /admin/media/batch/download         # 批量下载（ZIP）
POST   /admin/media/batch/tags             # 批量标签
POST   /admin/media/batch/copy             # 批量复制 ⭐
POST   /admin/media/batch/restore          # 批量恢复
```

#### 上传管理（6 端点）
```
POST   /admin/media/upload/init            # 初始化上传
POST   /admin/media/upload/chunk           # 上传分块
POST   /admin/media/upload/complete        # 完成上传
GET    /admin/media/upload/status/{id}     # 查询状态
```

#### 分享管理（5 端点）
```
POST   /admin/media/{id}/share             # 创建分享
GET    /admin/media/shares                 # 分享列表
GET    /admin/media/{id}/shares            # 文件的分享
PUT    /admin/media/shares/{id}            # 更新分享
DELETE /admin/media/shares/{id}            # 删除分享
```

#### 版本管理（4 端点）⭐
```
GET    /admin/media/{id}/versions          # 版本列表
POST   /admin/media/{id}/versions          # 上传新版本
POST   /admin/media/{id}/versions/{vid}/restore  # 恢复版本
DELETE /admin/media/{id}/versions/{vid}    # 删除版本
```

#### 回收站（5 端点）
```
GET    /admin/media/deleted                # 已删除列表
POST   /admin/media/batch/restore          # 批量恢复
DELETE /admin/media/batch/delete           # 永久删除
DELETE /admin/media/recycle-bin/clear      # 清空回收站
GET    /admin/media/recycle-bin/count      # 数量统计
```

### 公开 API（无需认证）

#### 分享访问（3 端点）⭐
```
GET    /api/v1/share/{code}                # 分享信息
GET    /api/v1/share/{code}/folder-contents # 文件夹内容
GET    /api/v1/share/{code}/download       # 下载文件
```

### 总计
- **管理员 API**：46+ 端点
- **公开 API**：3 端点
- **总计**：49+ 端点

## 🎯 功能对比

| 功能 | Mega.io | MediaManager | 备注 |
|------|---------|--------------|------|
| 文件夹树形结构 | ✅ | ✅ | 无限层级 |
| 拖拽上传 | ✅ | ✅ | 支持 |
| 分块上传 | ✅ | ✅ | 5MB/块 |
| 断点续传 | ✅ | ✅ | 支持 |
| 批量操作 | ✅ | ✅ | 8 种操作 |
| 回收站 | ✅ | ✅ | 完整功能 |
| 文件分享 | ✅ | ✅ | 支持 |
| 文件夹分享 | ✅ | ✅ | 支持 |
| 密码保护 | ✅ | ✅ | bcrypt |
| 过期时间 | ✅ | ✅ | 支持 |
| 访问限制 | ✅ | ✅ | 次数限制 |
| 文件复制 | ✅ | ✅ | 递归复制 |
| 版本历史 | ✅ | ✅ | 完整实现 |
| **标签管理** | ❌ | ✅ | **MediaManager 优势** ⭐ |
| **服务器端 ZIP** | ❌ | ✅ | **MediaManager 优势** ⭐ |
| **变更记录** | ❌ | ✅ | **MediaManager 优势** ⭐ |
| **公开 API** | 部分 | ✅ | **MediaManager 优势** ⭐ |
| **批量复制** | ✅ | ✅ | 递归支持 |

## 🔒 安全特性

### 认证与授权
- JWT 令牌认证
- 管理员权限验证
- 角色权限管理
- 会话管理

### 数据安全
- 密码 bcrypt 加密
- 分享链接密码保护
- 软删除防止误删
- 操作日志记录

### 访问控制
- 文件访问权限
- 分享链接访问控制
- 下载次数限制
- 访问次数限制

## 🚀 性能优化

### 后端优化
- 异步 I/O（AsyncIO）
- 数据库连接池（20+40）
- Redis 缓存
- 批量查询优化
- 服务器端处理（ZIP、复制）

### 前端优化
- 懒加载
- 虚拟滚动
- 分页加载
- 本地缓存
- 防抖节流

### 存储优化
- MinIO 对象存储
- 分块上传
- 增量复制
- 版本去重（未来）

## 📈 使用场景

### 企业文件管理
- 团队协作
- 文件共享
- 版本控制
- 权限管理

### 内容管理系统
- 媒体资源库
- 素材管理
- 版本追踪
- 分享发布

### 个人云盘
- 文件备份
- 在线访问
- 分享链接
- 版本保存

## 🎓 开发指南

### 环境要求
- Python 3.10+
- Node.js 16+
- PostgreSQL 13+
- Redis 6+
- MinIO

### 安装部署
```bash
# 后端
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# 前端
cd admin-frontend
pnpm install
pnpm run dev
```

### 配置文件
```env
# backend/.env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
REDIS_URL=redis://localhost:6379/0
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

## 📚 API 文档

访问 Swagger UI 查看完整 API 文档：
```
http://localhost:8000/api/docs
```

## 🎉 总结

MediaManager 是一个功能完整、生产级别的文件管理系统，具有以下特点：

### 核心优势
1. ✅ **功能完整**：覆盖文件管理所有核心功能
2. ✅ **版本控制**：完整的文件版本历史系统
3. ✅ **分享系统**：强大的文件/文件夹分享功能
4. ✅ **标签管理**：灵活的文件标签系统
5. ✅ **批量操作**：高效的批量处理能力
6. ✅ **回收站**：安全的软删除机制
7. ✅ **服务器端处理**：优化的大文件处理
8. ✅ **RESTful API**：完善的 API 设计
9. ✅ **企业级安全**：多层安全保障

### 技术亮点
- 异步架构（FastAPI + AsyncIO）
- 类型安全（TypeScript + Pydantic）
- 模块化设计
- 完整的测试覆盖
- 详细的 API 文档
- 数据库迁移管理

**MediaManager 不仅达到了 Mega.io 的水平，在某些方面还超越了它！** 🚀
