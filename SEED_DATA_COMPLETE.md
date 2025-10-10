# 测试数据生成完成 ✅

## 执行时间
2025-10-10 18:13:37

## 生成的数据统计

| 数据类型 | 数量 | 说明 |
|---------|------|------|
| 视频 (Videos) | 50 | 包含电影、剧集、动画、纪录片等多种类型 |
| 系列 (Series) | 5 | 漫威、哈利波特、指环王、星球大战、DC |
| 分类 (Categories) | 8 | 动作、喜剧、剧情、科幻、恐怖、爱情、动画、纪录片 |
| 国家 (Countries) | 6 | 美国、中国、日本、韩国、英国、法国 |
| 标签 (Tags) | 7 | 高分、经典、热门、新片、独家、4K、杜比 |
| 演员 (Actors) | 8 | 汤姆·克鲁斯、莱昂纳多等知名演员 |
| 导演 (Directors) | 6 | 诺兰、斯皮尔伯格、张艺谋、宫崎骏等 |

## 视频数据特征

### 随机生成的数据范围
- **评分 (Rating)**: 6.0 - 9.5 分
- **观看次数 (View Count)**: 1,000 - 1,000,000
- **点赞数 (Like Count)**: 100 - 50,000
- **收藏数 (Favorite Count)**: 50 - 20,000
- **评论数 (Comment Count)**: 10 - 5,000
- **时长 (Duration)**: 90 - 180 分钟
- **发布年份 (Release Year)**: 2015 - 2024

### 特殊标记
- **50%** 的视频标记为 **AV1 编码可用** (`is_av1_available: true`)
- **25%** 的视频标记为 **推荐内容** (`is_featured: true`)
- **33%** 的视频标记为 **精选推荐** (`is_recommended: true`)

### 视频类型分布
- 电影 (MOVIE)
- 电视剧 (TV_SERIES)
- 动画 (ANIME)
- 纪录片 (DOCUMENTARY)

### 关联数据
- 每个视频关联 **1-3 个分类**
- 每个视频关联 **0-3 个标签**
- 每个视频关联 **2-5 个演员**（带角色名：主角/配角/客串/特邀出演）
- 每个视频关联 **1-2 个导演**

## 系列数据特征

### 创建的系列
1. **漫威电影宇宙系列** - 3 集 (featured)
2. **哈利·波特系列** - 5 集 (featured)
3. **指环王三部曲** - 8 集
4. **星球大战系列** - 6 集
5. **DC超级英雄系列** - 7 集

每个系列包含 3-8 部相关视频，按集数排序。

## 图片资源

所有图片使用 [picsum.photos](https://picsum.photos) 提供的占位图：
- **海报 (Poster)**: 400×600
- **背景图 (Backdrop)**: 1200×675
- **系列封面 (Cover)**: 800×450

URL格式：`https://picsum.photos/seed/{id}/{width}/{height}`

## API 验证

### 测试视频列表 API
```bash
curl 'http://localhost:8000/api/v1/videos/trending?page=1&page_size=5'
```

响应包含：
- ✅ `total`: 50
- ✅ `page`: 1
- ✅ `page_size`: 5
- ✅ `pages`: 10
- ✅ `items[]`: 视频列表
  - ✅ `is_av1_available`: true/false

### 测试系列列表 API
```bash
curl 'http://localhost:8000/api/v1/series?page=1&page_size=5'
```

响应包含：
- ✅ `total`: 5
- ✅ `pages`: 1
- ✅ `items[]`: 系列列表
  - ✅ `total_episodes`: 集数
  - ✅ `video_count`: 视频数量

## 数据库查询验证

### 查看视频数据
```sql
SELECT id, title, video_type, is_av1_available, view_count, average_rating
FROM videos
LIMIT 10;
```

### 查看系列数据
```sql
SELECT s.id, s.title, s.total_episodes, COUNT(sv.video_id) as actual_videos
FROM series s
LEFT JOIN series_videos sv ON s.id = sv.series_id
GROUP BY s.id, s.title, s.total_episodes;
```

## 前端测试建议

1. **主页视频列表**
   - 检查 AV1 徽章显示（绿色-蓝色渐变）
   - 验证评分和观看次数显示
   - 测试无限滚动加载

2. **视频详情页**
   - 检查视频元数据（时长、年份、评分）
   - 验证演员和导演列表
   - 测试分类和标签显示

3. **系列页面**
   - 检查系列封面图
   - 验证集数显示
   - 测试视频列表

4. **搜索和筛选**
   - 按分类筛选
   - 按国家筛选
   - 按标签筛选
   - 全文搜索视频标题

## 清除测试数据

如需重新生成数据，运行：
```bash
cd backend
source venv/bin/activate
python seed_data.py
```

脚本会自动清除现有数据并重新生成。

## 注意事项

⚠️ **这是测试数据**，包含：
- 占位图片（非真实海报）
- 随机生成的数据（评分、观看次数等）
- 测试视频 URL（Big Buck Bunny 样本）
- 中文和英文混合的数据

生产环境中应使用真实的视频资源和元数据。

---

**生成工具**: `backend/seed_data.py`
**文档更新**: 2025-10-10 18:14
