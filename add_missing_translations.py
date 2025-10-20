#!/usr/bin/env python3
"""补充缺失的翻译"""
import json
from pathlib import Path

# 各语言的退款翻译
translations = {
    "de-DE": {
        "payment": {
            "payments": {
                "fullyRefunded": "Vollständig erstattet",
                "partiallyRefunded": "Teilweise erstattet",
                "refundAgain": "Erneut erstatten"
            },
            "refund": {
                "title": "Rückerstattung bearbeiten",
                "warning": "Die Rückerstattung ist irreversibel. Bitte vorsichtig vorgehen.",
                "confirm": "Rückerstattung bestätigen",
                "paymentInfo": "Zahlungsinformationen",
                "totalAmount": "Gesamtbetrag",
                "alreadyRefunded": "Bereits erstattet",
                "remainingAmount": "Erstattungsfähiger Betrag",
                "refundType": "Erstattungsart",
                "fullRefund": "Vollständige Rückerstattung",
                "partialRefund": "Teilrückerstattung",
                "refundAmount": "Rückerstattungsbetrag",
                "amountRequired": "Bitte Rückerstattungsbetrag eingeben",
                "amountInvalid": "Rückerstattungsbetrag muss zwischen 0,01 und dem verbleibenden Betrag liegen",
                "enterAmount": "Rückerstattungsbetrag eingeben",
                "reason": "Rückerstattungsgrund",
                "reasonRequired": "Bitte einen Rückerstattungsgrund auswählen",
                "selectReason": "Rückerstattungsgrund auswählen",
                "reasonDetail": "Detaillierte Erklärung",
                "reasonDetailRequired": "Bitte eine detaillierte Erklärung angeben",
                "reasonDetailTooLong": "Detaillierte Erklärung darf 500 Zeichen nicht überschreiten",
                "reasonDetailPlaceholder": "Bitte detaillierte Erklärung für Rückerstattung angeben...",
                "adminNote": "Admin-Notiz (Optional)",
                "adminNoteTooLong": "Notiz darf 1000 Zeichen nicht überschreiten",
                "adminNotePlaceholder": "Interne Notiz, für Benutzer nicht sichtbar...",
                "viewReason": "Grund anzeigen",
                "reasons": {
                    "userRequest": "Benutzeranfrage",
                    "serviceQuality": "Servicequalitätsproblem",
                    "technicalIssue": "Technisches Problem",
                    "duplicatePayment": "Doppelte Zahlung",
                    "fraud": "Betrügerische Bestellung",
                    "other": "Anderer Grund"
                }
            }
        }
    },
    "fr-FR": {
        "payment": {
            "payments": {
                "fullyRefunded": "Entièrement remboursé",
                "partiallyRefunded": "Partiellement remboursé",
                "refundAgain": "Rembourser à nouveau"
            },
            "refund": {
                "title": "Traiter le remboursement",
                "warning": "L'opération de remboursement est irréversible. Veuillez procéder avec prudence.",
                "confirm": "Confirmer le remboursement",
                "paymentInfo": "Informations de paiement",
                "totalAmount": "Montant total",
                "alreadyRefunded": "Déjà remboursé",
                "remainingAmount": "Montant remboursable",
                "refundType": "Type de remboursement",
                "fullRefund": "Remboursement complet",
                "partialRefund": "Remboursement partiel",
                "refundAmount": "Montant du remboursement",
                "amountRequired": "Veuillez saisir le montant du remboursement",
                "amountInvalid": "Le montant du remboursement doit être compris entre 0,01 et le montant restant",
                "enterAmount": "Saisir le montant du remboursement",
                "reason": "Raison du remboursement",
                "reasonRequired": "Veuillez sélectionner une raison de remboursement",
                "selectReason": "Sélectionner la raison du remboursement",
                "reasonDetail": "Explication détaillée",
                "reasonDetailRequired": "Veuillez fournir une explication détaillée",
                "reasonDetailTooLong": "L'explication détaillée ne peut pas dépasser 500 caractères",
                "reasonDetailPlaceholder": "Veuillez fournir une explication détaillée du remboursement...",
                "adminNote": "Note admin (Optionnel)",
                "adminNoteTooLong": "La note ne peut pas dépasser 1000 caractères",
                "adminNotePlaceholder": "Note interne, non visible pour les utilisateurs...",
                "viewReason": "Voir la raison",
                "reasons": {
                    "userRequest": "Demande de l'utilisateur",
                    "serviceQuality": "Problème de qualité de service",
                    "technicalIssue": "Problème technique",
                    "duplicatePayment": "Paiement en double",
                    "fraud": "Commande frauduleuse",
                    "other": "Autre raison"
                }
            }
        }
    },
    "ja-JP": {
        "payment": {
            "payments": {
                "fullyRefunded": "全額返金済み",
                "partiallyRefunded": "一部返金済み",
                "refundAgain": "再度返金"
            },
            "refund": {
                "title": "返金処理",
                "warning": "返金操作は元に戻せません。慎重に進めてください。",
                "confirm": "返金を確認",
                "paymentInfo": "支払い情報",
                "totalAmount": "合計金額",
                "alreadyRefunded": "既に返金済み",
                "remainingAmount": "返金可能金額",
                "refundType": "返金タイプ",
                "fullRefund": "全額返金",
                "partialRefund": "一部返金",
                "refundAmount": "返金金額",
                "amountRequired": "返金金額を入力してください",
                "amountInvalid": "返金金額は0.01から残額の間である必要があります",
                "enterAmount": "返金金額を入力",
                "reason": "返金理由",
                "reasonRequired": "返金理由を選択してください",
                "selectReason": "返金理由を選択",
                "reasonDetail": "詳細説明",
                "reasonDetailRequired": "詳細説明を入力してください",
                "reasonDetailTooLong": "詳細説明は500文字を超えることはできません",
                "reasonDetailPlaceholder": "返金の詳細説明を入力してください...",
                "adminNote": "管理者メモ（オプション）",
                "adminNoteTooLong": "メモは1000文字を超えることはできません",
                "adminNotePlaceholder": "内部メモ、ユーザーには表示されません...",
                "viewReason": "理由を表示",
                "reasons": {
                    "userRequest": "ユーザーリクエスト",
                    "serviceQuality": "サービス品質の問題",
                    "technicalIssue": "技術的問題",
                    "duplicatePayment": "重複支払い",
                    "fraud": "不正な注文",
                    "other": "その他の理由"
                }
            }
        }
    },
    "zh-TW": {
        "payment": {
            "payments": {
                "fullyRefunded": "已全額退款",
                "partiallyRefunded": "已部分退款",
                "refundAgain": "再次退款"
            },
            "refund": {
                "title": "處理退款",
                "warning": "退款操作不可逆，請謹慎操作。",
                "confirm": "確認退款",
                "paymentInfo": "支付資訊",
                "totalAmount": "總金額",
                "alreadyRefunded": "已退款",
                "remainingAmount": "可退款金額",
                "refundType": "退款類型",
                "fullRefund": "全額退款",
                "partialRefund": "部分退款",
                "refundAmount": "退款金額",
                "amountRequired": "請輸入退款金額",
                "amountInvalid": "退款金額必須在0.01到剩餘金額之間",
                "enterAmount": "輸入退款金額",
                "reason": "退款原因",
                "reasonRequired": "請選擇退款原因",
                "selectReason": "選擇退款原因",
                "reasonDetail": "詳細說明",
                "reasonDetailRequired": "請提供詳細說明",
                "reasonDetailTooLong": "詳細說明不能超過500個字符",
                "reasonDetailPlaceholder": "請提供退款詳細說明...",
                "adminNote": "管理員備註（可選）",
                "adminNoteTooLong": "備註不能超過1000個字符",
                "adminNotePlaceholder": "內部備註，用戶不可見...",
                "viewReason": "查看原因",
                "reasons": {
                    "userRequest": "用戶請求",
                    "serviceQuality": "服務質量問題",
                    "technicalIssue": "技術問題",
                    "duplicatePayment": "重複支付",
                    "fraud": "欺詐訂單",
                    "other": "其他原因"
                }
            }
        }
    }
}

def deep_merge(base: dict, update: dict) -> dict:
    """深度合并字典"""
    result = base.copy()
    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def update_translation_file(lang: str):
    """更新翻译文件"""
    file_path = Path(f"/home/eric/video/admin-frontend/src/i18n/locales/{lang}.json")

    # 读取现有翻译
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 合并新翻译
    updated_data = deep_merge(data, translations[lang])

    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 已更新 {lang}.json")


# 更新所有语言文件
for lang in ["de-DE", "fr-FR", "ja-JP", "zh-TW"]:
    update_translation_file(lang)

print("\n✅ 所有翻译文件已更新完成！")
