#!/usr/bin/env python3
"""
完美翻译系统 - 第九轮
专注于支付系统完整翻译
"""

import json
import re
from pathlib import Path
from typing import Dict, Any

# 完美德语翻译字典 - 支付系统完整版
DE_PETA = {
    # 支付计划
    "Funktion特性": "Funktionsmerkmale",
    "特性": "Merkmale",
    "订阅PlanErfolgreich erstellt": "Abonnementplan erfolgreich erstellt",
    "订阅PlanErfolgreich aktualisiert": "Abonnementplan erfolgreich aktualisiert",
    "订阅PlanErfolgreich gelöscht": "Abonnementplan erfolgreich gelöscht",
    "订阅Plan": "Abonnementplan",
    "订阅": "Abonnement",
    "Plan已激活": "Plan aktiviert",
    "已激活": "Aktiviert",
    "激活": "Aktivieren",
    "Plan已停用": "Plan deaktiviert",
    "已停用": "Deaktiviert",
    "停用": "Deaktivieren",

    # 支付相关
    "金额": "Betrag",
    "支付方式": "Zahlungsmethode",
    "支付": "Zahlung",
    "方式": "Methode",
    "支付Zeit": "Zahlungszeit",
    "退款": "Rückerstattung",
    "已退款": "Rückerstattet",
    "Möchten Sie wirklich退款?": "Möchten Sie wirklich eine Rückerstattung durchführen?",
    "退款Erfolg": "Rückerstattung erfolgreich",
    "Durchschnitt交易额": "Durchschnittlicher Transaktionsbetrag",
    "交易额": "Transaktionsbetrag",
    "交易": "Transaktion",
    "额": "Betrag",

    # 优惠券
    "优惠券代码": "Gutscheincode",
    "优惠券": "Gutschein",
    "代码": "Code",
    "折扣": "Rabatt",
    "固定金额": "Fester Betrag",
    "固定": "Fest",
    "折扣值": "Rabattwert",
    "值": "Wert",
    "Niedrigste消费金额": "Mindestkaufbetrag",
    "消费金额": "Kaufbetrag",
    "消费": "Kauf",
    "优惠券Erfolgreich erstellt": "Gutschein erfolgreich erstellt",
    "优惠券Erfolgreich aktualisiert": "Gutschein erfolgreich aktualisiert",
    "优惠券Erfolgreich gelöscht": "Gutschein erfolgreich gelöscht",
    "优惠券已激活": "Gutschein aktiviert",
    "优惠券已停用": "Gutschein deaktiviert",

    # 订阅管理
    "Automatisch续费": "Automatische Verlängerung",
    "续费": "Verlängerung",
    "逾期": "Überfällig",
    "Möchten Sie wirklichEntfernenDiesen订阅?": "Möchten Sie wirklich dieses Abonnement kündigen?",
    "EntfernenDiesen": "Dieses kündigen",
    "Diesen订阅": "Dieses Abonnement",
    "订阅EntfernenErfolg": "Abonnement erfolgreich gekündigt",
    "订阅续费Erfolg": "Abonnement erfolgreich verlängert",
    "Monat度经常性收入": "Monatlich wiederkehrende Einnahmen",
    "度经常性收入": "Wiederkehrende Einnahmen",
    "经常性收入": "Wiederkehrende Einnahmen",
    "经常性": "Wiederkehrend",
    "收入": "Einnahmen",
    "流失率": "Abwanderungsrate",
    "流失": "Abwanderung",
    "Test订阅Anzahl": "Anzahl der Testabonnements",
    "Test订阅": "Testabonnement",
    "逾期订阅Anzahl": "Anzahl überfälliger Abonnements",
    "逾期订阅": "Überfällige Abonnements",
    "Durchschnitt订阅价值": "Durchschnittlicher Abonnementwert",
    "订阅价值": "Abonnementwert",
    "价值": "Wert",
}

