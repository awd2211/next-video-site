#!/usr/bin/env python3
"""
Fix SystemHealth pages hardcoded English text
Only update zh-CN and en-US (仅中英双语策略)
"""

import re
import json
from pathlib import Path
from typing import Dict, Any

# Translation mapping for SystemHealth pages
SYSTEMHEALTH_TRANSLATIONS = {
    # index.tsx - Service names and labels
    'Database (PostgreSQL)': {'key': 'systemHealth.services.database', 'zh': '数据库 (PostgreSQL)'},
    'Redis Cache': {'key': 'systemHealth.services.redis', 'zh': 'Redis 缓存'},
    'Object Storage (MinIO)': {'key': 'systemHealth.services.storage', 'zh': '对象存储 (MinIO)'},
    'Task Queue (Celery)': {'key': 'systemHealth.services.celery', 'zh': '任务队列 (Celery)'},
    'System Resources': {'key': 'systemHealth.resources.title', 'zh': '系统资源'},
    'Network Statistics': {'key': 'systemHealth.network.title', 'zh': '网络统计'},

    # Service details labels
    'Response Time': {'key': 'systemHealth.labels.responseTime', 'zh': '响应时间'},
    'Pool Size': {'key': 'systemHealth.labels.poolSize', 'zh': '连接池大小'},
    'Checked Out': {'key': 'systemHealth.labels.checkedOut', 'zh': '已签出'},
    'Available': {'key': 'systemHealth.labels.available', 'zh': '可用'},
    'Pool Utilization': {'key': 'systemHealth.labels.poolUtilization', 'zh': '连接池利用率'},
    'Used Memory': {'key': 'systemHealth.labels.usedMemory', 'zh': '已用内存'},
    'Max Memory': {'key': 'systemHealth.labels.maxMemory', 'zh': '最大内存'},
    'Keys Count': {'key': 'systemHealth.labels.keysCount', 'zh': '键数量'},
    'Memory Utilization': {'key': 'systemHealth.labels.memoryUtilization', 'zh': '内存利用率'},
    'Storage Used': {'key': 'systemHealth.labels.storageUsed', 'zh': '已用存储'},
    'Objects': {'key': 'systemHealth.labels.objects', 'zh': '对象数量'},
    'Utilization': {'key': 'systemHealth.labels.utilization', 'zh': '利用率'},
    'Bucket Status': {'key': 'systemHealth.labels.bucketStatus', 'zh': '存储桶状态'},
    'Workers': {'key': 'systemHealth.labels.workers', 'zh': '工作进程'},
    'Active Tasks': {'key': 'systemHealth.labels.activeTasks', 'zh': '活跃任务'},
    'Reserved Tasks': {'key': 'systemHealth.labels.reservedTasks', 'zh': '预留任务'},
    'Status': {'key': 'systemHealth.labels.status', 'zh': '状态'},

    # Resource types
    'CPU Usage': {'key': 'systemHealth.cpu.title', 'zh': 'CPU 使用率'},
    'Memory Usage': {'key': 'systemHealth.memory.title', 'zh': '内存使用率'},
    'Disk Usage': {'key': 'systemHealth.disk.title', 'zh': '磁盘使用率'},
    'Processes': {'key': 'systemHealth.processes.title', 'zh': '进程'},

    # Network stats
    'Data Sent': {'key': 'systemHealth.network.dataSent', 'zh': '已发送数据'},
    'Data Received': {'key': 'systemHealth.network.dataReceived', 'zh': '已接收数据'},
    'Packets Sent': {'key': 'systemHealth.network.packetsSent', 'zh': '已发送数据包'},
    'Packets Received': {'key': 'systemHealth.network.packetsReceived', 'zh': '已接收数据包'},

    # Tabs
    'Overview': {'key': 'systemHealth.tabs.overview', 'zh': '总览'},
    'Trends': {'key': 'systemHealth.tabs.trends', 'zh': '趋势'},

    # Chart titles
    'CPU Usage Trend': {'key': 'systemHealth.charts.cpuTrend', 'zh': 'CPU 使用趋势'},
    'Memory Usage Trend': {'key': 'systemHealth.charts.memoryTrend', 'zh': '内存使用趋势'},
    'Disk Usage Trend': {'key': 'systemHealth.charts.diskTrend', 'zh': '磁盘使用趋势'},
    'Database Response Time': {'key': 'systemHealth.charts.dbResponseTime', 'zh': '数据库响应时间'},
    'Redis Response Time': {'key': 'systemHealth.charts.redisResponseTime', 'zh': 'Redis 响应时间'},
    'Storage Response Time': {'key': 'systemHealth.charts.storageResponseTime', 'zh': '存储响应时间'},

    # Status labels
    'Active processes': {'key': 'systemHealth.processes.active', 'zh': '活跃进程'},
    'HEALTHY': {'key': 'systemHealth.status.healthy', 'zh': '健康'},
    'DEGRADED': {'key': 'systemHealth.status.degraded', 'zh': '降级'},
    'UNHEALTHY': {'key': 'systemHealth.status.unhealthy', 'zh': '不健康'},
    'EXISTS': {'key': 'systemHealth.bucket.exists', 'zh': '存在'},
    'NOT FOUND': {'key': 'systemHealth.bucket.notFound', 'zh': '未找到'},

    # Messages (index.tsx)
    'View Details': {'key': 'systemHealth.actions.viewDetails', 'zh': '查看详情'},

    # Alerts.tsx - Page title and buttons
    'System Alerts': {'key': 'systemHealth.alerts.title', 'zh': '系统告警'},
    'Refresh': {'key': 'common.refresh', 'zh': '刷新'},

    # Alerts statistics
    'Active Alerts': {'key': 'systemHealth.alerts.activeAlerts', 'zh': '活跃告警'},
    'Critical': {'key': 'systemHealth.alerts.critical', 'zh': '严重'},
    'Warnings': {'key': 'systemHealth.alerts.warnings', 'zh': '警告'},
    'Resolved (24h)': {'key': 'systemHealth.alerts.resolved24h', 'zh': '已解决(24小时)'},

    # Filters
    'Filters:': {'key': 'common.filters', 'zh': '筛选条件：'},

    # Table columns (Alerts.tsx)
    'Severity': {'key': 'systemHealth.alerts.columns.severity', 'zh': '严重程度'},
    'Type': {'key': 'systemHealth.alerts.columns.type', 'zh': '类型'},
    'Title': {'key': 'systemHealth.alerts.columns.title', 'zh': '标题'},
    'Message': {'key': 'systemHealth.alerts.columns.message', 'zh': '消息'},
    'Metric': {'key': 'systemHealth.alerts.columns.metric', 'zh': '指标'},
    'Triggered At': {'key': 'systemHealth.alerts.columns.triggeredAt', 'zh': '触发时间'},
    'Actions': {'key': 'common.actions', 'zh': '操作'},

    # Filter options (Alerts.tsx)
    'Info': {'key': 'systemHealth.alerts.severity.info', 'zh': '信息'},
    'Warning': {'key': 'systemHealth.alerts.severity.warning', 'zh': '警告'},
    'Active': {'key': 'systemHealth.alerts.status.active', 'zh': '活跃'},
    'Resolved': {'key': 'systemHealth.alerts.status.resolved', 'zh': '已解决'},
    'All': {'key': 'common.all', 'zh': '全部'},

    # Alert types
    'CPU': {'key': 'systemHealth.alerts.types.cpu', 'zh': 'CPU'},
    'Memory': {'key': 'systemHealth.alerts.types.memory', 'zh': '内存'},
    'Disk': {'key': 'systemHealth.alerts.types.disk', 'zh': '磁盘'},
    'Database': {'key': 'systemHealth.alerts.types.database', 'zh': '数据库'},
    'Redis': {'key': 'systemHealth.alerts.types.redis', 'zh': 'Redis'},
    'Storage': {'key': 'systemHealth.alerts.types.storage', 'zh': '存储'},
    'Celery': {'key': 'systemHealth.alerts.types.celery', 'zh': 'Celery'},

    # Actions
    'Acknowledge': {'key': 'systemHealth.alerts.actions.acknowledge', 'zh': '确认'},
    'Resolve': {'key': 'systemHealth.alerts.actions.resolve', 'zh': '解决'},
    'Acknowledged': {'key': 'systemHealth.alerts.status.acknowledged', 'zh': '已确认'},

    # Modal titles
    'Acknowledge Alert': {'key': 'systemHealth.alerts.modals.acknowledgeTitle', 'zh': '确认告警'},
    'Resolve Alert': {'key': 'systemHealth.alerts.modals.resolveTitle', 'zh': '解决告警'},

    # Modal labels
    'Alert: ': {'key': 'systemHealth.alerts.modals.alert', 'zh': '告警：'},
    'Message: ': {'key': 'systemHealth.alerts.modals.message', 'zh': '消息：'},
    'Add notes (optional)': {'key': 'systemHealth.alerts.modals.addNotes', 'zh': '添加备注（可选）'},
    'Add resolution notes (optional)': {'key': 'systemHealth.alerts.modals.addResolutionNotes', 'zh': '添加解决备注（可选）'},

    # Expanded row labels
    'Alert ID': {'key': 'systemHealth.alerts.details.alertId', 'zh': '告警ID'},
    'Metric Name': {'key': 'systemHealth.alerts.details.metricName', 'zh': '指标名称'},
    'Resolved At': {'key': 'systemHealth.alerts.details.resolvedAt', 'zh': '解决时间'},
    'Acknowledged By': {'key': 'systemHealth.alerts.details.acknowledgedBy', 'zh': '确认人'},
    'Acknowledged At': {'key': 'systemHealth.alerts.details.acknowledgedAt', 'zh': '确认时间'},
    'Notes': {'key': 'systemHealth.alerts.details.notes', 'zh': '备注'},
    'Context': {'key': 'systemHealth.alerts.details.context', 'zh': '上下文'},

    # Messages (Alerts.tsx)
    'Alert acknowledged successfully': {'key': 'systemHealth.alerts.messages.acknowledgeSuccess', 'zh': '告警已确认'},
    'Failed to acknowledge alert': {'key': 'systemHealth.alerts.messages.acknowledgeFailed', 'zh': '确认告警失败'},
    'Alert resolved successfully': {'key': 'systemHealth.alerts.messages.resolveSuccess', 'zh': '告警已解决'},
    'Failed to resolve alert': {'key': 'systemHealth.alerts.messages.resolveFailed', 'zh': '解决告警失败'},

    # SLAReport.tsx - Page title and buttons
    'SLA Reports': {'key': 'systemHealth.sla.title', 'zh': 'SLA 报告'},
    'Generate Hourly': {'key': 'systemHealth.sla.actions.generateHourly', 'zh': '生成小时报告'},
    'Generate Daily': {'key': 'systemHealth.sla.actions.generateDaily', 'zh': '生成日报'},

    # Current SLA section
    "Today's SLA (Real-time)": {'key': 'systemHealth.sla.todayTitle', 'zh': '今日 SLA（实时）'},
    'Uptime': {'key': 'systemHealth.sla.uptime', 'zh': '正常运行时间'},
    'Elapsed Time': {'key': 'systemHealth.sla.elapsedTime', 'zh': '已运行时长'},
    'Avg Response Time': {'key': 'systemHealth.sla.avgResponseTime', 'zh': '平均响应时间'},

    # Summary section
    'Summary (Last': {'key': 'systemHealth.sla.summaryPrefix', 'zh': '汇总（最近'},
    'Days)': {'key': 'systemHealth.sla.summarySuffix', 'zh': '天）'},
    'Average Uptime': {'key': 'systemHealth.sla.averageUptime', 'zh': '平均正常运行时间'},
    'Total Downtime': {'key': 'systemHealth.sla.totalDowntime', 'zh': '总停机时间'},
    'Total Alerts': {'key': 'systemHealth.sla.totalAlerts', 'zh': '总告警数'},

    # Table columns (SLAReport.tsx)
    'Period': {'key': 'systemHealth.sla.columns.period', 'zh': '时段'},
    'Response Time': {'key': 'systemHealth.sla.columns.responseTime', 'zh': '响应时间'},
    'Avg': {'key': 'systemHealth.sla.columns.avg', 'zh': '平均'},
    'Alerts': {'key': 'systemHealth.sla.columns.alerts', 'zh': '告警'},
    'Total': {'key': 'systemHealth.sla.columns.total', 'zh': '总计'},
    'Resource Usage': {'key': 'systemHealth.sla.columns.resourceUsage', 'zh': '资源使用'},

    # Tabs (SLAReport.tsx)
    'Table View': {'key': 'systemHealth.sla.tabs.tableView', 'zh': '表格视图'},
    'Charts': {'key': 'systemHealth.sla.tabs.charts', 'zh': '图表'},

    # Period types
    'Period Type:': {'key': 'systemHealth.sla.periodTypeLabel', 'zh': '时段类型：'},
    'Hourly': {'key': 'systemHealth.sla.periodTypes.hourly', 'zh': '小时'},
    'Daily': {'key': 'systemHealth.sla.periodTypes.daily', 'zh': '每日'},
    'Weekly': {'key': 'systemHealth.sla.periodTypes.weekly', 'zh': '每周'},
    'Monthly': {'key': 'systemHealth.sla.periodTypes.monthly', 'zh': '每月'},
    'Limit:': {'key': 'systemHealth.sla.limitLabel', 'zh': '限制：'},

    # Chart titles (SLAReport.tsx)
    'Uptime Trend': {'key': 'systemHealth.sla.charts.uptimeTrend', 'zh': '正常运行趋势'},
    'Response Time Trend': {'key': 'systemHealth.sla.charts.responseTimeTrend', 'zh': '响应时间趋势'},
    'Target: 99.9%': {'key': 'systemHealth.sla.charts.target', 'zh': '目标：99.9%'},

    # Messages (SLAReport.tsx)
    'SLA report generated successfully': {'key': 'systemHealth.sla.messages.generateSuccess', 'zh': 'SLA 报告已生成'},
    'Failed to generate SLA report': {'key': 'systemHealth.sla.messages.generateFailed', 'zh': '生成 SLA 报告失败'},

    # Common units and suffixes
    'hours': {'key': 'common.units.hours', 'zh': '小时'},
    'minutes': {'key': 'common.units.minutes', 'zh': '分钟'},
    'cores': {'key': 'common.units.cores', 'zh': '核心'},
    'free': {'key': 'common.units.free', 'zh': '可用'},
    'metrics collected': {'key': 'systemHealth.metricsCollected', 'zh': '个指标已采集'},
}

