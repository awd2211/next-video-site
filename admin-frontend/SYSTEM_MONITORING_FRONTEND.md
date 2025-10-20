# 系统监控前端更新文档

## 概述

本文档详细说明了系统监控增强功能的前端实现，包括健康监控、告警管理和SLA报告页面。

## 新增文件

### 1. 服务层文件

**文件**: `src/services/systemHealthService.ts`

**功能**: 提供所有系统监控相关的API调用函数

**导出的类型**:
- `ServiceStatus` - 服务状态基础接口
- `DatabaseHealth` - 数据库健康状态
- `RedisHealth` - Redis健康状态
- `StorageHealth` - 存储健康状态（新增字段：used_gb, total_gb, utilization_percent, object_count）
- `CeleryHealth` - Celery健康状态（新增）
- `SystemResources` - 系统资源状态
- `AlertStatistics` - 告警统计
- `HealthData` - 完整健康数据（新增alerts字段）
- `SystemAlert` - 告警对象
- `SLARecord` - SLA记录
- `CurrentSLA` - 当前SLA状态

**导出的函数**:

健康监控:
- `getSystemHealth(useCache?: boolean)` - 获取系统健康状态
- `getSystemMetrics(useCache?: boolean)` - 获取系统指标
- `getMetricsHistory(limit?: number)` - 获取历史指标
- `getSystemInfo()` - 获取系统信息

告警管理:
- `getAlerts(params?)` - 获取告警列表
- `getAlertStatistics()` - 获取告警统计
- `getActiveAlertsCount()` - 获取活跃告警数量
- `acknowledgeAlert(alertId, notes?)` - 确认告警
- `resolveAlert(alertId, notes?)` - 解决告警

SLA追踪:
- `getSLAReport(params?)` - 获取SLA报告
- `getSLASummary(days?)` - 获取SLA汇总
- `getCurrentSLA()` - 获取当前SLA
- `generateSLAReport(periodType)` - 手动生成SLA报告

### 2. 页面组件

#### SystemHealth/index.tsx (已更新)

**路由**: `/system-health`

**新增功能**:
1. **Celery监控卡片**
   - Workers数量（带颜色徽章）
   - 活跃任务数
   - 保留任务数
   - 状态消息

2. **存储使用详情**
   - 已用空间（GB）
   - 对象数量
   - 使用率进度条
   - Bucket状态

3. **告警摘要横幅**
   - 显示活跃告警总数
   - 严重/警告分类统计
   - 24小时已解决告警数
   - 链接到详情页

**布局调整**:
- 服务卡片从3列改为4列（Database, Redis, Storage, Celery）
- 每列宽度：`xs={24} lg={6}`

**API集成**:
```typescript
import { getSystemHealth, type HealthData } from '@/services/systemHealthService';

const { data } = useQuery<HealthData>({
  queryKey: ['system-health'],
  queryFn: () => getSystemHealth(true),
  refetchInterval: autoRefresh ? refreshInterval : false,
});
```

#### SystemHealth/Alerts.tsx (新建)

**建议路由**: `/system-health/alerts`

**功能**:
1. **告警统计卡片** (4个)
   - 活跃告警总数
   - 严重告警数
   - 警告数
   - 24小时已解决数

2. **过滤器**
   - 状态过滤：Active / Resolved / All
   - 严重程度过滤：Critical / Warning / Info
   - 类型过滤：CPU / Memory / Disk / Database / Redis / Storage / Celery

3. **告警表格**
   - 列：Severity, Type, Title, Message, Metric, Status, Triggered At, Actions
   - 可展开行显示详细信息（Context, Notes等）
   - 分页支持
   - 自动每30秒刷新

4. **操作功能**
   - Acknowledge（确认告警）
   - Resolve（解决告警）
   - 添加备注

**关键组件**:
```typescript
// 确认告警
const acknowledgeMutation = useMutation({
  mutationFn: ({ id, notes }) => acknowledgeAlert(id, notes),
  onSuccess: () => {
    message.success('Alert acknowledged successfully');
    queryClient.invalidateQueries({ queryKey: ['system-alerts'] });
  }
});

// 解决告警
const resolveMutation = useMutation({
  mutationFn: ({ id, notes }) => resolveAlert(id, notes),
  onSuccess: () => {
    message.success('Alert resolved successfully');
  }
});
```

#### SystemHealth/SLAReport.tsx (新建)

