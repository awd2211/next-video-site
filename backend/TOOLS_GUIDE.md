# 🛠️ VideoSite Performance Tools Guide

完整的性能优化和监控工具集使用指南

---

## 📋 工具总览

VideoSite 后端现在配备了完整的性能优化工具链：

| 工具 | 文件 | 用途 |
|------|------|------|
| **性能测试** | `scripts/performance_test.py` | API压力测试和基准测试 |
| **系统诊断** | `scripts/diagnose.py` | 一键健康检查 |
| **代码质量检查** | `scripts/check_optimization.py` | 静态代码分析 |
| **索引优化** | `scripts/suggest_indexes.py` | 数据库索引建议 |
| **实时监控** | `scripts/monitor_dashboard.py` | 性能仪表板 |

---

## 🚀 快速开始

### 1. 性能测试脚本

**功能**: 对API端点进行并发压力测试，生成详细的性能报告。

**基础用法**:
```bash
# 运行默认测试套件（测试常见端点）
python scripts/performance_test.py

# 输出示例:
# ============================================================
# 📊 Results for /api/v1/videos?page=1&page_size=20
# ============================================================
# ✅ Successful: 98/100
# ❌ Errors: 2
# ⏱️  Total Time: 5.2s
# 🚀 Throughput: 19.2 req/s
#
# Response Times:
#   Average: 0.052s
#   Median:  0.048s
#   Min/Max: 0.021s / 0.145s
#   P95:     0.089s
#   P99:     0.132s
```

**高级用法**:
```bash
# 测试特定端点
python scripts/performance_test.py \
  --endpoint /api/v1/videos \
  --concurrent 50 \
  --total 200

# 测试生产环境
python scripts/performance_test.py \
  --base-url https://api.yoursite.com \
  --endpoint /api/v1/categories

# 自定义并发和请求数
python scripts/performance_test.py \
  --endpoint /api/v1/search?q=test \
  --concurrent 100 \
  --total 500
```

**何时使用**:
- ✅ 部署前性能验证
- ✅ 优化后对比测试
- ✅ 建立性能基准
- ✅ 查找性能瓶颈

---

### 2. 系统诊断工具

**功能**: 全面检查系统健康状况，包括API、数据库、缓存、安全配置等。

**基础用法**:
```bash
# 运行完整诊断
python scripts/diagnose.py

# 输出示例:
# ================================================================================
# 🔍 VideoSite Performance Diagnostic Tool
# 📅 2025-10-19 14:30:00
# ================================================================================
#
# 📋 Checking API Availability...
#   ✅ API is accessible
#
# 📋 Checking Health Status...
#   ✅ Health check passed
#     ✅ database: OK
#     ✅ redis: OK
#
# 📋 Checking Database Pool...
#   📊 Pool usage: 15.0% (3/20)
#   ✅ Pool usage healthy: 15.0%
#
# ...
#
# 📊 Diagnostic Summary
# ✅ PASSED (7):
#   ✅ API is accessible
#   ✅ Health check passed
#   ...
#
# Overall Health Score: 92.5% - EXCELLENT ✨
```

**高级用法**:
```bash
# 指定base URL
python scripts/diagnose.py --base-url http://production.com

# 详细输出模式
python scripts/diagnose.py --verbose

# 检查特定组件
python scripts/diagnose.py --check database
python scripts/diagnose.py --check health
```

**退出码**:
- `0`: 所有检查通过
- `1`: 发现问题

**何时使用**:
- ✅ 每日健康检查
- ✅ 部署后验证
- ✅ 故障排查
- ✅ CI/CD集成

**集成到CI/CD**:
```bash
# 在部署脚本中添加
if ! python scripts/diagnose.py; then
    echo "❌ Health check failed! Aborting deployment."
    exit 1
fi
```

---

### 3. 代码优化检查

**功能**: 扫描代码库，检查是否遵循性能最佳实践。

**基础用法**:
```bash
# 检查整个app目录
python scripts/check_optimization.py

# 输出示例:
# 🔍 Checking optimization best practices...
# Found 145 Python files
#
# ⚠️ WARNINGS (12):
#   ⚠️ app/api/videos.py: 3 routes without rate limiting
#   ⚠️ app/api/search.py: Database queries without caching
#   ...
#
# ❌ ISSUES (2):
#   ❌ app/api/comments.py: Possible N+1 query - use selectinload()
#   ...
#
# 💡 Recommendations:
#   1. Add @limiter.limit() decorators to API endpoints
#   2. Fix N+1 queries using selectinload()
#   3. Add caching for frequently accessed data
#
# Optimization Score: 78.5%
# Grade: B - Good, but room for improvement
```

