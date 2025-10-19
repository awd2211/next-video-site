# 🚀 VideoSite Performance Tools - Quick Reference

一页纸快速参考手册 - 所有优化工具的常用命令

---

## 📊 性能测试

```bash
# 快速测试
python scripts/performance_test.py

# 测试特定端点
python scripts/performance_test.py --endpoint /api/v1/videos --concurrent 50 --total 200

# 生产环境测试
python scripts/performance_test.py --base-url https://api.prod.com
```

**输出**: 成功率、吞吐量、响应时间（P50/P95/P99）

---

## 🔍 系统诊断

```bash
# 完整健康检查
python scripts/diagnose.py

# 特定组件检查
python scripts/diagnose.py --check database

# 详细模式
python scripts/diagnose.py --verbose
```

**退出码**: 0=成功, 1=有问题

---

## ✅ 代码质量检查

```bash
# 检查整个项目
python scripts/check_optimization.py

# 检查特定目录
python scripts/check_optimization.py --path app/api
```

**检查项**: 限流、缓存、N+1查询、批处理、错误处理

---

## 🗄️ 索引优化

```bash
# 分析索引
python scripts/suggest_indexes.py

# 包含代码查询分析
python scripts/suggest_indexes.py --analyze-queries

# 生成SQL文件
python scripts/suggest_indexes.py --generate-sql
# 输出: scripts/suggested_indexes.sql
```

**应用索引**:
```bash
# 审查
cat scripts/suggested_indexes.sql

# 测试（开发环境）
psql -h localhost -p 5434 -U videosite -d videosite -f scripts/suggested_indexes.sql

# 生产（创建迁移）
alembic revision -m "add_indexes"
# 编辑迁移文件，复制SQL
alembic upgrade head
```

---

## 📺 实时监控仪表板

```bash
# 基础监控
python scripts/monitor_dashboard.py

# 完整监控（需要admin token）
export ADMIN_TOKEN="your_jwt_token"
python scripts/monitor_dashboard.py --admin-token $ADMIN_TOKEN

# 自定义刷新间隔
python scripts/monitor_dashboard.py --refresh 5

# 监控生产
python scripts/monitor_dashboard.py --base-url https://api.prod.com --admin-token $TOKEN
```

**获取Token**:
```bash
curl -X POST http://localhost:8000/api/v1/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"pass"}' \
  | jq -r '.access_token'
```

---

## 🎯 常用工作流

### 📦 部署前检查
```bash
python scripts/diagnose.py && \
python scripts/check_optimization.py && \
python scripts/performance_test.py
```

### 🔧 性能优化流程
```bash
# 1. 启动监控（Terminal 1）
python scripts/monitor_dashboard.py --admin-token $TOKEN

# 2. 压力测试（Terminal 2）
python scripts/performance_test.py --concurrent 100 --total 1000

# 3. 查看慢函数和瓶颈

# 4. 应用优化
python scripts/suggest_indexes.py --generate-sql
# 应用索引、添加缓存、修复N+1

# 5. 验证改进
python scripts/performance_test.py
```

### 📅 每日健康检查
```bash
#!/bin/bash
# daily_check.sh
python scripts/diagnose.py || { echo "Health check failed!"; exit 1; }
python scripts/check_optimization.py > /tmp/opt_report.txt
echo "✅ Daily check completed"

# 添加到crontab: 0 9 * * * /path/to/daily_check.sh
```

---

## 🛠️ 代码中的优化工具

### Metrics（性能指标）
```python
from app.utils.metrics import Metrics

# 计数
await Metrics.increment("api_requests_total", labels={"endpoint": "/videos"})

# 当前值
await Metrics.gauge("active_connections", 45)

# 时间分布
await Metrics.histogram("api_duration_seconds", 0.145)
```

**查看**: `GET /api/v1/admin/metrics` (需要admin token)

---

### Profiler（性能分析）
```python
from app.utils.profiler import PerformanceProfiler

@PerformanceProfiler.profile()
async def expensive_operation():
    # 自动记录执行时间和调用次数
    ...

# 查看统计
PerformanceProfiler.print_stats(top_n=10)
```

**查看**: `GET /api/v1/admin/profiler/functions` (需要admin token)

---

### Query Profiler（SQL分析）
```python
from app.utils.profiler import QueryProfiler

# 启用
QueryProfiler.enable()

# 执行一些查询...

# 检测N+1
n_plus_one = QueryProfiler.detect_n_plus_one()

# 慢查询
slow = QueryProfiler.get_slow_queries(threshold=0.1)
```

**查看**: `GET /api/v1/admin/profiler/queries` (需要admin token)

---