**建议路由**: `/system-health/sla`

**功能**:
1. **当前SLA状态卡片** (今日实时)
   - Uptime百分比（带颜色编码）
   - 已运行时间
   - 平均响应时间
   - 活跃告警数
   - 状态标签（Healthy / Degraded / Poor）

2. **汇总统计卡片** (可配置天数)
   - 平均Uptime
   - 总Downtime
   - 总告警数
   - 平均响应时间

3. **表格视图**
   - 周期选择：Hourly / Daily / Weekly / Monthly
   - 记录数限制：10 / 30 / 60 / 90
   - 列分组：
     - Period（时间段）
     - Uptime（可用性+进度条）
     - Response Time（Avg / P95 / P99）
     - Alerts（Total / Critical / Warning）
     - Resource Usage（CPU / Memory / Disk）

4. **图表视图**
   - Uptime趋势图（折线图）
     - Y轴范围：98%-100%
     - 目标线：99.9%
   - Response Time趋势图（多线图）
     - Average / P95 / P99三条线

5. **手动操作**
   - Generate Hourly Report按钮
   - Generate Daily Report按钮
   - Refresh按钮

**图表配置**:
```typescript
// Uptime趋势图
<Line
  data={uptimeChartData}
  xField="date"
  yField="uptime"
  yAxis={{ min: 98, max: 100 }}
  annotations={[
    {
      type: 'line',
      start: ['min', 99.9],
      end: ['max', 99.9],
      text: { content: 'Target: 99.9%' }
    }
  ]}
/>

// Response Time趋势图
<Line
  data={responseTimeChartData}
  xField="date"
  yField="value"
  seriesField="type"  // Average, P95, P99
  smooth
/>
```

## 路由配置建议

需要在路由配置文件中添加以下路由（通常在 `src/routes.tsx` 或 `src/App.tsx`）:

```typescript
{
  path: '/system-health',
  element: <SystemHealth />,  // 已存在，已更新
},
{
  path: '/system-health/alerts',
  element: <SystemAlerts />,  // 新增
},
{
  path: '/system-health/sla',
  element: <SLAReportPage />,  // 新增
}
```

## 菜单配置建议

在侧边栏菜单中添加子菜单：

```typescript
{
  key: 'system-health',
  icon: <HeartOutlined />,
  label: 'System Health',
  children: [
    {
      key: '/system-health',
      label: 'Overview',
    },
    {
      key: '/system-health/alerts',
      label: 'Alerts',
      // 可选：显示徽章
      badge: activeAlertCount,
    },
    {
      key: '/system-health/sla',
      label: 'SLA Reports',
    },
  ],
}
```

## 依赖项

确保已安装以下依赖：

```json
{
  "@ant-design/charts": "^1.x",  // 图表库
  "@tanstack/react-query": "^4.x",  // 数据获取
  "antd": "^5.x",  // UI组件库
  "dayjs": "^1.x",  // 日期处理
  "react-i18next": "^12.x"  // 国际化（可选）
}
```

如果缺少 `@ant-design/charts`，需要安装：

```bash
pnpm add @ant-design/charts
```

## 颜色编码规范

### 可用性状态
- **Healthy** (>=99.9%): `#52c41a` (绿色)
- **Degraded** (>=99.0%): `#faad14` (橙色)
- **Unhealthy** (<99.0%): `#f5222d` (红色)

### 告警严重程度
- **Critical**: `red`
- **Warning**: `orange`
- **Info**: `blue`

### 告警类型
- **CPU**: `blue`
- **Memory**: `cyan`
- **Disk**: `purple`
- **Database**: `green`
- **Redis**: `red`
- **Storage**: `orange`
- **Celery**: `magenta`

## 自动刷新配置

### SystemHealth页面
- 默认刷新间隔：10秒
- 可选：5秒 / 10秒 / 30秒 / 1分钟
- 支持手动开关自动刷新

### Alerts页面
- 固定刷新间隔：30秒

### SLA页面
- 当前SLA刷新间隔：60秒（仅当前状态）
- 历史报告：手动刷新

## API端点映射

