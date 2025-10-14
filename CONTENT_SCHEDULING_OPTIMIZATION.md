# 内容调度系统优化实施方案

> 作者: Claude Code
> 日期: 2025-10-14
> 状态: 部分完成 - 数据库层和模型层已实现

---

## 📋 项目概述

本文档记录了视频流媒体平台内容调度系统的全面优化方案。该优化旨在将原有的基础定时发布功能升级为一个功能完善、业务场景丰富的企业级调度系统。

---

## ✅ 已完成工作

### 1. 数据库模型设计 ✓

创建了统一的内容调度数据库模型，支持多种内容类型的调度管理：

#### 核心表结构

**`content_schedules` - 统一内容调度表**
- 支持内容类型：视频、横幅、公告、推荐位、系列
- 调度状态：pending, published, failed, cancelled, expired
- 发布策略：immediate（立即）, progressive（渐进式）, regional（区域定时）, ab_test（AB测试）
- 重复类型：once（一次性）, daily（每日）, weekly（每周）, monthly（每月）
- 条件发布：支持设置发布前置条件
- 通知机制：支持订阅者通知和提前通知
- 错误处理：自动重试机制（最多3次）

**关键字段说明：**
```python
content_type: ScheduleContentType  # VIDEO, BANNER, ANNOUNCEMENT, RECOMMENDATION, SERIES
content_id: int                     # 关联的内容ID
scheduled_time: datetime            # 计划发布时间
actual_publish_time: datetime       # 实际发布时间
end_time: datetime                  # 自动下线时间
status: ScheduleStatus              # 调度状态
publish_strategy: PublishStrategy   # 发布策略
strategy_config: JSONB              # 策略详细配置
recurrence: ScheduleRecurrence      # 重复类型
recurrence_config: JSONB            # 重复规则配置
notify_subscribers: bool            # 是否通知订阅者
notify_before_minutes: int          # 提前通知分钟数
condition_type: str                 # 条件类型
condition_value: JSONB              # 条件参数
priority: int                       # 优先级
retry_count: int                    # 当前重试次数
max_retry: int                      # 最大重试次数
```

**`schedule_templates` - 调度模板表**
- 保存常用发布策略配置
- 支持多种内容类型
- 记录使用次数统计
- 区分系统模板和用户自定义模板

**`schedule_histories` - 调度历史表**
- 记录所有调度操作
- 审计追踪
- 性能指标（执行耗时）
- 支持错误回溯

#### 数据库迁移

迁移文件: `backend/alembic/versions/81dc6d5bbe3a_add_unified_content_scheduling_system.py`

创建了以下枚举类型：
- `ScheduleContentType`
- `ScheduleStatus`
- `PublishStrategy`
- `ScheduleRecurrence`

已应用到数据库：✅

---

## 🎯 业务场景支持

### 1. 视频定时发布
- **场景**: 剧集每日定时更新
- **配置**: 设置重复类型为 DAILY，指定每天发布时间
- **通知**: 自动通知订阅用户

### 2. 横幅轮播调度
- **场景**: 首页横幅定时切换，营销活动期间特殊横幅
- **配置**: 设置 start_time 和 end_time 实现自动上下线
- **策略**: 支持区域定时（不同地区不同横幅）

### 3. 公告管理
- **场景**: 系统维护公告、活动通知定时发布和过期
- **配置**: 设置 scheduled_time 和 end_time
- **提醒**: 支持提前15分钟通知管理员

### 4. 推荐位管理
- **场景**: 首页推荐、分类推荐定时切换
- **配置**: 周期性更新推荐内容（每周、每月）
- **策略**: AB测试不同推荐算法效果

### 5. 营销活动
- **场景**: 限时优惠、节日专题、会员活动
- **配置**: 精确控制活动开始和结束时间
- **策略**: 渐进式发布（先小范围测试，再全量）

---

## 🛠️ 技术实现

### 文件结构

```
backend/
├── app/
│   ├── models/
│   │   └── scheduling.py          ✅ 已完成 - 数据库模型
│   ├── schemas/
│   │   └── scheduling.py          ⏳ 待实现 - Pydantic验证模式
│   ├── services/
│   │   └── scheduling_service.py  ⏳ 待实现 - 业务逻辑层
│   ├── admin/
│   │   └── scheduling.py          ⏳ 待实现 - 管理API（替换现有scheduled_content.py）
│   ├── tasks/
│   │   └── scheduled_publish.py   ⏳ 待实现 - Celery定时任务
│   └── utils/
│       └── schedule_executor.py   ⏳ 待实现 - 调度执行器
├── alembic/versions/
│   └── 81dc6d5bbe3a_*.py         ✅ 已完成 - 数据库迁移
```