### BatchProcessor（批处理）
```python
from app.utils.batch_processor import BatchProcessor

# 批量插入（快10-100倍）
videos_data = [{"title": f"Video {i}", "slug": f"video-{i}"} for i in range(10000)]
await BatchProcessor.batch_insert(db, Video, videos_data, batch_size=1000)

# 批量更新
updates = [{"id": 1, "view_count": 100}, {"id": 2, "view_count": 200}]
await BatchProcessor.batch_update(db, Video, updates)

# 批量删除
await BatchProcessor.batch_delete(db, Video, [1, 2, 3])

# 分块查询
async for chunk in BatchProcessor.chunked_query(db, Video, chunk_size=1000):
    for video in chunk:
        await process(video)
```

---

### Retry & Circuit Breaker（重试和熔断）
```python
from app.utils.retry import retry, circuit_breaker, resilient

# 简单重试
@retry(max_attempts=3, delay=1.0, backoff=2.0)
async def fetch_data():
    return await external_api.call()

# 熔断器
@circuit_breaker(failure_threshold=5, recovery_timeout=60)
async def unstable_service():
    return await service.call()

# 组合使用
@resilient(max_attempts=3, circuit_threshold=5)
async def robust_call():
    return await api.fetch()
```

---

### Cache（缓存）
```python
from app.utils.cache import Cache, cache_result

# 手动缓存
await Cache.set("key", value, ttl=300)
result = await Cache.get("key")
await Cache.delete("key")

# 装饰器缓存
@cache_result("function_name", ttl=300)
async def expensive_function():
    ...

# 清理缓存
await Cache.delete_pattern("videos:*")
```

---

### Error Sanitizer（错误清理）
```python
from app.utils.error_sanitizer import ErrorSanitizer

try:
    raise Exception("Error: postgres://user:password@host/db")
except Exception as e:
    safe_message = ErrorSanitizer.sanitize(str(e))
    # 输出: "Error: postgres://***@host/db"

# 清理字典
user_data = {"username": "john", "password": "secret", "api_key": "key"}
safe_data = ErrorSanitizer.sanitize_dict(user_data)
# {"username": "john", "password": "***REDACTED***", "api_key": "***REDACTED***"}
```

---

## 🚨 常见问题

### API连接失败
```bash
# 检查API状态
curl http://localhost:8000/health

# 启动后端
cd backend && uvicorn app.main:app --reload
```

### 数据库连接失败
```bash
# 检查容器
docker-compose -f docker-compose.dev.yml ps

# 启动基础设施
make infra-up
```

### 缺少依赖
```bash
cd backend && source venv/bin/activate
pip install -r requirements.txt
pip install httpx rich loguru
```

### Token过期
```bash
# 重新登录
curl -X POST http://localhost:8000/api/v1/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"your_pass"}' \
  | jq -r '.access_token'
```

---

## 📊 性能优化优先级

### 🔴 HIGH - 立即处理
- ❌ 外键缺少索引
- ❌ N+1 查询问题
- ❌ API无限流保护
- ❌ 系统健康检查失败

### 🟡 MEDIUM - 尽快处理
- ⚠️ 常用查询列缺少索引
- ⚠️ 频繁查询无缓存
- ⚠️ 循环中的数据库操作
- ⚠️ 缓存命中率 < 50%

### 🟢 LOW - 持续改进
- ℹ️ 代码质量改进
- ℹ️ 复杂函数添加profiler
- ℹ️ 重复索引清理

---

## 📈 性能指标参考

| 指标 | 优秀 | 良好 | 需要改进 |
|------|------|------|---------|
| **API响应时间 (P95)** | < 100ms | < 500ms | > 500ms |
| **缓存命中率** | > 80% | > 50% | < 50% |
| **连接池使用率** | < 50% | < 80% | > 80% |
| **吞吐量** | > 100 req/s | > 50 req/s | < 50 req/s |
| **错误率** | < 0.1% | < 1% | > 1% |

---

## 🔗 快速链接

- 📘 [完整工具指南](TOOLS_GUIDE.md)
- 📙 [优化使用指南](OPTIMIZATION_GUIDE.md)
- 📗 [性能改进总结](PERFORMANCE_IMPROVEMENTS.md)
- 📕 [实战优化案例](OPTIMIZATION_CASES.md)
- 📖 [项目文档](CLAUDE.md)

---

## 💡 一句话总结

| 工具 | 用途 |
|------|------|
| `performance_test.py` | 压力测试找瓶颈 |
| `diagnose.py` | 健康检查保稳定 |
| `check_optimization.py` | 代码审查提质量 |
| `suggest_indexes.py` | 索引优化加速度 |
| `monitor_dashboard.py` | 实时监控看全局 |

**记住**: 先诊断 → 再优化 → 后验证 → 持续监控 ✅

---

*打印此页面作为快速参考 - VideoSite 开发团队*
