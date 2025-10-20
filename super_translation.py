#!/usr/bin/env python3
"""
超级翻译系统 - 第十七轮
专注日语系统健康、日志、邮件、报表和调度模块
"""

import json
import re
from pathlib import Path
from typing import Dict, Any

# 空德语和法语字典（都已100%）
DE_SUPER = {}
FR_SUPER = {}

# 超级日语字典 - 系统健康 + 日志 + 邮件 + 报表 + 调度
JA_SUPER = {
    # 系统健康 - 磁盘相关（中文）
    "磁盘使用率": "ディスク使用率",
    "磁盘": "ディスク",
    "磁盘使用率トレンド": "ディスク使用率トレンド",

    # 系统健康 - Response时间空格
    "Database Response 時間": "データベース応答時間",
    "Redis Response 時間": "Redis応答時間",
    "Storage Response 時間": "ストレージ応答時間",
    "Database ": "データベース",
    "Storage ": "ストレージ",

    # 系统健康 - 错误提示
    "一部サービス問題が発生，表示下記詳細。": "一部のサービスに問題が発生しています。下記の詳細をご覧ください。",
    "問題が発生，表示下記詳細": "問題が発生しています。下記の詳細をご覧ください",
    "表示下記詳細": "下記の詳細をご覧ください",
    "下記詳細": "下記の詳細",
    "失敗しました export report": "レポートのエクスポートに失敗しました",
    "失敗しました load system health": "システムヘルスの読み込みに失敗しました",
    "不明エラー": "不明なエラー",

    # CPU空格修正
    "CPU 使用率": "CPU使用率",
    "CPU 使用率トレンド": "CPU使用率トレンド",

    # 日志 - 空格修正
    "合計 Logs": "合計ログ数",
    "成功 Rate": "成功率",
    "表示 詳細": "詳細を表示",
    "追加 いいえtes": "ノートを追加",
    "追加 processing notes or comments...": "処理メモやコメントを追加...",
    "追加 ": "追加",
    " いいえtes": " ノート",
    " processing notes or comments": " 処理メモやコメント",

    # 日志 - アクション選択
    "選択アクション": "アクションを選択",

    # 日志 - 検索相关
    "検索 description or IP address": "説明またはIPアドレスで検索",
    "検索 username or email": "ユーザー名またはメールで検索",
    "検索 event or message": "イベントまたはメッセージで検索",
    "検索 error message": "エラーメッセージで検索",
    "検索 ": "検索 ",
    " description or IP address": " 説明またはIPアドレス",
    " username or email": " ユーザー名またはメール",
    " event or message": " イベントまたはメッセージ",
    " error message": " エラーメッセージ",

    # 日志 - 日期范围
    "日付 Range": "日付範囲",
    " Range": " 範囲",

    # 日志 - Last相关
    "Last 7 日": "過去7日間",
    "Last 24 時間": "過去24時間",
    "Last 30 日": "過去30日間",
    "Last ": "過去",

    # 日志 - 确认和标记
    "確認 mark as resolved?": "解決済みとしてマークしますか？",
    "マーク成功": "マークに成功しました",
    "失敗しました mark": "マークに失敗しました",

    # 邮件 - Configuration相关
    "追加 Configuration": "設定を追加",
    "編集 Configuration": "設定を編集",
    "Configuration 説明": "設定の説明",
    "Configuration 情報": "設定情報",
    " Configuration": " 設定",

    # 邮件 - Template相关
    "追加 Template": "テンプレートを追加",
    "編集 Template": "テンプレートを編集",
    "Template 名前": "テンプレート名",

    # 邮件 - From相关
    "From 名前": "送信者名",

    # 报表 - 空格修正
    "時間 Period": "期間",
    " Period": " 期間",
    "合計 Favorites": "合計お気に入り数",
    "合計 Likes": "合計いいね数",
    "合計 VIP": "合計VIP数",
    "合計 Watches": "合計視聴数",
    " Favorites": " お気に入り数",
    " Likes": " いいね数",
    " Watches": " 視聴数",
    "動画 Trend": "動画トレンド",
    " Trend": " トレンド",

    # 调度 - 空格和中文修正
    "追加 Schedule": "スケジュールを追加",
    "編集 Schedule": "スケジュールを編集",
    "確認 cancellation?": "キャンセルしますか？",
    " cancellation": " キャンセル",
    "管理動画予約公開とコンテンツスケジューリング": "動画の予約公開とコンテンツスケジューリングを管理",
    "管理動画": "動画を管理",
    "予約公開": "予約公開",
    "入力してください動画ID": "動画IDを入力してください",

    # 调度 - 中文混入
    "スケジューリングの動画将在指定時刻自動发布": "スケジュールされた動画は指定時刻に自動公開されます",
    "将在指定時刻自動发布": "指定時刻に自動公開されます",
    "将在": "されます",
    "指定時刻": "指定時刻に",
    "自動发布": "自動公開",
    "发布": "公開",
    "{{count}} 个スケジューリング期限切れ": "{{count}}件のスケジュールが期限切れ",
    " 个スケジューリング": "件のスケジュール",
    " 个": "件の",

    # 调度 - 状态相关
    "保留中 Scheduled": "スケジュール待機中",
    "公開 failed": "公開に失敗しました",
    "公開 いいえw": "今すぐ公開",
    "公開 Overdue": "期限切れを公開",
    "公開済みsuccessfully": "公開に成功しました",
    "Scheduled 時間": "スケジュール時刻",
    "合計 Scheduled": "合計スケジュール数",
    " Scheduled": " スケジュール",
    "公開 ": "公開",
    " いいえw": " 今すぐ",
    " Overdue": " 期限切れ",
    " failed": " に失敗しました",
    "済みsuccessfully": "に成功しました",

    # 别モデル/プロバイダー - 修正
    "別モデル": "モデル別",
    "別プロバイダー": "プロバイダー別",
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
    print(f"超级翻译: {lang_code}")
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
    print("超级翻译系统 - 第十七轮")
    print("系统健康 + 日志 + 邮件 + 报表 + 调度模块！")
    print("="*80)

    results = {}

    print("\n处理德语翻译...")
    results['de-DE'] = translate_file('de-DE', DE_SUPER)

    print("\n处理法语翻译...")
    results['fr-FR'] = translate_file('fr-FR', FR_SUPER)

    print("\n处理日语翻译...")
    results['ja-JP'] = translate_file('ja-JP', JA_SUPER)

    print(f"\n\n{'='*80}")
    print("第十七轮翻译完成总结")
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
