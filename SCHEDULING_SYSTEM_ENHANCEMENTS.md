# 内容调度系统增强功能说明

## 📋 概述

本次更新大幅增强了内容调度系统的功能，新增了后台自动化调度、智能优化、冲突检测、健康监控等多个高级特性。

---

## 🎯 新增功能

### 1. ⏰ **自动化后台调度系统**

#### 功能描述
- 每分钟自动检查并执行到期的调度任务
- 按优先级分组执行（高/中/低）
- 失败自动重试机制
- 执行结果统计和通知

#### 技术实现
- **文件**: `backend/app/tasks/scheduler_enhanced.py`
- **任务**: `scheduler.execute_due_schedules`
- **频率**: 每分钟执行
- **队列**: scheduler

#### 特性
- ✅ 优先级分组执行（高优先级先执行）
- ✅ 自动失败重试
- ✅ 执行失败自动通知管理员
- ✅ 详细的执行日志

---

### 2. 🔍 **智能冲突检测**

#### 功能描述
检测调度系统中的各种冲突情况：
- **重复内容调度**: 相同内容有多个待执行调度
- **高并发检测**: 同一时间段（5分钟内）任务过多
- **资源冲突**: 发布资源冲突预警

#### 技术实现
- **任务**: `scheduler.detect_conflicts`
- **频率**: 每小时执行（每小时30分）
- **通知**: 发现冲突时自动通知管理员

#### 检测规则
```python
# 重复内容检测
if same_content_has_multiple_schedules:
    conflict_type = "duplicate_content"

# 高并发检测
if tasks_in_5min_window > 5:
    conflict_type = "high_concurrency"
```

---

### 3. 📊 **每日调度报告**

#### 功能描述
每天自动生成调度系统运行报告：
- 昨日执行统计（成功/失败）
- 成功率分析
- 今日待执行任务数
- 过期未执行任务预警

#### 技术实现
- **任务**: `scheduler.generate_daily_report`
- **频率**: 每天凌晨2点
- **输出**: 自动发送报告给管理员

#### 报告内容
```markdown
📊 调度系统每日报告 (2025-10-14)

📈 昨日执行情况:
  ✅ 成功: 45
  ❌ 失败: 3
  📊 成功率: 93.75%

⏰ 今日计划:
  📅 待执行: 67
  ⚠️ 过期未执行: 2
```

---

### 4. 🎯 **智能调度优化**

#### 功能描述
分析历史数据，优化调度时间分布：
- 避开高峰时段
- 平衡服务器负载
- 推荐最佳发布时间

#### 技术实现
- **任务**: `scheduler.optimize_schedule_times`
- **频率**: 每6小时执行
- **算法**: 基于历史数据的负载均衡

#### 优化策略
- 检测负载集中时段
- 建议分散任务
- 自动调整低优先级任务时间（可配置）

---

### 5. 🏥 **系统健康检查**

#### 功能描述
定期检查调度系统健康状态：
- 检测卡住的任务（超过1小时未执行）
- 检测异常高的失败率
- 数据库连接健康检查

#### 技术实现
- **任务**: `scheduler.health_check`
- **频率**: 每30分钟
- **告警**: 发现问题自动通知管理员

#### 检查项目
```python
✅ 过期任务检查 (pending > 1 hour)
✅ 失败率检查 (failures in last hour > 10)
✅ 数据库连接检查
✅ 任务队列状态检查
```

---

### 6. 📅 **可视化日历视图**

#### 功能描述
提供直观的日历视图管理调度：
- 月视图/周视图/日视图切换
- 按内容类型和状态过滤
- 事件详情快速查看
- 颜色编码（按状态）

#### 技术实现
- **文件**: `admin-frontend/src/pages/Scheduling/Calendar.tsx`
- **技术栈**: FullCalendar + React + Ant Design
- **路由**: `/admin/scheduling/calendar`

#### 特性
- ✅ 三种视图模式（月/周/日）
- ✅ 拖拽式导航
- ✅ 事件点击查看详情
- ✅ 实时数据同步
- ✅ 响应式设计

---

## 🔧 安装和配置

### 1. 后端依赖

确保已安装 Celery 和相关依赖：

```bash
cd backend

# 如果还没有安装 Celery
pip install celery redis

# 或者使用 requirements.txt
pip install -r requirements.txt
```

### 2. 启动 Celery Worker

```bash
# 启动 Worker（处理任务）
celery -A app.celery_app worker --loglevel=info -Q scheduler,default

# 启动 Beat（定时调度）
celery -A app.celery_app beat --loglevel=info
```

### 3. 生产环境部署

使用 Supervisor 或 systemd 管理 Celery 进程：

**supervisor 配置示例**:
```ini
[program:celery_worker]
command=/path/to/venv/bin/celery -A app.celery_app worker -Q scheduler,default
directory=/path/to/backend
user=www-data
numprocs=1
autostart=true
autorestart=true
startsecs=10

[program:celery_beat]
command=/path/to/venv/bin/celery -A app.celery_app beat
directory=/path/to/backend
user=www-data
numprocs=1
autostart=true
autorestart=true
startsecs=10
```

### 4. 前端日历组件

安装 FullCalendar 依赖：

