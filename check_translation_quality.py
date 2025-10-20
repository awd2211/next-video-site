#!/usr/bin/env python3
"""
深度检查翻译质量
检查是否有翻译值和英文相同，或者翻译值为空
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


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


def is_likely_english(text: str) -> bool:
    """判断文本是否主要是英文"""
    # 去除数字、标点符号、空格、货币符号等
    import string
    text_clean = ''.join(c for c in text if c not in string.punctuation + string.digits + string.whitespace + '%€$¥£')
    if not text_clean:
        return False

    # 计算英文字母占比
    english_chars = sum(1 for c in text_clean if ord(c) < 128 and c.isalpha())
    total_chars = len(text_clean)

    if total_chars == 0:
        return False

    english_ratio = english_chars / total_chars
    return english_ratio > 0.5  # 超过50%是英文字母


def check_translation_quality(lang_code: str, base_path: Path):
    """检查翻译质量"""
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

    issues = []

    # 检查每个翻译
    for key, value in lang_values.items():
        en_value = en_values.get(key, "")

        # 1. 检查是否为空
        if not value or value.strip() == "":
            issues.append({
                'key': key,
                'type': '空值',
                'current': value,
                'english': en_value
            })
            continue

        # 2. 对于非英语语言，检查是否翻译值和英文值完全相同
        if lang_code != 'en-US' and value == en_value:
            # 排除一些特殊情况：数字、URL、常见缩写等
            if not re.match(r'^[\d\s%€$¥£.,:-]+$', value) and \
               not value.startswith('http') and \
               not value in ['ID', 'API', 'URL', 'HTTP', 'HTTPS', 'IP', 'SEO', 'MRR', 'ARPU', 'LTV', 'CSV', 'JSON', 'SQL']:
                issues.append({
                    'key': key,
                    'type': '未翻译（与英文相同）',
                    'current': value,
                    'english': en_value
                })
            continue

        # 3. 对于非英语语言，检查是否主要是英文
        if lang_code not in ['en-US'] and is_likely_english(value):
            # 排除一些特殊情况
            if not re.match(r'^[\d\s%€$¥£.,:-]+$', value) and \
               not value.startswith('http') and \
               len(value) > 3:  # 短词可能是缩写
                issues.append({
                    'key': key,
                    'type': '疑似英文未翻译',
                    'current': value,
                    'english': en_value
                })

    # 输出问题
    if issues:
        print(f"\n发现 {len(issues)} 个潜在问题：\n")

        # 按类型分组
        by_type = {}
        for issue in issues:
            issue_type = issue['type']
            if issue_type not in by_type:
                by_type[issue_type] = []
            by_type[issue_type].append(issue)

        for issue_type, type_issues in by_type.items():
            print(f"\n{issue_type} ({len(type_issues)} 个):")
            print("-" * 80)
            for issue in type_issues[:20]:  # 只显示前20个
                print(f"\n键: {issue['key']}")
                print(f"  当前值: {issue['current']}")
                print(f"  英文值: {issue['english']}")

            if len(type_issues) > 20:
                print(f"\n  ... 还有 {len(type_issues) - 20} 个类似问题")
    else:
        print("\n✅ 未发现明显的翻译质量问题")

    return issues


def main():
    """主函数"""
    admin_i18n = Path("/home/eric/video/admin-frontend/src/i18n/locales")

    # 检查各个语言
    all_issues = {}
    for lang in ["zh-CN", "zh-TW", "ja-JP", "de-DE", "fr-FR"]:
        issues = check_translation_quality(lang, admin_i18n)
        if issues:
            all_issues[lang] = issues

    # 总结
    print(f"\n\n{'='*80}")
    print("总结")
    print(f"{'='*80}")

    for lang, issues in all_issues.items():
        print(f"\n{lang}: {len(issues)} 个问题")

    if not all_issues:
        print("\n✅ 所有语言翻译质量良好！")
    else:
        print(f"\n⚠️  共发现 {sum(len(issues) for issues in all_issues.values())} 个潜在翻译问题")


if __name__ == "__main__":
    main()
