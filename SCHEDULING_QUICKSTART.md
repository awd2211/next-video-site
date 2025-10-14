# 内容调度系统 - 快速启动指南

> 5分钟快速上手新的内容调度系统

---

## 🚀 快速启动

### 步骤1: 启动 Celery

打开两个终端：

**终端1 - 启动 Worker:**
```bash
cd /home/eric/video/backend
source venv/bin/activate
celery -A app.celery_app worker --loglevel=info
```

**终端2 - 启动 Beat:**
```bash
cd /home/eric/video/backend
source venv/bin/activate
celery -A app.celery_app beat --loglevel=info
```

### 步骤2: 启动后端

**终端3 - 启动 FastAPI:**
```bash
cd /home/eric/video/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 步骤3: 访问 API 文档

打开浏览器访问：`http://localhost:8000/api/docs`

找到 **Admin - Content Scheduling** 标签，查看所有可用的API。

---

## 📝 常用操作

### 1. 创建视频定时发布

```bash
curl -X POST "http://localhost:8000/api/v1/admin/scheduling/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "VIDEO",
    "content_id": 1,
    "scheduled_time": "2025-10-15T20:00:00Z",
    "title": "新剧集首播",
    "auto_publish": true,
    "notify_subscribers": true,
    "priority": 90
  }'
```

### 2. 查看所有待发布任务

```bash
curl "http://localhost:8000/api/v1/admin/scheduling/?status=pending" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. 手动执行到期任务

```bash
curl -X POST "http://localhost:8000/api/v1/admin/scheduling/execute-due" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. 查看统计信息

```bash
curl "http://localhost:8000/api/v1/admin/scheduling/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎯 业务场景示例

### 场景1: 剧集每日更新

```json
{
  "content_type": "VIDEO",
  "content_id": 101,
  "scheduled_time": "2025-10-15T20:00:00Z",
  "recurrence": "daily",
  "title": "《热播剧》第1集",
  "notify_subscribers": true,
  "priority": 90
}
```

### 场景2: 营销活动横幅

```json
{
  "content_type": "BANNER",
  "content_id": 5,
  "scheduled_time": "2025-10-20T00:00:00Z",
  "end_time": "2025-10-27T23:59:59Z",
  "auto_expire": true,
  "title": "双11活动横幅",
  "priority": 100
}
```

### 场景3: 系统维护公告

```json
{
  "content_type": "ANNOUNCEMENT",
  "content_id": 10,
  "scheduled_time": "2025-10-18T02:00:00Z",
  "end_time": "2025-10-18T06:00:00Z",
  "auto_expire": true,
  "notify_before_minutes": 60,
  "title": "凌晨维护公告"
}
```

---

## 🔍 监控调度状态

### 查看 Celery 日志

```bash
# Worker 日志
tail -f /var/log/celery-worker.log

# Beat 日志
tail -f /var/log/celery-beat.log
```

### 数据库查询

```sql
-- 查看所有待发布任务
SELECT id, content_type, content_id, scheduled_time, title, priority
FROM content_schedules
WHERE status = 'PENDING'
ORDER BY scheduled_time;

-- 查看今天已发布
SELECT COUNT(*) as published_today
FROM content_schedules
WHERE status = 'PUBLISHED'
  AND DATE(actual_publish_time) = CURRENT_DATE;

-- 查看失败任务
SELECT id, content_type, content_id, error_message, retry_count
FROM content_schedules
WHERE status = 'FAILED';
```

---

## ⚠️ 常见问题

### Q: Celery Worker 不执行任务？

A: 检查：
1. Worker 是否正在运行：`ps aux | grep celery`
2. Redis 是否正常：`redis-cli ping`
3. 查看 Worker 日志确认错误

### Q: 任务执行失败？

A: 查看错误信息：
```bash
curl "http://localhost:8000/api/v1/admin/scheduling/{schedule_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

查看 `error_message` 和 `retry_count` 字段。

### Q: 如何取消调度？

A:
```bash
curl -X DELETE "http://localhost:8000/api/v1/admin/scheduling/{schedule_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📚 更多文档

- [完整实施报告](./CONTENT_SCHEDULING_IMPLEMENTATION_COMPLETE.md)
- [详细优化方案](./CONTENT_SCHEDULING_OPTIMIZATION.md)
- [项目开发指南](./CLAUDE.md)

---

🎉 **恭喜！你已经成功启动了内容调度系统！**

如有问题，请查看详细文档或联系开发团队。

🤖 Generated with [Claude Code](https://claude.com/claude-code)
