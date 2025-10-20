#!/usr/bin/env python3
"""
终极翻译系统 - 第五轮
基于最新CSV内容的针对性翻译
"""

import json
import re
from pathlib import Path
from typing import Dict, Any

# 终极德语翻译字典
DE_ULTRA = {
    # 修正错误翻译
    "聊Tage": "Chat",
    "聊": "Chat",

    # 系统健康和监控
    "Verbindung池": "Verbindungspool",
    "池大小": "Poolgröße",
    "池Auslastung": "Pool-Auslastung",
    "池": "Pool",
    "已使用": "Verwendet",
    "存储桶存在": "Bucket vorhanden",
    "读取权限": "Leseberechtigung",
    "受限": "Eingeschränkt",
    "进程": "Prozesse",
    "核心": "Kerne",
    "频率": "Frequenz",
    "空闲": "Frei",
    "无Limit": "Unbegrenzt",
    "网络统计": "Netzwerkstatistiken",
    "接收数据": "Empfangene Daten",
    "Senden数据包": "Gesendete Pakete",
    "接收数据包": "Empfangene Pakete",
    "接收丢包": "Empfangener Paketverlust",
    "Senden丢包": "Gesendeter Paketverlust",
    "丢包": "Paketverlust",
    "部分Dienst出现问题，请查看下方Details": "Einige Dienste haben Probleme, siehe Details unten",
    "报告Erfolgreich exportiert": "Bericht erfolgreich exportiert",

    # 日志相关
    "系统日志": "Systemprotokolle",
    "登录日志": "Anmeldeprotokolle",
    "今日日志": "Heutige Protokolle",
    "Fehlgeschlagen率": "Fehlerrate",
    "Markieren als已解决": "Als gelöst markieren",
    "已解决": "Gelöst",
    "未解决": "Ungelöst",
    "Stapel解决": "Stapelauflösung",
    "管理员": "Administrator",
    "模块": "Modul",
    "请求方法": "Anfragemethode",
    "请求URL": "Anfrage-URL",
    "Anzahl der Anfragen据": "Anfragedaten",
    "请求数据": "Anfragedaten",
    "被拦截": "Blockiert",
    "Fehlgeschlagen原因": "Fehlergrund",
    "设备": "Gerät",
    "浏览器": "Browser",
    "操作系统": "Betriebssystem",
    "地理位置": "Standort",
    "级别": "Stufe",
    "事件": "Ereignis",
    "消息": "Nachricht",
    "来源": "Quelle",
    "Detailliert信息": "Detaillierte Informationen",
    "Status码": "Statuscode",
    "堆栈跟踪": "Stack-Trace",
    "解决人": "Gelöst von",
    "解决Zeit": "Gelöst am",
    "选择模块": "Modul auswählen",
    "选择操作": "Aktion auswählen",
    "选择级别": "Stufe auswählen",
    "选择解决Status": "Lösungsstatus auswählen",
    "统计数据": "Statistiken",
    "标记Erfolg": "Erfolgreich markiert",
    "今Tage": "Heute",

    # 邮件相关
    "邮件Konfiguration": "E-Mail-Konfiguration",
    "发件人E-Mail": "Absender-E-Mail",
    "发件人Name": "Absender-Name",
    "发件人": "Absender",
    "E-Mail格式无效": "Ungültiges E-Mail-Format",
    "标识": "Kennung",
    "SMTP主机": "SMTP-Host",
    "SMTP密码": "SMTP-Passwort",
    "SMTP端口": "SMTP-Port",
    "主题": "Betreff",
    "邮件模板": "E-Mail-Vorlagen",
    "Testen邮件": "Test-E-Mail",
    "Testen邮件已Senden": "Test-E-Mail gesendet",

    # 报表相关
    "行为统计": "Verhaltensstatistiken",
    "过期率": "Ablaufrate",
    "即将过期": "Läuft bald ab",
    "VIP提醒": "VIP-Erinnerungen",
    "VIP转化率": "VIP-Konversionsrate",
    "转化率": "Konversionsrate",

    # 调度相关
    "VerwaltungVideos定时发布和Inhalt调度": "Videos planen und Inhalte verwalten",
    "调度的Videos将在指定Zeit自动发布": "Geplante Videos werden zum angegebenen Zeitpunkt automatisch veröffentlicht",
    "定时发布": "Geplante Veröffentlichung",
    "内容调度": "Inhaltsplanung",
    "调度": "Planung",
    "过期提醒": "Ablauferinnerung",
    "{{count}} 个调度Abgelaufen": "{{count}} geplante Veröffentlichungen abgelaufen",
    "调度Erfolgreich erstellt": "Planung erfolgreich erstellt",
    "调度Abgelaufen": "Planung abgelaufen",
    "今日发布": "Heute veröffentlicht",
    "未来24Stunde": "Nächste 24 Stunden",
    "横幅": "Banner",
    "公告": "Ankündigung",
    "empfohlen位": "Empfohlener Platz",
    "优先级": "Priorität",
    "重复": "Wiederholung",
    "一次性": "Einmalig",
    "每周": "Wöchentlich",
    "立即发布": "Sofort veröffentlichen",
    "渐进式": "Progressiv",
    "区域定时": "Regionale Zeitplanung",
    "Stapel执行": "Stapelausführung",
    "批量执行": "Stapelausführung",
    "自动下线": "Automatisch offline",
    "历史记录": "Verlauf",

    # 通用词汇补充
    "Variablen名": "Variablennamen",
    "（如：": " (z.B.:",
    "已用": "Verwendet",
    "最大": "Maximum",
    "最小": "Minimum",
    "当前": "Aktuell",
    "今日": "Heute",
    "昨日": "Gestern",
    "本周": "Diese Woche",
    "本月": "Dieser Monat",
    "本年": "Dieses Jahr",
    "总数": "Gesamt",
    "数量": "Anzahl",
    "次数": "Häufigkeit",
    "比例": "Verhältnis",
    "百分比": "Prozentsatz",
    "增长": "Wachstum",
    "下降": "Rückgang",
    "平均": "Durchschnitt",
    "最高": "Höchste",
    "最低": "Niedrigste",
}

