#!/usr/bin/env python3
"""
完整翻译工具 - 使用扩展词典和句子模式
"""
import json
import re
from pathlib import Path
from typing import Dict, Tuple


# 扩展翻译词典 - 德语
DE_TRANSLATIONS = {
    # 已有的词汇...
    "菜单": "Menü",
    "搜索": "Suchen",
    "新增": "Neu",
    "编辑": "Bearbeiten",
    "删除": "Löschen",
    "剧集": "Serie",
    "详情": "Details",
    "上传中": "Hochladen",
    "置顶": "Angeheftet",
    "不置顶": "Nicht angeheftet",
    "确认": "Bestätigen",
    "创建成功": "Erfolgreich erstellt",
    "创建时间": "Erstellungszeit",
    "天": "Tage",
    "删除成功": "Erfolgreich gelöscht",
    "描述": "Beschreibung",
    "导出": "Exportieren",
    "导出失败": "Export fehlgeschlagen",
    "导出成功": "Erfolgreich exportiert",
    "操作失败": "Operation fehlgeschlagen",
    "预览": "Vorschau",
    "排名": "Rang",
    "刷新": "Aktualisieren",
    "刷新成功": "Erfolgreich aktualisiert",
    "必填": "Erforderlich",
    "状态": "Status",
    "更新成功": "Erfolgreich aktualisiert",
    "视频": "Videos",
    "快速筛选": "Schnellfilter",
    "清空筛选": "Filter löschen",
    "筛选已清空": "Filter gelöscht",
    "筛选器": "Filter",
    "自动刷新": "Auto-Aktualisierung",
    "收起": "Einklappen",
    "展开": "Ausklappen",
    "开始日期": "Startdatum",
    "结束日期": "Enddatum",
    "降序": "Absteigend",
    "升序": "Aufsteigend",
    "已选择": "Ausgewählt",
    "清空": "Löschen",
    "详情": "Details",
    "错误": "Fehler",
    "时间": "Zeit",
    "筛选": "Filtern",
    "共": "Gesamt",
    "条": "Einträge",
    "成功": "Erfolg",
    "失败": "Fehlgeschlagen",
    "超时": "Zeitüberschreitung",
    "提示词": "Eingabeaufforderung",
    "完成": "Abgeschlossen",
    "是": "Ja",
    "否": "Nein",
    "复制全部": "Alles kopieren",

    # 设置相关
    "系统设置": "Systemeinstellungen",
    "搜索设置": "Einstellungen suchen",
    "基本设置": "Grundeinstellungen",
    "功能设置": "Funktionseinstellungen",
    "高级设置": "Erweiterte Einstellungen",
    "网站信息": "Website-Informationen",
    "区域语言": "Region und Sprache",
    "视频设置": "Video-Einstellungen",
    "评论设置": "Kommentar-Einstellungen",
    "用户设置": "Benutzereinstellungen",
    "上传设置": "Upload-Einstellungen",
    "邮件服务": "E-Mail-Dienst",
    "安全配置": "Sicherheitskonfiguration",
    "缓存管理": "Cache-Verwaltung",
    "备份": "Sicherung",
    "还原": "Wiederherstellen",
    "其他设置": "Weitere Einstellungen",

    # 邮件相关
    "发送测试邮件": "Test-E-Mail senden",
    "发送测试": "Test senden",
    "测试成功": "Test erfolgreich",
    "最后测试": "Letzter Test",
    "测试状态": "Teststatus",
    "未测试": "Nicht getestet",
    "请输入邮箱地址": "Bitte E-Mail-Adresse eingeben",
    "测试邮件发送成功": "Test-E-Mail erfolgreich gesendet",
    "测试邮件发送失败": "Test-E-Mail konnte nicht gesendet werden",

    # 缓存相关
    "缓存统计": "Cache-Statistiken",
    "命中率": "Trefferquote",
    "总命中数": "Gesamttreffer",
    "总未命中数": "Gesamtfehlschläge",
    "已清除": "Gelöscht",
    "个键": "Schlüssel",
    "选择要清除的缓存模式": "Wählen Sie das zu löschende Cache-Muster",
    "缓存清除成功": "Cache erfolgreich gelöscht",

    # 备份相关
    "选择备份文件": "Backup-Datei auswählen",
    "备份时间": "Backup-Zeit",
    "备份文件格式错误": "Ungültiges Backup-Dateiformat",

    # 支付相关
    "启用支付网关": "Zahlungsgateway aktivieren",
    "环境": "Umgebung",
    "测试连接": "Verbindung testen",
    "连接测试成功": "Verbindungstest erfolgreich",
    "连接测试失败": "Verbindungstest fehlgeschlagen",
    "私钥": "Privater Schlüssel",
    "公钥": "Öffentlicher Schlüssel",
    "支付宝": "Alipay",
    "网关地址": "Gateway-Adresse",

    # 仪表盘
    "数据概览": "Datenübersicht",
    "最近视频": "Neueste Videos",
    "数据趋势": "Datentrends",
    "自定义仪表盘": "Dashboard anpassen",
    "编辑模式": "Bearbeitungsmodus",
    "完成编辑": "Bearbeitung abschließen",
    "保存布局": "Layout speichern",
    "重置为默认": "Auf Standard zurücksetzen",
    "布局保存成功": "Layout erfolgreich gespeichert",
    "布局已恢复默认": "Layout auf Standard zurückgesetzt",

    # 视频管理
    "电影": "Film",
    "动漫": "Anime",
    "纪录片": "Dokumentation",
    "草稿": "Entwurf",
    "已发布": "Veröffentlicht",
    "已归档": "Archiviert",
    "批量发布": "Massenveröffentlichung",
    "批量下架": "Massenlöschung",
    "批量删除": "Massenlöschung",
    "此操作不可恢复": "Dieser Vorgang kann nicht rückgängig gemacht werden",
    "批量上传": "Massen-Upload",
    "收藏数": "Favoriten",
    "视频ID": "Video-ID",
    "点赞数": "Likes",
    "评分": "Bewertung",

    # 用户管理
    "用户名": "Benutzername",
    "邮箱": "E-Mail",
    "全名": "Vollständiger Name",
    "普通": "Normal",
    "已过期": "Abgelaufen",
    "注册时间": "Registrierungszeit",
    "最后登录": "Letzte Anmeldung",
    "活跃": "Aktiv",
    "已封禁": "Gesperrt",
    "封禁": "Sperren",
    "解封": "Entsperren",
    "批量封禁": "Massensperrung",
    "批量解封": "Massenentsperrung",
    "授予": "Gewähren",
    "取消": "Entfernen",
    "到期日期": "Ablaufdatum",
    "所有状态": "Alle Status",
    "所有用户": "Alle Benutzer",
    "批量授予": "Massengewährung",
    "活跃用户": "Aktive Benutzer",
    "被封禁用户": "Gesperrte Benutzer",

    # 评论管理
    "内容": "Inhalt",
    "待审核": "Ausstehend",
    "已通过": "Genehmigt",
    "已拒绝": "Abgelehnt",
    "通过": "Genehmigen",
    "拒绝": "Ablehnen",
    "批量通过": "Massengenehmigung",
    "批量拒绝": "Massenablehnung",

    # 表格
    "名称": "Name",
    "更新时间": "Aktualisierungszeit",

    # 表单
    "此字段为必填项": "Dieses Feld ist erforderlich",
    "请输入": "Bitte eingeben",
    "请选择": "Bitte auswählen",

    # 消息
    "操作成功": "Operation erfolgreich",
    "请先选择": "Bitte zuerst auswählen",
    "此操作不可撤销": "Dieser Vorgang kann nicht rückgängig gemacht werden",
    "尝试调整搜索条件或筛选条件": "Versuchen Sie, Such- oder Filterbedingungen anzupassen",
    "已成功启用": "Erfolgreich aktiviert",
    "设置已初始化": "Einstellungen initialisiert",
    "已禁用": "Deaktiviert",
    "个人资料更新成功": "Profil erfolgreich aktualisiert",
    "密码修改成功，建议重新登录": "Passwort erfolgreich geändert, bitte erneut anmelden",
    "邮箱修改成功": "E-Mail erfolgreich geändert",
    "已复制到剪贴板": "In die Zwischenablage kopiert",
    "复制失败": "Kopieren fehlgeschlagen",
    "测试失败": "Test fehlgeschlagen",
    "已删除": "Gelöscht",
    "公告已删除": "Ankündigung gelöscht",
    "已复制": "Kopiert",
    "堆栈跟踪已复制到剪贴板": "Stack-Trace in die Zwischenablage kopiert",
    "堆栈跟踪已下载": "Stack-Trace heruntergeladen",
    "完整错误报告已复制到剪贴板": "Vollständiger Fehlerbericht in die Zwischenablage kopiert",
    "回收站已清空": "Papierkorb geleert",
    "图片上传成功": "Bild erfolgreich hochgeladen",
    "已清空历史记录": "Verlauf gelöscht",
    "重置为默认": "Auf Standard zurücksetzen",
    "开始转码": "Transkodierung starten",
    "服务器错误，请稍后重试": "Serverfehler, bitte später erneut versuchen",
    "登录已过期，请重新登录": "Sitzung abgelaufen, bitte erneut anmelden",
    "两次输入的密码不一致": "Passwörter stimmen nicht überein",
    "名称不能为空": "Name darf nicht leer sein",

    # AI管理
    "管理AI提供商配置并测试AI功能": "AI-Anbieter konfigurieren und AI-Funktionen testen",
    "模型": "Modell",
    "已启用": "Aktiviert",
    "已禁用": "Deaktiviert",
    "默认": "Standard",
    "使用情况": "Nutzung",
    "请求次数": "Anfragen",
    "令牌数": "Token",
    "测试": "Testen",
    "添加提供商": "Anbieter hinzufügen",
    "编辑提供商": "Anbieter bearbeiten",
    "删除提供商": "Anbieter löschen",
    "确定要删除此提供商吗": "Möchten Sie diesen Anbieter wirklich löschen?",
    "连接成功": "Verbindung erfolgreich",
    "连接失败": "Verbindung fehlgeschlagen",
    "你": "Sie",
    "正在思考": "Denkt nach",
    "发送": "Senden",
    "基本信息": "Grundinformationen",
    "配置": "Konfiguration",
    "模型参数": "Modellparameter",
    "请输入名称": "Bitte Namen eingeben",
    "提供商类型": "Anbietertyp",
    "密钥": "Schlüssel",
    "请输入API密钥": "Bitte API-Schlüssel eingeben",
    "基础": "Basis",
    "请选择模型": "Bitte Modell auswählen",
    "选择AI模型": "AI-Modell auswählen",
    "最大令牌数": "Maximale Token",
    "温度": "Temperatur",
    "采样": "Sampling",
    "频率惩罚": "Frequenzstrafe",
    "存在惩罚": "Existenzstrafe",
    "设为默认": "Als Standard festlegen",
    "总请求数": "Gesamtanfragen",
    "请求日志": "Anforderungsprotokoll",
    "成本监控": "Kostenüberwachung",
    "配额管理": "Kontingentsverwaltung",
    "模板管理": "Vorlagenverwaltung",
    "提供商": "Anbieter",
    "请求类型": "Anforderungstyp",
    "成本": "Kosten",
    "日志详情": "Protokolldetails",
    "使用统计": "Nutzungsstatistik",
    "预估成本": "Geschätzte Kosten",
    "响应": "Antwort",
    "元数据": "Metadaten",
    "地址": "Adresse",
    "选择提供商": "Anbieter auswählen",
    "模型名称": "Modellname",
    "总成本": "Gesamtkosten",
    "成功率": "Erfolgsquote",
    "今日成本": "Heutige Kosten",
    "本月成本": "Monatliche Kosten",
    "预计月度成本": "Geschätzte monatliche Kosten",
    "成本趋势": "Kostentrend",
    "按模型统计成本": "Kosten nach Modell",
    "按提供商统计成本": "Kosten nach Anbieter",
    "平均响应时间": "Durchschnittliche Antwortzeit",
    "配额类型": "Kontingenttyp",
    "目标ID": "Ziel-ID",
    "每日请求": "Tägliche Anfragen",
    "每月请求": "Monatliche Anfragen",
    "每日成本": "Tägliche Kosten",
    "速率限制": "Ratenlimit",
    "创建配额": "Kontingent erstellen",
    "编辑配额": "Kontingent bearbeiten",
    "全局配额": "Globales Kontingent",
    "用户配额": "Benutzerkontingent",
    "提供商配额": "Anbieterkontingent",
    "全局配额留空": "Leer lassen für globales Kontingent",
    "每日请求限制": "Tägliches Anforderungslimit",
    "每月请求限制": "Monatliches Anforderungslimit",
    "每月成本限制": "Monatliches Kostenlimit",
    "每分钟速率限制": "Ratenlimit pro Minute",
    "每小时速率限制": "Ratenlimit pro Stunde",
    "全局配额状态": "Globaler Kontingentstatus",
    "配额受限": "Kontingent begrenzt",
    "每日剩余请求": "Verbleibende tägliche Anfragen",
    "每月剩余请求": "Verbleibende monatliche Anfragen",
    "每日剩余成本": "Verbleibende tägliche Kosten",
    "类别": "Kategorie",
    "变量": "Variablen",
    "推荐模型": "Empfohlenes Modell",
    "使用次数": "Nutzungshäufigkeit",
    "创建模板": "Vorlage erstellen",
    "编辑模板": "Vorlage bearbeiten",
    "选择类别": "Kategorie auswählen",
    "内容生成": "Inhaltsgenerierung",
    "内容审核": "Inhaltsmoderation",
    "摘要总结": "Zusammenfassung",
    "翻译": "Übersetzung",
    "分析": "Analyse",
    "模板详情": "Vorlagendetails",
    "示例变量": "Beispielvariablen",
    "推荐提供商": "Empfohlener Anbieter",
    "推荐参数": "Empfohlene Parameter",
    "标签": "Tags",
    "无效的示例变量JSON格式": "Ungültiges JSON-Format für Beispielvariablen",
    "无效的推荐参数JSON格式": "Ungültiges JSON-Format für empfohlene Parameter",
    "推荐配置": "Empfohlene Konfiguration",
}

