# 测试数据生成指南

## 快速开始

### 1. 启动基础设施

```bash
# 启动 PostgreSQL, Redis, MinIO
make infra-up

# 或者
docker-compose -f docker-compose.dev.yml up -d postgres redis minio
```

### 2. 运行数据库迁移

```bash
cd backend
source venv/bin/activate

# 运行迁移
alembic upgrade head
```

### 3. 生成测试数据

```bash
# 确保在 backend 目录，且虚拟环境已激活
cd backend
source venv/bin/activate

# 运行种子数据脚本
python seed_data.py
```

## 生成的数据

脚本会创建以下测试数据：

### 基础数据
- ✅ **8 个分类**: 动作、喜剧、剧情、科幻、恐怖、爱情、动画、纪录片
- ✅ **6 个国家**: 美国、中国、日本、韩国、英国、法国
- ✅ **7 个标签**: 高分、经典、热门、新片、独家、4K、杜比
- ✅ **8 个演员**: 汤姆·克鲁斯、莱昂纳多等知名演员
- ✅ **6 个导演**: 诺兰、斯皮尔伯格等知名导演

### 核心数据
- ✅ **50 个视频**:
  - 随机类型 (电影/剧集/动画/纪录片)
  - 随机评分 (6.0-9.5)
  - 随机观看量 (1K-1M)
  - 25% 精选视频
  - 33% 推荐视频
  - 50% 支持 AV1 编码
  - 每个视频有 1-3 个分类
  - 每个视频有 0-3 个标签
  - 每个视频有 2-5 个演员
  - 每个视频有 1-2 个导演

- ✅ **5 个系列**:
  - 漫威电影宇宙系列
  - 哈利·波特系列
  - 指环王三部曲
  - 星球大战系列
  - DC超级英雄系列
  - 每个系列包含 3-8 个视频

## 数据特点

### 视频数据
```python
{
  "title": "星际穿越 1",
  "slug": "video-1",
  "description": "一部震撼人心的科幻巨作...",
  "video_type": "movie",
  "status": "published",
  "poster_url": "https://picsum.photos/seed/1/400/600",  # 随机图片
  "backdrop_url": "https://picsum.photos/seed/1/1200/675",
  "video_url": "https://test-videos.co.uk/...",  # 测试视频
  "release_year": 2015-2024,  # 随机年份
  "duration": 90-180,  # 分钟
  "average_rating": 6.0-9.5,  # 随机评分
  "view_count": 1000-1000000,  # 随机观看量
  "is_av1_available": true/false,  # 50% 概率
}
```

### 图片来源
- **海报图片**: https://picsum.photos (随机高质量图片)
- **背景图片**: https://picsum.photos (宽屏格式)

### 视频来源
- **测试视频**: Big Buck Bunny (开源测试视频)
- **时长**: 10秒 720p MP4

## 验证数据

### 1. 检查数据库

```bash
# 连接到 PostgreSQL
docker exec -it video_postgres psql -U videosite -d videosite

# 查询视频数量
SELECT COUNT(*) FROM videos;

# 查询系列数量
SELECT COUNT(*) FROM series;

# 查询分类
SELECT * FROM categories;
```

### 2. 测试 API

```bash
# 获取视频列表
curl http://localhost:8000/api/v1/videos?page=1&page_size=10

# 获取热门视频
curl http://localhost:8000/api/v1/videos/trending?page=1&page_size=10

# 获取系列列表
curl http://localhost:8000/api/v1/series?page=1&page_size=10

# 获取分类列表
curl http://localhost:8000/api/v1/categories
```

### 3. 查看前端效果

```bash
# 启动后端
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端（新终端）
cd frontend
pnpm run dev
```

访问 http://localhost:3000 查看效果：
- ✅ 首页应该显示热门视频
- ✅ 分类导航应该有 8 个分类
- ✅ 系列板块应该显示 5 个系列
- ✅ 部分视频卡片应该显示 AV1 徽章

## 清空数据（可选）

如果需要重新生成数据：

```bash
cd backend

# 方法 1: 删除并重建数据库
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d postgres
alembic upgrade head
python seed_data.py

# 方法 2: 手动删除表数据
# 连接数据库后执行：
TRUNCATE videos, categories, tags, actors, directors, countries, series RESTART IDENTITY CASCADE;
```

## 自定义数据量

编辑 `seed_data.py` 中的 `main()` 函数：

```python
# 修改视频数量（默认 50）
videos = await create_videos(
    session,
    categories,
    countries,
    tags,
    actors,
    directors,
    count=100  # 改成 100 个视频
)

# 修改系列数量（默认 5）
series = await create_series(session, videos, count=10)  # 改成 10 个系列
```

## 注意事项

1. **图片显示**: 使用的是 picsum.photos 的随机图片服务，需要网络连接
2. **视频播放**: 测试视频是公开的测试资源，只有 10 秒
3. **数据真实性**: 数据是随机生成的，仅用于前端展示测试
4. **性能**: 50 个视频对于测试来说足够了，如果需要测试大量数据，可以增加到 200+

## 常见问题

### Q: 脚本运行报错 "Table doesn't exist"
**A**: 先运行数据库迁移 `alembic upgrade head`

### Q: 图片不显示
**A**: 检查网络连接，picsum.photos 需要互联网访问

### Q: 视频无法播放
**A**:
1. 检查 video_url 是否可访问
2. 可以替换为本地视频文件路径
3. 或者使用 MinIO 上传真实视频

### Q: 想要更多演员/导演
**A**: 编辑 `seed_data.py` 中的 `ACTORS` 和 `DIRECTORS` 列表

## 下一步

数据生成后，你可以：

1. ✅ 测试首页的无限滚动
2. ✅ 测试视频详情页
3. ✅ 测试搜索功能
4. ✅ 测试分类筛选
5. ✅ 测试系列功能
6. ✅ 查看 AV1 徽章显示
7. ✅ 测试性能优化效果

---

**生成时间**: 2025-10-10
**脚本位置**: `backend/seed_data.py`