| 前端函数 | 后端端点 | 方法 |
|---------|---------|------|
| getSystemHealth() | /api/v1/admin/system-health/health | GET |
| getSystemMetrics() | /api/v1/admin/system-health/metrics | GET |
| getMetricsHistory() | /api/v1/admin/system-health/history | GET |
| getSystemInfo() | /api/v1/admin/system-health/info | GET |
| getAlerts() | /api/v1/admin/system-health/alerts | GET |
| getAlertStatistics() | /api/v1/admin/system-health/alerts/statistics | GET |
| getActiveAlertsCount() | /api/v1/admin/system-health/alerts/active/count | GET |
| acknowledgeAlert() | /api/v1/admin/system-health/alerts/{id}/acknowledge | POST |
| resolveAlert() | /api/v1/admin/system-health/alerts/{id}/resolve | POST |
| getSLAReport() | /api/v1/admin/system-health/sla/report | GET |
| getSLASummary() | /api/v1/admin/system-health/sla/summary | GET |
| getCurrentSLA() | /api/v1/admin/system-health/sla/current | GET |
| generateSLAReport() | /api/v1/admin/system-health/sla/generate | POST |

## 国际化（i18n）支持

如果项目启用了国际化，建议添加以下翻译键：

```json
{
  "systemHealth": {
    "title": "System Health",
    "overview": "Overview",
    "alerts": "Alerts",
    "sla": "SLA Reports",
    "healthy": "Healthy",
    "degraded": "Degraded",
    "unhealthy": "Unhealthy",
    "refreshInterval": "Refresh Interval",
    "lastUpdated": "Last Updated",
    "activeAlerts": "Active Alerts",
    "criticalAlerts": "Critical Alerts",
    "warnings": "Warnings",
    "resolved24h": "Resolved (24h)"
  }
}
```

## 测试建议

### 单元测试
```typescript
// systemHealthService.test.ts
describe('systemHealthService', () => {
  test('getSystemHealth should fetch health data', async () => {
    const data = await getSystemHealth(true);
    expect(data).toHaveProperty('overall_status');
    expect(data.services).toHaveProperty('celery');
  });

  test('getAlerts should support pagination', async () => {
    const data = await getAlerts({ page: 1, page_size: 20 });
    expect(data).toHaveProperty('items');
    expect(data).toHaveProperty('total');
  });
});
```

### 集成测试
1. 测试告警确认流程
2. 测试告警解决流程
3. 测试SLA报告生成
4. 测试图表数据渲染

## 性能优化

### 1. React Query缓存
所有查询已配置适当的缓存策略：
- 健康状态：5-60秒刷新
- 告警列表：30秒刷新
- SLA报告：手动刷新

### 2. 表格虚拟滚动
对于大量告警数据，可以启用虚拟滚动：
```typescript
<Table
  virtual
  scroll={{ y: 600 }}
  // ...其他配置
/>
```

### 3. 图表懒加载
```typescript
import { lazy, Suspense } from 'react';

const LineChart = lazy(() => import('@ant-design/charts').then(m => ({ default: m.Line })));

// 使用时
<Suspense fallback={<Spin />}>
  <LineChart {...config} />
</Suspense>
```

## 故障排查

### 问题：告警列表不显示
**检查**:
1. 后端API是否正常：`curl http://localhost:8000/api/v1/admin/system-health/alerts`
2. 浏览器控制台是否有错误
3. 确认用户有管理员权限

### 问题：图表不显示
**检查**:
1. 是否安装 `@ant-design/charts`
2. 数据格式是否正确
3. 浏览器控制台是否有警告

### 问题：SLA报告为空
**检查**:
1. 后端是否有历史数据：查询 `system_sla` 表
2. 确认Celery定时任务是否运行
3. 手动触发报告生成测试

## 后续改进建议

1. **实时通知**
   - 使用WebSocket推送新告警
   - 浏览器通知API集成

2. **导出功能**
   - 导出SLA报告为PDF
   - 导出告警列表为CSV

3. **自定义仪表板**
   - 允许用户自定义监控面板
   - 拖拽式组件布局

4. **告警规则配置**
   - 前端界面配置告警阈值
   - 自定义告警通知渠道

5. **移动端优化**
   - 响应式布局改进
   - 移动端专用视图

## 总结

前端更新已完整实现了系统监控增强功能的所有界面：

✅ **SystemHealth页面更新** - 新增Celery和存储监控
✅ **Alerts页面** - 完整的告警管理功能
✅ **SLA Report页面** - 可视化SLA报告和趋势分析
✅ **systemHealthService** - 统一的API服务层
✅ **类型定义** - 完整的TypeScript类型支持

所有功能已准备就绪，只需配置路由即可使用！
