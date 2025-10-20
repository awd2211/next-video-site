#!/usr/bin/env python3
"""
高级字典翻译系统 - 处理混合语言字符串和复杂模式
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple

# 扩展德语翻译字典 - 包含更多短语和完整句子
DE_ADVANCED = {
    # 完整句子和短语
    "以验证SMTP配置": "um die SMTP-Konfiguration zu verifizieren",
    "管理Redis缓存并查看统计信息": "Redis-Cache verwalten und Statistiken anzeigen",
    "管理AI提供商配置并测试AI功能": "AI-Anbieter-Konfiguration verwalten und AI-Funktionen testen",
    "实时系统监控与性能指标": "Echtzeit-Systemüberwachung und Leistungsmetriken",
    "请输入您注册时使用的邮箱地址，我们将向您发送6位数字验证码": "Bitte geben Sie die bei der Registrierung verwendete E-Mail-Adresse ein. Wir senden Ihnen einen 6-stelligen Verifizierungscode",
    "此操作不可恢复": "Dieser Vorgang kann nicht rückgängig gemacht werden",
    "逗号分隔的变量名": "Durch Komma getrennte Variablennamen",
    "如：title, description": "z.B.: title, description",
    "例如：GPT-4 生产": "z.B.: GPT-4 Produktion",
    "输入您的API": "Geben Sie Ihren API",
    "将被加密存储": "wird verschlüsselt gespeichert",
    "每日Token限制": "Tägliches Token-Limit",
    "每月Token限制": "Monatliches Token-Limit",
    "描述此模板的用途": "Beschreiben Sie den Zweck dieser Vorlage",
    "输入带有": "Eingabe mit",
    "的": "",
    "模板": "Vorlage",
    "逗号分隔的": "Durch Komma getrennte",
    "名": "Namen",
    "包含": "Enthält",
    "示例值": "Beispielwerte",
    "对象": "Objekt",
    "包含推荐": "Enthält empfohlene",
    "批量启用": "Batch-Aktivierung",
    "批量禁用": "Batch-Deaktivierung",
    "聊天测试": "Chat-Test",
    "连接测试": "Verbindungstest",
    "聊天成功": "Chat erfolgreich",
    "聊天失败": "Chat fehlgeschlagen",
    "连接成功": "Verbindung erfolgreich",
    "连接失败": "Verbindung fehlgeschlagen",
    "配置": "Konfiguration",
    "管理": "Verwaltung",
    "设置": "Einstellungen",
    "统计": "Statistiken",
    "信息": "Informationen",
    "数据": "Daten",
    "系统": "System",
    "用户": "Benutzer",
    "内容": "Inhalt",
    "操作": "Operation",
    "日志": "Protokoll",
    "搜索": "Suchen",
    "编辑": "Bearbeiten",
    "删除": "Löschen",
    "添加": "Hinzufügen",
    "保存": "Speichern",
    "取消": "Abbrechen",
    "确认": "Bestätigen",
    "提交": "Absenden",
    "重置": "Zurücksetzen",
    "刷新": "Aktualisieren",
    "导出": "Exportieren",
    "导入": "Importieren",
    "下载": "Herunterladen",
    "上传": "Hochladen",
    "预览": "Vorschau",
    "详情": "Details",
    "列表": "Liste",
    "查看": "Ansicht",
    "修改": "Ändern",
    "更新": "Aktualisieren",
    "创建": "Erstellen",
    "新增": "Neu hinzufügen",
    "复制": "Kopieren",
    "移动": "Verschieben",
    "分享": "Teilen",
    "发布": "Veröffentlichen",
    "草稿": "Entwurf",
    "已发布": "Veröffentlicht",
    "已禁用": "Deaktiviert",
    "已启用": "Aktiviert",
    "启用": "Aktivieren",
    "禁用": "Deaktivieren",
    "成功": "Erfolgreich",
    "失败": "Fehlgeschlagen",
    "错误": "Fehler",
    "警告": "Warnung",
    "提示": "Hinweis",
    "请": "Bitte",
    "输入": "Eingabe",
    "选择": "Auswählen",
    "文件": "Datei",
    "图片": "Bild",
    "视频": "Video",
    "标题": "Titel",
    "描述": "Beschreibung",
    "名称": "Name",
    "类型": "Typ",
    "状态": "Status",
    "时间": "Zeit",
    "日期": "Datum",
    "开始": "Start",
    "结束": "Ende",
    "总计": "Gesamt",
    "当前": "Aktuell",
    "历史": "Verlauf",
    "最新": "Neueste",
    "推荐": "Empfohlen",
    "热门": "Beliebt",
    "排序": "Sortieren",
    "筛选": "Filtern",
    "全部": "Alle",
    "部分": "Teilweise",
    "无": "Keine",
    "有": "Vorhanden",
    "是": "Ja",
    "否": "Nein",
    "或": "Oder",
    "和": "Und",
    "到": "Bis",
    "从": "Von",
    "在": "In",
    "于": "Am",
    "中": "In",
    "上": "Oben",
    "下": "Unten",
    "前": "Vor",
    "后": "Nach",
    "左": "Links",
    "右": "Rechts",
    "第": "",
    "个": "",
    "项": "Artikel",
    "条": "Einträge",
    "页": "Seite",
    "次": "Mal",
    "人": "Person",
    "天": "Tag",
    "月": "Monat",
    "年": "Jahr",
    "小时": "Stunde",
    "分钟": "Minute",
    "秒": "Sekunde",
}

# 扩展法语翻译字典
FR_ADVANCED = {
    # 完整句子和短语
    "以验证SMTP配置": "pour vérifier la configuration SMTP",
    "管理Redis缓存并查看统计信息": "Gérer le cache Redis et afficher les statistiques",
    "管理AI提供商配置并测试AI功能": "Gérer la configuration du fournisseur d'IA et tester les fonctionnalités d'IA",
    "实时系统监控与性能指标": "Surveillance système en temps réel et métriques de performance",
    "请输入您注册时使用的邮箱地址，我们将向您发送6位数字验证码": "Veuillez entrer l'adresse e-mail utilisée lors de l'inscription. Nous vous enverrons un code de vérification à 6 chiffres",
    "此操作不可恢复": "Cette opération est irréversible",
    "逗号分隔的变量名": "Noms de variables séparés par des virgules",
    "如：title, description": "par exemple: title, description",
    "例如：GPT-4 生产": "par exemple: GPT-4 Production",
    "输入您的API": "Entrez votre API",
    "将被加密存储": "sera stocké chiffré",
    "每日Token限制": "Limite quotidienne de tokens",
    "每月Token限制": "Limite mensuelle de tokens",
    "描述此模板的用途": "Décrivez l'objectif de ce modèle",
    "输入带有": "Entrer avec",
    "的": "",
    "模板": "modèle",
    "逗号分隔的": "Séparé par des virgules",
    "名": "noms",
    "包含": "Contient",
    "示例值": "valeurs d'exemple",
    "对象": "objet",
    "包含推荐": "Contient recommandé",
    "选择": "Sélectionner",
    "文件": "fichier",
    "启用支付网关": "Activer la passerelle de paiement",
    "环境": "Environnement",
    "测试连接": "Tester la connexion",
    "连接测试成功": "Test de connexion réussi",
    "连接测试失败": "Test de connexion échoué",
    "私钥": "Clé privée",
    "公钥（支付宝）": "Clé publique (Alipay)",
    "网关地址": "Adresse de la passerelle",
    "数据概览": "Aperçu des données",
    "数据趋势": "Tendances des données",
    "自定义仪表盘": "Personnaliser le tableau de bord",
    "布局保存": "Mise en page enregistrée",
    "布局已恢复默认": "Mise en page restaurée par défaut",
    "类型": "Type",
    "已通过": "Approuvé",
    "已拒绝": "Rejeté",
    "通过": "Approuver",
    "配置": "Configuration",
    "管理": "Gestion",
    "设置": "Paramètres",
    "统计": "Statistiques",
    "信息": "Informations",
    "数据": "Données",
    "系统": "Système",
    "用户": "Utilisateur",
    "内容": "Contenu",
    "操作": "Opération",
    "日志": "Journal",
    "搜索": "Rechercher",
    "编辑": "Modifier",
    "删除": "Supprimer",
    "添加": "Ajouter",
    "保存": "Enregistrer",
    "取消": "Annuler",
    "确认": "Confirmer",
    "提交": "Soumettre",
    "重置": "Réinitialiser",
    "刷新": "Actualiser",
    "导出": "Exporter",
    "导入": "Importer",
    "下载": "Télécharger",
    "上传": "Téléverser",
    "预览": "Aperçu",
    "详情": "Détails",
    "列表": "Liste",
    "查看": "Voir",
    "修改": "Modifier",
    "更新": "Mettre à jour",
    "创建": "Créer",
    "新增": "Nouveau",
    "复制": "Copier",
    "移动": "Déplacer",
    "分享": "Partager",
    "发布": "Publier",
    "草稿": "Brouillon",
    "已发布": "Publié",
    "已禁用": "Désactivé",
    "已启用": "Activé",
    "启用": "Activer",
    "禁用": "Désactiver",
    "成功": "Succès",
    "失败": "Échec",
    "错误": "Erreur",
    "警告": "Avertissement",
    "提示": "Astuce",
    "请": "Veuillez",
    "输入": "Saisir",
}

# 扩展日语翻译字典
JA_ADVANCED = {
    # 完整句子和短语
    "以验证SMTP配置": "してSMTP設定を検証する",
    "管理Redis缓存并查看统计信息": "Redisキャッシュを管理し、統計情報を表示する",
    "管理AI提供商配置并测试AI功能": "AIプロバイダー設定を管理し、AI機能をテストする",
    "实时系统监控与性能指标": "リアルタイムシステム監視とパフォーマンス指標",
    "请输入您注册时使用的邮箱地址，我们将向您发送6位数字验证码": "登録時に使用したメールアドレスを入力してください。6桁の確認コードを送信します",
    "此操作不可恢复": "この操作は元に戻せません",
    "逗号分隔的变量名": "カンマ区切りの変数名",
    "如：title, description": "例：title, description",
    "例如：GPT-4 生产": "例：GPT-4プロダクション",
    "输入您的API": "APIを入力してください",
    "将被加密存储": "暗号化して保存されます",
    "每日Token限制": "1日のトークン制限",
    "每月Token限制": "1ヶ月のトークン制限",
    "描述此模板的用途": "このテンプレートの目的を説明してください",
    "输入带有": "を含む入力",
    "的": "の",
    "模板": "テンプレート",
    "逗号分隔的": "カンマ区切りの",
    "名": "名",
    "包含": "を含む",
    "示例值": "サンプル値",
    "对象": "オブジェクト",
    "包含推荐": "推奨を含む",
    "搜索菜单": "メニューを検索",
    "控制台": "ダッシュボード",
    "影片管理": "動画管理",
    "用户管理": "ユーザー管理",
    "评论管理": "コメント管理",
    "横幅管理": "バナー管理",
    "公告管理": "お知らせ管理",
    "演员管理": "俳優管理",
    "导演管理": "監督管理",
    "媒体管理": "メディア管理",
    "数据统计": "データ統計",
    "系统设定": "システム設定",
    "操作日志": "操作ログ",
    "IP黑名单": "IPブラックリスト",
    "剧集管理": "シリーズ管理",
    "AI日志": "AIログ",
    "系统健康": "システムヘルス",
    "角色管理": "ロール管理",
    "报告": "レポート",
    "邮件管理": "メール管理",
    "OAuth设置": "OAuth設定",
    "配置": "設定",
    "管理": "管理",
    "设置": "設定",
    "统计": "統計",
    "信息": "情報",
    "数据": "データ",
    "系统": "システム",
    "用户": "ユーザー",
    "内容": "コンテンツ",
    "操作": "操作",
    "日志": "ログ",
    "搜索": "検索",
    "编辑": "編集",
    "删除": "削除",
    "添加": "追加",
    "保存": "保存",
    "取消": "キャンセル",
    "确认": "確認",
    "提交": "送信",
    "重置": "リセット",
    "刷新": "更新",
    "导出": "エクスポート",
    "导入": "インポート",
    "下载": "ダウンロード",
    "上传": "アップロード",
    "预览": "プレビュー",
    "详情": "詳細",
    "列表": "リスト",
    "查看": "表示",
    "修改": "変更",
    "更新": "更新",
    "创建": "作成",
    "新增": "新規追加",
    "复制": "コピー",
    "移动": "移動",
    "分享": "共有",
    "发布": "公開",
    "草稿": "下書き",
    "已发布": "公開済み",
    "已禁用": "無効",
    "已启用": "有効",
    "启用": "有効化",
    "禁用": "無効化",
    "成功": "成功",
    "失败": "失敗",
    "错误": "エラー",
    "警告": "警告",
    "提示": "ヒント",
    "请": "してください",
    "输入": "入力",
    "选择": "選択",
    "文件": "ファイル",
    "图片": "画像",
    "视频": "動画",
    "标题": "タイトル",
    "描述": "説明",
    "名称": "名前",
    "类型": "タイプ",
    "状态": "ステータス",
    "时间": "時間",
    "日期": "日付",
}

def contains_chinese(text: str) -> bool:
    """检查文本是否包含中文字符"""
    return bool(re.search(r'[\u4e00-\u9fff]', str(text)))

def translate_mixed_text(text: str, translations: Dict[str, str]) -> str:
    """
    翻译混合语言文本
    策略：
    1. 先尝试完整匹配
    2. 然后按长度降序替换中文片段
    3. 最后处理单个字符
    """
    if not contains_chinese(text):
        return text

    result = text

    # 1. 尝试完整匹配
    if text in translations:
        return translations[text]

    # 2. 提取所有中文片段并按长度降序排列
    chinese_segments = list(set(re.findall(r'[\u4e00-\u9fff]+', text)))
    chinese_segments.sort(key=len, reverse=True)

    # 3. 逐个替换
    for segment in chinese_segments:
        if segment in translations:
            result = result.replace(segment, translations[segment])

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
    print(f"高级翻译: {lang_code}")
    print(f"{'='*80}\n")

    # 读取文件
    admin_i18n = Path('/home/eric/video/admin-frontend/src/i18n/locales')
    lang_file = admin_i18n / f'{lang_code}.json'

    with open(lang_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 统计信息
    stats = {'total': 0, 'translated': 0}

    # 翻译
    translated_data = translate_value(data, translations, stats)

    # 保存
    with open(lang_file, 'w', encoding='utf-8') as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)

    # 计算剩余未翻译项
    remaining = count_chinese_items(translated_data)

    print(f"✅ {lang_code} 翻译完成！")
    print(f"📊 成功翻译: {stats['translated']} / {stats['total']} 项")
    print(f"📊 剩余未翻译项: {remaining}")

    return {'total': stats['total'], 'translated': stats['translated'], 'remaining': remaining}

def main():
    print("="*80)
    print("高级字典翻译系统")
    print("="*80)

    results = {}

    # 翻译德语
    print("\n处理德语翻译...")
    results['de-DE'] = translate_file('de-DE', DE_ADVANCED)

    # 翻译法语
    print("\n处理法语翻译...")
    results['fr-FR'] = translate_file('fr-FR', FR_ADVANCED)

    # 翻译日语
    print("\n处理日语翻译...")
    results['ja-JP'] = translate_file('ja-JP', JA_ADVANCED)

    # 总结
    print(f"\n\n{'='*80}")
    print("高级翻译完成总结")
    print(f"{'='*80}\n")

    total_remaining = sum(r['remaining'] for r in results.values())
    total_translated = sum(r['translated'] for r in results.values())

    for lang, stats in results.items():
        completion = 100 - (stats['remaining'] / (stats['total'] + stats['remaining']) * 100) if stats['total'] + stats['remaining'] > 0 else 100
        print(f"{lang}: {completion:.1f}% 完成 (剩余 {stats['remaining']} 项)")

    print(f"\n总剩余未翻译项: {total_remaining}")
    print(f"本轮翻译数: {total_translated}")

if __name__ == '__main__':
    main()
