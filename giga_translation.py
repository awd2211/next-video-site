#!/usr/bin/env python3
"""
超级翻译系统 - 第十九轮
专注日语角色权限、公告、支付计划和验证模块
"""

import json
import re
from pathlib import Path
from typing import Dict, Any

# 空德语和法语字典（都已100%）
DE_GIGA = {}
FR_GIGA = {}

# 超级日语字典 - 角色 + 公告 + 支付 + 验证
JA_GIGA = {
    # Roles - 中文修正
    "简要説明そのロールの責任": "このロールの責任を簡潔に説明",
    "简要説明その": "簡潔に説明",
    "简要": "簡潔に",
    "少なくとも選択1つ権限": "少なくとも1つの権限を選択してください",
    "選択1つ権限": "1つの権限を選択してください",
    "選択1つ": "1つを選択",
    "1つ権限": "1つの権限",
    '削除してもよろしいですかロール""{{name}}""か？この操作は元に戻せません。': 'ロール「{{name}}」を削除してもよろしいですか？この操作は元に戻せません。',
    "削除してもよろしいですかロール": "ロールを削除してもよろしいですか",
    '""{{name}}""か？': '「{{name}}」を',
    "か？": "を",
    "削除に失敗しました role": "ロールの削除に失敗しました",
    " {{username}} ロールを割り当て": " {{username}} にロールを割り当て",
    "超级管理者所有すべての権限，不要ロールを割り当て": "スーパー管理者はすべての権限を持っています。ロールの割り当ては不要です",
    "超级管理者所有すべての権限": "スーパー管理者はすべての権限を持っています",
    "超级管理者": "スーパー管理者",
    "所有すべての": "すべての",
    "所有": "持っています",
    "不要ロールを割り当て": "ロールの割り当ては不要です",
    "不要": "不要です",
    "失敗しました assign role": "ロールの割り当てに失敗しました",
    " assign role": " ロールの割り当て",
    "選択ロール（空白のまま表示キャンセル割り当て）": "ロールを選択（空白のままでキャンセル）",
    "空白のまま表示キャンセル割り当て": "空白のままでキャンセル",
    "表示キャンセル割り当て": "でキャンセル",
    "キャンセル割り当て": "キャンセル",
    "検索 roles...": "ロールを検索...",
    "検索 permissions...": "権限を検索...",
    "検索 admins...": "管理者を検索...",

    # Announcement - 空格修正
    "追加Announcement": "お知らせを追加",
    "編集するAnnouncement": "お知らせを編集",
    "削除 Announcement": "お知らせを削除",
    " Announcement": " お知らせ",

    # System - 时间范围
    "時間 範囲:": "時間範囲:",
    "よく使用される: 1小时=3600, 1日=86400, 1周=604800": "よく使用される: 1時間=3600, 1日=86400, 1週=604800",
    "1小时": "1時間",
    "小时": "時間",
    "1周": "1週",
    "周": "週",

    # OAuth - Configuration
    "保存Configuration": "設定を保存",

    # Page - 描述
    "快速作成新の動画内容": "新しい動画コンテンツを素早く作成",
    "快速作成新の": "新しいを素早く作成",
    "快速": "素早く",
    "作成新の": "新しいを作成",
    "新の": "新しい",
    '表示 and manage system users': 'システムユーザーを表示して管理',
    ' and manage system users': ' システムユーザーを表示して管理',
    "レビュー用户送信の评论": "ユーザーが送信したコメントをレビュー",
    "用户送信の评论": "ユーザーが送信したコメント",
    "用户": "ユーザー",
    "评论": "コメント",
    "戻るホーム": "ホームに戻る",

    # Action - IP/Actor/Director
    "追加IP": "IPを追加",
    "追加Actor": "俳優を追加",
    "追加Director": "監督を追加",

    # Validation - 有效/应在/間
    "入力してください有効のメールアドレス": "有効なメールアドレスを入力してください",
    "入力してください有効のURLアドレス（需するため http:// または https:// で始まる）": "有効なURLアドレスを入力してください（http:// または https:// で始まる必要があります）",
    "入力してください有効のIPアドレス": "有効なIPアドレスを入力してください",
    "有効の": "有効な",
    "（需するため http:// または https:// で始まる）": "（http:// または https:// で始まる必要があります）",
    "需するため": "必要があります",
    "需": "必要",
    "長さ应在 {{min}} まで {{max}}件の文字間": "長さは {{min}} から {{max}} 文字の間である必要があります",
    "长应在 {{min}} まで {{max}}件の文字間": "長さは {{min}} から {{max}} 文字の間である必要があります",
    "应在 {{min}} まで {{max}}件の文字間": "は {{min}} から {{max}} 文字の間である必要があります",
    "应在 {{min}} まで {{max}}": "は {{min}} から {{max}}",
    "应在": "は",
    "件の文字間": "文字の間である必要があります",
    "間": "の間である必要があります",
    "超えることはできません {{max}}件の文字": "{{max}} 文字を超えることはできません",
    "超えることはできません": "を超えることはできません",
    "少なくとも必要 {{min}}件の文字": "少なくとも {{min}} 文字が必要です",
    "少なくとも必要": "少なくとも必要です",
    "件の文字": "文字",
    "值应在 {{min}} まで {{max}} 間": "値は {{min}} から {{max}} の間である必要があります",
    "值应在 {{min}} まで {{max}}": "値は {{min}} から {{max}}",
    "值应在": "値は",
    "值超えることはできません {{max}}": "値は {{max}} を超えることはできません",
    "值未満にすることはできません {{min}}": "値は {{min}} 未満にすることはできません",
    "值超えることはできません": "値はを超えることはできません",
    "值未満にすることはできません": "値は未満にすることはできません",
    "值": "値は",
    "ファイルサイズ超える制限（最大 {{max}}MB）": "ファイルサイズが制限を超えています（最大 {{max}}MB）",
    "超える制限": "が制限を超えています",
    "超える": "を超えています",
    "入力してください動画タイトル": "動画タイトルを入力してください",
    "選択してください動画タイプ": "動画タイプを選択してください",
    "選択してくださいステータス": "ステータスを選択してください",
    "アップロードまたは入力画像URL": "画像をアップロードまたは画像URLを入力",

    # Payment Plans - Create/Edit
    "作成するPlan": "プランを作成",
    "編集するPlan": "プランを編集",
    "合計 Plans": "合計プラン数",
    " Plans": " プラン数",
    "Plan 名": "プラン名",
    "名前 (English)": "名前（英語）",
    "名前 (Chinese)": "名前（中国語）",
    "説明 (English)": "説明（英語）",
    "説明 (Chinese)": "説明（中国語）",
    " (English)": "（英語）",
    " (Chinese)": "（中国語）",

    # Payment Plans - 別の
    "別の月": "月額",
    "別のシーズン": "四半期",
    "別の年": "年額",
    "別の": "",
    "別": "",

    # Payment Plans - 空格修正
    "Trial 日": "トライアル日数",
    " 日": " 日数",
    "動画 Quality": "動画品質",
    " Quality": " 品質",
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
    print("超级翻译系统 - 第十九轮")
    print("角色权限 + 公告 + 支付计划 + 验证模块大规模清理！")
    print("="*80)

    results = {}

    print("\n处理德语翻译...")
    results['de-DE'] = translate_file('de-DE', DE_GIGA)

    print("\n处理法语翻译...")
    results['fr-FR'] = translate_file('fr-FR', FR_GIGA)

    print("\n处理日语翻译...")
    results['ja-JP'] = translate_file('ja-JP', JA_GIGA)

    print(f"\n\n{'='*80}")
    print("第十九轮翻译完成总结")
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
