# 系统监控增强功能使用指南

## 概述

系统监控增强功能提供了全面的系统健康监控、告警管理和SLA追踪能力，帮助管理员实时了解系统状态，及时发现和解决问题。

## 主要功能

### 1. 实时健康监控

监控系统各项关键指标：

- **数据库**: 连接池状态、响应时间、连接数使用率
- **Redis**: 内存使用、响应时间、键数量
- **MinIO存储**: 响应时间、存储使用量、对象数量
- **Celery任务队列**: Worker数量、活跃任务、任务积压
- **系统资源**: CPU、内存、磁盘、网络使用情况

### 2. 多维度告警系统

自动监控并触发告警：

- **CPU告警**: 70%警告, 90%严重
- **内存告警**: 80%警告, 95%严重
- **磁盘告警**: 80%警告, 95%严重
- **数据库连接池**: 70%警告, 90%严重
- **数据库响应时间**: 100ms警告, 500ms严重
- **Redis内存**: 80%警告, 95%严重
- **Redis响应时间**: 50ms警告, 200ms严重
- **存储使用**: 80%警告, 95%严重
- **存储响应时间**: 200ms警告, 1000ms严重
- **Celery Worker**: 最少1个worker
- **Celery任务积压**: 100警告, 500严重

### 3. SLA追踪

定期计算和存储SLA指标：

- **可用性百分比**: 系统正常运行时间占比
- **响应时间统计**: 平均值、P50、P95、P99、最大值
- **告警统计**: 总告警数、严重告警数、警告数
- **资源使用统计**: 平均CPU、内存、磁盘使用率
- **支持多种周期**: 小时、每日、每周、每月

## API接口文档

所有API端点都在 `/api/v1/admin/system-health` 路径下，需要管理员权限。

### 健康监控API

#### GET /health
获取系统实时健康状态

**查询参数:**
- `use_cache` (boolean, 可选): 是否使用缓存，默认true

**响应示例:**
```json
{
  "timestamp": "2025-10-19T12:00:00.000Z",
  "overall_status": "healthy",
  "services": {
    "database": {
      "status": "healthy",
      "response_time_ms": 12.5,
      "pool_size": 20,
      "checked_out": 3,
      "utilization_percent": 15.0
    },
    "redis": {
      "status": "healthy",
      "response_time_ms": 5.2,
      "used_memory_mb": 128.5,
      "keys_count": 1523
    },
    "storage": {
      "status": "healthy",
      "response_time_ms": 45.8,
      "used_gb": 234.56,
      "total_gb": 1000.0,
      "utilization_percent": 23.46,
      "object_count": 5432
    },
    "celery": {
      "status": "healthy",
      "workers_count": 2,
      "active_tasks": 5,
      "reserved_tasks": 12
    }
  },
  "system_resources": {
    "cpu": {
      "usage_percent": 35.2,
      "cores": 8,
      "status": "healthy"
    },
    "memory": {
      "used_gb": 12.5,
      "total_gb": 32.0,
      "usage_percent": 39.1,
      "status": "healthy"
    },
    "disk": {
      "used_gb": 456.7,
      "total_gb": 1000.0,
      "usage_percent": 45.7,
      "status": "healthy"
    }
  },
  "alerts": {
    "statistics": {
      "active_total": 2,
      "critical": 0,
      "warning": 2,
      "resolved_24h": 15
    },
    "new_alerts_count": 0
  }
}
```

#### GET /metrics
获取详细系统指标和数据库统计

**响应示例:**
```json
{
  "timestamp": "2025-10-19T12:00:00.000Z",
  "database": {
    "total_videos": 1523,
    "total_users": 8945,
    "total_comments": 3421,
    "new_videos_24h": 15,
    "new_users_24h": 234,
    "new_comments_24h": 89
  }
}
```

#### GET /history
获取历史指标趋势数据

**查询参数:**
- `limit` (int): 返回记录数，范围1-100，默认50

**响应示例:**
```json
{
  "count": 50,
  "history": [
    {
      "timestamp": "2025-10-19T11:55:00.000Z",
      "data": {
        "cpu_usage": 35.2,
        "memory_usage": 39.1,
        "disk_usage": 45.7,
        "db_response_time": 12.5,
        "redis_response_time": 5.2,
        "storage_response_time": 45.8
      }
    }
  ]
}
```

#### GET /info
获取系统详细信息

**响应示例:**
```json
{
  "timestamp": "2025-10-19T12:00:00.000Z",
  "server": {
    "hostname": "video-server-01",
    "platform": "Linux",
    "architecture": "x86_64"
  },
  "python": {
    "version": "3.11.5",
    "implementation": "CPython"
  },
  "application": {
    "start_time": "2025-10-19T08:00:00.000Z",
    "uptime_formatted": "4h 0m 0s"
  }
}
```