# 终极法语翻译字典
FR_ULTRA = {
    # 系统健康和监控
    "连接池": "Pool de connexions",
    "池大小": "Taille du pool",
    "已使用": "Utilisé",
    "存储桶存在": "Bucket existe",
    "读取权限": "Permission de lecture",
    "受限": "Limité",
    "进程": "Processus",
    "核心": "Cœurs",
    "频率": "Fréquence",
    "空闲": "Libre",
    "无限制": "Illimité",
    "网络统计": "Statistiques réseau",
    "接收数据": "Données reçues",
    "发送数据包": "Paquets envoyés",
    "接收数据包": "Paquets reçus",
    "接收丢包": "Perte de paquets reçus",
    "发送丢包": "Perte de paquets envoyés",
    "丢包": "Perte de paquets",

    # 日志相关
    "系统日志": "Journaux système",
    "登录日志": "Journaux de connexion",
    "今日日志": "Journaux du jour",
    "失败率": "Taux d'échec",
    "标记为已解决": "Marquer comme résolu",
    "已解决": "Résolu",
    "未解决": "Non résolu",
    "批量解决": "Résolution en lot",
    "管理员": "Administrateur",
    "模块": "Module",
    "请求方法": "Méthode de requête",
    "请求URL": "URL de requête",
    "请求数据": "Données de requête",
    "被拦截": "Bloqué",
    "失败原因": "Raison de l'échec",
    "设备": "Appareil",
    "浏览器": "Navigateur",
    "操作系统": "Système d'exploitation",
    "地理位置": "Emplacement",
    "级别": "Niveau",
    "事件": "Événement",
    "消息": "Message",
    "来源": "Source",
    "详细信息": "Informations détaillées",
    "状态码": "Code d'état",
    "堆栈跟踪": "Trace de pile",
    "解决人": "Résolu par",
    "解决时间": "Résolu le",
    "选择模块": "Sélectionner le module",
    "选择操作": "Sélectionner l'action",
    "选择级别": "Sélectionner le niveau",
    "选择解决状态": "Sélectionner l'état de résolution",
    "统计数据": "Statistiques",
    "标记成功": "Marqué avec succès",
    "今天": "Aujourd'hui",

    # 邮件相关
    "邮件配置": "Configuration e-mail",
    "发件人邮箱": "E-mail de l'expéditeur",
    "发件人名称": "Nom de l'expéditeur",
    "发件人": "Expéditeur",
    "邮箱格式无效": "Format d'e-mail invalide",
    "标识": "Identifiant",
    "SMTP主机": "Hôte SMTP",
    "SMTP密码": "Mot de passe SMTP",
    "SMTP端口": "Port SMTP",
    "主题": "Sujet",
    "邮件模板": "Modèles d'e-mail",
    "测试邮件": "E-mail de test",
    "测试邮件已发送": "E-mail de test envoyé",

    # 报表相关
    "行为统计": "Statistiques de comportement",
    "过期率": "Taux d'expiration",
    "即将过期": "Expire bientôt",
    "VIP提醒": "Rappels VIP",
    "VIP转化率": "Taux de conversion VIP",
    "转化率": "Taux de conversion",

    # 调度相关
    "定时发布": "Publication planifiée",
    "内容调度": "Planification de contenu",
    "调度": "Planification",
    "过期提醒": "Rappel d'expiration",
    "今日发布": "Publié aujourd'hui",
    "未来24小时": "Prochaines 24 heures",
    "横幅": "Bannière",
    "公告": "Annonce",
    "推荐位": "Position recommandée",
    "优先级": "Priorité",
    "重复": "Répétition",
    "一次性": "Une fois",
    "每周": "Hebdomadaire",
    "立即发布": "Publier immédiatement",
    "渐进式": "Progressif",
    "区域定时": "Planification régionale",
    "批量执行": "Exécution par lot",
    "自动下线": "Hors ligne automatique",
    "历史记录": "Historique",
}