### 核心功能模块

#### 1. 调度执行器 (ScheduleExecutor)
```python
class ScheduleExecutor:
    """
    调度执行器 - 负责执行调度任务
    """
    async def execute_schedule(self, schedule: ContentSchedule) -> bool:
        """执行调度任务"""
        pass

    async def publish_video(self, video_id: int) -> bool:
        """发布视频"""
        pass

    async def activate_banner(self, banner_id: int) -> bool:
        """激活横幅"""
        pass

    async def publish_announcement(self, announcement_id: int) -> bool:
        """发布公告"""
        pass

    async def update_recommendation(self, recommendation_id: int) -> bool:
        """更新推荐位"""
        pass
```

#### 2. Celery Beat 定时任务
```python
@celery_app.task
def check_due_schedules():
    """
    每分钟检查一次到期的调度任务
    由 Celery Beat 定时触发
    """
    pass

@celery_app.task
def check_expired_schedules():
    """
    每小时检查一次过期的内容
    自动下线到达 end_time 的内容
    """
    pass

@celery_app.task
def send_schedule_reminders():
    """
    每5分钟检查一次需要提前通知的任务
    """
    pass
```

#### 3. API 端点设计

**基础CRUD**
- `POST /api/v1/admin/scheduling/` - 创建调度任务
- `GET /api/v1/admin/scheduling/` - 获取调度列表（支持筛选）
- `GET /api/v1/admin/scheduling/{id}` - 获取调度详情
- `PUT /api/v1/admin/scheduling/{id}` - 更新调度
- `DELETE /api/v1/admin/scheduling/{id}` - 取消调度

**批量操作**
- `POST /api/v1/admin/scheduling/batch` - 批量创建调度
- `PUT /api/v1/admin/scheduling/batch/update` - 批量更新
- `DELETE /api/v1/admin/scheduling/batch/cancel` - 批量取消

**模板管理**
- `GET /api/v1/admin/scheduling/templates/` - 获取模板列表
- `POST /api/v1/admin/scheduling/templates/` - 创建模板
- `POST /api/v1/admin/scheduling/templates/{id}/apply` - 应用模板

**执行控制**
- `POST /api/v1/admin/scheduling/{id}/execute` - 手动触发执行
- `POST /api/v1/admin/scheduling/{id}/rollback` - 回滚已发布的内容
- `POST /api/v1/admin/scheduling/execute-due` - 手动发布所有到期任务

**统计分析**
- `GET /api/v1/admin/scheduling/stats` - 调度统计信息
- `GET /api/v1/admin/scheduling/analytics` - 发布效果分析
- `GET /api/v1/admin/scheduling/calendar` - 日历视图数据
- `GET /api/v1/admin/scheduling/suggest-time` - 智能推荐发布时间

**历史查询**
- `GET /api/v1/admin/scheduling/{id}/history` - 获取调度历史
- `GET /api/v1/admin/scheduling/history` - 获取所有历史记录

---

## 📊 数据流程图

### 1. 创建调度任务流程

```
管理员创建调度
    ↓
验证内容是否存在
    ↓
检查时间是否合法
    ↓
应用模板（可选）
    ↓
保存到 content_schedules
    ↓
记录到 schedule_histories (action=created)
    ↓
如果有提前通知，计算提醒时间
    ↓
返回调度详情
```

### 2. 自动发布流程

```
Celery Beat 每分钟触发
    ↓
查询 status=PENDING && scheduled_time <= now()
    ↓
按优先级排序
    ↓
遍历到期任务
    ├─→ 检查条件是否满足
    ├─→ 获取内容详情
    ├─→ 根据内容类型执行相应操作
    │   ├─ VIDEO: 更新状态为 PUBLISHED
    │   ├─ BANNER: 设置为 ACTIVE
    │   ├─ ANNOUNCEMENT: 发布公告
    │   └─ RECOMMENDATION: 更新推荐位
    ├─→ 更新 actual_publish_time
    ├─→ 状态改为 PUBLISHED
    ├─→ 记录历史 (action=published)
    ├─→ 发送通知（如果启用）
    └─→ 处理重复任务（创建下次调度）
```

### 3. 渐进式发布流程

```
初始发布 (10%用户)
    ↓
监控指标 (24小时)
    ├─→ 播放率
    ├─→ 完播率
    ├─→ 评分
    └─→ 错误率
    ↓
指标正常？
    ├─ 是 → 扩大到 50%
    │       ├─ 监控 (24小时)
    │       └─→ 100% 全量发布
    └─ 否 → 暂停发布
            └─→ 通知管理员
```