# 法语翻译词典
FR_TRANSLATIONS = {
    "菜单": "Menu",
    "搜索": "Rechercher",
    "新增": "Nouveau",
    "编辑": "Modifier",
    "删除": "Supprimer",
    "剧集": "Série",
    "详情": "Détails",
    "上传中": "Téléchargement en cours",
    "置顶": "Épinglé",
    "不置顶": "Non épinglé",
    "确认": "Confirmer",
    "创建成功": "Créé avec succès",
    "创建时间": "Date de création",
    "天": "Jours",
    "删除成功": "Supprimé avec succès",
    "描述": "Description",
    "导出": "Exporter",
    "导出失败": "Échec de l'export",
    "导出成功": "Exporté avec succès",
    "操作失败": "Opération échouée",
    "预览": "Aperçu",
    "排名": "Classement",
    "刷新": "Actualiser",
    "刷新成功": "Actualisé avec succès",
    "必填": "Obligatoire",
    "状态": "Statut",
    "更新成功": "Mis à jour avec succès",
    "视频": "Vidéos",
    "快速筛选": "Filtres rapides",
    "清空筛选": "Effacer les filtres",
    "筛选已清空": "Filtres effacés",
    "筛选器": "Filtres",
    "自动刷新": "Actualisation automatique",
    "收起": "Réduire",
    "展开": "Développer",
    "开始日期": "Date de début",
    "结束日期": "Date de fin",
    "降序": "Décroissant",
    "升序": "Croissant",
    "已选择": "Sélectionné",
    "清空": "Effacer",
    "详情": "Détails",
    "错误": "Erreur",
    "时间": "Heure",
    "筛选": "Filtrer",
    "共": "Total",
    "条": "éléments",
    "成功": "Succès",
    "失败": "Échec",
    "超时": "Délai dépassé",
    "提示词": "Invite",
    "完成": "Terminé",
    "是": "Oui",
    "否": "Non",
    "复制全部": "Tout copier",

    # 设置
    "系统设置": "Paramètres système",
    "搜索设置": "Rechercher dans les paramètres",
    "基本设置": "Paramètres de base",
    "功能设置": "Paramètres de fonctionnalités",
    "高级设置": "Paramètres avancés",
    "网站信息": "Informations du site",
    "区域语言": "Région et langue",
    "视频设置": "Paramètres vidéo",
    "评论设置": "Paramètres des commentaires",
    "用户设置": "Paramètres utilisateur",
    "上传设置": "Paramètres de téléchargement",
    "邮件服务": "Service de messagerie",
    "安全配置": "Configuration de sécurité",
    "缓存管理": "Gestion du cache",
    "备份": "Sauvegarde",
    "还原": "Restaurer",
    "其他设置": "Autres paramètres",

    # 邮件
    "发送测试邮件": "Envoyer un e-mail de test",
    "发送测试": "Envoyer un test",
    "测试成功": "Test réussi",
    "最后测试": "Dernier test",
    "测试状态": "État du test",
    "未测试": "Non testé",
    "请输入邮箱地址": "Veuillez saisir l'adresse e-mail",
    "测试邮件发送成功": "E-mail de test envoyé avec succès",
    "测试邮件发送失败": "Échec de l'envoi de l'e-mail de test",

    # 缓存
    "缓存统计": "Statistiques du cache",
    "命中率": "Taux de réussite",
    "总命中数": "Total de réussites",
    "总未命中数": "Total d'échecs",
    "已清除": "Effacé",
    "个键": "clés",
    "选择要清除的缓存模式": "Sélectionnez le modèle de cache à effacer",
    "缓存清除成功": "Cache effacé avec succès",

    # Plus de traductions...
    "此操作不可恢复": "Cette opération est irréversible",
    "电影": "Film",
    "动漫": "Anime",
    "纪录片": "Documentaire",
    "草稿": "Brouillon",
    "已发布": "Publié",
    "已归档": "Archivé",
    "批量发布": "Publication en masse",
    "批量下架": "Retrait en masse",
    "批量删除": "Suppression en masse",
    "批量上传": "Téléchargement en masse",
    "收藏数": "Favoris",
    "视频ID": "ID vidéo",
    "点赞数": "Likes",
    "评分": "Note",

    # Gestion des utilisateurs
    "用户名": "Nom d'utilisateur",
    "邮箱": "E-mail",
    "全名": "Nom complet",
    "普通": "Normal",
    "已过期": "Expiré",
    "注册时间": "Date d'inscription",
    "最后登录": "Dernière connexion",
    "活跃": "Actif",
    "已封禁": "Banni",
    "封禁": "Bannir",
    "解封": "Débannir",
    "批量封禁": "Bannissement en masse",
    "批量解封": "Débannissement en masse",
    "授予": "Accorder",
    "取消": "Annuler",
    "到期日期": "Date d'expiration",
    "所有状态": "Tous les statuts",
    "所有用户": "Tous les utilisateurs",
    "批量授予": "Attribution en masse",
    "活跃用户": "Utilisateurs actifs",
    "被封禁用户": "Utilisateurs bannis",
}