**高级用法**:
```bash
# 检查特定目录
python scripts/check_optimization.py --path app/api

# 检查特定文件
python scripts/check_optimization.py --path app/api/videos.py
```

**检查项目**:
1. ✅ **限流保护**: 是否为API端点添加了 `@limiter.limit`
2. ✅ **缓存使用**: 数据库查询是否使用了缓存
3. ✅ **N+1查询**: 是否使用了 `selectinload()` / `joinedload()`
4. ✅ **批量操作**: 循环中的DB操作是否应该批处理
5. ✅ **错误处理**: 是否避免了裸 `except:` 子句
6. ✅ **性能分析**: 复杂函数是否添加了profiler

**何时使用**:
- ✅ 代码审查前
- ✅ 提交PR前
- ✅ 定期代码质量检查
- ✅ 新人培训

---

### 4. 数据库索引建议

**功能**: 分析数据库模式和查询模式，提出索引优化建议。

**基础用法**:
```bash
# 运行索引分析
python scripts/suggest_indexes.py

# 输出示例:
# 🔍 Starting database index analysis...
#
# 📊 Analyzing existing indexes...
#   Found 47 indexes across 23 tables
#
# 🔗 Checking foreign key indexes...
#   ⚠️  Found 3 foreign keys without indexes
#
# 🔎 Checking common query column indexes...
#   Analyzed common query patterns for 8 tables
#
# 📊 Database Index Analysis Report
# ================================================================================
#
# 💡 INDEX SUGGESTIONS (5):
#
# 🔴 HIGH PRIORITY (3):
#
#   Table: comments
#   Columns: video_id
#   Reason: Foreign key to videos without index
#   SQL: CREATE INDEX idx_comments_video_id ON "comments" ("video_id");
#
#   Table: watch_history
#   Columns: user_id
#   Reason: Foreign key to users without index
#   SQL: CREATE INDEX idx_watch_history_user_id ON "watch_history" ("user_id");
#
# ...
#
# ✅ Found 5 opportunities for optimization
```

**高级用法**:
```bash
# 分析代码中的查询模式
python scripts/suggest_indexes.py --analyze-queries

# 生成SQL迁移文件
python scripts/suggest_indexes.py --generate-sql

# 生成的文件: scripts/suggested_indexes.sql
```

**生成的SQL文件**:
```sql
-- Database Index Optimization Migration
-- Generated by suggest_indexes.py
-- Review and test before applying to production!

-- HIGH PRIORITY INDEXES
-- These should be created immediately

-- Foreign key to videos without index
CREATE INDEX idx_comments_video_id ON "comments" ("video_id");

-- Foreign key to users without index
CREATE INDEX idx_watch_history_user_id ON "watch_history" ("user_id");

...
```

**应用建议的索引**:
```bash
# 1. 审查生成的SQL
cat scripts/suggested_indexes.sql

# 2. 在开发环境测试
psql -h localhost -p 5434 -U videosite -d videosite -f scripts/suggested_indexes.sql

# 3. 创建Alembic迁移（推荐）
cd backend
alembic revision -m "add_suggested_indexes"

# 4. 编辑迁移文件，复制SQL到upgrade()函数

# 5. 应用迁移
alembic upgrade head
```

**何时使用**:
- ✅ 性能优化前
- ✅ 查询变慢时
- ✅ 数据量增长后
- ✅ 定期审查（每月/季度）

**⚠️ 注意事项**:
- ⚠️ 索引会占用存储空间
- ⚠️ 索引会减慢写入速度
- ⚠️ 在生产环境应用前必须测试
- ⚠️ 使用 `CREATE INDEX CONCURRENTLY` 避免锁表

---

### 5. 实时监控仪表板

**功能**: 终端实时监控系统性能，显示关键指标和告警。

**基础用法**:
```bash
# 启动监控仪表板（需要先安装依赖）
pip install httpx rich

# 基础模式（只显示健康状态）
python scripts/monitor_dashboard.py

# 完整模式（需要admin token）
export ADMIN_TOKEN="your_admin_jwt_token"
python scripts/monitor_dashboard.py --admin-token $ADMIN_TOKEN
```

