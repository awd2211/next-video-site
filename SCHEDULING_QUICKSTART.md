# 内容调度系统 - 快速上手指南

## 🚀 5分钟快速启动

### 1. 安装 FullCalendar 依赖（前端）

```bash
cd admin-frontend
pnpm install @fullcalendar/react @fullcalendar/daygrid @fullcalendar/timegrid @fullcalendar/interaction
```

### 2. 启动 Celery 服务（后端）

```bash
cd backend
source venv/bin/activate

# Terminal 1: 启动 Worker
celery -A app.celery_app worker --loglevel=info -Q scheduler,default

# Terminal 2: 启动 Beat（定时调度）
celery -A app.celery_app beat --loglevel=info
```

### 3. 访问日历视图

在浏览器中访问管理后台，导航到：
```
http://localhost:3001/scheduling/calendar
```

---

## ✨ 新功能亮点

### 🤖 自动化调度
- **每分钟自动执行到期任务**
- 无需手动点击"发布"
- 按优先级智能执行
- 失败自动重试

### 📊 智能分析
- **每日自动报告**：每天凌晨2点生成
- **冲突检测**：每小时检查调度冲突
- **健康监控**：每30分钟检查系统状态
- **负载优化**：每6小时优化调度分布

### 📅 可视化日历
- **月/周/日三种视图**
- **拖拽式导航**
- **颜色编码**：按状态和类型
- **事件详情**：点击查看完整信息

---

## 📝 使用场景示例

### 场景1: 定时发布视频

1. 创建调度任务：
   - 内容类型: Video
   - 内容ID: 123
   - 计划时间: 2025-10-15 20:00
   - 优先级: 80（高优先级）

2. 系统自动处理：
   - ✅ 2025-10-15 20:00 自动发布
   - ✅ 发布成功后标记为 "published"
   - ✅ 创建历史记录
   - ✅ 发送通知（如果开启）

### 场景2: 横幅定时上下线

1. 创建调度任务：
   - 内容类型: Banner
   - 内容ID: 456
   - 计划时间: 2025-10-16 08:00
   - 结束时间: 2025-10-16 20:00
   - 自动过期: 开启

2. 系统自动处理：
   - ✅ 08:00 自动激活横幅
   - ✅ 20:00 自动停用横幅
   - ✅ 全程无需人工干预

### 场景3: 周期性公告

1. 创建调度任务：
   - 内容类型: Announcement
   - 内容ID: 789
   - 计划时间: 2025-10-17 09:00
   - 重复类型: 每日

2. 系统自动处理：
   - ✅ 每天09:00自动发布
   - ✅ 自动创建下一天的调度
   - ✅ 持续执行直到手动取消

---

## 🔔 通知类型

### 执行失败通知
```
🚨 调度任务执行失败
- 失败数量: 3
- Schedule #123: Video:456 - Database connection error
- Schedule #124: Banner:789 - Content not found
```

### 冲突检测通知
```
⚠️ 检测到 2 个调度冲突
- 重复内容: video:123 有 3 个待执行调度
- 高并发: 2025-10-15 20:00-20:05 有 8 个任务
```

### 每日报告
```
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

## 🎯 最佳实践

### 1. 设置合理的优先级
```
- 80-100: 重要内容（首页推荐、热门视频）
- 50-79:  普通内容（常规视频发布）
- 0-49:   低优先级（测试内容、备份任务）
```

### 2. 避免同一时间过多任务
```
✅ 好的做法：
  - 20:00 发布 3 个视频
  - 20:05 发布 2 个横幅
  - 20:10 发布 1 个公告

❌ 避免：
  - 20:00 同时发布 10+ 个任务
```

### 3. 使用通知功能
```python
# 重要任务开启提前通知
notify_subscribers = True
notify_before_minutes = 15  # 提前15分钟通知
```

### 4. 定期检查健康状态
```
- 访问 /admin/scheduling 查看统计
- 关注"过期未执行"数量
- 查看失败任务原因
```

---

## 🛠️ 常用命令

### Celery 管理

```bash
# 查看活跃任务
celery -A app.celery_app inspect active

# 查看已注册任务
celery -A app.celery_app inspect registered

# 查看任务统计
celery -A app.celery_app inspect stats

# 清空所有任务
celery -A app.celery_app purge

# 重启 Worker（使配置生效）
pkill -9 celery
celery -A app.celery_app worker --loglevel=info -Q scheduler,default
```

### 监控命令

```bash
# 启动 Flower 监控面板
celery -A app.celery_app flower --port=5555

# 实时查看日志
tail -f logs/celery-worker.log
tail -f logs/celery-beat.log

# 检查 Redis 队列
redis-cli LLEN celery  # 队列长度
redis-cli KEYS "celery-task-meta-*" | wc -l  # 任务结果数
```

---

## 🔥 高级功能预览

### 1. Cron 表达式支持（计划中）

```python
# 未来支持：
recurrence_cron = "0 9,12,18 * * 1-5"  # 周一到周五的 9点、12点、18点
```

### 2. 审批工作流（计划中）

```python
# 未来支持：
approval_required = True
approval_workflow_id = 1  # 使用预定义的审批流程
```

### 3. A/B 测试（计划中）

```python
# 未来支持：
publish_strategy = "ab_test"
strategy_config = {
    "group_a": {"content_id": 123, "percentage": 50},
    "group_b": {"content_id": 456, "percentage": 50}
}
```

---

## 📞 需要帮助？

### 常见问题

**Q: 任务没有自动执行？**
A: 检查 Celery Beat 是否运行：`ps aux | grep "celery beat"`

**Q: 如何查看任务执行历史？**
A: 访问 `/admin/scheduling/history` 或查询 `schedule_histories` 表

**Q: 如何调整任务执行频率？**
A: 编辑 `backend/app/celery_app.py` 中的 `beat_schedule`

**Q: 日历视图不显示数据？**
A: 检查 API `/api/v1/admin/scheduling/calendar` 是否返回数据

---

## 🎉 开始使用

1. ✅ 启动 Celery Worker 和 Beat
2. ✅ 创建第一个调度任务
3. ✅ 在日历视图中查看
4. ✅ 等待自动执行或手动触发
5. ✅ 查看执行结果和通知

**祝您使用愉快！** 🚀

---

**文档版本**: 1.0
**最后更新**: 2025-10-14
