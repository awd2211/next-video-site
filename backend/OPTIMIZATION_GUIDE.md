# 🚀 VideoSite 后端优化工具使用指南

本指南介绍后端架构的各种优化工具和最佳实践。

---

## 📊 **1. 性能监控 (Metrics)**

### 基础用法

```python
from app.utils.metrics import Metrics, MetricsCollector

# 记录API请求
@MetricsCollector.track_api_request("/api/v1/videos", "GET")
async def list_videos(...):
    ...

# 手动记录指标
await Metrics.increment("video_uploads_total")
await Metrics.gauge("active_users", 1250)
await Metrics.histogram("video_processing_time", 45.2)
```

### 查看指标

```bash
# 管理员API
GET /api/v1/admin/metrics
GET /api/v1/admin/metrics/summary

# 示例响应
{
  "database": {
    "pool_size": "20",
    "checked_out": "3",
    "overflow": "0"
  },
  "cache": {
    "hit_rate": "89.5",
    "total_requests": "15234"
  }
}
```

### 集成到现有代码

```python
# app/api/videos.py
from app.utils.metrics import track_video_view

@router.get("/{video_id}")
async def get_video(video_id: int, ...):
    video = await fetch_video(video_id)

    # 记录播放次数
    await track_video_view(video_id)

    return video
```

---

## 🛡️ **2. API 限流 (Rate Limiting)**

### 预设配置

```python
from app.utils.rate_limit import RateLimitPresets

# 严格限流 (5/分钟) - 用于登录、注册
RateLimitPresets.STRICT

# 中等限流 (60/分钟) - 用于搜索
RateLimitPresets.MODERATE

# 宽松限流 (200/分钟) - 用于浏览
RateLimitPresets.RELAXED
```

### 应用限流

```python
from fastapi import Request
from app.utils.rate_limit import limiter, RateLimitPresets

@router.post("/comments")
@limiter.limit(RateLimitPresets.COMMENT)  # 30/分钟
async def create_comment(request: Request, ...):
    ...
```

### IP 黑名单

```python
from app.utils.rate_limit import AutoBanDetector

# 记录失败尝试（自动封禁）
await AutoBanDetector.record_failed_attempt(ip, "login")
# 15分钟内失败10次 → 自动封禁1小时

# 手动管理黑名单
from app.utils.rate_limit import add_to_blacklist, remove_from_blacklist

await add_to_blacklist("192.168.1.100", reason="Spam", duration=3600)
await remove_from_blacklist("192.168.1.100")
```

---

## 🔁 **3. 请求重试 (Retry & Circuit Breaker)**

### 简单重试

```python
from app.utils.retry import retry

@retry(max_attempts=3, delay=1.0, backoff=2.0)
async def fetch_external_data():
    # 可能失败的操作
    return await external_api.fetch()

# 重试时间: 立即 → 1秒 → 2秒 → 失败
```

### 熔断器模式

```python
from app.utils.retry import circuit_breaker

@circuit_breaker(failure_threshold=5, recovery_timeout=60)
async def call_unstable_service():
    # 5次失败后自动熔断60秒
    return await unstable_api.call()
```

### 组合使用

```python
from app.utils.retry import resilient

@resilient(max_attempts=3, circuit_threshold=5)
async def robust_api_call():
    # 既有重试，又有熔断保护
    return await api.fetch()
```

---

## 📦 **4. 批量处理 (Batch Processing)**

### 批量插入（性能提升 10-100倍）

```python
from app.utils.batch_processor import BatchProcessor

# 插入10,000条记录
videos_data = [
    {"title": "Video 1", "slug": "video-1"},
    {"title": "Video 2", "slug": "video-2"},
    # ... 9,998 more
]

count = await BatchProcessor.batch_insert(
    db,
    Video,
    videos_data,
    batch_size=1000
)
# ✅ 比逐条插入快 50-100倍
```

### 批量更新

```python
# 更新观看次数
updates = [
    {"id": 1, "view_count": 150},
    {"id": 2, "view_count": 200},
]

await BatchProcessor.batch_update(db, Video, updates)
```

### 批量增量

```python
# 批量增加观看次数
from app.utils.batch_processor import bulk_increment

video_ids = [1, 2, 3, 4, 5]
await bulk_increment(db, Video, "view_count", video_ids, increment=1)
```

### 分块查询大表

```python
# 处理100万条记录，避免内存溢出
async for chunk in BatchProcessor.chunked_query(db, Video, chunk_size=1000):
    for video in chunk:
        await process_video(video)
    # 每次只加载1000条到内存
```

---

## 🔒 **5. 错误处理安全**

### 清理敏感信息

```python
from app.utils.error_sanitizer import ErrorSanitizer

try:
    # 可能抛出包含敏感信息的异常
    raise Exception("Database error: postgres://user:password123@localhost/db")
except Exception as e:
    # 清理后记录日志
    safe_message = ErrorSanitizer.sanitize(str(e))
    logger.error(safe_message)
    # 输出: "Database error: postgres://***@localhost/db"
```