**仪表板界面**:
```
╭─────────────────────────────────────────────────────────────────────────────╮
│                   VideoSite Performance Dashboard                           │
│  URL: http://localhost:8000  |  Updated: 14:30:45  |  Admin: ✅             │
╰─────────────────────────────────────────────────────────────────────────────╯

╭─ System Health ────────────╮  ╭─ API Metrics ──────────────╮
│ Status      ✅ HEALTHY      │  │ Total Requests    15,234   │
│   Database  ✅ ok           │  │ Total Views       45,678   │
│   Redis     ✅ ok           │  │ Cache Hit Rate    89.5%    │
│ Pool Usage  3/20 (15.0%)   │  │ Cache Requests    12,345   │
╰────────────────────────────╯  ╰────────────────────────────╯

╭─ Top Functions ────────────────────────────────────────────────╮
│ Function                     Calls    Avg (ms)    Total (s)   │
│ list_videos                  1,234      45.20        55.83    │
│ get_video_detail             5,678      12.50        70.98    │
│ search_videos                  234     180.30        42.19    │
╰────────────────────────────────────────────────────────────────╯

╭─ Alerts ───────────────────────────────────────────────────────╮
│ ✅ ALL CLEAR    No alerts                                      │
╰────────────────────────────────────────────────────────────────╯

Press Ctrl+C to exit  |  ✅ Full metrics enabled
```

**高级用法**:
```bash
# 自定义刷新间隔（秒）
python scripts/monitor_dashboard.py --refresh 5

# 监控生产环境
python scripts/monitor_dashboard.py \
  --base-url https://api.production.com \
  --admin-token $PROD_ADMIN_TOKEN

# 使用环境变量
export API_BASE_URL="http://localhost:8000"
export ADMIN_TOKEN="your_token_here"
python scripts/monitor_dashboard.py
```

**获取Admin Token**:
```bash
# 方法1: 通过API登录
curl -X POST http://localhost:8000/api/v1/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"your_password"}' \
  | jq -r '.access_token'

# 方法2: 使用现有token（从浏览器开发者工具获取）
# 打开Admin前端 → 开发者工具 → Application → Local Storage → token
```

**监控指标**:
1. **系统健康**: 整体状态、组件检查
2. **数据库连接池**: 使用率、溢出警告
3. **API请求**: 总请求数、视频浏览量
4. **缓存性能**: 命中率、请求数
5. **函数性能**: Top 5慢函数
6. **实时告警**: 连接池警告、慢函数、低缓存命中率

**告警级别**:
- 🔴 **CRITICAL**: 系统不健康、连接池>90%
- 🟡 **WARNING**: 连接池>80%、缓存命中率<50%、慢函数>500ms

**何时使用**:
- ✅ 开发时实时监控
- ✅ 压力测试时观察
- ✅ 生产环境监控（配合screen/tmux）
- ✅ 故障排查

**生产环境持续运行**:
```bash
# 使用screen或tmux
screen -S monitor
python scripts/monitor_dashboard.py --admin-token $TOKEN
# Ctrl+A, D 分离

# 恢复监控
screen -r monitor
```

---

## 🎯 完整工作流示例

### 场景1: 部署前性能验证

```bash
# 1. 运行系统诊断
python scripts/diagnose.py
# 确保所有检查通过 ✅

# 2. 检查代码优化
python scripts/check_optimization.py
# 修复所有HIGH优先级问题 ✅

# 3. 运行性能测试
python scripts/performance_test.py
# 确保响应时间符合SLA ✅

# 4. 检查索引优化
python scripts/suggest_indexes.py --generate-sql
# 应用建议的索引 ✅

# 5. 再次测试性能
python scripts/performance_test.py
# 验证性能提升 ✅

# ✅ 准备部署！
```

---

### 场景2: 性能优化流程

```bash
# 1. 启动实时监控（Terminal 1）
python scripts/monitor_dashboard.py --admin-token $TOKEN

# 2. 运行性能测试（Terminal 2）
python scripts/performance_test.py \
  --endpoint /api/v1/videos \
  --concurrent 100 \
  --total 1000

# 3. 观察监控仪表板
# - 查看响应时间
# - 识别慢函数
# - 检查连接池使用率
# - 观察缓存命中率

# 4. 分析瓶颈
# - 如果连接池高 → 优化查询、添加索引
# - 如果缓存命中率低 → 添加缓存
# - 如果有慢函数 → 使用profiler分析

# 5. 应用优化
# - 添加索引: python scripts/suggest_indexes.py --generate-sql
# - 添加缓存: 在代码中使用 @cache_result
# - 修复N+1: 使用 selectinload()

# 6. 验证改进
python scripts/performance_test.py  # 再次测试
```

