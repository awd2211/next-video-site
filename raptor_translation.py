#!/usr/bin/env python3
"""
迅猛龙翻译系统 - 第十四轮
专注日语大幅提升：修复英文和中文混入的日语内容
"""

import json
import re
from pathlib import Path
from typing import Dict, Any

# 空德语和法语字典（都已100%）
DE_RAPTOR = {}
FR_RAPTOR = {}

# 迅猛龙日语字典 - 大型翻译
JA_RAPTOR = {
    # 英文词修正
    "New 動画": "新しい動画",
    "New ": "新しい",
    "編エピソード 動画": "動画を編集",
    "編エピソード シリーズ": "シリーズを編集",
    "編エピソード": "編集",
    "編エピソードing": "編集中",
    "エピソード": "",

    # Common actions with English
    "Auto 更新": "自動更新",
    "Auto ": "自動",
    "Start 日付": "開始日",
    "Start ": "開始",
    "End 日付": "終了日",
    "End ": "終了",
    "Recent 動画": "最近の動画",
    "Recent ": "最近の",
    "Top 10 Popular 動画": "トップ10人気動画",
    "Top ": "トップ",
    "Popular ": "人気",
    "Batch 公開": "一括公開",
    "Batch 削除": "一括削除",
    "Batch ": "一括",
    "Full 名前": "フルネーム",
    "Full ": "フル",
    "Email 追加ress": "メールアドレス",
    "追加ress": "アドレス",

    # Settings related
    "検索 settings": "設定を検索",
    " settings": " 設定",
    "Basic 設定": "基本設定",
    "Basic ": "基本",
    "Feature 設定": "機能設定",
    "Feature ": "機能",
    "Advanced 設定": "詳細設定",
    "Advanced ": "詳細",
    "Other 設定": "その他の設定",
    "Other ": "その他の",
    "Site 情報rmation": "サイト情報",
    "情報rmation": "情報",

    # Backup related
    "戻るup & Restore": "バックアップと復元",
    "戻るup": "バックアップ",
    "エクスポート 戻るup": "バックアップをエクスポート",
    "インポート 戻るup": "バックアップをインポート",
    "ダウンロード 戻るup": "バックアップをダウンロード",
    "アップロード 戻るup": "バックアップをアップロード",
    "戻るup 時間": "バックアップ時刻",
    "戻るup created successfully": "バックアップの作成に成功しました",

    # Cache related
    "クリア 動画 Cache": "動画キャッシュをクリア",
    "クリア 設定 Cache": "設定キャッシュをクリア",
    "クリア": "クリア",
    " Cache": " キャッシュ",
    "合計 Hits": "合計ヒット数",
    "合計 Misses": "合計ミス数",
    " Hits": " ヒット数",
    " Misses": " ミス数",

    # Common words
    "を示す": "表示",
    "を示すs": "表示数",
    "確認 deletion": "削除を確認",
    "確認 to clear cache": "キャッシュをクリアしますか",
    "確認 to restore settings": "設定を復元しますか",
    "確認 to reset all settings to defaults": "すべての設定をデフォルトにリセットしますか",
    "確認 削除": "削除を確認",
    "確認 Ban": "禁止を確認",
    "確認 ": "確認 ",
    " deletion": " 削除",

    "作成d At": "作成日時",
    "作成d ": "作成",
    " At": " 日時",
    "公開ed": "公開済み",
    "公開ed ": "公開済み",

    "合計 {{total}} items": "合計 {{total}} 項目",
    " items": " 項目",

    "Done 編エピソードing": "編集完了",
    "Done ": "完了",

    # Status and actions
    "保存 すべて 設定": "すべての設定を保存",
    "保存 Layout": "レイアウトを保存",
    "保存 ": "保存",
    " Layout": " レイアウト",

    "失敗 to send test email": "テストメールの送信に失敗しました",
    "失敗 to clear cache": "キャッシュのクリアに失敗しました",
    "失敗 to create backup": "バックアップの作成に失敗しました",
    "失敗 to restore settings": "設定の復元に失敗しました",
    "失敗 to save layout": "レイアウトの保存に失敗しました",
    "失敗 to ": "失敗しました ",
    "失敗": "失敗",

    # Video types
    " タイプs Distribution": " タイプ分布",
    " タイプs": " タイプ",

    # Chinese mixed in
    "有効支付网关": "ゲートウェイを有効化",
    "支付网关": "支払いゲートウェイ",
    "网关": "ゲートウェイ",
    "环境": "環境",
    "テスト连接": "接続をテスト",
    "连接テスト成功！": "接続テスト成功！",
    "连接テスト失敗": "接続テスト失敗",
    "连接": "接続",
    "私钥": "秘密鍵",
    "公钥（支付宝）": "公開鍵（Alipay）",
    "公钥": "公開鍵",
    "支付宝": "Alipay",
    "网关地址": "ゲートウェイURL",
    "地址": "アドレス",

    "数据概要": "データ概要",
    "数据トレンド": "データトレンド",
    "数据": "データ",

    "自定义仪表盘": "ダッシュボードをカスタマイズ",
    "仪表盘": "ダッシュボード",
    "自定义": "カスタマイズ",

    "布局保存成功": "レイアウトの保存に成功しました",
    "布局已復元デフォルト": "レイアウトをデフォルトに復元しました",
    "布局": "レイアウト",

    "此アクション不可復元": "この操作は元に戻せません",
    "此": "この",
    "不可復元": "元に戻せません",

    "已通过": "承認済み",
    "已拒绝": "拒否済み",
    "通过": "承認",
    "拒绝": "拒否",
    "一括通过": "一括承認",
    "一括拒绝": "一括拒否",

    "付与VIP": "VIPを付与",
    "VIP Expiry 日付": "VIP有効期限",
    " Expiry ": " 有効期限",
    "一括付与VIP": "一括VIP付与",
    "Batch 削除 VIP": "一括VIP削除",

    # Common phrases
    "確認して": "確認する",
    "并を示す統計信息": "および統計情報を表示",
    "统计信息": "統計情報",
    "信息": "情報",

    # Settings descriptions
    "Redisキャッシュを管理する并を示す統計信息": "Redisキャッシュを管理し、統計情報を表示します",
    "テストメールを送信して確認するSMTP設定": "テストメールを送信してSMTP設定を確認します",

    # File operations
    "選択バックアップファイル": "バックアップファイルを選択",

    # Payment related
    "保留": "保留中",

    # Mode
    " Mode": " モード",
}