def set_nested_key(data: dict, key_path: str, value: str):
    """Set value in nested dict using dot notation"""
    parts = key_path.split('.')
    current = data
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        elif not isinstance(current[part], dict):
            return False
        current = current[part]
    if parts[-1] not in current or isinstance(current.get(parts[-1]), str):
        current[parts[-1]] = value
        return True
    return False

def load_locale(lang_code: str) -> dict:
    """Load locale file"""
    locale_path = Path(f'/home/eric/video/admin-frontend/src/i18n/locales/{lang_code}.json')
    with open(locale_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_locale(lang_code: str, data: dict):
    """Save locale file"""
    locale_path = Path(f'/home/eric/video/admin-frontend/src/i18n/locales/{lang_code}.json')
    with open(locale_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def update_translations():
    """Update only zh-CN and en-US"""
    print("📝 更新翻译文件（仅中英双语）...")

    zh_cn = load_locale('zh-CN')
    en_us = load_locale('en-US')

    added = 0
    skipped = 0

    for english_text, trans_data in SYSTEMHEALTH_TRANSLATIONS.items():
        key = trans_data['key']
        zh_text = trans_data['zh']

        if set_nested_key(zh_cn, key, zh_text):
            added += 1
        else:
            skipped += 1

        if set_nested_key(en_us, key, english_text):
            added += 1
        else:
            skipped += 1

    save_locale('zh-CN', zh_cn)
    save_locale('en-US', en_us)

    print(f"✅ 添加了 {added} 个翻译条目")
    if skipped > 0:
        print(f"⚪ 跳过了 {skipped} 个已存在的键")
    print(f"⚪ 未修改其他语言文件")

    return added

def fix_file(file_path: str, file_name: str):
    """Fix a single file"""
    print(f"\n修复 {file_name}...")

    path = Path(file_path)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    replacements = 0

    # Sort by length (longest first) to avoid partial matches
    sorted_map = sorted(SYSTEMHEALTH_TRANSLATIONS.items(), key=lambda x: len(x[0]), reverse=True)

    for english_text, trans_data in sorted_map:
        key = trans_data['key']

        # Skip if this text is not in the file
        if english_text not in content:
            continue

        patterns = [
            # Regular strings
            (f'"{english_text}"', f"t('{key}')"),
            (f"'{english_text}'", f"t('{key}')"),

            # JSX text content
            (f'>{english_text}<', f">{{t('{key}')}}<"),

            # Table column titles
            (f"title: '{english_text}'", f"title: t('{key}')"),
            (f'title: "{english_text}"', f"title: t('{key}')"),

            # Modal titles and labels
            (f'title="{english_text}"', f"title={{t('{key}')}}"),

            # Placeholder attributes
            (f'placeholder="{english_text}"', f"placeholder={{t('{key}')}}"),

            # Select options
            (f"label: '{english_text}'", f"label: t('{key}')"),
            (f'label: "{english_text}"', f"label: t('{key}')"),

            # Tag text content
            (f'text="{english_text}"', f"text={{t('{key}')}}"),
        ]

        for old_pattern, new_replacement in patterns:
            if old_pattern in content:
                content = content.replace(old_pattern, new_replacement)
                replacements += 1

    if content != original_content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 修复了 {file_name}: {replacements} 处替换")
        return replacements
    else:
        print(f"⚠️  {file_name} 没有需要修复的内容")
        return 0

def main():
    print("="*80)
    print("修复 SystemHealth 页面硬编码文本（仅中英双语）")
    print("="*80)
    print()

    # Update translations
    added = update_translations()
    print()

    # Fix files
    total_replacements = 0

    files = [
        ('/home/eric/video/admin-frontend/src/pages/SystemHealth/index.tsx', 'SystemHealth/index.tsx'),
        ('/home/eric/video/admin-frontend/src/pages/SystemHealth/Alerts.tsx', 'SystemHealth/Alerts.tsx'),
        ('/home/eric/video/admin-frontend/src/pages/SystemHealth/SLAReport.tsx', 'SystemHealth/SLAReport.tsx'),
    ]

    for file_path, file_name in files:
        total_replacements += fix_file(file_path, file_name)

    print()
    print("="*80)
    print("✅ 修复完成!")
    print(f"   - 新增翻译键: {len(SYSTEMHEALTH_TRANSLATIONS)} 个")
    print(f"   - 代码替换: {total_replacements} 处")
    print(f"   - 修改文件: {len(files) + 2} 个 (3个tsx + zh-CN.json + en-US.json)")
    print(f"   - 未修改: 4 个语言文件")
    print("="*80)

if __name__ == '__main__':
    main()