---

### 场景3: 日常健康检查

```bash
#!/bin/bash
# daily_health_check.sh

echo "🔍 Running daily health check..."

# 1. 系统诊断
if ! python scripts/diagnose.py; then
    echo "❌ System health check FAILED!"
    # 发送告警邮件/Slack通知
    exit 1
fi

# 2. 代码优化检查
python scripts/check_optimization.py > /tmp/optimization_report.txt
SCORE=$(grep "Optimization Score:" /tmp/optimization_report.txt | awk '{print $3}' | tr -d '%')

if (( $(echo "$SCORE < 70" | bc -l) )); then
    echo "⚠️ Optimization score below threshold: $SCORE%"
    # 发送警告
fi

# 3. 索引检查（每周一次）
if [ $(date +%u) -eq 1 ]; then
    python scripts/suggest_indexes.py > /tmp/index_report.txt
    # 发送报告
fi

echo "✅ Daily health check completed!"
```

**设置定时任务**:
```bash
# 添加到crontab
crontab -e

# 每天早上9点运行
0 9 * * * /path/to/daily_health_check.sh
```

---

## 📊 工具对比表

| 工具 | 运行频率 | 需要Token | 输出 | 用途 |
|------|---------|----------|------|------|
| **performance_test** | 按需 | ❌ | 统计报告 | 压力测试 |
| **diagnose** | 每日 | ❌ | 健康报告 | 健康检查 |
| **check_optimization** | 提交前 | ❌ | 代码分析 | 代码质量 |
| **suggest_indexes** | 每月 | ❌ | SQL建议 | 索引优化 |
| **monitor_dashboard** | 实时 | ✅ | 可视化 | 实时监控 |

---

## 🎓 最佳实践

### 1. 开发阶段
- ✅ 提交代码前运行 `check_optimization.py`
- ✅ 添加新API后运行 `performance_test.py`
- ✅ 使用 `monitor_dashboard.py` 进行本地监控

### 2. 测试阶段
- ✅ 运行完整的 `diagnose.py` 检查
- ✅ 压力测试关键端点
- ✅ 检查并应用索引建议

### 3. 生产部署
- ✅ 部署前：运行所有工具验证
- ✅ 部署后：立即运行 `diagnose.py`
- ✅ 持续运行：设置每日健康检查

### 4. 性能优化
1. 🔍 **发现**: 使用 `monitor_dashboard.py` 识别问题
2. 📊 **分析**: 使用 `check_optimization.py` 找出代码问题
3. 💡 **优化**: 应用建议（索引、缓存、批处理）
4. ✅ **验证**: 使用 `performance_test.py` 验证改进

---

## 🆘 故障排查

### 问题: "无法连接到API"

```bash
# 检查API是否运行
curl http://localhost:8000/health

# 检查端口
netstat -tlnp | grep 8000

# 启动后端
cd backend && uvicorn app.main:app --reload
```

### 问题: "Admin token无效"

```bash
# 重新登录获取token
curl -X POST http://localhost:8000/api/v1/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"your_password"}'
```

### 问题: "数据库连接失败"

```bash
# 检查数据库是否运行
docker-compose -f docker-compose.dev.yml ps

# 启动基础设施
make infra-up

# 检查连接
psql -h localhost -p 5434 -U videosite -d videosite
```

### 问题: "缺少Python依赖"

```bash
# 安装所有依赖
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 安装特定工具依赖
pip install httpx rich loguru sqlalchemy asyncpg
```

---

## 📚 相关文档

- [OPTIMIZATION_GUIDE.md](OPTIMIZATION_GUIDE.md) - 优化工具详细使用指南
- [PERFORMANCE_IMPROVEMENTS.md](PERFORMANCE_IMPROVEMENTS.md) - 性能改进总结
- [OPTIMIZATION_CASES.md](OPTIMIZATION_CASES.md) - 实战优化案例
- [CLAUDE.md](CLAUDE.md) - 项目整体文档

---

## 🎉 总结

这套工具链为VideoSite提供了**世界级的性能监控和优化能力**：

✅ **自动化**: 所有工具可集成到CI/CD
✅ **可视化**: 实时仪表板直观展示
✅ **可操作**: 生成具体的优化建议和SQL
✅ **可验证**: 性能测试验证优化效果
✅ **可持续**: 日常健康检查保持最佳状态

**立即开始使用这些工具，让你的应用性能提升10倍！** 🚀

---

*最后更新: 2025-10-19*
*维护者: VideoSite 开发团队*