### 告警管理API

#### GET /alerts
获取告警列表

**查询参数:**
- `status` (string): 状态过滤 (active/resolved/all)，默认active
- `alert_type` (string, 可选): 类型过滤 (cpu/memory/disk/database/redis/storage/celery)
- `severity` (string, 可选): 严重程度 (critical/warning)
- `page` (int): 页码，默认1
- `page_size` (int): 每页数量，范围1-100，默认20

**响应示例:**
```json
{
  "items": [
    {
      "id": 123,
      "alert_type": "memory",
      "severity": "warning",
      "title": "内存使用率告警",
      "message": "内存使用率达到 82.5%，已超过告警阈值 80.0%",
      "metric_name": "memory_usage_percent",
      "metric_value": 82.5,
      "threshold_value": 80.0,
      "status": "active",
      "triggered_at": "2025-10-19T11:30:00.000Z",
      "acknowledged_by": null,
      "notes": null
    }
  ],
  "total": 2,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

#### GET /alerts/statistics
获取告警统计

**响应示例:**
```json
{
  "timestamp": "2025-10-19T12:00:00.000Z",
  "statistics": {
    "active_total": 2,
    "critical": 0,
    "warning": 2,
    "resolved_24h": 15
  }
}
```

#### GET /alerts/active/count
获取活跃告警数量（快速接口，用于徽章显示）

**响应示例:**
```json
{
  "total": 2,
  "critical": 0
}
```

#### POST /alerts/{alert_id}/acknowledge
确认告警

**查询参数:**
- `notes` (string, 可选): 处理备注

**响应示例:**
```json
{
  "success": true,
  "message": "Alert acknowledged successfully",
  "alert": {
    "id": 123,
    "title": "内存使用率告警",
    "acknowledged_by": 1,
    "acknowledged_at": "2025-10-19T12:00:00.000Z",
    "notes": "已知晓，监控中"
  }
}
```

#### POST /alerts/{alert_id}/resolve
手动解决告警

**查询参数:**
- `notes` (string, 可选): 解决备注

**响应示例:**
```json
{
  "success": true,
  "message": "Alert resolved successfully",
  "alert": {
    "id": 123,
    "title": "内存使用率告警",
    "status": "resolved",
    "resolved_at": "2025-10-19T12:00:00.000Z"
  }
}
```

### SLA追踪API

#### GET /sla/report
获取SLA历史报告

**查询参数:**
- `period_type` (string): 周期类型 (hourly/daily/weekly/monthly)，默认daily
- `limit` (int): 返回记录数，范围1-365，默认30

**响应示例:**
```json
{
  "period_type": "daily",
  "count": 30,
  "records": [
    {
      "id": 456,
      "period_start": "2025-10-18T00:00:00.000Z",
      "period_end": "2025-10-19T00:00:00.000Z",
      "period_type": "daily",
      "uptime_percentage": 99.95,
      "avg_response_time_ms": 15.3,
      "p95_response_time_ms": 45.2,
      "p99_response_time_ms": 78.5,
      "total_alerts": 3,
      "critical_alerts": 0,
      "warning_alerts": 3,
      "avg_cpu_usage": 42.3,
      "avg_memory_usage": 56.7,
      "avg_disk_usage": 45.8
    }
  ]
}
```

#### GET /sla/summary
获取SLA汇总统计

**查询参数:**
- `days` (int): 汇总天数，范围1-365，默认30

**响应示例:**
```json
{
  "period_start": "2025-09-19T12:00:00.000Z",
  "period_end": "2025-10-19T12:00:00.000Z",
  "record_count": 30,
  "avg_uptime_percentage": 99.89,
  "total_uptime_seconds": 2591280,
  "total_downtime_seconds": 720,
  "total_alerts": 45,
  "critical_alerts": 2,
  "avg_response_time_ms": 18.5
}
```

#### GET /sla/current
获取当前实时SLA状态（今天截至目前）

**响应示例:**
```json
{
  "period_start": "2025-10-19T00:00:00.000Z",
  "period_end": "2025-10-19T12:00:00.000Z",
  "elapsed_hours": 12.0,
  "uptime_percentage": 99.92,
  "metrics_collected": 8640,
  "avg_db_response_time_ms": 14.2,
  "total_alerts": 2,
  "critical_alerts": 0,
  "status": "healthy"
}
```

#### POST /sla/generate
手动生成SLA报告

**查询参数:**
- `period_type` (string): 周期类型 (hourly/daily)

**响应示例:**
```json
{
  "success": true,
  "message": "Daily SLA report generated successfully",
  "sla": {
    "id": 789,
    "period_start": "2025-10-18T00:00:00.000Z",
    "period_end": "2025-10-19T00:00:00.000Z",
    "uptime_percentage": 99.95,
    "avg_response_time_ms": 15.3,
    "total_alerts": 3,
    "critical_alerts": 0
  }
}
```

## 自动化任务配置

### Celery定时任务

系统提供了自动生成SLA报告的Celery任务，需要在 `app/celery_app.py` 中配置 Celery Beat 调度。

**配置示例:**

```python
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    # 每小时第5分钟生成SLA报告
    'generate-hourly-sla': {
        'task': 'generate_hourly_sla_report',
        'schedule': crontab(minute=5),
    },

    # 每天凌晨00:10生成日报
    'generate-daily-sla': {
        'task': 'generate_daily_sla_report',
        'schedule': crontab(hour=0, minute=10),
    },

    # 每周一凌晨00:30生成周报
    'generate-weekly-sla': {
        'task': 'generate_weekly_sla_report',
        'schedule': crontab(day_of_week=1, hour=0, minute=30),
    },

    # 每月1号凌晨01:00生成月报
    'generate-monthly-sla': {
        'task': 'generate_monthly_sla_report',
        'schedule': crontab(day_of_month=1, hour=1, minute=0),
    },
}
```

**启动Celery Worker和Beat:**

```bash
# 启动Worker（处理任务）
celery -A app.celery_app worker --loglevel=info

