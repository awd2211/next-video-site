#!/usr/bin/env python3
"""
Fix Logs-enhanced.tsx hardcoded text - Chinese and English ONLY
不修改其他语言文件，避免产生 TODO 条目
"""

import re
import json
from pathlib import Path
from typing import Dict

# 中文 -> 翻译键 -> 英文翻译
TRANSLATION_MAP = {
    # 页面标题
    '系统日志': {'key': 'logs.title', 'en': 'System Logs'},

    # Tab 标签
    '操作日志': {'key': 'logs.tabs.operation', 'en': 'Operation Logs'},
    '登录日志': {'key': 'logs.tabs.login', 'en': 'Login Logs'},
    '系统日志': {'key': 'logs.tabs.system', 'en': 'System Logs'},
    '错误日志': {'key': 'logs.tabs.error', 'en': 'Error Logs'},

    # 表格列
    '管理员': {'key': 'logs.table.admin', 'en': 'Admin'},
    '模块': {'key': 'logs.table.module', 'en': 'Module'},
    '操作': {'key': 'logs.table.action', 'en': 'Action'},
    '描述': {'key': 'logs.table.description', 'en': 'Description'},
    'IP地址': {'key': 'logs.table.ipAddress', 'en': 'IP Address'},
    '时间': {'key': 'logs.table.time', 'en': 'Time'},
    '详情': {'key': 'logs.table.details', 'en': 'Details'},

    # 搜索和筛选
    '搜索描述或IP地址': {'key': 'logs.search.placeholder', 'en': 'Search description or IP address'},
    '选择模块': {'key': 'logs.filter.selectModule', 'en': 'Select module'},
    '选择操作': {'key': 'logs.filter.selectAction', 'en': 'Select action'},
    '刷新': {'key': 'common.refresh', 'en': 'Refresh'},
    '导出': {'key': 'common.export', 'en': 'Export'},

    # 模态框
    '操作日志详情': {'key': 'logs.modal.operationDetails', 'en': 'Operation Log Details'},
    '关闭': {'key': 'common.close', 'en': 'Close'},

    # Descriptions 标签
    '请求方法': {'key': 'logs.details.requestMethod', 'en': 'Request Method'},
    '请求URL': {'key': 'logs.details.requestUrl', 'en': 'Request URL'},
    '请求数据': {'key': 'logs.details.requestData', 'en': 'Request Data'},
    '创建时间': {'key': 'logs.details.createTime', 'en': 'Created At'},
    '用户': {'key': 'logs.details.user', 'en': 'User'},
    '用户名': {'key': 'logs.details.username', 'en': 'Username'},
    '邮箱': {'key': 'logs.details.email', 'en': 'Email'},
    '登录方式': {'key': 'logs.details.loginMethod', 'en': 'Login Method'},
    '状态': {'key': 'logs.details.status', 'en': 'Status'},
    '成功': {'key': 'logs.status.success', 'en': 'Success'},
    '失败': {'key': 'logs.status.failed', 'en': 'Failed'},
    '失败原因': {'key': 'logs.details.failureReason', 'en': 'Failure Reason'},

    # 系统日志
    '日志级别': {'key': 'logs.details.logLevel', 'en': 'Log Level'},
    '消息': {'key': 'logs.details.message', 'en': 'Message'},
    '来源': {'key': 'logs.details.source', 'en': 'Source'},
    '堆栈追踪': {'key': 'logs.details.stackTrace', 'en': 'Stack Trace'},

    # 错误日志
    '错误类型': {'key': 'logs.details.errorType', 'en': 'Error Type'},
    '错误信息': {'key': 'logs.details.errorMessage', 'en': 'Error Message'},
    '请求路径': {'key': 'logs.details.requestPath', 'en': 'Request Path'},
    '用户代理': {'key': 'logs.details.userAgent', 'en': 'User Agent'},

    # 消息提示
    '获取日志详情失败': {'key': 'logs.message.fetchDetailsFailed', 'en': 'Failed to fetch log details'},
    '导出日志成功': {'key': 'logs.message.exportSuccess', 'en': 'Logs exported successfully'},
    '导出日志失败': {'key': 'logs.message.exportFailed', 'en': 'Failed to export logs'},

    # 分页
    '共': {'key': 'common.total', 'en': 'Total'},
    '条': {'key': 'common.items', 'en': 'items'},

    # 统计
    '今日操作': {'key': 'logs.stats.todayOperations', 'en': 'Today\'s Operations'},
    '今日登录': {'key': 'logs.stats.todayLogins', 'en': 'Today\'s Logins'},
    '今日错误': {'key': 'logs.stats.todayErrors', 'en': 'Today\'s Errors'},
    '活跃管理员': {'key': 'logs.stats.activeAdmins', 'en': 'Active Admins'},

    # 按钮
    '查看': {'key': 'common.view', 'en': 'View'},
    '删除': {'key': 'common.delete', 'en': 'Delete'},
    '确认': {'key': 'common.confirm', 'en': 'Confirm'},
    '取消': {'key': 'common.cancel', 'en': 'Cancel'},
}