# 终极日语翻译字典
JA_ULTRA = {
    # 系统健康和监控
    "连接池": "コネクションプール",
    "池大小": "プールサイズ",
    "已使用": "使用中",
    "存储桶存在": "バケット存在",
    "读取权限": "読み取り権限",
    "受限": "制限付き",
    "进程": "プロセス",
    "核心": "コア",
    "频率": "周波数",
    "空闲": "空き",
    "无限制": "無制限",
    "网络统计": "ネットワーク統計",
    "接收数据": "受信データ",
    "发送数据包": "送信パケット",
    "接收数据包": "受信パケット",
    "接收丢包": "受信パケット損失",
    "发送丢包": "送信パケット損失",
    "丢包": "パケット損失",

    # 日志相关
    "系统日志": "システムログ",
    "登录日志": "ログインログ",
    "今日日志": "今日のログ",
    "失败率": "失敗率",
    "标记为已解决": "解決済みとしてマーク",
    "已解决": "解決済み",
    "未解决": "未解決",
    "批量解决": "一括解決",
    "管理员": "管理者",
    "模块": "モジュール",
    "请求方法": "リクエストメソッド",
    "请求URL": "リクエストURL",
    "请求数据": "リクエストデータ",
    "被拦截": "ブロック済み",
    "失败原因": "失敗理由",
    "设备": "デバイス",
    "浏览器": "ブラウザ",
    "操作系统": "オペレーティングシステム",
    "地理位置": "位置情報",
    "级别": "レベル",
    "事件": "イベント",
    "消息": "メッセージ",
    "来源": "ソース",
    "详细信息": "詳細情報",
    "状态码": "ステータスコード",
    "堆栈跟踪": "スタックトレース",
    "解决人": "解決者",
    "解决时间": "解決日時",
    "选择模块": "モジュールを選択",
    "选择操作": "操作を選択",
    "选择级别": "レベルを選択",
    "选择解决状态": "解決ステータスを選択",
    "统计数据": "統計データ",
    "标记成功": "マーク成功",
    "今天": "今日",

    # 邮件相关
    "邮件配置": "メール設定",
    "发件人邮箱": "送信者メール",
    "发件人名称": "送信者名",
    "发件人": "送信者",
    "邮箱格式无效": "メール形式が無効",
    "标识": "識別子",
    "SMTP主机": "SMTPホスト",
    "SMTP密码": "SMTPパスワード",
    "SMTP端口": "SMTPポート",
    "主题": "件名",
    "邮件模板": "メールテンプレート",
    "测试邮件": "テストメール",
    "测试邮件已发送": "テストメール送信済み",

    # 报表相关
    "行为统计": "行動統計",
    "过期率": "有効期限切れ率",
    "即将过期": "まもなく期限切れ",
    "VIP提醒": "VIPリマインダー",
    "VIP转化率": "VIPコンバージョン率",
    "转化率": "コンバージョン率",

    # 调度相关
    "定时发布": "予約公開",
    "内容调度": "コンテンツスケジューリング",
    "调度": "スケジューリング",
    "过期提醒": "期限切れリマインダー",
    "今日发布": "今日公開",
    "未来24小时": "今後24時間",
    "横幅": "バナー",
    "公告": "お知らせ",
    "推荐位": "おすすめ枠",
    "优先级": "優先度",
    "重复": "繰り返し",
    "一次性": "1回のみ",
    "每周": "週次",
    "立即发布": "即座に公開",
    "渐进式": "段階的",
    "区域定时": "地域別タイミング",
    "批量执行": "一括実行",
    "自动下线": "自動オフライン",
    "历史记录": "履歴",
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

    print(f"✅ {lang_code} 翻译完成！")
    print(f"📊 翻译前: {before_count} 项")
    print(f"📊 翻译后: {after_count} 项")
    print(f"📊 本轮翻译: {before_count - after_count} 项")

    return {'before': before_count, 'after': after_count, 'translated': before_count - after_count}

def main():
    print("="*80)
    print("终极翻译系统 - 第五轮")
    print("="*80)

    results = {}

    # 翻译德语
    print("\n处理德语翻译...")
    results['de-DE'] = translate_file('de-DE', DE_ULTRA)

    # 翻译法语
    print("\n处理法语翻译...")
    results['fr-FR'] = translate_file('fr-FR', FR_ULTRA)

    # 翻译日语
    print("\n处理日语翻译...")
    results['ja-JP'] = translate_file('ja-JP', JA_ULTRA)

    # 总结
    print(f"\n\n{'='*80}")
    print("第五轮翻译完成总结")
    print(f"{'='*80}\n")

    total_translated = sum(r['translated'] for r in results.values())
    total_remaining = sum(r['after'] for r in results.values())

    for lang, stats in results.items():
        print(f"{lang}:")
        print(f"  - 本轮翻译: {stats['translated']} 项")
        print(f"  - 剩余: {stats['after']} 项")

    print(f"\n本轮总计翻译: {total_translated} 项")
    print(f"总剩余未翻译: {total_remaining} 项")

if __name__ == '__main__':
    main()
