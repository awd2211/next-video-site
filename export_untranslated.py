#!/usr/bin/env python3
"""
导出未翻译的内容为CSV格式，方便使用翻译服务
"""
import json
import csv
import re
from pathlib import Path
from typing import Dict, List


def contains_chinese(text: str) -> bool:
    """检查文本是否包含中文字符"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))


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


def export_for_language(lang_code: str, base_path: Path, output_dir: Path):
    """为指定语言导出未翻译内容"""
    lang_file = base_path / f"{lang_code}.json"

    with open(lang_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    values = get_all_values(data)
    untranslated = []

    for key, value in values.items():
        if contains_chinese(value):
            untranslated.append({
                'key': key,
                'chinese': value,
                'translation': ''  # 留空等待翻译
            })

    if untranslated:
        # 导出为CSV
        output_file = output_dir / f"untranslated_{lang_code}.csv"
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['key', 'chinese', 'translation'])
            writer.writeheader()
            writer.writerows(untranslated)

        print(f"✅ 已导出 {lang_code}: {len(untranslated)} 项 -> {output_file}")
        return len(untranslated)

    return 0


def main():
    """主函数"""
    admin_i18n = Path("/home/eric/video/admin-frontend/src/i18n/locales")
    output_dir = Path("/home/eric/video/translations_to_fix")
    output_dir.mkdir(exist_ok=True)

    print("="*80)
    print("导出未翻译内容")
    print("="*80)
    print()

    total = 0
    for lang in ["de-DE", "fr-FR", "ja-JP"]:
        count = export_for_language(lang, admin_i18n, output_dir)
        total += count

    print()
    print("="*80)
    print(f"总计: {total} 个项需要翻译")
    print(f"文件已保存到: {output_dir}")
    print("="*80)
    print()
    print("下一步:")
    print("1. 使用翻译服务（如Google Translate API、DeepL等）翻译CSV文件")
    print("2. 在'translation'列填入翻译后的内容")
    print("3. 运行 import_translations.py 导入翻译")


if __name__ == "__main__":
    main()
