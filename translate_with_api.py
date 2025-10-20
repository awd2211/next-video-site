#!/usr/bin/env python3
"""
使用翻译API完成剩余的翻译工作
支持 googletrans (免费) 或 Google Cloud Translation API (付费)
"""

import json
import re
import time
from pathlib import Path
from typing import Dict, Any

# 尝试导入 googletrans (免费版本)
try:
    from googletrans import Translator
    HAS_GOOGLETRANS = True
except ImportError:
    HAS_GOOGLETRANS = False
    print("⚠️  googletrans 未安装。安装方法: pip install googletrans==4.0.0-rc1")

def contains_chinese(text: str) -> bool:
    """检查文本是否包含中文字符"""
    return bool(re.search(r'[\u4e00-\u9fff]', str(text)))

def extract_chinese_only(text: str) -> str:
    """提取文本中的中文部分"""
    chinese_chars = re.findall(r'[\u4e00-\u9fff]+', str(text))
    return ''.join(chinese_chars)

def translate_text(text: str, target_lang: str, translator) -> str:
    """
    翻译文本

    Args:
        text: 要翻译的文本
        target_lang: 目标语言代码 (de, fr, ja)
        translator: Translator 实例
    """
    try:
        # 提取中文部分
        chinese_text = extract_chinese_only(text)
        if not chinese_text:
            return text

        # 翻译中文部分
        result = translator.translate(chinese_text, src='zh-cn', dest=target_lang)

        # 将翻译结果替换回原文本
        translated_text = text
        for i, char_group in enumerate(re.finditer(r'[\u4e00-\u9fff]+', text)):
            if i < len(result.text):
                # 逐个替换中文片段
                pass

        # 简单策略：如果原文只有中文，返回完整翻译
        if chinese_text == text:
            return result.text

        # 如果是混合文本，尝试智能替换
        # 这是一个简化版本，可能需要更复杂的逻辑
        translated = text
        for match in re.finditer(r'[\u4e00-\u9fff]+', text):
            chinese_part = match.group()
            try:
                translation = translator.translate(chinese_part, src='zh-cn', dest=target_lang)
                translated = translated.replace(chinese_part, translation.text, 1)
            except Exception as e:
                print(f"    警告: 翻译失败 '{chinese_part}': {e}")
                continue

        return translated

    except Exception as e:
        print(f"    错误: 翻译失败 - {e}")
        return text

def translate_value(value: Any, target_lang: str, translator, stats: Dict) -> Any:
    """递归翻译JSON值"""
    if isinstance(value, dict):
        result = {}
        for k, v in value.items():
            result[k] = translate_value(v, target_lang, translator, stats)
        return result
    elif isinstance(value, list):
        return [translate_value(item, target_lang, translator, stats) for item in value]
    elif isinstance(value, str):
        if contains_chinese(value):
            stats['total'] += 1
            print(f"    翻译: {value[:50]}...")
            translated = translate_text(value, target_lang, translator)
            if translated != value and not contains_chinese(translated):
                stats['translated'] += 1
                print(f"    ✅ -> {translated[:50]}...")
            else:
                print(f"    ⚠️  翻译未完成或仍包含中文")
            return translated
        return value
    else:
        return value

def translate_file(lang_code: str, lang_map: Dict[str, str]):
    """翻译单个语言文件"""
    print(f"\n{'='*80}")
    print(f"开始翻译: {lang_code}")
    print(f"{'='*80}\n")

    if not HAS_GOOGLETRANS:
        print("❌ 需要安装 googletrans: pip install googletrans==4.0.0-rc1")
        return {'total': 0, 'translated': 0, 'remaining': 0}

    # 初始化翻译器
    translator = Translator()

    # 读取文件
    admin_i18n = Path('/home/eric/video/admin-frontend/src/i18n/locales')
    lang_file = admin_i18n / f'{lang_code}.json'

    with open(lang_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 统计信息
    stats = {'total': 0, 'translated': 0}

    # 翻译
    target_lang = lang_map[lang_code]
    translated_data = translate_value(data, target_lang, translator, stats)

    # 保存
    with open(lang_file, 'w', encoding='utf-8') as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)

    # 计算剩余未翻译项
    remaining = count_chinese_items(translated_data)
    stats['remaining'] = remaining

    print(f"\n✅ {lang_code} 翻译完成！")
    print(f"📊 处理了 {stats['total']} 项，成功翻译 {stats['translated']} 项")
    print(f"📊 剩余未翻译项: {remaining}")

    return stats

def count_chinese_items(data: Any) -> int:
    """递归统计包含中文的项目数"""
    count = 0
    if isinstance(data, dict):
        for v in data.values():
            count += count_chinese_items(v)
    elif isinstance(data, list):
        for item in data:
            count += count_chinese_items(item)
    elif isinstance(data, str) and contains_chinese(data):
        count += 1
    return count

def main():
    print("="*80)
    print("使用翻译API完成剩余翻译")
    print("="*80)

    if not HAS_GOOGLETRANS:
        print("\n❌ 错误: googletrans 未安装")
        print("\n安装方法:")
        print("  pip install googletrans==4.0.0-rc1")
        print("\n注意: googletrans 是免费的但可能不稳定。")
        print("      如需更高质量，建议使用 DeepL 或 Google Cloud Translation API")
        return

    # 语言映射
    lang_map = {
        'de-DE': 'de',  # 德语
        'fr-FR': 'fr',  # 法语
        'ja-JP': 'ja',  # 日语
    }

    results = {}

    # 翻译每种语言
    for lang_code in lang_map:
        try:
            results[lang_code] = translate_file(lang_code, lang_map)
            # 延迟避免API限流
            time.sleep(2)
        except Exception as e:
            print(f"\n❌ {lang_code} 翻译失败: {e}")
            results[lang_code] = {'total': 0, 'translated': 0, 'remaining': '未知'}

    # 总结
    print(f"\n\n{'='*80}")
    print("翻译完成总结")
    print(f"{'='*80}\n")

    total_remaining = 0
    for lang, stats in results.items():
        remaining = stats.get('remaining', 0)
        if isinstance(remaining, int):
            total_remaining += remaining
        print(f"{lang}: 剩余 {remaining} 项")

    print(f"\n总剩余未翻译项: {total_remaining}")

    if total_remaining > 0:
        print(f"\n💡 建议:")
        print(f"   - googletrans 可能无法翻译所有内容")
        print(f"   - 对于剩余项，考虑使用:")
        print(f"     1. DeepL API (最高质量)")
        print(f"     2. Google Cloud Translation API")
        print(f"     3. 人工翻译关键内容")

if __name__ == '__main__':
    main()