# 启动Beat（定时调度）
celery -A app.celery_app beat --loglevel=info
```

## 数据库表结构

### system_metrics
存储系统健康指标的时间序列数据

**主要字段:**
- `timestamp`: 指标采集时间
- `cpu_usage_percent`: CPU使用率
- `memory_usage_percent`: 内存使用率
- `disk_usage_percent`: 磁盘使用率
- `db_response_time_ms`: 数据库响应时间
- `redis_response_time_ms`: Redis响应时间
- `storage_response_time_ms`: 存储响应时间
- `celery_active_tasks`: Celery活跃任务数
- `celery_workers_count`: Celery Worker数量
- `overall_status`: 总体状态 (healthy/degraded/unhealthy)

**索引:**
- `idx_system_metrics_timestamp`: 时间戳索引，优化时间范围查询
- `idx_system_metrics_status`: 状态索引，快速筛选异常记录
- `idx_system_metrics_created_at`: 创建时间索引

### system_alerts
存储系统告警记录

**主要字段:**
- `alert_type`: 告警类型 (cpu/memory/disk/database/redis/storage/celery)
- `severity`: 严重程度 (info/warning/critical)
- `title`: 告警标题
- `message`: 告警消息
- `metric_name`: 相关指标名称
- `metric_value`: 指标当前值
- `threshold_value`: 阈值
- `status`: 告警状态 (active/resolved/ignored)
- `triggered_at`: 触发时间
- `resolved_at`: 解决时间
- `acknowledged_by`: 确认人ID
- `acknowledged_at`: 确认时间
- `notes`: 处理备注

**索引:**
- `idx_system_alerts_type_severity`: 类型和严重程度复合索引
- `idx_system_alerts_status`: 状态索引
- `idx_system_alerts_triggered_at`: 触发时间索引

### system_sla
存储SLA统计数据

**主要字段:**
- `period_start`: 统计周期开始时间
- `period_end`: 统计周期结束时间
- `period_type`: 周期类型 (hourly/daily/weekly/monthly)
- `uptime_percentage`: 可用性百分比
- `avg_response_time_ms`: 平均响应时间
- `p50/p95/p99_response_time_ms`: 响应时间百分位数
- `total_alerts`: 总告警数
- `critical_alerts`: 严重告警数
- `avg_cpu_usage`: 平均CPU使用率
- `avg_memory_usage`: 平均内存使用率

**索引:**
- `idx_system_sla_period`: 周期起止时间复合索引
- `idx_system_sla_type`: 周期类型索引

## 配置调优

### 告警阈值调整

可以在 `app/services/alert_service.py` 的 `AlertThresholds` 类中修改告警阈值：

```python
class AlertThresholds:
    # CPU 告警阈值
    CPU_WARNING = 70.0
    CPU_CRITICAL = 90.0

    # 内存告警阈值
    MEMORY_WARNING = 80.0
    MEMORY_CRITICAL = 95.0

    # 根据实际业务需求调整...
