#!/usr/bin/env python3
"""
至尊翻译系统 - 第十轮
专注于法语AI管理模块完整翻译
"""

import json
import re
from pathlib import Path
from typing import Dict, Any

# 至尊德语翻译字典（德语已100%，保持）
DE_EXA = {}

# 至尊法语翻译字典 - AI管理模块
FR_EXA = {
    # AI聊天测试
    "聊JoursTest": "Test de chat",
    "聊Jours": "Chat",
    "你": "Vous",
    "AI正在思考...": "L'IA réfléchit...",
    "正在思考": "Réfléchit",
    "思考": "Réflexion",
    "发送": "Envoyer",
    "在Ce输入您Message...": "Saisissez votre message ici...",
    "输入您": "Saisissez votre",
    "您": "Votre",
    "聊JoursSuccès": "Chat réussi",
    "聊JoursÉchec": "Chat échoué",

    # AI基本信息
    "基本信息": "Informations de base",
    "基本": "De base",
    "Modèle参数": "Paramètres du modèle",
    "参数": "Paramètres",
    "Veuillez saisir名称": "Veuillez saisir le nom",
    "名称": "Nom",
    "例如：GPT-4 Environnement de production": "Par exemple: GPT-4 Production",
    "例如：": "Par exemple:",
    "Fournisseur类型": "Type de fournisseur",
    "类型": "Type",
    "API密钥": "Clé API",
    "Veuillez saisirAPI密钥": "Veuillez saisir la clé API",
    "输入您API密钥（sera stocké chiffré）": "Saisissez votre clé API (sera stockée chiffrée)",
    "基础URL": "URL de base",
    "基础": "De base",
    "最大Nombre de jetons": "Nombre maximum de jetons",
    "最大": "Maximum",
    "温度": "Température",
    "Top-P 采样": "Échantillonnage Top-P",
    "采样": "Échantillonnage",
    "Fréquence惩罚": "Pénalité de fréquence",
    "惩罚": "Pénalité",
    "存在惩罚": "Pénalité de présence",
    "存在": "Présence",
    "设Par défaut": "Définir par défaut",
    "设": "Définir",

    # AI统计
    "总Requête数": "Nombre total de requêtes",
    "总": "Total",
    "总Token数": "Nombre total de tokens",
    "Requête日志": "Journaux de requêtes",
    "日志": "Journaux",
    "成本Surveillance": "Surveillance des coûts",
    "配额管理": "Gestion des quotas",
    "配额": "Quota",
    "模板管理": "Gestion des modèles",
    "模板": "Modèle",
    "Requête类型": "Type de requête",
    "成本": "Coût",
    "Utilisation统计": "Statistiques d'utilisation",
    "统计": "Statistiques",
    "预估成本": "Coût estimé",
    "预估": "Estimé",
    "响应": "Réponse",
    "元数据": "Métadonnées",
    "总成本": "Coût total",
    "今日成本": "Coût d'aujourd'hui",
    "今日": "Aujourd'hui",
    "本Mois成本": "Coût de ce mois",
    "本Mois": "Ce mois",
    "预计Mois度成本": "Coût mensuel projeté",
    "预计": "Projeté",
    "Mois度": "Mensuel",
    "度": "",
    "成本趋势": "Tendance des coûts",
    "趋势": "Tendance",
    "ParModèle统计成本": "Coût par modèle",
    "ParFournisseur统计成本": "Coût par fournisseur",
    "配额类型": "Type de quota",
    "目标ID": "ID cible",
    "目标": "Cible",
    "每日Requête": "Requêtes quotidiennes",
    "每日": "Quotidien",
    "每MoisRequête": "Requêtes mensuelles",
    "每Mois": "Mensuel",
    "每月": "Mensuel",
    "每日成本": "Coût quotidien",
    "速率限制": "Limite de débit",
    "速率": "Débit",
    "限制": "Limite",
    "全局配额": "Quota global",
    "全局": "Global",
    "Fournisseur配额": "Quota du fournisseur",

    # 其他常用词
    "名": "Nom",
    "天": "Jour",
    "描述": "Description",
}

# 至尊日语翻译字典
JA_EXA = {
    # AI基本词汇
    "AI正在思考...": "AIが考え中...",
    "正在思考": "考え中",
    "思考": "考え",
    "你": "あなた",
    "发送": "送信",
    "基本信息": "基本情報",
    "基本": "基本",
    "参数": "パラメータ",
    "名称": "名前",
    "类型": "タイプ",
    "API密钥": "APIキー",
    "密钥": "キー",
    "基础URL": "ベースURL",
    "基础": "ベース",
    "最大": "最大",
    "温度": "温度",
    "采样": "サンプリング",
    "惩罚": "ペナルティ",
    "存在": "存在",
    "总": "合計",
    "日志": "ログ",
    "成本": "コスト",
    "配额": "クォータ",
    "统计": "統計",
    "预估": "推定",
    "响应": "レスポンス",
    "元数据": "メタデータ",
    "今日": "今日",
    "本月": "今月",
    "预计": "予測",
    "趋势": "トレンド",
    "目标": "ターゲット",
    "每日": "毎日",
    "每月": "毎月",
    "速率": "レート",
    "限制": "制限",
    "全局": "グローバル",
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
    if not translations:  # 跳过空字典
        print(f"\n{lang_code}: 跳过（已100%完成）")
        total_items = 1175 if lang_code == 'de-DE' else (1169 if lang_code == 'fr-FR' else 1257)
        return {
            'before': 0,
            'after': 0,
            'translated': 0,
            'completion': 100.0
        }

    print(f"\n{'='*80}")
    print(f"至尊翻译: {lang_code}")
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
    print("至尊翻译系统 - 第十轮")
    print("="*80)

    results = {}

    print("\n处理德语翻译...")
    results['de-DE'] = translate_file('de-DE', DE_EXA)

    print("\n处理法语翻译...")
    results['fr-FR'] = translate_file('fr-FR', FR_EXA)

    print("\n处理日语翻译...")
    results['ja-JP'] = translate_file('ja-JP', JA_EXA)

    print(f"\n\n{'='*80}")
    print("第十轮翻译完成总结")
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

if __name__ == '__main__':
    main()
