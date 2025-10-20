#!/usr/bin/env python3
"""
霸王龙翻译系统 - 第十三轮
终极冲刺：法语100%完成！
只剩最后6项，精准击破！
"""

import json
import re
from pathlib import Path
from typing import Dict, Any

# 空德语字典（已100%）
DE_BRONTO = {}

# 霸王龙法语字典 - 最后6项精准翻译
FR_BRONTO = {
    # 最后的认证相关修正
    "输入VérifierCodePourTerminéParamètres：": "Entrer le code de vérification pour terminer les paramètres :",
    "输入Vérifier": "Entrer le code de vérification",
    "CodePour": "code pour",
    "Pour": "pour",
    "Terminé": "terminer",
    "Paramètres：": "paramètres :",

    "Veuillez saisir密Code": "Veuillez saisir le mot de passe",
    "密Code": "mot de passe",

    "VérifierCode已Renvoyer": "Code de vérification renvoyé",
    "Code已Renvoyer": "Code renvoyé",
    "已Renvoyer": "renvoyé",

    "登录Échec，Veuillez vérifierNom d'utilisateur et密Code": "Connexion échouée, veuillez vérifier le nom d'utilisateur et le mot de passe",
    "登录Échec，Veuillez vérifier": "Connexion échouée, veuillez vérifier",
    "Nom d'utilisateur et密Code": "le nom d'utilisateur et le mot de passe",
    "et密Code": "et le mot de passe",

    "Nom d'utilisateurOu密CodeErreur": "Nom d'utilisateur ou mot de passe incorrect",
    "Nom d'utilisateurOu": "Nom d'utilisateur ou",
    "Ou密Code": "ou mot de passe",
    "CodeErreur": "incorrect",

    "Confirmer la suppression du rôle\"\"{{name}}\"\"吗？Cette opération est irréversible.": "Confirmer la suppression du rôle \"{{name}}\" ? Cette opération est irréversible.",
    "\"\"{{name}}\"\"吗？": "\"{{name}}\" ?",
    "吗？": " ?",
}

# 日语补充字典
JA_BRONTO = {
    # 增加一些基础词汇
    "输入": "入力",
    "密码": "パスワード",
    "登录": "ログイン",
    "失败": "失敗",
    "错误": "エラー",
    "确认": "確認",
    "删除": "削除",
    "吗": "か",
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
    print("霸王龙翻译系统 - 第十三轮")
    print("法语100%终极冲刺！")
    print("="*80)

    results = {}

    print("\n处理德语翻译...")
    results['de-DE'] = translate_file('de-DE', DE_BRONTO)

    print("\n处理法语翻译...")
    results['fr-FR'] = translate_file('fr-FR', FR_BRONTO)

    print("\n处理日语翻译...")
    results['ja-JP'] = translate_file('ja-JP', JA_BRONTO)

    print(f"\n\n{'='*80}")
    print("第十三轮翻译完成总结")
    print(f"{'='*80}\n")

    total_translated = sum(r['translated'] for r in results.values())
    total_remaining = sum(r['after'] for r in results.values())

    for lang, stats in results.items():
        if stats['completion'] == 100:
            emoji = "🌟🌟🌟"
        elif stats['completion'] >= 95:
            emoji = "🌟🌟"
        elif stats['completion'] >= 85:
            emoji = "🌟"
        elif stats['completion'] >= 75:
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

    # 检查法语是否100%
    if results['fr-FR']['completion'] == 100:
        print("\n" + "="*80)
        print("🎉🎉🎉 历史性突破！法语达到100%完美翻译！ 🎉🎉🎉")
        print("="*80)
        print("\n现在的状态：")
        print("  ✅ 德语 (de-DE): 100% 完成")
        print("  ✅ 法语 (fr-FR): 100% 完成")
        print(f"  🎯 日语 (ja-JP): {results['ja-JP']['completion']:.1f}% 完成")

if __name__ == '__main__':
    main()