def contains_chinese(text: str) -> bool:
    """检查文本是否包含中文字符"""
    return bool(re.search(r'[\u4e00-\u9fff]', str(text)))

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
    print(f"迅猛龙翻译: {lang_code}")
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
    print(f"📊 本轮翻译: {before_count - after_count} 项")
    print(f"🎯 完成度: {completion_rate:.1f}%")

    return {
        'before': before_count,
        'after': after_count,
        'translated': before_count - after_count,
        'completion': completion_rate
    }

def main():
    print("="*80)
    print("迅猛龙翻译系统 - 第十四轮")
    print("日语大幅提升专场！")
    print("="*80)

    results = {}

    print("\n处理德语翻译...")
    results['de-DE'] = translate_file('de-DE', DE_RAPTOR)

    print("\n处理法语翻译...")
    results['fr-FR'] = translate_file('fr-FR', FR_RAPTOR)

    print("\n处理日语翻译...")
    results['ja-JP'] = translate_file('ja-JP', JA_RAPTOR)

    print(f"\n\n{'='*80}")
    print("第十四轮翻译完成总结")
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
        elif stats['completion'] >= 20:
            emoji = "✨"
        else:
            emoji = "🎯"
        print(f"{lang}:")
        print(f"  - 本轮翻译: {stats['translated']} 项")
        print(f"  - 剩余: {stats['after']} 项")
        print(f"  - 完成度: {stats['completion']:.1f}% {emoji}")

    print(f"\n本轮总计翻译: {total_translated} 项")
    print(f"总剩余未翻译: {total_remaining} 项")

    # 计算总体完成度
    original_total = 3601
    completed = original_total - total_remaining
    completion_rate = (completed / original_total) * 100

    print(f"\n🎊 总体完成度: {completion_rate:.1f}% ({completed}/{original_total})")

    # 特别提示
    if results['ja-JP']['completion'] >= 30:
        print(f"\n🎉 日语突破30%！继续努力！")
    elif results['ja-JP']['completion'] >= 25:
        print(f"\n✨ 日语稳步提升！")

if __name__ == '__main__':
    main()
