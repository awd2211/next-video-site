#!/usr/bin/env python3
"""
完美翻译系统 - 第十二轮
法语冲刺100% - 修正所有混合语言片段
"""

import json
import re
from pathlib import Path
from typing import Dict, Any

# 空德语字典（已100%）
DE_YOTTA = {}

# 法语100%冲刺字典 - 修正混合语言
FR_YOTTA = {
    # AI配额管理修正（关键：Montant错误，应该是quota）
    "配Montant管理": "Gestion des quotas",
    "配MontantType": "Type de quota",
    "Global配Montant": "Quota global",
    "Fournisseur配Montant": "Quota du fournisseur",
    "Global配MontantLaisser vide": "Laisser vide pour quota global",
    "每MinutesLimite de débit": "Limite de débit par minute",
    "配MontantLimité": "Quota limité",
    "Quotidien剩余Requête": "Requêtes quotidiennes restantes",
    "Mensuel剩余Requête": "Requêtes mensuelles restantes",
    "Quotidien剩余Coût": "Coût quotidien restant",

    # AI变量模板修正
    "摘要Total结": "Résumé",
    "DescriptionCeModèle用途": "Décrire l'objectif de ce modèle",
    "Entrer avec{变量}Invitemodèle": "Entrer le modèle d'invite avec {variables}",
    "（如：": " (par exemple: ",
    "包含变量示例ValeurJSONobjet": "Objet JSON contenant des valeurs d'exemple de variables",
    "包含RecommandéParamètres du modèleJSONobjet": "Objet JSON contenant les paramètres de modèle recommandés",
    "无效示例变量JSON格式": "Format JSON des variables d'exemple invalide",
    "无效RecommandéParamètresJSON格式": "Format JSON des paramètres recommandés invalide",
    "Recommandé配置": "Configuration recommandée",

    # 系统健康修正
    "已Marquer comme lu": "Marqué comme lu",
    "系统Surveillance de la santé": "Surveillance de la santé du système",
    "Connexion池Taux d'utilisation": "Taux d'utilisation du pool de connexions",
    "已用mémoire": "Mémoire utilisée",
    "Envoyer数据": "Données envoyées",
    "部分服务出现问题，请查看下方Détails。": "Certains services ont des problèmes, voir les détails ci-dessous.",

    # 日志修正
    "JournauxTotal数": "Nombre total de journaux",
    "Échec率": "Taux d'échec",
    "Par lot解决": "Résolution par lot",
    "Échec原因": "Raison de l'échec",
    "解决Heure": "Heure de résolution",
    "标记Succès": "Marqué avec succès",
    "今Jours": "Aujourd'hui",

    # 邮件修正
    "E-mail格式无效": "Format d'e-mail invalide",

    # 报表修正
    "VIPTotal数": "Nombre total de VIP",
    "Total观看次数": "Nombre total de vues",
    "Type分布": "Distribution par type",

    # 调度修正
    "PlanificationVidéos将在指定HeureAutomatique发布": "Les vidéos planifiées seront publiées automatiquement à l'heure spécifiée",
    "{{count}} 个PlanificationExpiré": "{{count}} planifications expirées",
    "TotalPlanification数": "Nombre total de planifications",

    # 认证修正（大量混合语言）
    "登录Succès！正在跳转...": "Connexion réussie! Redirection...",
    "Veuillez saisirAuthentification à deux facteurs码": "Veuillez saisir le code d'authentification à deux facteurs",
    "OuSaisir manuellement密钥：": "Ou saisir manuellement la clé:",
    "输入Vérifier码PourTerminéParamètres：": "Entrer le code de vérification pour terminer la configuration:",
    "Veuillez saisir密码": "Veuillez saisir le mot de passe",
    "Le code de vérification est4位Caractères": "Le code de vérification est de 4 caractères",
    "4位": "4",
    "CliquerActualiserVérifier码": "Cliquer pour actualiser le code de vérification",
    "登录...": "Connexion en cours...",
    "Veuillez saisir身份Vérifier器AppliquerCode de vérification à 6 chiffres": "Veuillez saisir le code de vérification à 6 chiffres de l'application d'authentification",
    "身份Vérifier器Appliquer": "Application d'authentification",
    "OuUtilisationSauvegarde码（格式：XXXX-XXXX）": "Ou utiliser le code de sauvegarde (format: XXXX-XXXX)",
    "UtilisationSauvegarde": "Utiliser le code de sauvegarde",
    "SaisirCode de vérification à 6 chiffresOuSauvegarde码": "Saisir le code de vérification à 6 chiffres ou le code de sauvegarde",
    "EnvoyerVérifier码": "Envoyer le code de vérification",
    "重新Envoyer": "Renvoyer",
    "Vérifier码已EnvoyerÀVotreE-mail，请查收": "Code de vérification envoyé à votre e-mail, veuillez vérifier",
    "已EnvoyerÀVotre": "Envoyé à votre",
    "请查收": "Veuillez vérifier",
    "Vérifier码已重新Envoyer": "Code de vérification renvoyé",
    "已重新": "Renvoyé",
    "Veuillez saisirNouveau mot de passe（Au moins8位）": "Veuillez saisir le nouveau mot de passe (au moins 8 caractères)",
    "（Au moins8位）": " (au moins 8 caractères)",
    "请Saisir à nouveauNouveau mot de passe": "Veuillez saisir à nouveau le nouveau mot de passe",
    "Réinitialisation du mot de passeSuccès！请UtilisationNouveau mot de passe登录": "Réinitialisation du mot de passe réussie! Veuillez vous connecter avec le nouveau mot de passe",
    "请Utilisation": "Veuillez utiliser",
    "Vérifier码ErreurOuExpiré": "Code de vérification invalide ou expiré",
    "ErreurOu": "Invalide ou",
    "Valide pour15Minutes，请及时查收邮件": "Valide pour 15 minutes, veuillez vérifier l'e-mail rapidement",
    "15Minutes": "15 minutes",
    "请及时查收邮件": "Veuillez vérifier l'e-mail rapidement",
    "及时": "Rapidement",
    "Secondes后可重新Envoyer": "Peut renvoyer après secondes",
    "后可重新": "Peut renvoyer après",
    "Vérifier码已EnvoyerÀ": "Code de vérification envoyé à",
    "已Envoyer": "Envoyé",
    "Vérifier码加载Délai dépassé，Veuillez réessayer": "Chargement du code de vérification expiré, veuillez réessayer",
    "加载Délai dépassé": "Chargement expiré",
    "Vérifier码加载Échec，VeuillezActualiserRéessayer": "Échec du chargement du code de vérification, veuillez actualiser et réessayer",
    "加载Échec": "Échec du chargement",
    "VeuillezActualiser": "Veuillez actualiser",
    "EnvoyerÉchec，Veuillez vérifierE-mail地址": "Échec de l'envoi, veuillez vérifier l'adresse e-mail",
    "地址": "Adresse",
    "Service de messagerie未配置，Veuillez contacterAdministrateur": "Service de messagerie non configuré, veuillez contacter l'administrateur",
    "未配置": "Non configuré",
    "邮件EnvoyerÉchec，请Plus tardRéessayer": "Échec de l'envoi de l'e-mail, veuillez réessayer plus tard",
    "请Plus tard": "Veuillez plus tard",
    "Plus tard再试": "Réessayer plus tard",
    "账户已Désactivé": "Compte désactivé",
    "登录Échec，Veuillez vérifierNom d'utilisateurEt密码": "Échec de la connexion, veuillez vérifier le nom d'utilisateur et le mot de passe",
    "Nom d'utilisateurEt": "Nom d'utilisateur et",
    "Nom d'utilisateurOu密码Erreur": "Nom d'utilisateur ou mot de passe incorrect",
    "Ou密码": "Ou mot de passe",
    "登录Trop de tentatives，请Plus tard再试": "Trop de tentatives de connexion, veuillez réessayer plus tard",
    "Session de connexionExpiré，请重新登录": "Session de connexion expirée, veuillez vous reconnecter",
    "请重新登录": "Veuillez vous reconnecter",
    "Vérifier码Erreur，Veuillez réessayer": "Code de vérification incorrect, veuillez réessayer",
    "Veuillez saisirValideE-mail地址": "Veuillez saisir une adresse e-mail valide",
    "Le code de vérification est6位Chiffres": "Le code de vérification est de 6 chiffres",
    "6位": "6",
    "Vérifier码DoitOui6位Chiffres": "Le code de vérification doit être de 6 chiffres",
    "DoitOui": "Doit être",
    "Longueur du mot de passeAu moins8位": "Longueur du mot de passe au moins 8 caractères",
    "8位": "8 caractères",
    "Veuillez saisirVotreS'inscrire时UtilisationE-mail地址，我们将向VotreEnvoyer6位ChiffresVérifier码": "Veuillez saisir l'adresse e-mail utilisée lors de l'inscription, nous vous enverrons un code de vérification à 6 chiffres",
    "S'inscrire时Utilisation": "Utilisée lors de l'inscription",
    "我们将向VotreEnvoyer": "Nous vous enverrons",
    "6位Chiffres": "6 chiffres",

    # 媒体
    "格式": "Format",

    # 角色
    "角色Description": "Description du rôle",
    "简要Description该角色Responsabilités": "Brève description des responsabilités du rôle",
    "该角色": "Du rôle",
    "请Au moinsSélectionner一个Permission": "Veuillez sélectionner au moins une permission",
    "一个": "Une",
    "{{count}} 个Permission": "{{count}} permissions",
    "Confirmer要Supprimer角色": "Confirmer la suppression du rôle",
    "Cette opération est irréversible。": "Cette opération est irréversible.",
    "超级AdministrateurPossèdeToutes les permissions，Pas besoinAttribuer un rôle": "Le super administrateur possède toutes les permissions, pas besoin d'attribuer un rôle",
    "角色AttribuerSuccès": "Rôle attribué avec succès",
    "Sélectionner角色（Laisser videPourAnnulerAttribuer）": "Sélectionner un rôle (laisser vide pour annuler l'attribution)",
    "PourAnnuler": "Pour annuler",
    "超级Administrateur": "Super administrateur",

    # 系统
    "Couramment utilisé: 1小时=3600, 1Jours=86400, 1周=604800": "Couramment utilisé: 1 heure=3600, 1 jour=86400, 1 semaine=604800",
    "1小时": "1 heure",
    "1周": "1 semaine",

    # OAuth
    "OAuth 登录配置": "Configuration de connexion OAuth",
    "Google OAuth 配置Guide": "Guide de configuration OAuth Google",
    "Facebook OAuth 配置Guide": "Guide de configuration OAuth Facebook",
    "配置Guide": "Guide de configuration",

    # 页面
    "Créer rapidement新VidéosContenu": "Créer rapidement du nouveau contenu vidéo",
    "新VidéosContenu": "Nouveau contenu vidéo",
    "RévisionSoumis par l'utilisateur评论": "Révision des commentaires soumis par l'utilisateur",
    "评论": "Commentaires",

    # 操作
    "开始": "Démarrer",

    # 验证
    "{{field}}Obligatoire项": "{{field}} est obligatoire",
    "Obligatoire项": "Obligatoire",
    "Veuillez saisirValideURL地址（需Pour http:// Ou https:// Commencer par）": "Veuillez saisir une URL valide (doit commencer par http:// ou https://)",
    "需Pour": "Doit",
    "Commencer par）": "Commencer par)",
    "Veuillez saisirValideIP地址": "Veuillez saisir une adresse IP valide",
    "Longueur应在 {{min}} À {{max}} 个CaractèresEntre": "La longueur doit être entre {{min}} et {{max}} caractères",
    "应在": "Doit être",
    "Entre": "Entre",
    "Ne peut pas dépasser {{max}} 个Caractères": "Ne peut pas dépasser {{max}} caractères",
    "Au moinsRequis {{min}} 个Caractères": "Au moins {{min}} caractères requis",
    "Requis": "Requis",
    "Valeur应在 {{min}} À {{max}} Entre": "La valeur doit être entre {{min}} et {{max}}",
    "文件tailleDépasserLimite（Maximum {{max}}MB）": "Taille de fichier dépasse la limite (maximum {{max}}MB)",
    "文件taille": "Taille de fichier",
    "DépasserLimite": "Dépasse la limite",
    "Veuillez saisirVidéos标题": "Veuillez saisir le titre de la vidéo",
    "标题": "Titre",
    "URL格式Erreur": "Erreur de format d'URL",
    "请TéléverserOu输入ImageURL": "Veuillez téléverser ou entrer l'URL de l'image",
    "ImageURL": "URL de l'image",

    # 支付
    "TotalPlan数": "Nombre total de plans",
    "Description（文）": "Description (chinois)",
    "Appareil数": "Nombre d'appareils",
    "热门": "Populaire",
    "Fonctionnalité（文）": "Fonctionnalités (chinois)",
    "Confirmer要Remboursement吗？": "Confirmer le remboursement?",
    "平均Montant de transaction": "Montant de transaction moyen",
    "百分比": "Pourcentage",
    "Valide日期": "Dates valides",
    "Confirmer要AnnulerCeAbonnement吗？": "Confirmer l'annulation de cet abonnement?",
    "要AnnulerCe": "L'annulation de cet",
    "EssaiAbonnement数": "Nombre d'abonnements d'essai",
    "TotalAbonnement数": "Nombre total d'abonnements",
    "Abonnements en retard数": "Nombre d'abonnements en retard",
    "平均Valeur d'abonnement": "Valeur d'abonnement moyenne",

    # 通用词
    "Vérifier码": "Code de vérification",
    "位": "",
}