# 日语翻译词典
JA_TRANSLATIONS = {
    "菜单": "メニュー",
    "搜索": "検索",
    "新增": "新規",
    "编辑": "編集",
    "删除": "削除",
    "剧集": "シリーズ",
    "详情": "詳細",
    "上传中": "アップロード中",
    "置顶": "ピン留め",
    "不置顶": "ピン留め解除",
    "确认": "確認",
    "创建成功": "作成に成功しました",
    "创建时间": "作成時間",
    "天": "日",
    "删除成功": "削除に成功しました",
    "描述": "説明",
    "导出": "エクスポート",
    "导出失败": "エクスポートに失敗しました",
    "导出成功": "エクスポートに成功しました",
    "操作失败": "操作に失敗しました",
    "预览": "プレビュー",
    "排名": "ランキング",
    "刷新": "更新",
    "刷新成功": "更新に成功しました",
    "必填": "必須",
    "状态": "ステータス",
    "更新成功": "更新に成功しました",
    "视频": "動画",
    "快速筛选": "クイックフィルター",
    "清空筛选": "フィルターをクリア",
    "筛选已清空": "フィルターをクリアしました",
    "筛选器": "フィルター",
    "自动刷新": "自動更新",
    "收起": "折りたたむ",
    "展开": "展開",
    "开始日期": "開始日",
    "结束日期": "終了日",
    "降序": "降順",
    "升序": "昇順",
    "已选择": "選択済み",
    "清空": "クリア",
    "详情": "詳細",
    "错误": "エラー",
    "时间": "時間",
    "筛选": "フィルター",
    "共": "合計",
    "条": "件",
    "成功": "成功",
    "失败": "失敗",
    "超时": "タイムアウト",
    "提示词": "プロンプト",
    "完成": "完了",
    "是": "はい",
    "否": "いいえ",
    "复制全部": "すべてコピー",

    # 設定
    "系统设置": "システム設定",
    "搜索设置": "設定を検索",
    "基本设置": "基本設定",
    "功能设置": "機能設定",
    "高级设置": "詳細設定",
    "网站信息": "サイト情報",
    "区域语言": "地域と言語",
    "视频设置": "動画設定",
    "评论设置": "コメント設定",
    "用户设置": "ユーザー設定",
    "上传设置": "アップロード設定",
    "邮件服务": "メールサービス",
    "安全配置": "セキュリティ設定",
    "缓存管理": "キャッシュ管理",
    "备份": "バックアップ",
    "还原": "復元",
    "其他设置": "その他の設定",

    # メール
    "发送测试邮件": "テストメールを送信",
    "发送测试": "テスト送信",
    "测试成功": "テスト成功",
    "最后测试": "最後のテスト",
    "测试状态": "テスト状態",
    "未测试": "未テスト",
    "请输入邮箱地址": "メールアドレスを入力してください",
    "测试邮件发送成功": "テストメールが正常に送信されました",
    "测试邮件发送失败": "テストメールの送信に失敗しました",

    # キャッシュ
    "缓存统计": "キャッシュ統計",
    "命中率": "ヒット率",
    "总命中数": "総ヒット数",
    "总未命中数": "総ミス数",
    "已清除": "クリアしました",
    "个键": "キー",
    "选择要清除的缓存模式": "クリアするキャッシュパターンを選択",
    "缓存清除成功": "キャッシュを正常にクリアしました",

    # その他
    "此操作不可恢复": "この操作は元に戻せません",
    "电影": "映画",
    "动漫": "アニメ",
    "纪录片": "ドキュメンタリー",
    "草稿": "下書き",
    "已发布": "公開済み",
    "已归档": "アーカイブ済み",
    "批量发布": "一括公開",
    "批量下架": "一括非公開",
    "批量删除": "一括削除",
    "批量上传": "一括アップロード",
    "收藏数": "お気に入り",
    "视频ID": "動画ID",
    "点赞数": "いいね数",
    "评分": "評価",

    # ユーザー管理
    "用户名": "ユーザー名",
    "邮箱": "メール",
    "全名": "フルネーム",
    "普通": "通常",
    "已过期": "期限切れ",
    "注册时间": "登録日時",
    "最后登录": "最終ログイン",
    "活跃": "アクティブ",
    "已封禁": "禁止済み",
    "封禁": "禁止",
    "解封": "禁止解除",
    "批量封禁": "一括禁止",
    "批量解封": "一括禁止解除",
    "授予": "付与",
    "取消": "取り消し",
    "到期日期": "有効期限",
    "所有状态": "すべてのステータス",
    "所有用户": "すべてのユーザー",
    "批量授予": "一括付与",
    "活跃用户": "アクティブユーザー",
    "被封禁用户": "禁止されたユーザー",
}