---

## 🎨 前端界面设计

### 1. 调度列表页面

**功能特性：**
- 表格视图 + 日历视图切换
- 状态筛选（pending, published, failed, cancelled, expired）
- 内容类型筛选
- 时间范围筛选
- 搜索功能（按标题、内容ID）
- 批量操作工具栏

**表格列：**
- ID
- 标题
- 内容类型
- 计划时间
- 实际时间
- 状态标签
- 优先级
- 操作按钮（编辑、取消、立即执行）

### 2. 日历视图

**功能：**
- 月视图 / 周视图 / 日视图切换
- 拖拽调整发布时间
- 点击日期快速创建调度
- 不同内容类型用不同颜色标识
- 显示状态图标（待发布、已发布、失败）

### 3. 创建/编辑调度表单

**基本信息：**
- 内容类型选择
- 内容选择器（根据类型动态显示）
- 标题（可选，用于识别）
- 描述

**时间设置：**
- 计划发布时间（日期时间选择器）
- 结束时间（可选，用于自动下线）
- 重复类型选择
- 重复规则配置（根据类型显示）

**发布策略：**
- 策略类型选择（立即/渐进/区域/AB测试）
- 策略详细配置（根据类型显示）
- 优先级设置

**通知设置：**
- 是否通知订阅者
- 提前通知时间

**高级选项：**
- 条件发布设置
- 最大重试次数

### 4. 模板管理页面

**功能：**
- 系统模板展示（不可编辑）
- 用户自定义模板
- 创建新模板
- 应用模板到调度
- 使用统计显示

### 5. 统计仪表板

**指标卡片：**
- 待发布任务数
- 今日已发布数
- 本周发布数
- 失败任务数

**图表：**
- 发布时间分布（24小时热力图）
- 成功率趋势
- 不同内容类型占比
- 发布策略使用情况

**智能推荐：**
- 基于历史数据的最佳发布时间建议
- 用户活跃时段分析

---

## 🔄 迁移策略

### 从旧系统迁移

当前系统使用 `video.scheduled_publish_at` 字段，需要平滑迁移：

**步骤1: 数据迁移脚本**
```python
async def migrate_old_schedules():
    """
    将现有的 video.scheduled_publish_at 数据迁移到新表
    """
    videos = await db.execute(
        select(Video).where(Video.scheduled_publish_at.isnot(None))
    )

    for video in videos.scalars():
        schedule = ContentSchedule(
            content_type=ScheduleContentType.VIDEO,
            content_id=video.id,
            scheduled_time=video.scheduled_publish_at,
            status=ScheduleStatus.PENDING if video.status == VideoStatus.DRAFT else ScheduleStatus.PUBLISHED,
            auto_publish=True,
            publish_strategy=PublishStrategy.IMMEDIATE,
            recurrence=ScheduleRecurrence.ONCE,
            title=f"视频定时发布: {video.title}",
            created_by=1,  # 系统管理员
        )
        db.add(schedule)

    await db.commit()
```

**步骤2: 保持双写期**
- 新系统生效后，继续更新 `video.scheduled_publish_at`（3个月过渡期）
- 保证向后兼容

**步骤3: 废弃旧字段**
- 过渡期后，停止写入旧字段
- 创建新迁移移除 `video.scheduled_publish_at`

---

## 📈 性能优化

### 1. 数据库索引

已创建的索引：
```sql
CREATE INDEX ix_content_schedules_content_id ON content_schedules(content_id);
CREATE INDEX ix_content_schedules_content_type ON content_schedules(content_type);
CREATE INDEX ix_content_schedules_status ON content_schedules(status);
CREATE INDEX ix_content_schedules_scheduled_time ON content_schedules(scheduled_time);
CREATE INDEX ix_content_schedules_created_at ON content_schedules(created_at);
```

建议添加的复合索引：
```sql
-- 查询到期任务的高效索引
CREATE INDEX ix_content_schedules_due
ON content_schedules(status, scheduled_time)
WHERE status = 'PENDING';

-- 按内容类型和状态查询
CREATE INDEX ix_content_schedules_type_status
ON content_schedules(content_type, status);
```

### 2. 缓存策略

**Redis 缓存：**
- 模板列表（TTL: 1小时）
- 统计数据（TTL: 5分钟）
- 最近24小时调度列表（TTL: 1分钟）

**缓存失效：**
- 调度创建/更新/删除时清除相关缓存
- 发布完成后清除统计缓存

### 3. 批量操作优化

