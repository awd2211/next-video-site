#!/usr/bin/env python3
"""
查找真正未翻译的内容（值与英文完全相同的）
"""
import json
from pathlib import Path
from typing import Dict


def get_all_values(obj: dict, prefix: str = "") -> Dict[str, str]:
    """递归获取JSON对象中的所有键值对"""
    values = {}
    for key, value in obj.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            values.update(get_all_values(value, full_key))
        else:
            values[full_key] = str(value)
    return values


# 常见的技术术语和缩写，这些通常不需要翻译
TECH_TERMS = {
    'VIP', 'AI', 'API', 'URL', 'HTTP', 'HTTPS', 'IP', 'SEO', 'MRR', 'ARPU',
    'LTV', 'CSV', 'JSON', 'SQL', 'OAuth', 'Token', 'Excel', 'Banner',
    'Captcha', 'ID', 'UUID', 'CDN', 'DNS', 'SSL', 'TLS', 'SMTP', 'POP3',
    'IMAP', 'FTP', 'SSH', 'TCP', 'UDP', 'WebSocket', 'Cookie', 'Session'
}

# 应该翻译但很多语言没有翻译的常见词
SHOULD_TRANSLATE = {
    'Dashboard', 'Total', 'Actions', 'Coupons', 'Settings', 'Status',
    'Type', 'Name', 'Description', 'Title', 'Content', 'Create', 'Edit',
    'Delete', 'Cancel', 'Confirm', 'Submit', 'Reset', 'Search', 'Filter',
    'Export', 'Import', 'Download', 'Upload', 'Preview', 'Publish',
    'Draft', 'Active', 'Inactive', 'Enabled', 'Disabled', 'Success',
    'Error', 'Warning', 'Info', 'Loading', 'Save', 'Update', 'Add',
    'Remove', 'View', 'Details', 'List', 'Grid', 'Table', 'Chart'
}


def check_untranslated(lang_code: str, base_path: Path):
    """检查未翻译的内容"""
    print(f"\n{'='*80}")
    print(f"检查语言: {lang_code}")
    print(f"{'='*80}")

    lang_file = base_path / f"{lang_code}.json"
    en_file = base_path / "en-US.json"

    with open(lang_file, 'r', encoding='utf-8') as f:
        lang_data = json.load(f)
    with open(en_file, 'r', encoding='utf-8') as f:
        en_data = json.load(f)

    lang_values = get_all_values(lang_data)
    en_values = get_all_values(en_data)

    untranslated = []
    partially_translated = []

    for key, en_value in en_values.items():
        lang_value = lang_values.get(key, "")

        # 完全相同且不是技术术语
        if lang_value == en_value:
            # 检查是否包含在不需要翻译的列表中
            if en_value.strip() in TECH_TERMS:
                continue
            # 检查是否是邮箱、链接、版权信息等
            if '@' in en_value or en_value.startswith('http') or '©' in en_value:
                if '©' in en_value or '@example.com' in en_value:
                    continue  # 这些可以保持相同
            # 检查是否是纯数字或特殊符号
            if en_value.replace('.', '').replace('%', '').replace('$', '').isdigit():
                continue

            # 如果值在应该翻译列表中
            if en_value.strip() in SHOULD_TRANSLATE:
                untranslated.append({
                    'key': key,
                    'value': en_value,
                    'priority': 'high'
                })
            elif len(en_value.strip()) > 2:  # 忽略单个字母缩写
                untranslated.append({
                    'key': key,
                    'value': en_value,
                    'priority': 'medium'
                })

    # 输出结果
    if untranslated:
        print(f"\n发现 {len(untranslated)} 个未翻译项：\n")

        # 高优先级
        high_priority = [u for u in untranslated if u['priority'] == 'high']
        if high_priority:
            print(f"\n⚠️  高优先级（{len(high_priority)} 个）- 常见词汇应该翻译：")
            print("-" * 80)
            for item in high_priority[:30]:
                print(f"  {item['key']}: \"{item['value']}\"")
            if len(high_priority) > 30:
                print(f"  ... 还有 {len(high_priority) - 30} 个")

        # 中优先级
        medium_priority = [u for u in untranslated if u['priority'] == 'medium']
        if medium_priority:
            print(f"\n  中优先级（{len(medium_priority)} 个）- 建议检查：")
            print("-" * 80)
            for item in medium_priority[:20]:
                print(f"  {item['key']}: \"{item['value']}\"")
            if len(medium_priority) > 20:
                print(f"  ... 还有 {len(medium_priority) - 20} 个")
    else:
        print("\n✅ 未发现明显未翻译的内容")

    return untranslated


def main():
    """主函数"""
    admin_i18n = Path("/home/eric/video/admin-frontend/src/i18n/locales")

    all_issues = {}
    for lang in ["zh-CN", "zh-TW", "ja-JP", "de-DE", "fr-FR"]:
        issues = check_untranslated(lang, admin_i18n)
        if issues:
            all_issues[lang] = issues

    # 总结
    print(f"\n\n{'='*80}")
    print("总结")
    print(f"{'='*80}")

    if all_issues:
        for lang, issues in all_issues.items():
            high = len([i for i in issues if i['priority'] == 'high'])
            medium = len([i for i in issues if i['priority'] == 'medium'])
            print(f"\n{lang}: {len(issues)} 个未翻译项（高优先级: {high}, 中优先级: {medium}）")

        total_high = sum(len([i for i in issues if i['priority'] == 'high'])
                        for issues in all_issues.values())
        print(f"\n⚠️  需要优先处理的高优先级翻译: {total_high} 个")
    else:
        print("\n✅ 所有语言都已正确翻译！")


if __name__ == "__main__":
    main()