def contains_chinese(text: str) -> bool:
    """检查是否包含中文"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def translate_chinese_text(text: str, lang_dict: Dict[str, str]) -> str:
    """翻译中文文本"""
    if not contains_chinese(text):
        return text

    # 完全匹配
    if text in lang_dict:
        return lang_dict[text]

    # 尝试分词匹配和替换
    result = text
    # 按长度降序排序，优先匹配较长的短语
    sorted_keys = sorted(lang_dict.keys(), key=len, reverse=True)

    for cn, translation in [(k, lang_dict[k]) for k in sorted_keys]:
        if cn in result:
            result = result.replace(cn, translation)

    return result


def translate_file(lang_code: str, lang_dict: Dict[str, str], base_path: Path):
    """翻译文件"""
    print(f"\n{'='*80}")
    print(f"完整翻译: {lang_code}")
    print(f"{'='*80}\n")

    lang_file = base_path / f"{lang_code}.json"

    with open(lang_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    def translate_recursive(obj):
        """递归翻译"""
        if isinstance(obj, dict):
            return {k: translate_recursive(v) for k, v in obj.items()}
        elif isinstance(obj, str):
            if contains_chinese(obj):
                return translate_chinese_text(obj, lang_dict)
            return obj
        else:
            return obj

    # 翻译整个文件
    translated_data = translate_recursive(data)

    # 保存
    with open(lang_file, 'w', encoding='utf-8') as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)

    # 统计
    def count_chinese(obj):
        count = 0
        if isinstance(obj, dict):
            for v in obj.values():
                count += count_chinese(v)
        elif isinstance(obj, str) and contains_chinese(obj):
            count += 1
        return count

    remaining = count_chinese(translated_data)
    print(f"✅ 翻译完成！")
    print(f"📊 剩余未翻译项: {remaining}")

    return remaining


def main():
    """主函数"""
    admin_i18n = Path("/home/eric/video/admin-frontend/src/i18n/locales")

    print("="*80)
    print("完整翻译系统 - 使用扩展词典")
    print("="*80)

    results = {}

    # 翻译德语
    print("\n处理德语翻译...")
    results['de-DE'] = translate_file('de-DE', DE_TRANSLATIONS, admin_i18n)

    # 翻译法语
    print("\n处理法语翻译...")
    results['fr-FR'] = translate_file('fr-FR', FR_TRANSLATIONS, admin_i18n)

    # 翻译日语
    print("\n处理日语翻译...")
    results['ja-JP'] = translate_file('ja-JP', JA_TRANSLATIONS, admin_i18n)

    # 总结
    print(f"\n\n{'='*80}")
    print("翻译完成总结")
    print(f"{'='*80}\n")

    total_remaining = sum(results.values())

    for lang, remaining in results.items():
        completion = ((1402 - remaining) / 1402) * 100
        print(f"{lang}: {completion:.1f}% 完成 (剩余 {remaining} 项)")

    overall_completion = ((1402 * 3 - total_remaining) / (1402 * 3)) * 100
    print(f"\n总体完成度: {overall_completion:.1f}%")
    print(f"剩余未翻译项: {total_remaining}")


if __name__ == "__main__":
    main()
