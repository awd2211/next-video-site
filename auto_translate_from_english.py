#!/usr/bin/env python3
"""
基于英文翻译自动翻译其他语言
对于每个包含中文的键，从英文版本获取对应值，然后翻译到目标语言
"""
import json
import re
from pathlib import Path
from typing import Dict


# 常见词汇的翻译字典
TRANSLATIONS = {
    'de-DE': {
        # 常用操作
        'Search': 'Suchen',
        'Create': 'Erstellen',
        'Edit': 'Bearbeiten',
        'Delete': 'Löschen',
        'Cancel': 'Abbrechen',
        'Confirm': 'Bestätigen',
        'Save': 'Speichern',
        'Submit': 'Absenden',
        'Reset': 'Zurücksetzen',
        'Update': 'Aktualisieren',
        'Add': 'Hinzufügen',
        'Remove': 'Entfernen',
        'View': 'Ansehen',
        'Export': 'Exportieren',
        'Import': 'Importieren',
        'Download': 'Herunterladen',
        'Upload': 'Hochladen',
        'Uploading': 'Hochladen',
        'Preview': 'Vorschau',
        'Refresh': 'Aktualisieren',
        'Filter': 'Filtern',
        'Clear': 'Löschen',
        'Apply': 'Anwenden',
        'Close': 'Schließen',
        'Back': 'Zurück',
        'Next': 'Weiter',
        'Previous': 'Vorherige',
        'Publish': 'Veröffentlichen',
        'Draft': 'Entwurf',

        # 状态
        'Active': 'Aktiv',
        'Inactive': 'Inaktiv',
        'Enabled': 'Aktiviert',
        'Disabled': 'Deaktiviert',
        'Success': 'Erfolg',
        'Failed': 'Fehlgeschlagen',
        'Error': 'Fehler',
        'Warning': 'Warnung',
        'Info': 'Info',
        'Loading': 'Laden',
        'Pending': 'Ausstehend',
        'Completed': 'Abgeschlossen',
        'Pinned': 'Angeheftet',
        'Unpinned': 'Nicht angeheftet',

        # 通用词汇
        'Status': 'Status',
        'Type': 'Typ',
        'Name': 'Name',
        'Title': 'Titel',
        'Description': 'Beschreibung',
        'Content': 'Inhalt',
        'Category': 'Kategorie',
        'Tag': 'Tag',
        'Tags': 'Tags',
        'Date': 'Datum',
        'Time': 'Zeit',
        'Actions': 'Aktionen',
        'Details': 'Details',
        'Settings': 'Einstellungen',
        'Total': 'Gesamt',
        'Count': 'Anzahl',
        'All': 'Alle',
        'None': 'Keine',
        'Yes': 'Ja',
        'No': 'Nein',
        'Required': 'Erforderlich',
        'Optional': 'Optional',
        'Rank': 'Rang',
        'Order': 'Reihenfolge',
        'Sort': 'Sortieren',
        'Videos': 'Videos',
        'Video': 'Video',
        'Users': 'Benutzer',
        'User': 'Benutzer',
        'Comments': 'Kommentare',
        'Comment': 'Kommentar',
        'Series': 'Serien',
        'Episode': 'Episode',
        'Episodes': 'Episoden',

        # 消息
        'Success!': 'Erfolg!',
        'Created successfully': 'Erfolgreich erstellt',
        'Updated successfully': 'Erfolgreich aktualisiert',
        'Deleted successfully': 'Erfolgreich gelöscht',
        'Saved successfully': 'Erfolgreich gespeichert',
        'Operation failed': 'Operation fehlgeschlagen',
        'Confirm delete?': 'Löschen bestätigen?',
        'Are you sure?': 'Sind Sie sicher?',
        'No data': 'Keine Daten',
        'Loading...': 'Laden...',
        'Please wait...': 'Bitte warten...',
        'Refreshed successfully': 'Erfolgreich aktualisiert',
        'Export failed': 'Export fehlgeschlagen',
        'Export success': 'Export erfolgreich',
        'Exported successfully': 'Erfolgreich exportiert',

        # 时间相关
        'Created at': 'Erstellt am',
        'Updated at': 'Aktualisiert am',
        'Created time': 'Erstellungszeit',
        'Update time': 'Aktualisierungszeit',
        'Days': 'Tage',
        'Hours': 'Stunden',
        'Minutes': 'Minuten',

        # 菜单和导航
        'Search menu...': 'Menü durchsuchen...',
        'Quick filters': 'Schnellfilter',
        'Clear filters': 'Filter löschen',
        'Filters cleared': 'Filter gelöscht',
        'Filters': 'Filter',

        # Series相关
        'New series': 'Neue Serie',
        'Series details': 'Seriendetails',
        'Edit series': 'Serie bearbeiten',
        'New episode': 'Neue Episode',
    },

    'fr-FR': {
        # 常用操作
        'Search': 'Rechercher',
        'Create': 'Créer',
        'Edit': 'Modifier',
        'Delete': 'Supprimer',
        'Cancel': 'Annuler',
        'Confirm': 'Confirmer',
        'Save': 'Enregistrer',
        'Submit': 'Soumettre',
        'Reset': 'Réinitialiser',
        'Update': 'Mettre à jour',
        'Add': 'Ajouter',
        'Remove': 'Retirer',
        'View': 'Voir',
        'Export': 'Exporter',
        'Import': 'Importer',
        'Download': 'Télécharger',
        'Upload': 'Téléverser',
        'Uploading': 'Téléversement',
        'Preview': 'Aperçu',
        'Refresh': 'Actualiser',
        'Filter': 'Filtrer',
        'Clear': 'Effacer',
        'Apply': 'Appliquer',
        'Close': 'Fermer',
        'Back': 'Retour',
        'Next': 'Suivant',
        'Previous': 'Précédent',
        'Publish': 'Publier',
        'Draft': 'Brouillon',

        # 状态
        'Active': 'Actif',
        'Inactive': 'Inactif',
        'Enabled': 'Activé',
        'Disabled': 'Désactivé',
        'Success': 'Succès',
        'Failed': 'Échoué',
        'Error': 'Erreur',
        'Warning': 'Avertissement',
        'Info': 'Info',
        'Loading': 'Chargement',
        'Pending': 'En attente',
        'Completed': 'Terminé',
        'Pinned': 'Épinglé',
        'Unpinned': 'Non épinglé',

        # 通用词汇
        'Status': 'Statut',
        'Type': 'Type',
        'Name': 'Nom',
        'Title': 'Titre',
        'Description': 'Description',
        'Content': 'Contenu',
        'Category': 'Catégorie',
        'Tag': 'Tag',
        'Tags': 'Tags',
        'Date': 'Date',
        'Time': 'Heure',
        'Actions': 'Opérations',
        'Details': 'Détails',
        'Settings': 'Paramètres',
        'Total': 'Total',
        'Count': 'Nombre',
        'All': 'Tout',
        'None': 'Aucun',
        'Yes': 'Oui',
        'No': 'Non',
        'Required': 'Obligatoire',
        'Optional': 'Optionnel',
        'Rank': 'Rang',
        'Order': 'Ordre',
        'Sort': 'Trier',
        'Videos': 'Vidéos',
        'Video': 'Vidéo',
        'Users': 'Utilisateurs',
        'User': 'Utilisateur',
        'Comments': 'Commentaires',
        'Comment': 'Commentaire',
        'Series': 'Séries',
        'Episode': 'Épisode',
        'Episodes': 'Épisodes',

        # 消息
        'Success!': 'Succès !',
        'Created successfully': 'Créé avec succès',
        'Updated successfully': 'Mis à jour avec succès',
        'Deleted successfully': 'Supprimé avec succès',
        'Saved successfully': 'Enregistré avec succès',
        'Operation failed': 'Opération échouée',
        'Confirm delete?': 'Confirmer la suppression ?',
        'Are you sure?': 'Êtes-vous sûr ?',
        'No data': 'Aucune donnée',
        'Loading...': 'Chargement...',
        'Please wait...': 'Veuillez patienter...',
        'Refreshed successfully': 'Actualisé avec succès',
        'Export failed': 'Export échoué',
        'Export success': 'Export réussi',
        'Exported successfully': 'Exporté avec succès',

        # 时间相关
        'Created at': 'Créé le',
        'Updated at': 'Mis à jour le',
        'Created time': 'Date de création',
        'Update time': 'Date de mise à jour',
        'Days': 'Jours',
        'Hours': 'Heures',
        'Minutes': 'Minutes',

        # 菜单和导航
        'Search menu...': 'Rechercher dans le menu...',
        'Quick filters': 'Filtres rapides',
        'Clear filters': 'Effacer les filtres',
        'Filters cleared': 'Filtres effacés',
        'Filters': 'Filtres',

        # Series相关
        'New series': 'Nouvelle série',
        'Series details': 'Détails de la série',
        'Edit series': 'Modifier la série',
        'New episode': 'Nouvel épisode',
    },

    'ja-JP': {
        # 常用操作
        'Search': '検索',
        'Create': '作成',
        'Edit': '編集',
        'Delete': '削除',
        'Cancel': 'キャンセル',
        'Confirm': '確認',
        'Save': '保存',
        'Submit': '送信',
        'Reset': 'リセット',
        'Update': '更新',
        'Add': '追加',
        'Remove': '削除',
        'View': '表示',
        'Export': 'エクスポート',
        'Import': 'インポート',
        'Download': 'ダウンロード',
        'Upload': 'アップロード',
        'Uploading': 'アップロード中',
        'Preview': 'プレビュー',
        'Refresh': '更新',
        'Filter': 'フィルター',
        'Clear': 'クリア',
        'Apply': '適用',
        'Close': '閉じる',
        'Back': '戻る',
        'Next': '次へ',
        'Previous': '前へ',
        'Publish': '公開',
        'Draft': '下書き',

        # 状态
        'Active': 'アクティブ',
        'Inactive': '非アクティブ',
        'Enabled': '有効',
        'Disabled': '無効',
        'Success': '成功',
        'Failed': '失敗',
        'Error': 'エラー',
        'Warning': '警告',
        'Info': '情報',
        'Loading': '読み込み中',
        'Pending': '保留中',
        'Completed': '完了',
        'Pinned': 'ピン留め',
        'Unpinned': 'ピン留め解除',

        # 通用词汇
        'Status': 'ステータス',
        'Type': 'タイプ',
        'Name': '名前',
        'Title': 'タイトル',
        'Description': '説明',
        'Content': 'コンテンツ',
        'Category': 'カテゴリ',
        'Tag': 'タグ',
        'Tags': 'タグ',
        'Date': '日付',
        'Time': '時間',
        'Actions': '操作',
        'Details': '詳細',
        'Settings': '設定',
        'Total': '合計',
        'Count': '件数',
        'All': 'すべて',
        'None': 'なし',
        'Yes': 'はい',
        'No': 'いいえ',
        'Required': '必須',
        'Optional': '任意',
        'Rank': 'ランク',
        'Order': '順序',
        'Sort': '並び替え',
        'Videos': '動画',
        'Video': '動画',
        'Users': 'ユーザー',
        'User': 'ユーザー',
        'Comments': 'コメント',
        'Comment': 'コメント',
        'Series': 'シリーズ',
        'Episode': 'エピソード',
        'Episodes': 'エピソード',

        # 消息
        'Success!': '成功！',
        'Created successfully': '作成に成功しました',
        'Updated successfully': '更新に成功しました',
        'Deleted successfully': '削除に成功しました',
        'Saved successfully': '保存に成功しました',
        'Operation failed': '操作が失敗しました',
        'Confirm delete?': '削除しますか？',
        'Are you sure?': 'よろしいですか？',
        'No data': 'データがありません',
        'Loading...': '読み込み中...',
        'Please wait...': 'お待ちください...',
        'Refreshed successfully': '更新に成功しました',
        'Export failed': 'エクスポートに失敗しました',
        'Export success': 'エクスポート成功',
        'Exported successfully': 'エクスポートに成功しました',

        # 时间相关
        'Created at': '作成日時',
        'Updated at': '更新日時',
        'Created time': '作成時間',
        'Update time': '更新時間',
        'Days': '日',
        'Hours': '時間',
        'Minutes': '分',

        # 菜单和导航
        'Search menu...': 'メニューを検索...',
        'Quick filters': 'クイックフィルター',
        'Clear filters': 'フィルターをクリア',
        'Filters cleared': 'フィルターをクリアしました',
        'Filters': 'フィルター',

        # Series相关
        'New series': '新しいシリーズ',
        'Series details': 'シリーズの詳細',
        'Edit series': 'シリーズを編集',
        'New episode': '新しいエピソード',
    }
}


