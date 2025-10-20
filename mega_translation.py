#!/usr/bin/env python3
"""
超级翻译系统 - 第十八轮
专注日语认证、调度、媒体、角色模块大规模清理
"""

import json
import re
from pathlib import Path
from typing import Dict, Any

# 空德语和法语字典（都已100%）
DE_MEGA = {}
FR_MEGA = {}

# 超级日语字典 - 认证 + 调度 + 媒体 + 角色
JA_MEGA = {
    # Scheduling - 空格修正
    "Calendar 表示": "カレンダー表示",
    "List 表示": "リスト表示",
    "適用 テンプレート": "テンプレートを適用",
    "Smart Suggested 時間": "スマート推奨時間",
    "Use Suggested 時間": "推奨時間を使用",
    "アクション历史": "アクション履歴",
    "历史": "履歴",
    "作成d": "作成済み",
    "Execution 時間": "実行時間",
    "表示 History": "履歴を表示",
    " History": " 履歴",
    "確認 to execute このschedule?": "このスケジュールを実行しますか？",
    " to execute ": " 実行",
    "このschedule": "このスケジュール",
    "Template 名": "テンプレート名",
    "並び替え by 時間": "時間で並び替え",
    "並び替え by Priority": "優先度で並び替え",
    "並び替え by 作成d": "作成日で並び替え",
    "並び替え by ": "で並び替え",
    " by ": " で",
    "作成人": "作成者",
    "戦略別の": "戦略別",

    # Auth - 二要素认证
    "入力してください二要素認証コード": "二要素認証コードを入力してください",
    "設定を開始 2FA": "2FA設定を開始",
    "設定を開始": "設定を開始",
    "入力確認コードするため完了設定置：": "確認コードを入力して設定を完了してください：",
    "するため完了設定置": "して設定を完了してください",
    "設定置": "設定",

    # Auth - 动画站点
    "動画 Site Admin Panel": "動画サイト管理パネル",
    " Site Admin Panel": " サイト管理パネル",

    # Auth - 用户名密码
    "入力してくださいユーザー名": "ユーザー名を入力してください",
    "入力してくださいしたパスワード": "パスワードを入力してください",
    "入力してくださいした": "を入力してください",
    "入力してください4桁の確認コード": "4桁の確認コードを入力してください",
    "確認コードは4位文字": "確認コードは4文字です",
    "位文字": "文字",
    "クリック更新確認コード": "クリックして確認コードを更新",
    "クリック更新": "クリックして更新",

    # Auth - 返回登录
    "戻る to Login": "ログインに戻る",
    " to Login": " ログインに",
    "編集or": "編集者",

    # Auth - 身份验证
    "入力してください身份確認器適用の6桁の確認コード": "認証アプリの6桁の確認コードを入力してください",
    "身份確認器適用の": "認証アプリの",
    "身份": "認証",
    "適用の": "アプリの",
    "または使用バックアップコード（フォーマット：XXXX-XXXX）": "またはバックアップコードを使用（形式：XXXX-XXXX）",
    "または使用": "または使用",
    "使用バックアップコード": "バックアップコードを使用",
    "入力6桁の確認コードまたはバックアップコード": "6桁の確認コードまたはバックアップコードを入力",

    # Auth - 验证码发送
    "送信確認コード": "確認コードを送信",
    "重新送信": "再送信",
    "確認コード送信まであなたのメール，查収": "確認コードがあなたのメールに送信されました。ご確認ください",
    "送信まであなたのメール，查收": "があなたのメールに送信されました。ご確認ください",
    "送信まで": "が送信されました",
    "あなたのメール，查収": "あなたのメールに。ご確認ください",
    "查収": "ご確認ください",
    "確認コード重新送信": "確認コードを再送信しました",
    "重新": "再",
    "入力してください6桁の確認コード": "6桁の確認コードを入力してください",

    # Auth - 确认密码
    "確認 Password": "パスワードを確認",
    " Password": " パスワード",
    "入力してください新しいパスワード（少なくとも8位）": "新しいパスワードを入力してください（少なくとも8文字）",
    "（少なくとも8位）": "（少なくとも8文字）",
    "少なくとも8位": "少なくとも8文字",
    "再入力新しいパスワード": "新しいパスワードを再入力してください",
    "再入力": "再入力してください",
    "パスワードリセット成功！使用新しいパスワードログイン": "パスワードのリセットに成功しました！新しいパスワードでログインしてください",
    "使用新しいパスワードログイン": "新しいパスワードでログインしてください",
    "使用新しいパスワード": "新しいパスワードで",
    "確認 リセット": "リセットを確認",
    " リセット": " リセット",

    # Auth - 密码强度
    "程度": "普通",

    # Auth - 有效期限
    "有効期限15分，及时查收邮件": "有効期限は15分です。すぐにメールをご確認ください",
    "及时查收邮件": "すぐにメールをご確認ください",
    "及时": "すぐに",
    "秒后可重新送信": "秒後に再送信できます",
    "秒后可": "秒後に",
    "可重新": "再送信できます",

    # Auth - 验证失败
    "確認コード加载タイムアウト，再試行してください": "確認コードの読み込みがタイムアウトしました。再試行してください",
    "加载タイムアウト": "の読み込みがタイムアウトしました",
    "加载": "読み込み",
    "確認コード加载失敗，更新再試行": "確認コードの読み込みに失敗しました。更新して再試行してください",
    "加载失敗": "の読み込みに失敗しました",
    "更新再試行": "更新して再試行してください",
    "送信失敗，確認するくださいメールアドレス": "送信に失敗しました。メールアドレスをご確認ください",
    "確認するくださいメールアドレス": "メールアドレスをご確認ください",
    "確認するください": "ご確認ください",
    "メールサービス未設定，連絡してください管理者": "メールサービスが設定されていません。管理者にお問い合わせください",
    "未設定，連絡してください管理者": "が設定されていません。管理者にお問い合わせください",
    "未設定": "設定されていません",
    "連絡してください管理者": "管理者にお問い合わせください",
    "連絡してください": "お問い合わせください",
    "邮件送信失敗，後で再試行": "メール送信に失敗しました。後で再試行してください",
    "邮件送信失敗": "メール送信に失敗しました",
    "邮件": "メール",
    "後で再试": "後で再試行してください",
    "再试": "再試行",
    "账户被無効": "アカウントが無効化されています",
    "账户被": "アカウントが",
    "账户": "アカウント",
    "被無効": "無効化されています",

    # Auth - 登录失败
    "ログイン失敗，確認するくださいユーザー名とパスワード": "ログインに失敗しました。ユーザー名とパスワードをご確認ください",
    "確認するくださいユーザー名とパスワード": "ユーザー名とパスワードをご確認ください",
    "確認するくださいネットワーク": "ネットワークをご確認ください",
    "ログインセッション期限切れ，重新ログイン": "ログインセッションが期限切れです。再ログインしてください",
    "重新ログイン": "再ログインしてください",

    # Auth - 验证码规则
    "確認コードは6位数字": "確認コードは6桁の数字です",
    "位数字": "桁の数字",
    "確認コード必須はい6位数字": "確認コードは6桁の数字である必要があります",
    "必須はい6位数字": "は6桁の数字である必要があります",
    "必須はい": "である必要があります",
    "はい": "",
    "パスワード長少なくとも8位": "パスワードの長さは少なくとも8文字です",
    "長少なくとも8位": "の長さは少なくとも8文字です",
    "長少なくとも": "の長さは少なくとも",
    "確認新しいパスワード": "新しいパスワードを確認してください",

    # Auth - 步骤
    "前へ Step": "前のステップへ",
    " Step": " ステップ",
    "入力してください您登録时使用のメールアドレス，我们将向您送信6位数字確認コード": "登録時に使用したメールアドレスを入力してください。6桁の数字の確認コードを送信します",
    "您登録时使用のメールアドレス，我们将向您送信6位数字確認コード": "登録時に使用したメールアドレスを入力してください。6桁の数字の確認コードを送信します",
    "您登録时使用の": "登録時に使用した",
    "您": "あなたの",
    "登録时使用の": "登録時に使用した",
    "时使用の": "時に使用した",
    "我们将向您送信": "を送信します",
    "我们": "私たちは",
    "将向": "に",
    "向您": "あなたに",
    "6位数字確認コード": "6桁の数字の確認コード",
    "位数字": "桁の数字",

    # Media - 永久删除
    "Permanent 削除": "完全削除",
    " 削除": " 削除",
    "クリアゴミ箱": "ゴミ箱をクリア",
    "作成するFolder": "フォルダーを作成",
    "作成する": "を作成",
    "修改時刻": "更新時刻",
    "修改": "更新",

    # Series - 剧集
    "シリーズ 名": "シリーズ名",
    "シリーズ 説明": "シリーズの説明",
    "合計 s": "合計エピソード数",
    " s": " エピソード数",
    "削除 ": "削除",
    "編集する": "を編集",

    # Roles - 角色权限
    "作成するRole": "ロールを作成",
    "編集するRole": "ロールを編集",
    "削除 Role": "ロールを削除",
    " Role": " ロール",
    "Role 名": "ロール名",
    "Role 説明": "ロールの説明",
    '"例: コンテンツ 編集or, モードrator"': '"例: コンテンツ編集者、モデレーター"',
    "コンテンツ 編集or": "コンテンツ編集者",
    " 編集or": " 編集者",
    "モードrator": "モデレーター",
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
    print("超级翻译系统 - 第十八轮")
    print("认证 + 调度 + 媒体 + 角色模块大规模清理！")
    print("="*80)

    results = {}

    print("\n处理德语翻译...")
    results['de-DE'] = translate_file('de-DE', DE_MEGA)

    print("\n处理法语翻译...")
    results['fr-FR'] = translate_file('fr-FR', FR_MEGA)

    print("\n处理日语翻译...")
    results['ja-JP'] = translate_file('ja-JP', JA_MEGA)

    print(f"\n\n{'='*80}")
    print("第十八轮翻译完成总结")
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