# 完美法语翻译字典
FR_PETA = {
    # 支付计划
    "功能特性": "Caractéristiques",
    "特性": "Caractéristiques",
    "订阅计划": "Plan d'abonnement",
    "订阅": "Abonnement",
    "计划": "Plan",
    "已激活": "Activé",
    "激活": "Activer",
    "已停用": "Désactivé",
    "停用": "Désactiver",

    # 支付相关
    "金额": "Montant",
    "支付方式": "Méthode de paiement",
    "支付": "Paiement",
    "方式": "Méthode",
    "支付时间": "Heure de paiement",
    "退款": "Remboursement",
    "已退款": "Remboursé",
    "交易额": "Montant de transaction",
    "交易": "Transaction",
    "额": "Montant",

    # 优惠券
    "优惠券代码": "Code du coupon",
    "优惠券": "Coupon",
    "代码": "Code",
    "折扣": "Réduction",
    "固定金额": "Montant fixe",
    "固定": "Fixe",
    "折扣值": "Valeur de réduction",
    "值": "Valeur",
    "最低消费金额": "Montant d'achat minimum",
    "消费金额": "Montant d'achat",
    "消费": "Achat",

    # 订阅管理
    "自动续费": "Renouvellement automatique",
    "续费": "Renouvellement",
    "逾期": "En retard",
    "流失率": "Taux d'attrition",
    "流失": "Attrition",
    "测试订阅": "Abonnement d'essai",
    "逾期订阅": "Abonnements en retard",
    "订阅价值": "Valeur d'abonnement",
    "价值": "Valeur",
    "月度经常性收入": "Revenu mensuel récurrent",
    "经常性收入": "Revenu récurrent",
    "经常性": "Récurrent",
    "收入": "Revenu",
}

# 完美日语翻译字典
JA_PETA = {
    # 支付计划
    "功能特性": "機能特性",
    "特性": "特性",
    "订阅计划": "サブスクリプションプラン",
    "订阅": "サブスクリプション",
    "已激活": "アクティブ化済み",
    "激活": "アクティブ化",
    "已停用": "非アクティブ化済み",
    "停用": "非アクティブ化",

    # 支付相关
    "金额": "金額",
    "支付方式": "支払い方法",
    "支付时间": "支払い時間",
    "退款": "返金",
    "已退款": "返金済み",
    "交易额": "取引金額",
    "交易": "取引",
    "额": "金額",

    # 优惠券
    "优惠券代码": "クーポンコード",
    "优惠券": "クーポン",
    "代码": "コード",
    "折扣": "割引",
    "固定金额": "固定金額",
    "固定": "固定",
    "折扣值": "割引値",
    "最低消费金额": "最低購入金額",
    "消费金额": "購入金額",
    "消费": "購入",

    # 订阅管理
    "自动续费": "自動更新",
    "续费": "更新",
    "逾期": "期限切れ",
    "流失率": "解約率",
    "流失": "解約",
    "测试订阅": "試用サブスクリプション",
    "逾期订阅": "期限切れサブスクリプション",
    "订阅价值": "サブスクリプション価値",
    "月度经常性收入": "月次経常収益",
    "经常性收入": "経常収益",
    "经常性": "経常",
    "收入": "収益",
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
    print(f"\n{'='*80}")
    print(f"完美翻译: {lang_code}")
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
    print("完美翻译系统 - 第九轮")
    print("="*80)

    results = {}

    print("\n处理德语翻译...")
    results['de-DE'] = translate_file('de-DE', DE_PETA)

    print("\n处理法语翻译...")
    results['fr-FR'] = translate_file('fr-FR', FR_PETA)

    print("\n处理日语翻译...")
    results['ja-JP'] = translate_file('ja-JP', JA_PETA)

    print(f"\n\n{'='*80}")
    print("第九轮翻译完成总结")
    print(f"{'='*80}\n")

    total_translated = sum(r['translated'] for r in results.values())
    total_remaining = sum(r['after'] for r in results.values())

    for lang, stats in results.items():
        emoji = "🌟" if stats['completion'] >= 95 else ("✨" if stats['completion'] >= 80 else "🎯")
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

    print(f"\n总体完成度: {completion_rate:.1f}% ({completed}/{original_total})")

if __name__ == '__main__':
    main()