```bash
cd admin-frontend

pnpm install @fullcalendar/react @fullcalendar/daygrid @fullcalendar/timegrid @fullcalendar/interaction
```

添加路由（在 `admin-frontend/src/routes/index.tsx`）:

```tsx
{
  path: '/scheduling/calendar',
  element: <SchedulingCalendar />,
}
```

---

## 📊 监控和日志

### Celery 任务监控

使用 Flower 监控 Celery 任务：

```bash
pip install flower
celery -A app.celery_app flower --port=5555
```

访问 http://localhost:5555 查看任务执行情况

### 日志查看

所有调度任务的日志都会记录到：
- **应用日志**: 使用 loguru
- **数据库**: `schedule_histories` 表
- **Celery 日志**: Celery worker 输出

查看日志：
```bash
# 实时查看 Worker 日志
tail -f /var/log/celery/worker.log

# 实时查看 Beat 日志
tail -f /var/log/celery/beat.log
```

---

## 🔔 通知配置

### 管理员通知

所有重要事件都会通过 `AdminNotificationService` 发送通知：

- ✅ 执行失败通知
- ✅ 冲突检测通知
- ✅ 健康问题告警
- ✅ 每日报告

通知类型和严重性：
```python
# 严重性级别
- "info": 信息性通知（每日报告）
- "medium": 中等问题（冲突检测）
- "high": 严重问题（执行失败、健康问题）
```

---

## 🎨 自定义配置

### 调整任务执行频率

编辑 `backend/app/celery_app.py` 中的 `beat_schedule`:

```python
beat_schedule={
    # 调整为每30秒执行一次
    "execute-due-schedules-enhanced": {
        "task": "scheduler.execute_due_schedules",
        "schedule": 30.0,  # 改为 30 秒
        "options": {"queue": "scheduler"},
    },
}
```

### 调整冲突检测阈值

编辑 `backend/app/tasks/scheduler_enhanced.py`:

```python
# 修改高并发阈值
if len(schedule_list) > 10:  # 改为 10 个任务
    conflicts.append({...})

# 修改时间桶大小
bucket_time = schedule.scheduled_time.replace(
    minute=(schedule.scheduled_time.minute // 10) * 10,  # 改为 10 分钟
)
```

### 自定义通知方式

可以扩展通知系统支持更多渠道：

```python
# 添加邮件通知
await send_email_notification(...)

# 添加 Slack 通知
await send_slack_notification(...)

# 添加 webhook 通知
await send_webhook_notification(...)
```

---

## 📈 性能优化建议

### 1. 数据库索引

确保以下字段有索引：
```sql
-- 调度表索引
CREATE INDEX idx_schedules_status_time ON content_schedules(status, scheduled_time);
CREATE INDEX idx_schedules_priority ON content_schedules(priority DESC);

-- 历史表索引
CREATE INDEX idx_histories_executed_at ON schedule_histories(executed_at DESC);
```

### 2. Celery 优化

```python
# 增加 Worker 并发数
celery -A app.celery_app worker --concurrency=4

# 使用 eventlet 或 gevent 提升性能
celery -A app.celery_app worker -P eventlet --concurrency=100
```

### 3. Redis 优化

```ini
# Redis 配置优化
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
```

---

## 🐛 故障排查

### 问题1: 任务不执行

**检查项**:
```bash
# 1. 检查 Celery Worker 是否运行
ps aux | grep celery

# 2. 检查 Beat 是否运行
ps aux | grep "celery beat"

# 3. 检查 Redis 连接
redis-cli ping

# 4. 查看任务队列
celery -A app.celery_app inspect active
```

### 问题2: 任务执行失败

**检查项**:
```bash
# 查看 Worker 日志
celery -A app.celery_app events

# 查看具体任务状态
celery -A app.celery_app result <task-id>

# 检查数据库连接
python -c "from app.database import get_db; print('DB OK')"
```

### 问题3: 内存占用过高

**解决方案**:
```bash
# 限制 Worker 内存
celery -A app.celery_app worker --max-memory-per-child=200000

# 减少 Worker 数量
celery -A app.celery_app worker --concurrency=2

# 设置任务过期时间
task_expires = 3600  # 1 小时后过期
```

---

## 📚 API 文档

### 新增 API 端点

所有调度相关的 API 端点保持不变，增强功能主要在后台任务层面。

前端可以通过现有 API 获取数据：
- `GET /api/v1/admin/scheduling/calendar` - 获取日历数据
- `GET /api/v1/admin/scheduling/stats` - 获取统计信息
- `GET /api/v1/admin/scheduling/analytics` - 获取分析数据

---

## 🚀 未来规划

### Phase 2 功能
- [ ] Cron 表达式支持
- [ ] 审批工作流
- [ ] A/B 测试分析
- [ ] 性能预测算法
- [ ] 移动端推送通知

### Phase 3 功能
- [ ] AI 智能推荐
- [ ] 自动化内容优化
- [ ] 多租户支持
- [ ] 国际化时区管理

---

## 📞 技术支持

如有问题或建议，请：
1. 查看日志文件
2. 查阅本文档
3. 联系技术团队

---

**文档版本**: 1.0
**最后更新**: 2025-10-14
**作者**: Claude Code
