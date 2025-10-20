#!/usr/bin/env python3
"""
终极翻译系统 - 第十六轮
专注日语AI管理和系统健康模块大规模清理
"""

import json
import re
from pathlib import Path
from typing import Dict, Any

# 空德语和法语字典（都已100%）
DE_ULTIMATE = {}
FR_ULTIMATE = {}

# 终极日语字典 - AI管理 + 系统健康大规模翻译
JA_ULTIMATE = {
    # AI Provider 相关
    "追加 Provider": "プロバイダーを追加",
    "編集 Provider": "プロバイダーを編集",
    "削除 Provider": "プロバイダーを削除",
    "確定要削除このプロバイダーか？": "このプロバイダーを削除してもよろしいですか？",
    "確定要削除": "削除してもよろしいですか",
    "削除に失敗しました provider": "プロバイダーの削除に失敗しました",
    "失敗しました create provider": "プロバイダーの作成に失敗しました",
    "失敗しました update provider": "プロバイダーの更新に失敗しました",

    # 聊天测试
    "聊日テスト": "チャットテスト",
    "聊日": "チャット",
    "聊日成功": "チャットに成功しました",
    "聊日失敗": "チャットに失敗しました",

    # 表单提示
    "入力してください名前": "名前を入力してください",
    "例如：GPT-4 生产環境": "例: GPT-4 本番環境",
    "例如：": "例: ",
    "生产環境": "本番環境",
    "追加 a description for this provider configuration": "このプロバイダー設定の説明を追加",
    "入力してくださいAPIキー": "APIキーを入力してください",
    "入力您のAPIキー（暗号化して保存されます）": "APIキーを入力してください（暗号化して保存されます）",
    "入力您の": "入力してください",
    "您の": "あなたの",
    "選択してくださいモデル": "モデルを選択してください",
    "選択AIモデル": "AIモデルを選択",

    # 设置相关
    "设デフォルト": "デフォルトに設定",
    "设": "設定",

    # AI统计 - 空格修正
    "合計 Requests": "合計リクエスト数",
    "合計 Tokens": "合計トークン数",
    "合計 Cost": "合計コスト",
    "成功 Rate": "成功率",
    "Model 名前": "モデル名",
    "Response 時間": "応答時間",
    "Avg Response 時間": "平均応答時間",
    "Usage 件数": "使用回数",
    " Requests": " リクエスト数",
    " Tokens": " トークン数",
    " Cost": " コスト",
    " Rate": " 率",
    " 名前": " 名",
    " 時間": " 時間",
    " 件数": " 回数",

    # 配额相关 - 中文修正
    "配金額管理": "クォータ管理",
    "配金額": "クォータ",
    "グローバル配金額": "グローバルクォータ",
    "プロバイダー配金額": "プロバイダークォータ",
    "グローバル配金額空白のまま": "グローバルクォータは空白のまま",
    "配金額制限付き": "クォータ制限付き",

    # Quota操作
    "作成 Quota": "クォータを作成",
    "編集 Quota": "クォータを編集",
    "確認 delete this quota?": "このクォータを削除しますか？",
    "作成 ": "作成する",
    "編集 ": "編集する",

    # 速率限制 - 中文修正
    "每分レート制限": "分あたりのレート制限",
    "每小时レート制限": "時間あたりのレート制限",
    "每分": "分あたり",
    "每小时": "時間あたり",

    # 模板相关 - 中文修正
    "模板管理": "テンプレート管理",
    "模板": "テンプレート",
    "模板詳細": "テンプレート詳細",
    "模板の用途": "テンプレートの用途",
    "この模板の用途": "このテンプレートの用途",
    "作成 Template": "テンプレートを作成",
    "編集 Template": "テンプレートを編集",
    "確認 delete this template?": "このテンプレートを削除しますか？",
    " Template": " テンプレート",

    # 摘要相关 - 中文修正
    "要約合計结": "要約とまとめ",
    "合計结": "まとめ",

    # JSON相关 - 中文修正
    "包含変数例值のJSONオブジェクト": "変数のサンプル値を含むJSONオブジェクト",
    "包含推奨モデルパラメータのJSONオブジェクト": "推奨モデルパラメータを含むJSONオブジェクト",
    "包含": "含む",
    "例値": "サンプル値",
    "無効の例変数JSONフォーマット": "無効なサンプル変数のJSONフォーマット",
    "無効の推奨パラメータJSONフォーマット": "無効な推奨パラメータのJSONフォーマット",
    "無効の": "無効な",

    # 变量相关
    "例変数": "サンプル変数",
    "を含む入力{変数}のプロンプトテンプレート": "{変数}を含むプロンプトテンプレートを入力",
    "を含む入力": "を含む入力",
    "説明この模板の用途": "このテンプレートの用途を説明",
    "説明この": "説明する",

    # 提示文本 - 中文修正
    "カンマ区切りの変数名（如：title, description）": "カンマ区切りの変数名（例: title, description）",
    "（如：": "（例: ",
    "如：": "例: ",

    # 成本相关
    "今日コスト": "今日のコスト",
    "今月コスト": "今月のコスト",
    "予測月度コスト": "予測月間コスト",
    "月度": "月間",
    "別モデル統計コスト": "モデル別のコスト統計",
    "別プロバイダー統計コスト": "プロバイダー別のコスト統計",
    "別": "別の",
    "統計": "統計",

    # 完了Token
    "完了Token": "完了トークン",

    # 通知相关
    "すべて标既読": "すべて既読にする",
    "标既読": "既読にする",
    "已既読にする": "既読にしました",
    "已": "",
    "削除 this notification?": "この通知を削除しますか？",

    # 系统健康 - 更新间隔
    "更新 Interval": "更新間隔",
    " Interval": " 間隔",

    # 系统健康 - Keys
    "Keys 件数": "キー数",
    "Keys ": "キー",

    # 其他常用词修正
    "確認 delete this log?": "このログを削除しますか？",
    "確認 delete ": "削除しますか ",
    " delete this ": " この",
    " delete ": " 削除",
    "this ": "この",

    # e.g. 修正
    '"e.g., 動画 説明 Generator"': '"例: 動画説明ジェネレーター"',
    "e.g., ": "例: ",

    # Generator 修正
    " Generator": " ジェネレーター",

    # 説明相关空格修正
    "動画 説明 Generator": "動画説明ジェネレーター",
    "動画 説明": "動画説明",
    " 説明 ": "説明",
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
    print(f"终极翻译: {lang_code}")
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
    print("终极翻译系统 - 第十六轮")
    print("AI管理 + 系统健康模块大规模翻译！")
    print("="*80)

    results = {}

    print("\n处理德语翻译...")
    results['de-DE'] = translate_file('de-DE', DE_ULTIMATE)

    print("\n处理法语翻译...")
    results['fr-FR'] = translate_file('fr-FR', FR_ULTIMATE)

    print("\n处理日语翻译...")
    results['ja-JP'] = translate_file('ja-JP', JA_ULTIMATE)

    print(f"\n\n{'='*80}")
    print("第十六轮翻译完成总结")
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