def set_nested_key(data: dict, key_path: str, value: str):
    """Set value in nested dict using dot notation"""
    parts = key_path.split('.')
    current = data
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        elif not isinstance(current[part], dict):
            # Key exists but is not a dict, skip to avoid overwriting
            return False
        current = current[part]

    # Only set if key doesn't exist or we're updating it
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
    """Update ONLY zh-CN and en-US locale files"""
    print("📝 更新翻译文件（仅中英双语）...")

    # Load only Chinese and English
    zh_cn = load_locale('zh-CN')
    en_us = load_locale('en-US')

    added_count = 0
    skipped_count = 0

    for chinese_text, trans_data in TRANSLATION_MAP.items():
        key = trans_data['key']
        en_text = trans_data['en']

        # Add to Chinese
        if set_nested_key(zh_cn, key, chinese_text):
            added_count += 1
        else:
            skipped_count += 1

        # Add to English
        if set_nested_key(en_us, key, en_text):
            added_count += 1
        else:
            skipped_count += 1

    # Save only Chinese and English
    save_locale('zh-CN', zh_cn)
    save_locale('en-US', en_us)

    print(f"✅ 添加了 {added_count} 个翻译条目")
    if skipped_count > 0:
        print(f"⚪ 跳过了 {skipped_count} 个已存在的键")
    print(f"⚪ 未修改其他语言文件（de-DE, fr-FR, ja-JP, zh-TW）")

    return added_count

def fix_logs_file():
    """Fix Logs-enhanced.tsx file"""
    file_path = Path('/home/eric/video/admin-frontend/src/pages/Logs-enhanced.tsx')

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 1. Add useTranslation import if not present
    if 'useTranslation' not in content:
        # Add after other imports
        import_line = "import { useTranslation } from 'react-i18next'"
        # Find the last import statement
        import_match = re.search(r'(import.*\n)+', content)
        if import_match:
            last_import_end = import_match.end()
            content = content[:last_import_end] + import_line + '\n' + content[last_import_end:]

    # 2. Add t hook initialization
    if not re.search(r'const\s+{\s*t\s*}\s*=\s*useTranslation\(\)', content):
        # Find the component function
        component_match = re.search(r'(const\s+\w+\s*=\s*\(\)\s*=>|export\s+default\s+function\s+\w+\s*\(\)\s*{)', content)
        if component_match:
            # Find the opening brace and add after it
            brace_pos = content.find('{', component_match.end())
            if brace_pos > 0:
                content = content[:brace_pos+1] + '\n  const { t } = useTranslation()\n' + content[brace_pos+1:]

    # 3. Replace hardcoded text
    replacements = 0

    # Sort by length (longest first) to avoid partial replacements
    sorted_map = sorted(TRANSLATION_MAP.items(), key=lambda x: len(x[0]), reverse=True)

    for chinese_text, trans_data in sorted_map:
        key = trans_data['key']

        # Different patterns for different contexts
        patterns = [
            # Regular strings
            (f'"{chinese_text}"', f't(\'{key}\')'),
            (f"'{chinese_text}'", f"t('{key}')"),

            # JSX attributes
            (f'title="{chinese_text}"', f'title={{t(\'{key}\')}}'),
            (f'label="{chinese_text}"', f'label={{t(\'{key}\')}}'),
            (f'placeholder="{chinese_text}"', f'placeholder={{t(\'{key}\')}}'),

            # JSX children
            (f'>{chinese_text}<', f'>{{t(\'{key}\')}}<'),

            # Table column titles (special case)
            (f"title: '{chinese_text}'", f"title: t('{key}')"),
            (f'title: "{chinese_text}"', f"title: t('{key}')"),

            # showTotal function (special case for pagination)
            (f'`{chinese_text} ${{total}} 条`', f't(\'{trans_data.get("total_key", key)}\', {{ count: total }})' if '共' in chinese_text else f'`{{t(\'{key}\')}} ${{total}} {{t(\'common.items\')}}`'),
        ]

        for old_pattern, new_replacement in patterns:
            if old_pattern in content:
                content = content.replace(old_pattern, new_replacement)
                replacements += 1

    # Save file if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 修复了 Logs-enhanced.tsx: {replacements} 处替换")
        return replacements
    else:
        print("⚠️  Logs-enhanced.tsx 没有需要修复的内容")
        return 0

def main():
    print("="*80)
    print("修复 Logs-enhanced.tsx 硬编码文本（仅中英双语）")
    print("="*80)
    print()

    # Step 1: Update translations (only zh-CN and en-US)
    update_translations()
    print()

    # Step 2: Fix the file
    replacements = fix_logs_file()
    print()

    print("="*80)
    print("✅ 修复完成!")
    print(f"   - 新增翻译键: {len(TRANSLATION_MAP)} 个")
    print(f"   - 代码替换: {replacements} 处")
    print(f"   - 修改文件: 3 个 (Logs-enhanced.tsx, zh-CN.json, en-US.json)")
    print(f"   - 未修改: 4 个语言文件 (de-DE, fr-FR, ja-JP, zh-TW)")
    print("="*80)

if __name__ == '__main__':
    main()
