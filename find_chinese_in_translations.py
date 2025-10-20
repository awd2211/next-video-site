#!/usr/bin/env python3
"""
查找翻译文件中的中文字符
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


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


def find_chinese_in_file(file_path: Path) -> List[Tuple[str, str]]:
    """在文件中查找包含中文的键值对"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    values = get_all_values(data)
    chinese_items = []

    for key, value in values.items():
        if contains_chinese(value):
            chinese_items.append((key, value))

    return chinese_items


def main():
    """主函数"""
    admin_i18n = Path("/home/eric/video/admin-frontend/src/i18n/locales")

    print("检查非中文语言文件中的中文字符\n")
    print("="*80)

    for lang in ["en-US", "de-DE", "fr-FR", "ja-JP", "zh-TW"]:
        file_path = admin_i18n / f"{lang}.json"
        chinese_items = find_chinese_in_file(file_path)

        if chinese_items:
            print(f"\n{lang}: 发现 {len(chinese_items)} 个包含中文的项")
            print("-" * 80)
            for key, value in chinese_items[:20]:
                print(f"  {key}: \"{value}\"")

            if len(chinese_items) > 20:
                print(f"  ... 还有 {len(chinese_items) - 20} 个")
        else:
            print(f"\n{lang}: ✅ 未发现中文字符")

    print("\n" + "="*80)


if __name__ == "__main__":
    main()