```

### 缓存配置

健康检查API使用Redis缓存，默认TTL为5秒。可在 `app/admin/system_health.py` 中调整：

```python
CACHE_TTL = 5  # 秒
```

### 存储容量配置

MinIO存储总容量默认为1TB，可在 `app/admin/system_health.py` 的 `check_minio_health()` 函数中调整：

```python
response["total_gb"] = 1000.0  # 修改为实际容量
```

或者通过环境变量配置（推荐）：

```bash
# .env
MINIO_STORAGE_CAPACITY_GB=2000
```

## 监控最佳实践

### 1. 告警处理流程

1. **接收告警**: 通过 `/alerts` API或前端监控面板查看活跃告警
2. **确认告警**: 使用 `/alerts/{id}/acknowledge` 确认已知晓
3. **调查问题**: 查看告警上下文数据和历史指标趋势
4. **解决问题**: 采取必要措施（扩容、优化、重启等）
5. **标记解决**: 使用 `/alerts/{id}/resolve` 标记为已解决

### 2. SLA监控

- **每日检查**: 查看 `/sla/current` 了解当天实时SLA
- **每周回顾**: 查看 `/sla/report?period_type=daily&limit=7` 分析周趋势
- **每月总结**: 查看 `/sla/summary?days=30` 生成月度报告

### 3. 容量规划

定期查看以下指标进行容量规划：

- **存储增长率**: 观察 `storage_used_gb` 的增长趋势
- **数据库连接池**: 监控 `db_pool_utilization`，超过80%考虑扩容
- **任务队列**: 监控 `celery_active_tasks`，持续高位考虑增加Worker

### 4. 性能优化

根据SLA报告优化系统性能：

- **响应时间**: P95和P99超标时检查慢查询和缓存命中率
- **可用性**: 低于99.9%时检查告警历史找出问题根源
- **资源使用**: CPU/内存持续高位时进行代码和配置优化

## 故障排查

### 指标未收集

**症状**: `/sla/generate` 返回 "No metrics data available"

**检查:**
1. 确认健康检查API是否正常: `curl http://localhost:8000/api/v1/admin/system-health/health`
2. 检查数据库表是否存在: `SELECT COUNT(*) FROM system_metrics;`
3. 查看应用日志是否有错误

**解决:**
- 确保定期调用 `/health` API（前端每5秒自动调用）
- 检查数据库迁移是否已应用: `alembic current`

### Celery任务不执行

**症状**: 定时SLA报告未生成

**检查:**
1. Celery Worker是否运行: `ps aux | grep celery`
2. Celery Beat是否运行
3. 查看Celery日志

**解决:**
```bash
# 启动Worker
celery -A app.celery_app worker --loglevel=info

# 启动Beat
celery -A app.celery_app beat --loglevel=info
```

### 告警风暴

**症状**: 大量重复告警

**原因**: 系统在阈值边界波动

**解决:**
- 告警系统已内置1小时去重机制
- 考虑调整告警阈值或增加缓冲区间
- 优化系统性能，消除波动根源

## 前端集成示例

### 实时监控面板

```typescript
// 定时获取健康状态
const fetchHealthStatus = async () => {
  const response = await api.get('/api/v1/admin/system-health/health');
  return response.data;
};

// 每5秒刷新一次
useEffect(() => {
  const interval = setInterval(() => {
    fetchHealthStatus().then(setHealthData);
  }, 5000);

  return () => clearInterval(interval);
}, []);
```

### 告警徽章

```typescript
// 获取活跃告警数量
const fetchAlertCount = async () => {
  const response = await api.get('/api/v1/admin/system-health/alerts/active/count');
  return response.data;
};

// 显示徽章
<Badge count={alertCount.critical} status="error">
  <BellOutlined />
</Badge>
```

### SLA趋势图

```typescript
// 获取最近7天SLA
const fetchSLATrend = async () => {
  const response = await api.get('/api/v1/admin/system-health/sla/report', {
    params: { period_type: 'daily', limit: 7 }
  });
  return response.data.records;
};

// 使用图表库展示趋势
<LineChart data={slaRecords}>
  <Line dataKey="uptime_percentage" name="可用性" />
  <Line dataKey="avg_response_time_ms" name="响应时间" />
</LineChart>
```

## 总结

系统监控增强功能提供了完整的监控、告警和SLA追踪能力：

✅ **自动化**: 指标自动收集、告警自动触发、SLA自动计算
✅ **全面性**: 覆盖数据库、缓存、存储、任务队列、系统资源
✅ **可靠性**: 告警去重、自动解决、历史记录完整
✅ **可扩展**: 易于添加新的监控指标和告警规则

通过合理使用这些功能，可以大幅提升系统可观测性和运维效率。
