#!/usr/bin/env python3
"""
修复翻译系统 - 第二十轮
修复之前的翻译错误和中文残留
"""

import json
import re
from pathlib import Path
from typing import Dict, Any

# 空德语和法语字典（都已100%）
DE_TERA = {}
FR_TERA = {}

# 修复日语字典 - 修正之前的翻译错误
JA_TERA = {
    # 修复"時の間である必要があります"错误
    "時の間である必要があります": "時間",
    "時の間である必要がありますあたり": "時間あたり",
    "過去7日の間である必要があります": "過去7日間",
    "過去24時の間である必要があります": "過去24時間",
    "過去30日の間である必要があります": "過去30日間",
    "更新の間である必要があります隔": "更新間隔",
    "応答時の間である必要があります": "応答時間",
    "データベース応答時の間である必要があります": "データベース応答時間",
    "Redis 応答時の間である必要があります": "Redis応答時間",
    "ストレージ応答時の間である必要があります": "ストレージ応答時間",
    "期の間である必要があります": "期間",
    "今後24時の間である必要があります": "今後24時間",
    "終了時の間である必要があります": "終了時間",
    "スマート推奨時の間である必要があります": "スマート推奨時間",
    "推奨時の間である必要がありますを使用": "推奨時間を使用",
    "実行時の間である必要があります": "実行時間",
    "時の間である必要がありますで並び替え": "時間で並び替え",
    "請求期の間である必要があります": "請求期間",
    "時の間である必要があります範囲:": "時間範囲:",
    "よく使用される: 1時の間である必要があります=3600, 1日=86400, 1週=604800": "よく使用される: 1時間=3600, 1日=86400, 1週=604800",
    "予測月の間である必要がありますコスト": "予測月間コスト",
    "平均応答時の間である必要があります": "平均応答時間",
    
    # 修复重复的助词和标点
    "設定を復元しますを現在の設定が上書きされます。": "設定を復元しますか？現在の設定が上書きされます。",
    "すべての設定をデフォルトにリセットしますをこの操作は元に戻せません。": "すべての設定をデフォルトにリセットしますか？この操作は元に戻せません。",
    "しますを": "しますか？",
    "ロールを削除してもよろしいですか\"{{name}}\"をこの操作は元に戻せません。": "ロール「{{name}}」を削除してもよろしいですか？この操作は元に戻せません。",
    "\"{{name}}\"をこの": "「{{name}}」を削除してもよろしいですか？この",
    
    # 修复中文逗号和标点
    "送信失敗，後で再試行": "送信に失敗しました。後で再試行してください",
    "ログイン試行回数が多すぎます，後で再試行してください": "ログイン試行回数が多すぎます。後で再試行してください",
    "確認コードエラー，再試行してください": "確認コードエラー。再試行してください",
    "ネットワーク接続失敗，ネットワークをご確認ください": "ネットワーク接続に失敗しました。ネットワークをご確認ください",
    "接続失敗，": "接続に失敗しました。",
    "，": "。",
    
    # 修复"作成成功"
    "スケジューリング作成成功": "スケジューリングの作成に成功しました",
    "サブスクリプションプラン作成成功": "サブスクリプションプランの作成に成功しました",
    "クーポン作成成功": "クーポンの作成に成功しました",
    "作成成功": "の作成に成功しました",
    
    # 修复"テスト成功"
    "接続テスト成功！": "接続テストに成功しました！",
    "テスト成功": "テストに成功しました",
    
    # 修复"ログイン成功"
    "ログイン成功！": "ログインに成功しました！",
    "成功！": "に成功しました！",
    
    # 修复"の間である必要があります"模式
    "文字のの間である必要がありますである必要があります": "文字の間である必要があります",
    "のの間である必要があります": "の間である必要があります",
    
    # 修复"超级管理者"
    "スーパー管理者はすべての権限を持っています。ロールの割り当ては不要ですです": "スーパー管理者はすべての権限を持っています。ロールの割り当ては不要です",
    "不要ですです": "不要です",
    "です です": "です",
    
    # 修复"を作成"
    "を作成Plan": "プランを作成",
    "を作成Coupon": "クーポンを作成",
    "を作成": "を作成する",
    
    # 修复"返金金額は0.01から残額のの間である必要がありますである必要があります"
    "返金金額は0.01から残額のの間である必要がありますである必要があります": "返金金額は0.01から残額の間である必要があります",
    "から残額のの間である必要がありますである必要があります": "から残額の間である必要があります",
}

def contains_chinese(text: str) -> bool:
    """检查文本是否包含中文字符或错误模式"""
    # 检查中文字符
    if re.search(r'[\u4e00-\u9fff]', str(text)):
        return True
    return False

