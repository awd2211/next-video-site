#!/usr/bin/env python3
"""
霸王龙翻译系统 - 第十五轮
专注日语深度清理：消除中文和英文混入
"""

import json
import re
from pathlib import Path
from typing import Dict, Any

# 空德语和法语字典（都已100%）
DE_TREX = {}
FR_TREX = {}

# 霸王龙日语字典 - 深度清理
JA_TREX = {
    # 修复英文混入的完整句子
    "設定 restored successfully": "設定の復元に成功しました",
    "設定を復元しますか? This will override current 設定.": "設定を復元しますか？現在の設定が上書きされます。",
    "すべての設定をデフォルトにリセットしますか? This action cannot be undone.": "すべての設定をデフォルトにリセットしますか？この操作は元に戻せません。",
    "失敗しました delete": "削除に失敗しました",
    "追加ed successfully": "追加に成功しました",
    "作成 your first {{type}} to get started": "最初の{{type}}を作成して始めましょう",
    "名前 cannot be empty": "名前を空にすることはできません",
    "失敗しました load file list": "ファイルリストの読み込みに失敗しました",
    "失敗しました load folder tree": "フォルダツリーの読み込みに失敗しました",
    "失敗しました load recycle bin": "ゴミ箱の読み込みに失敗しました",
    "失敗しました export backup": "バックアップのエクスポートに失敗しました",
    "確認 delete {{count}} selected item(s)?": "選択した{{count}}項目を削除しますか？",
    "確認 to {{action}} {{count}} selected {{type}}?": "選択した{{count}}個の{{type}}を{{action}}しますか？",

    # 修复中文混入的句子
    "このフィールド必須件": "このフィールドは必須です",
    "请入力": "入力してください",
    "请選択": "選択してください",
    "请先選択": "先に選択してください",
    "尝试调整検索件件またはフィルター件件": "検索条件またはフィルター条件を調整してください",
    "2FA已成功有効！": "2FAが正常に有効化されました！",
    "2FA设置已初始化": "2FA設定が初期化されました",
    "2FA 已無効": "2FAが無効化されました",
    "密コード修改成功，建议重新ログイン": "パスワードの変更に成功しました。再ログインすることをお勧めします",
    "メール修改成功": "メールの変更に成功しました",
    "已复制まで剪贴板": "クリップボードにコピーしました",
    "复制失敗": "コピーに失敗しました",
    "Banner已削除": "バナーが削除されました",
    "お知らせ已削除": "お知らせが削除されました",
    "IP已复制": "IPがコピーされました",
    "SQL已复制": "SQLがコピーされました",
    "URL已复制": "URLがコピーされました",
    "スタックトレース已复制まで剪贴板": "スタックトレースがクリップボードにコピーされました",
    "スタックトレース已ダウンロード": "スタックトレースがダウンロードされました",
    "完整エラーレポート已复制まで剪贴板": "完全なエラーレポートがクリップボードにコピーされました",
    "ゴミ箱已クリア": "ゴミ箱がクリアされました",
    "已クリア履歴": "履歴がクリアされました",
    "サーバーエラー，请後で再試行": "サーバーエラー、後で再試行してください",
    "ログイン期限切れ，请重新ログイン": "ログインが期限切れです。再ログインしてください",
    "2回入力の密コード一致しません": "2回入力したパスワードが一致しません",
    "バックアップ文件フォーマットエラー": "バックアップファイルのフォーマットエラー",
    "アクション成功": "アクションに成功しました",
    "並び替え 順序": "並び替え順序",

    # 中文词汇修正
    "必須件": "必須です",
    "件件": "条件",
    "已成功有効": "が正常に有効化されました",
    "设置已初始化": "設定が初期化されました",
    "已無効": "が無効化されました",
    "修改成功": "の変更に成功しました",
    "已复制": "がコピーされました",
    "复制": "コピー",
    "已削除": "が削除されました",
    "已ダウンロード": "がダウンロードされました",
    "まで剪贴板": "クリップボードに",
    "剪贴板": "クリップボード",
    "已クリア": "がクリアされました",
    "请": "",
    "建议": "お勧めします",
    "完整": "完全な",
    "文件": "ファイル",

    # 英文词汇修正
    " restored successfully": "の復元に成功しました",
    " This will override current ": " 現在の",
    " This action cannot be undone.": " この操作は元に戻せません。",
    " cannot be empty": "を空にすることはできません",
    " your first ": "最初の",
    " to get started": "を作成して始めましょう",
    "ed successfully": "に成功しました",
    " selected item(s)": " 選択した項目",
    " selected ": " 選択した",
    "item(s)": "項目",

    # 其他空格修正
    "編集 モード": "編集モード",
    "更新d 日時": "更新日時",
    "合計 ユーザー": "合計ユーザー",
    "合計 動画": "合計動画",
    "合計 コメント": "合計コメント",
    "合計 表示数": "合計表示数",
    "動画 ID": "動画ID",
    "動画 設定": "動画設定",
    "コメント 設定": "コメント設定",
    "ユーザー 設定": "ユーザー設定",
    "アップロード 設定": "アップロード設定",
    "動画 タイプ分布": "動画タイプ分布",

    # 密码相关
    "密コード": "パスワード",
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
    print(f"霸王龙翻译: {lang_code}")
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
    print("霸王龙翻译系统 - 第十五轮")
    print("日语深度清理专场！")
    print("="*80)

    results = {}

    print("\n处理德语翻译...")
    results['de-DE'] = translate_file('de-DE', DE_TREX)

    print("\n处理法语翻译...")
    results['fr-FR'] = translate_file('fr-FR', FR_TREX)

    print("\n处理日语翻译...")
    results['ja-JP'] = translate_file('ja-JP', JA_TREX)

    print(f"\n\n{'='*80}")
    print("第十五轮翻译完成总结")
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
    if results['ja-JP']['completion'] >= 35:
        print(f"\n🎉🎉 日语突破35%！大幅进步！")
    elif results['ja-JP']['completion'] >= 30:
        print(f"\n🎉 日语突破30%！继续努力！")
    elif results['ja-JP']['completion'] >= 25:
        print(f"\n✨ 日语稳步提升！")

if __name__ == '__main__':
    main()
