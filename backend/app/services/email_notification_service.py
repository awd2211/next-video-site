"""
邮件通知服务

用于发送订阅相关的邮件通知
"""

from typing import Dict, Any, Optional
from datetime import datetime
from decimal import Decimal

from app.utils.email import send_email
from app.models.subscription import UserSubscription, SubscriptionPlan
from app.models.payment import Payment
from app.models.invoice import Invoice
from app.models.user import User


class EmailNotificationService:
    """邮件通知服务"""

    @staticmethod
    async def send_subscription_created(
        user: User,
        subscription: UserSubscription,
        plan: SubscriptionPlan
    ) -> bool:
        """发送订阅创建确认邮件"""

        subject = f"Welcome to {plan.name_en}! 🎉"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #3b82f6; color: white; padding: 20px; text-align: center;">
                <h1>Welcome to VideoSite Premium!</h1>
            </div>

            <div style="padding: 30px; background-color: #f9fafb;">
                <p>Hi {user.username},</p>

                <p>Thank you for subscribing to <strong>{plan.name_en}</strong>!</p>

                <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h2 style="color: #1f2937; margin-top: 0;">Your Subscription Details</h2>

                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb;">Plan:</td>
                            <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb; font-weight: bold;">{plan.name_en}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb;">Price:</td>
                            <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb; font-weight: bold;">${plan.price_usd} / {plan.billing_period.value}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb;">Video Quality:</td>
                            <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb;">{plan.max_video_quality.upper()}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb;">Concurrent Streams:</td>
                            <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb;">{plan.max_concurrent_streams}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0;">Next Billing Date:</td>
                            <td style="padding: 10px 0; font-weight: bold;">{subscription.current_period_end.strftime('%B %d, %Y')}</td>
                        </tr>
                    </table>
                </div>

                <div style="background-color: #dbeafe; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0; color: #1e40af;">
                        <strong>💡 Tip:</strong> You can manage your subscription, update payment methods, or cancel anytime from your account settings.
                    </p>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://videosite.com/account/subscription"
                       style="background-color: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block;">
                        Manage Subscription
                    </a>
                </div>

                <p style="color: #6b7280; font-size: 14px;">
                    If you have any questions, feel free to contact our support team.
                </p>

                <p>Best regards,<br>The VideoSite Team</p>
            </div>

            <div style="background-color: #1f2937; color: #9ca3af; padding: 20px; text-align: center; font-size: 12px;">
                <p>© 2025 VideoSite. All rights reserved.</p>
                <p>
                    <a href="https://videosite.com/terms" style="color: #9ca3af; text-decoration: none;">Terms</a> |
                    <a href="https://videosite.com/privacy" style="color: #9ca3af; text-decoration: none;">Privacy</a>
                </p>
            </div>
        </body>
        </html>
        """

        return await send_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content
        )

    @staticmethod
    async def send_payment_success(
        user: User,
        payment: Payment,
        subscription: Optional[UserSubscription] = None
    ) -> bool:
        """发送支付成功通知"""

        subject = f"Payment Received - ${payment.amount}"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #10b981; color: white; padding: 20px; text-align: center;">
                <h1>✓ Payment Successful</h1>
            </div>

            <div style="padding: 30px; background-color: #f9fafb;">
                <p>Hi {user.username},</p>

                <p>We've successfully received your payment!</p>

                <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h2 style="color: #1f2937; margin-top: 0;">Payment Details</h2>

                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb;">Amount:</td>
                            <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb; font-weight: bold; color: #10b981;">${payment.amount} {payment.currency.upper()}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb;">Payment Method:</td>
                            <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb;">{payment.payment_method or payment.payment_provider.upper()}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb;">Transaction ID:</td>
                            <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb; font-family: monospace;">{payment.provider_payment_id or payment.id}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0;">Date:</td>
                            <td style="padding: 10px 0; font-weight: bold;">{payment.paid_at.strftime('%B %d, %Y %I:%M %p') if payment.paid_at else 'N/A'}</td>
                        </tr>
                    </table>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://videosite.com/account/subscription"
                       style="background-color: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block;">
                        View Payment History
                    </a>
                </div>

                <p>Thank you for your business!</p>

                <p>Best regards,<br>The VideoSite Team</p>
            </div>

            <div style="background-color: #1f2937; color: #9ca3af; padding: 20px; text-align: center; font-size: 12px;">
                <p>© 2025 VideoSite. All rights reserved.</p>
            </div>
        </body>
        </html>
        """

        return await send_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content
        )

    @staticmethod
    async def send_subscription_canceled(
        user: User,
        subscription: UserSubscription,
        plan: SubscriptionPlan,
        cancel_immediately: bool = False
    ) -> bool:
        """发送订阅取消通知"""

        if cancel_immediately:
            subject = "Subscription Canceled"
            message = "Your subscription has been canceled and your access has ended."
        else:
            subject = "Subscription Will Be Canceled"
            message = f"Your subscription will be canceled on {subscription.current_period_end.strftime('%B %d, %Y')}. You'll continue to have access until then."

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #ef4444; color: white; padding: 20px; text-align: center;">
                <h1>Subscription Canceled</h1>
            </div>

            <div style="padding: 30px; background-color: #f9fafb;">
                <p>Hi {user.username},</p>

                <p>{message}</p>

                <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #1f2937;">Canceled Plan: {plan.name_en}</h3>

                    {'' if cancel_immediately else f'<p><strong>Access Until:</strong> {subscription.current_period_end.strftime("%B %d, %Y")}</p>'}
                </div>

                <div style="background-color: #fef3c7; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0; color: #92400e;">
                        We're sorry to see you go! If you change your mind, you can always resubscribe anytime.
                    </p>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://videosite.com/subscription"
                       style="background-color: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block;">
                        Browse Plans
                    </a>
                </div>

                <p>Best regards,<br>The VideoSite Team</p>
            </div>

            <div style="background-color: #1f2937; color: #9ca3af; padding: 20px; text-align: center; font-size: 12px;">
                <p>© 2025 VideoSite. All rights reserved.</p>
            </div>
        </body>
        </html>
        """

        return await send_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content
        )

    @staticmethod
    async def send_payment_failed(
        user: User,
        payment: Payment,
        subscription: Optional[UserSubscription] = None
    ) -> bool:
        """发送支付失败通知"""

        subject = "Payment Failed - Action Required"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #ef4444; color: white; padding: 20px; text-align: center;">
                <h1>⚠️ Payment Failed</h1>
            </div>

            <div style="padding: 30px; background-color: #f9fafb;">
                <p>Hi {user.username},</p>

                <p>We were unable to process your payment of <strong>${payment.amount} {payment.currency.upper()}</strong>.</p>

                {f'<p style="color: #dc2626;"><strong>Reason:</strong> {payment.error_message}</p>' if payment.error_message else ''}

                <div style="background-color: #fee2e2; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #dc2626;">
                    <p style="margin: 0; color: #991b1b;">
                        Please update your payment method to avoid service interruption.
                    </p>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://videosite.com/account/subscription"
                       style="background-color: #ef4444; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block;">
                        Update Payment Method
                    </a>
                </div>

                <p style="color: #6b7280; font-size: 14px;">
                    If you continue to experience issues, please contact our support team.
                </p>

                <p>Best regards,<br>The VideoSite Team</p>
            </div>

            <div style="background-color: #1f2937; color: #9ca3af; padding: 20px; text-align: center; font-size: 12px;">
                <p>© 2025 VideoSite. All rights reserved.</p>
            </div>
        </body>
        </html>
        """

        return await send_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content
        )

    @staticmethod
    async def send_invoice_email(
        user: User,
        invoice: Invoice,
        pdf_url: Optional[str] = None
    ) -> bool:
        """发送发票邮件"""

        subject = f"Invoice {invoice.invoice_number} from VideoSite"

        pdf_link = f'<p><a href="{pdf_url}" style="color: #3b82f6;">Download PDF Invoice</a></p>' if pdf_url else ''

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #3b82f6; color: white; padding: 20px; text-align: center;">
                <h1>Invoice</h1>
            </div>

            <div style="padding: 30px; background-color: #f9fafb;">
                <p>Hi {invoice.billing_name or user.username},</p>

                <p>Please find your invoice attached below.</p>

                <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb;">Invoice Number:</td>
                            <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb; font-weight: bold;">{invoice.invoice_number}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb;">Date:</td>
                            <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb;">{invoice.created_at.strftime('%B %d, %Y')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb;">Amount:</td>
                            <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb; font-weight: bold;">${invoice.total} {invoice.currency.upper()}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0;">Status:</td>
                            <td style="padding: 10px 0;">
                                <span style="background-color: {'#dcfce7' if invoice.status.value == 'paid' else '#fee2e2'};
                                             color: {'#166534' if invoice.status.value == 'paid' else '#991b1b'};
                                             padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">
                                    {invoice.status.value.upper()}
                                </span>
                            </td>
                        </tr>
                    </table>
                </div>

                {pdf_link}

                <p>Thank you for your business!</p>

                <p>Best regards,<br>The VideoSite Team</p>
            </div>

            <div style="background-color: #1f2937; color: #9ca3af; padding: 20px; text-align: center; font-size: 12px;">
                <p>© 2025 VideoSite. All rights reserved.</p>
            </div>
        </body>
        </html>
        """

        return await send_email(
            to_email=invoice.billing_email,
            subject=subject,
            html_content=html_content
        )