def translate_mixed_text(text: str, translations: Dict[str, str]) -> str:
    """翻译混合语言文本 - 按长度降序匹配"""
    if not contains_chinese(text):
        return text

    result = text
    sorted_translations = sorted(translations.items(), key=lambda x: len(x[0]), reverse=True)

    for chinese, translation in sorted_translations:
        if chinese in result:
            result = result.replace(chinese, translation)
            if not contains_chinese(result):
                return result

    return result

def translate_value(value: Any, translations: Dict[str, str], stats: Dict) -> Any:
    """递归翻译JSON值"""
    if isinstance(value, dict):
        return {k: translate_value(v, translations, stats) for k, v in value.items()}
    elif isinstance(value, list):
        return [translate_value(item, translations, stats) for item in value]
    elif isinstance(value, str):
        if contains_chinese(value):
            stats['total'] += 1
            translated = translate_mixed_text(value, translations)
            if not contains_chinese(translated):
                stats['translated'] += 1
            return translated
        return value
    else:
        return value

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

def translate_file(lang_code: str, translations: Dict[str, str]):
    """翻译单个语言文件"""
    if not translations:
        print(f"\n{lang_code}: 跳过（已100%完成）")
        return {
            'before': 0,
            'after': 0,
            'translated': 0,
            'completion': 100.0
        }

    print(f"\n{'='*80}")
    print(f"修复翻译: {lang_code}")
    print(f"{'='*80}\n")

    admin_i18n = Path('/home/eric/video/admin-frontend/src/i18n/locales')
    lang_file = admin_i18n / f'{lang_code}.json'

    with open(lang_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    before_count = count_chinese_items(data)
    stats = {'total': 0, 'translated': 0}
    translated_data = translate_value(data, translations, stats)

    with open(lang_file, 'w', encoding='utf-8') as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)

    after_count = count_chinese_items(translated_data)

    # 计算完成度
    total_items = 1175 if lang_code == 'de-DE' else (1169 if lang_code == 'fr-FR' else 1257)
    completion_rate = ((total_items - after_count) / total_items) * 100

    print(f"✅ {lang_code} 翻译完成！")
    print(f"📊 翻译前: {before_count} 项")
    print(f"📊 翻译后: {after_count} 项")
    print(f"📊 本轮修复: {before_count - after_count} 项")
    print(f"🎯 完成度: {completion_rate:.1f}%")

    return {
        'before': before_count,
        'after': after_count,
        'translated': before_count - after_count,
        'completion': completion_rate
    }

def main():
    print("="*80)
    print("修复翻译系统 - 第二十轮")
    print("修复之前的翻译错误和中文残留！")
    print("="*80)

    results = {}

    print("\n处理德语翻译...")
    results['de-DE'] = translate_file('de-DE', DE_TERA)

    print("\n处理法语翻译...")
    results['fr-FR'] = translate_file('fr-FR', FR_TERA)

    print("\n处理日语翻译...")
    results['ja-JP'] = translate_file('ja-JP', JA_TERA)

    print(f"\n\n{'='*80}")
    print("第二十轮翻译完成总结")
    print(f"{'='*80}\n")

    total_translated = sum(r['translated'] for r in results.values())
    total_remaining = sum(r['after'] for r in results.values())

    for lang, stats in results.items():
        if stats['completion'] == 100:
            emoji = "🌟🌟🌟"
        elif stats['completion'] >= 50:
            emoji = "🌟🌟"
        elif stats['completion'] >= 30:
            emoji = "🌟"
        elif stats['completion'] >= 25:
            emoji = "✨"
        else:
            emoji = "🎯"
        print(f"{lang}:")
        print(f"  - 本轮修复: {stats['translated']} 项")
        print(f"  - 剩余: {stats['after']} 项")
        print(f"  - 完成度: {stats['completion']:.1f}% {emoji}")

    print(f"\n本轮总计修复: {total_translated} 项")
    print(f"总剩余未翻译: {total_remaining} 项")

    # 计算总体完成度
    original_total = 3601
    completed = original_total - total_remaining
    completion_rate = (completed / original_total) * 100

    print(f"\n🎊 总体完成度: {completion_rate:.1f}% ({completed}/{original_total})")

    # 特别提示
    if results['ja-JP']['completion'] >= 40:
        print(f"\n🎉🎉🎉 日语突破40%！重大进展！")
    elif results['ja-JP']['completion'] >= 35:
        print(f"\n🎉🎉 日语突破35%！继续加油！")
    elif results['ja-JP']['completion'] >= 30:
        print(f"\n🎉 日语突破30%！稳步前进！")
    elif results['ja-JP']['completion'] >= 27:
        print(f"\n✨ 日语稳步提升！")

if __name__ == '__main__':
    main()
