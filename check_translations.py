#!/usr/bin/env python3
"""
检查翻译文件的完整性
"""
import json
import os
from pathlib import Path
from typing import Dict, Set, List, Tuple


def get_all_keys(obj: dict, prefix: str = "") -> Set[str]:
    """递归获取JSON对象中的所有键路径"""
    keys = set()
    for key, value in obj.items():
        full_key = f"{prefix}.{key}" if prefix else key
        keys.add(full_key)
        if isinstance(value, dict):
            keys.update(get_all_keys(value, full_key))
    return keys


def compare_translations(base_file: Path, compare_file: Path) -> Tuple[Set[str], Set[str]]:
    """比较两个翻译文件，返回缺失和多余的键"""
    with open(base_file, 'r', encoding='utf-8') as f:
        base_data = json.load(f)

    with open(compare_file, 'r', encoding='utf-8') as f:
        compare_data = json.load(f)

    base_keys = get_all_keys(base_data)
    compare_keys = get_all_keys(compare_data)

    missing = base_keys - compare_keys  # 在基准中有，在比较中缺失
    extra = compare_keys - base_keys    # 在比较中多余

    return missing, extra


def check_directory(dir_path: Path, base_lang: str = "en-US"):
    """检查某个目录下的所有翻译文件"""
    print(f"\n{'='*80}")
    print(f"检查目录: {dir_path}")
    print(f"{'='*80}")

    base_file = dir_path / f"{base_lang}.json"
    if not base_file.exists():
        print(f"❌ 基准文件不存在: {base_file}")
        return

    # 获取所有翻译文件
    translation_files = sorted(dir_path.glob("*.json"))

    print(f"\n找到 {len(translation_files)} 个翻译文件:")
    for f in translation_files:
        print(f"  - {f.name}")

    # 统计信息
    with open(base_file, 'r', encoding='utf-8') as f:
        base_data = json.load(f)
    base_keys = get_all_keys(base_data)
    print(f"\n基准语言 ({base_lang}) 共有 {len(base_keys)} 个翻译键")

    # 比较每个文件
    has_issues = False
    for trans_file in translation_files:
        if trans_file.name == f"{base_lang}.json":
            continue

        lang_name = trans_file.stem
        missing, extra = compare_translations(base_file, trans_file)

        if missing or extra:
            has_issues = True
            print(f"\n{'─'*80}")
            print(f"🔍 {lang_name}")
            print(f"{'─'*80}")

            if missing:
                print(f"\n❌ 缺失 {len(missing)} 个键:")
                for key in sorted(missing)[:20]:  # 只显示前20个
                    print(f"   - {key}")
                if len(missing) > 20:
                    print(f"   ... 还有 {len(missing) - 20} 个")

            if extra:
                print(f"\n⚠️  多余 {len(extra)} 个键:")
                for key in sorted(extra)[:10]:  # 只显示前10个
                    print(f"   - {key}")
                if len(extra) > 10:
                    print(f"   ... 还有 {len(extra) - 10} 个")

            # 计算完整度
            with open(trans_file, 'r', encoding='utf-8') as f:
                trans_data = json.load(f)
            trans_keys = get_all_keys(trans_data)
            completeness = (len(trans_keys & base_keys) / len(base_keys)) * 100
            print(f"\n📊 完整度: {completeness:.1f}% ({len(trans_keys & base_keys)}/{len(base_keys)})")
        else:
            print(f"\n✅ {lang_name}: 完整")

    if not has_issues:
        print("\n✅ 所有翻译文件都是完整的！")


def main():
    """主函数"""
    video_path = Path("/home/eric/video")

    # 检查前端翻译
    frontend_i18n = video_path / "frontend" / "src" / "i18n" / "locales"
    if frontend_i18n.exists():
        check_directory(frontend_i18n)

    # 检查管理后台翻译
    admin_i18n = video_path / "admin-frontend" / "src" / "i18n" / "locales"
    if admin_i18n.exists():
        check_directory(admin_i18n)

    print(f"\n{'='*80}")
    print("检查完成！")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