def contains_chinese(text: str) -> bool:
    """检查文本是否包含中文字符"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def get_all_values(obj: dict, prefix: str = "") -> Dict[str, str]:
    """递归获取JSON对象中的所有键值对"""
    values = {}
    for key, value in obj.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            values.update(get_all_values(value, full_key))
        else:
            values[full_key] = str(value)
    return values


def set_nested_value(obj: dict, key_path: str, value: str):
    """设置嵌套字典的值"""
    keys = key_path.split('.')
    current = obj
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value


def translate_text(text: str, lang_code: str) -> str:
    """尝试翻译文本"""
    translations = TRANSLATIONS.get(lang_code, {})

    # 完全匹配
    if text in translations:
        return translations[text]

    # 尝试部分匹配和替换
    for en, translated in translations.items():
        if en.lower() in text.lower():
            # 简单替换
            text = text.replace(en, translated)

    return text


def translate_file(lang_code: str, base_path: Path):
    """翻译指定语言文件"""
    print(f"\n{'='*80}")
    print(f"翻译 {lang_code}")
    print(f"{'='*80}\n")

    lang_file = base_path / f"{lang_code}.json"
    en_file = base_path / "en-US.json"

    # 读取文件
    with open(lang_file, 'r', encoding='utf-8') as f:
        lang_data = json.load(f)
    with open(en_file, 'r', encoding='utf-8') as f:
        en_data = json.load(f)

    # 获取所有键值对
    lang_values = get_all_values(lang_data)
    en_values = get_all_values(en_data)

    # 统计
    total_chinese = 0
    translated = 0

    # 翻译
    for key, value in lang_values.items():
        if contains_chinese(value):
            total_chinese += 1
            en_value = en_values.get(key, "")

            if en_value and not contains_chinese(en_value):
                # 尝试翻译英文值
                new_value = translate_text(en_value, lang_code)

                if new_value != en_value:  # 翻译成功
                    set_nested_value(lang_data, key, new_value)
                    translated += 1
                    if translated <= 5:  # 显示前5个翻译
                        print(f"✓ {key}")
                        print(f"  原: {value}")
                        print(f"  新: {new_value}")
                        print()

    # 保存文件
    with open(lang_file, 'w', encoding='utf-8') as f:
        json.dump(lang_data, f, ensure_ascii=False, indent=2)

    print(f"完成！共翻译 {translated}/{total_chinese} 项")
    print(f"剩余 {total_chinese - translated} 项需要人工翻译")

    return translated, total_chinese


def main():
    """主函数"""
    admin_i18n = Path("/home/eric/video/admin-frontend/src/i18n/locales")

    print("="*80)
    print("自动翻译工具 - 基于英文翻译和常用词典")
    print("="*80)

    total_translated = 0
    total_remaining = 0

    for lang in ["de-DE", "fr-FR", "ja-JP"]:
        translated, total = translate_file(lang, admin_i18n)
        total_translated += translated
        total_remaining += (total - translated)

    print(f"\n{'='*80}")
    print("总结")
    print(f"{'='*80}")
    print(f"✅ 自动翻译: {total_translated} 项")
    print(f"⚠️  仍需人工翻译: {total_remaining} 项")
    print(f"📊 自动化率: {total_translated / (total_translated + total_remaining) * 100:.1f}%")


if __name__ == "__main__":
    main()