- 使用 `bulk_insert_mappings()` 进行批量插入
- 使用数据库事务确保原子性
- 异步执行大批量操作（Celery任务）

---

## 🔐 安全考虑

### 1. 权限控制

- 基于 RBAC 系统的权限验证
- 普通管理员：创建、编辑、取消自己的调度
- 高级管理员：管理所有调度、手动触发执行
- 超级管理员：模板管理、系统配置

### 2. 审计日志

- 所有操作记录在 `schedule_histories` 表
- 记录操作人、操作时间、操作类型
- 支持审计查询和导出

### 3. 数据验证

- 时间必须是未来时间
- 内容必须存在且有效
- 防止重复调度同一内容
- 优先级范围验证（0-100）

---

## 🧪 测试策略

### 1. 单元测试

```python
# tests/test_scheduling_service.py
async def test_create_schedule():
    """测试创建调度任务"""
    pass

async def test_execute_due_schedules():
    """测试执行到期任务"""
    pass

async def test_recurring_schedule():
    """测试重复任务"""
    pass

async def test_progressive_publishing():
    """测试渐进式发布"""
    pass
```

### 2. 集成测试

- 测试完整的发布流程
- 测试 Celery 任务执行
- 测试通知系统集成
- 测试回滚机制

### 3. 性能测试

- 大量调度任务的查询性能
- 批量创建性能
- Celery 任务执行效率
- 数据库并发操作

---

## 📝 待实现任务清单

### 高优先级 ⚠️

- [ ] **Celery Beat 配置** - 添加定时任务配置文件
- [ ] **调度服务层** - 实现核心业务逻辑
- [ ] **调度执行器** - 实现内容发布逻辑
- [ ] **API 端点重构** - 替换现有的 `scheduled_content.py`
- [ ] **Pydantic schemas** - 请求/响应验证模式

### 中优先级 📋

- [ ] **批量操作API** - 批量创建、更新、取消
- [ ] **模板管理** - 模板CRUD接口
- [ ] **通知集成** - 对接现有通知系统
- [ ] **数据迁移脚本** - 从旧系统迁移数据

### 低优先级 🎨

- [ ] **前端日历视图** - 可视化调度日历
- [ ] **拖拽调整** - 拖拽修改发布时间
- [ ] **智能推荐** - 基于数据的最佳时间推荐
- [ ] **A/B测试集成** - 发布策略实现
- [ ] **区域定时** - 基于地理位置的发布
- [ ] **统计报表** - 发布效果分析

---

## 🚀 部署步骤

### 1. 数据库迁移

```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

### 2. 数据迁移（可选）

```bash
python scripts/migrate_old_schedules.py
```

### 3. 配置 Celery Beat

编辑 `backend/celeryconfig.py`:

```python
beat_schedule = {
    'check-due-schedules': {
        'task': 'app.tasks.scheduled_publish.check_due_schedules',
        'schedule': 60.0,  # 每分钟
    },
    'check-expired-schedules': {
        'task': 'app.tasks.scheduled_publish.check_expired_schedules',
        'schedule': 3600.0,  # 每小时
    },
    'send-schedule-reminders': {
        'task': 'app.tasks.scheduled_publish.send_schedule_reminders',
        'schedule': 300.0,  # 每5分钟
    },
}
```

### 4. 启动 Celery Worker 和 Beat

```bash
# 启动 Worker
celery -A app.celery_app worker --loglevel=info

# 启动 Beat（另一个终端）
celery -A app.celery_app beat --loglevel=info
```

### 5. 重启应用

```bash
docker-compose restart backend
# 或
uvicorn app.main:app --reload
```

---

## 📚 相关文档

- [Celery 文档](https://docs.celeryproject.org/)
- [Celery Beat 调度](https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html)
- [SQLAlchemy 异步](https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html)
- [Alembic 迁移](https://alembic.sqlalchemy.org/en/latest/)
- [CLAUDE.md](./CLAUDE.md) - 项目开发指南

---

## 🤝 贡献指南

欢迎提交 PR 完善此功能！重点关注：

1. **Celery 任务实现** - 自动化调度核心
2. **API 端点完善** - RESTful 接口设计
3. **前端界面** - 日历视图和可视化
4. **测试覆盖** - 保证代码质量
5. **文档更新** - 保持文档同步

---

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 创建 GitHub Issue
- 项目讨论区

---

**生成时间**: 2025-10-14
**最后更新**: 2025-10-14
**当前状态**: 数据库层完成，服务层待实现

🤖 本文档由 [Claude Code](https://claude.com/claude-code) 生成