### 清理字典数据

```python
user_data = {
    "username": "john",
    "password": "secret123",
    "api_key": "sk_live_abc123"
}

safe_data = ErrorSanitizer.sanitize_dict(user_data)
# {
#     "username": "john",
#     "password": "***REDACTED***",
#     "api_key": "***REDACTED***"
# }
```

---

## 📈 **6. 缓存最佳实践**

### 使用装饰器缓存

```python
from app.utils.cache import cache_result

@cache_result(key_prefix="popular_videos", ttl=300)
async def get_popular_videos(limit: int = 10):
    # 缓存5分钟
    return await db.query(Video).order_by(Video.view_count).limit(limit)
```

### 手动缓存控制

```python
from app.utils.cache import Cache

# 设置缓存
await Cache.set("key", value, ttl=3600)

# 获取缓存
value = await Cache.get("key", default=None)

# 删除缓存
await Cache.delete("key")

# 批量删除
await Cache.delete_pattern("videos_list:*")
```

### 缓存失效策略

```python
# 在 CRUD 操作后清理相关缓存
async def create_video(video_data):
    video = Video(**video_data)
    db.add(video)
    await db.commit()

    # 清除相关缓存
    await Cache.delete_pattern("videos_list:*")
    await Cache.delete_pattern("trending_videos:*")

    return video
```

---

## ⚡ **性能优化清单**

### ✅ **数据库查询**

- [ ] 使用 `selectinload` 避免 N+1 查询
- [ ] 为常用查询字段添加索引
- [ ] 使用批量操作代替循环
- [ ] 分页查询大结果集

```python
# ❌ 不好：N+1 查询
videos = await db.query(Video).all()
for video in videos:
    categories = video.categories  # 每次都查询数据库

# ✅ 好：预加载
from sqlalchemy.orm import selectinload

videos = await db.execute(
    select(Video).options(
        selectinload(Video.video_categories).selectinload(VideoCategory.category)
    )
)
```

### ✅ **缓存策略**

- [ ] 热点数据必须缓存
- [ ] 设置合理的 TTL
- [ ] 更新后清理缓存
- [ ] 记录缓存命中率

### ✅ **API 设计**

- [ ] 所有端点添加限流
- [ ] 敏感操作使用严格限流
- [ ] 启用 GZip 压缩
- [ ] 返回适当的HTTP状态码

---

## 🔍 **监控和告警**

### 连接池监控

```bash
# 检查连接池状态
GET /health

{
  "database_pool": {
    "pool_size": 20,
    "checked_out": 3,
    "checked_in": 17,
    "overflow": 0
  },
  "warnings": []  # 使用率 > 80% 时会有警告
}
```

### 慢 API 监控

```python
# app/main.py 已配置
# 响应时间 > 1秒的API会自动记录到日志
```

### 慢查询监控

```python
# app/main.py startup 已配置
# SQL执行时间 > 500ms 会记录到日志
```

---

## 🎯 **快速优化检查表**

### 新增 API 端点时

1. ✅ 添加适当的限流装饰器
2. ✅ 使用 `selectinload` 预加载关联数据
3. ✅ 对热点查询添加缓存
4. ✅ 在更新操作后清理缓存
5. ✅ 添加 metrics 跟踪

### 处理大量数据时

1. ✅ 使用 `BatchProcessor` 批量操作
2. ✅ 使用 `chunked_query` 分块查询
3. ✅ 添加进度日志
4. ✅ 考虑异步任务（Celery）

### 调用外部服务时

1. ✅ 添加重试装饰器
2. ✅ 设置超时时间
3. ✅ 考虑熔断器保护
4. ✅ 记录响应时间

---

## 📚 **更多资源**

- [FastAPI 性能优化](https://fastapi.tiangolo.com/advanced/)
- [SQLAlchemy 性能提示](https://docs.sqlalchemy.org/en/20/faq/performance.html)
- [Redis 最佳实践](https://redis.io/docs/manual/patterns/)

---

## 🆘 **常见问题**

### Q: 限流装饰器不生效？

确保函数参数中有 `request: Request`：

```python
@limiter.limit("5/minute")
async def my_endpoint(request: Request, ...):  # ✅ 必须有 request
    ...
```

### Q: 批量插入报错？

检查数据格式是否为字典列表：

```python
# ❌ 错误
items = [Video(title="A"), Video(title="B")]

# ✅ 正确
items = [{"title": "A"}, {"title": "B"}]
```

### Q: 缓存没有生效？

检查缓存键是否包含所有查询参数：

```python
# 缓存键应该包含所有影响结果的参数
cache_key = f"videos:{page}:{page_size}:{status}:{sort_by}"
```

---

**🎉 恭喜！你现在掌握了所有后端优化工具的使用方法。**