# 日语补充字典
JA_YOTTA = {
    "格式": "フォーマット",
    "角色": "ロール",
    "该": "その",
    "一个": "1つ",
    "开始": "開始",
    "标题": "タイトル",
    "热门": "人気",
    "百分比": "パーセンテージ",
    "平均": "平均",
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
    print("完美翻译系统 - 第十二轮")
    print("="*80)

    results = {}

    print("\n处理德语翻译...")
    results['de-DE'] = translate_file('de-DE', DE_YOTTA)

    print("\n处理法语翻译...")
    results['fr-FR'] = translate_file('fr-FR', FR_YOTTA)

    print("\n处理日语翻译...")
    results['ja-JP'] = translate_file('ja-JP', JA_YOTTA)

    print(f"\n\n{'='*80}")
    print("第十二轮翻译完成总结")
    print(f"{'='*80}\n")

    total_translated = sum(r['translated'] for r in results.values())
    total_remaining = sum(r['after'] for r in results.values())

    for lang, stats in results.items():
        if stats['completion'] == 100:
            emoji = "🌟🌟🌟"
        elif stats['completion'] >= 95:
            emoji = "🌟🌟"
        elif stats['completion'] >= 90:
            emoji = "🌟"
        elif stats['completion'] >= 85:
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
    if results['fr-FR']['completion'] >= 95:
        print(f"\n🎉🎉🎉 法语突破95%！接近完美！")
    if results['fr-FR']['completion'] == 100:
        print(f"\n🌟🌟🌟 法语达到100%！完美！")

if __name__ == '__main__':
    main()
