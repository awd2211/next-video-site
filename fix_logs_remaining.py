#!/usr/bin/env python3
"""
Fix remaining hardcoded text in Logs-enhanced.tsx
Only update zh-CN and en-US
"""

import re
import json
from pathlib import Path

# Additional translations for remaining text
ADDITIONAL_TRANSLATIONS = {
    # Login logs
    '登录日志详情': {'key': 'logs.modal.loginDetails', 'en': 'Login Log Details'},
    '用户类型': {'key': 'logs.details.userType', 'en': 'User Type'},
    '地理位置': {'key': 'logs.details.location', 'en': 'Location'},
    '设备类型': {'key': 'logs.details.deviceType', 'en': 'Device Type'},
    '浏览器': {'key': 'logs.details.browser', 'en': 'Browser'},
    '操作系统': {'key': 'logs.details.os', 'en': 'Operating System'},
    '设备': {'key': 'logs.table.device', 'en': 'Device'},
    '搜索用户名或邮箱': {'key': 'logs.search.usernameOrEmail', 'en': 'Search username or email'},
    '被拦截': {'key': 'logs.status.blocked', 'en': 'Blocked'},

    # System logs
    '系统日志详情': {'key': 'logs.modal.systemDetails', 'en': 'System Log Details'},
    '级别': {'key': 'logs.details.level', 'en': 'Level'},
    '分类': {'key': 'logs.details.category', 'en': 'Category'},
    '事件': {'key': 'logs.details.event', 'en': 'Event'},
    '详细信息': {'key': 'logs.details.detailedInfo', 'en': 'Detailed Information'},
    '搜索事件或消息': {'key': 'logs.search.eventOrMessage', 'en': 'Search event or message'},

    # Error logs
    '错误日志详情': {'key': 'logs.modal.errorDetails', 'en': 'Error Log Details'},
    '错误消息': {'key': 'logs.table.errorMessage', 'en': 'Error Message'},
    '状态码': {'key': 'logs.details.statusCode', 'en': 'Status Code'},
    '解决状态': {'key': 'logs.details.resolveStatus', 'en': 'Resolution Status'},
    '解决时间': {'key': 'logs.details.resolveTime', 'en': 'Resolution Time'},
    '管理员备注': {'key': 'logs.details.adminNote', 'en': 'Admin Note'},
    '管理员备注（可选）：': {'key': 'logs.details.adminNoteOptional', 'en': 'Admin Note (Optional):'},
    '堆栈跟踪': {'key': 'logs.details.stackTrace', 'en': 'Stack Trace'},
    '已解决': {'key': 'logs.status.resolved', 'en': 'Resolved'},
    '未解决': {'key': 'logs.status.unresolved', 'en': 'Unresolved'},
    '标记错误为已解决': {'key': 'logs.actions.markResolved', 'en': 'Mark as Resolved'},
    '搜索错误消息': {'key': 'logs.search.errorMessage', 'en': 'Search error message'},

    # Messages
    '错误已标记为已解决': {'key': 'logs.message.markedResolved', 'en': 'Error marked as resolved'},
    '操作失败': {'key': 'logs.message.operationFailed', 'en': 'Operation failed'},
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
    print("📝 添加剩余翻译...")

    zh_cn = load_locale('zh-CN')
    en_us = load_locale('en-US')

    added = 0
    skipped = 0

    for chinese_text, trans_data in ADDITIONAL_TRANSLATIONS.items():
        key = trans_data['key']
        en_text = trans_data['en']

        if set_nested_key(zh_cn, key, chinese_text):
            added += 1
        else:
            skipped += 1

        if set_nested_key(en_us, key, en_text):
            added += 1
        else:
            skipped += 1

    save_locale('zh-CN', zh_cn)
    save_locale('en-US', en_us)

    print(f"✅ 添加了 {added} 个翻译条目")
    if skipped > 0:
        print(f"⚪ 跳过了 {skipped} 个已存在的键")

    return added

def fix_file():
    """Fix remaining hardcoded text in Logs-enhanced.tsx"""
    file_path = Path('/home/eric/video/admin-frontend/src/pages/Logs-enhanced.tsx')

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    replacements = 0

    # Sort by length (longest first)
    sorted_map = sorted(ADDITIONAL_TRANSLATIONS.items(), key=lambda x: len(x[0]), reverse=True)

    for chinese_text, trans_data in sorted_map:
        key = trans_data['key']

        # Different replacement patterns
        patterns = [
            # Strings in code
            (f'"{chinese_text}"', f't(\'{key}\')'),
            (f"'{chinese_text}'", f"t('{key}')"),

            # JSX attributes
            (f'title="{chinese_text}"', f'title={{t(\'{key}\')}}'),
            (f'label="{chinese_text}"', f'label={{t(\'{key}\')}}'),
            (f'placeholder="{chinese_text}"', f'placeholder={{t(\'{key}\')}}'),

            # JSX children
            (f'>{chinese_text}<', f'>{{t(\'{key}\')}}<'),

            # Table column titles
            (f"title: '{chinese_text}'", f"title: t('{key}')"),
            (f'title: "{chinese_text}"', f"title: t('{key}')"),

            # Descriptions.Item label
            (f'<Descriptions.Item label="{chinese_text}"', f'<Descriptions.Item label={{t(\'{key}\')}}'),

            # Option value
            (f'<Option value="blocked">被拦截</Option>' if chinese_text == '被拦截' else '',
             f'<Option value="blocked">{{t(\'logs.status.blocked\')}}</Option>' if chinese_text == '被拦截' else ''),
        ]

        for old_pattern, new_replacement in patterns:
            if old_pattern and old_pattern in content:
                content = content.replace(old_pattern, new_replacement)
                replacements += 1

    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 修复了 Logs-enhanced.tsx: {replacements} 处替换")
        return replacements
    else:
        print("⚠️  没有需要修复的内容")
        return 0

def main():
    print("="*80)
    print("修复 Logs-enhanced.tsx 剩余硬编码")
    print("="*80)
    print()

    # Update translations
    added = update_translations()
    print()

    # Fix file
    replacements = fix_file()
    print()

    print("="*80)
    print("✅ 完成!")
    print(f"   - 新增翻译: {len(ADDITIONAL_TRANSLATIONS)} 个")
    print(f"   - 代码替换: {replacements} 处")
    print("="*80)

if __name__ == '__main__':
    main()
