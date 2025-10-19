"""
支付网关抽象基类和工厂

定义统一的支付网关接口，支持多个支付提供商
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional, Dict, Any
from datetime import datetime

from app.models.payment import PaymentProvider, Currency


class PaymentGatewayException(Exception):
    """支付网关异常基类"""
    pass


class PaymentGatewayConfig:
    """支付网关配置"""

    def __init__(
        self,
        provider: PaymentProvider,
        api_key: str,
        api_secret: Optional[str] = None,
        webhook_secret: Optional[str] = None,
        environment: str = "sandbox",  # sandbox or production
        **kwargs
    ):
        self.provider = provider
        self.api_key = api_key
        self.api_secret = api_secret
        self.webhook_secret = webhook_secret
        self.environment = environment
        self.extra_config = kwargs


class PaymentResult:
    """支付结果封装"""

    def __init__(
        self,
        success: bool,
        provider_payment_id: Optional[str] = None,
        provider_customer_id: Optional[str] = None,
        amount: Optional[Decimal] = None,
        currency: Optional[Currency] = None,
        status: Optional[str] = None,
        failure_code: Optional[str] = None,
        failure_message: Optional[str] = None,
        receipt_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.success = success
        self.provider_payment_id = provider_payment_id
        self.provider_customer_id = provider_customer_id
        self.amount = amount
        self.currency = currency
        self.status = status
        self.failure_code = failure_code
        self.failure_message = failure_message
        self.receipt_url = receipt_url
        self.metadata = metadata or {}


class RefundResult:
    """退款结果封装"""

    def __init__(
        self,
        success: bool,
        refund_id: Optional[str] = None,
        amount: Optional[Decimal] = None,
        failure_message: Optional[str] = None,
        refunded_at: Optional[datetime] = None,
    ):
        self.success = success
        self.refund_id = refund_id
        self.amount = amount
        self.failure_message = failure_message
        self.refunded_at = refunded_at


class PaymentGateway(ABC):
    """支付网关抽象基类"""

    def __init__(self, config: PaymentGatewayConfig):
        self.config = config

    @abstractmethod
    async def create_payment_intent(
        self,
        amount: Decimal,
        currency: Currency,
        customer_id: Optional[str] = None,
        payment_method_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PaymentResult:
        """
        创建支付意图

        Args:
            amount: 支付金额
            currency: 货币类型
            customer_id: 客户ID (可选，用于保存支付方式)
            payment_method_id: 支付方式ID (可选)
            description: 支付描述
            metadata: 额外元数据

        Returns:
            PaymentResult: 支付结果
        """
        pass

    @abstractmethod
    async def confirm_payment(
        self,
        payment_intent_id: str,
        payment_method_id: Optional[str] = None,
    ) -> PaymentResult:
        """
        确认支付

        Args:
            payment_intent_id: 支付意图ID
            payment_method_id: 支付方式ID

        Returns:
            PaymentResult: 支付结果
        """
        pass

    @abstractmethod
    async def get_payment_status(
        self,
        payment_id: str,
    ) -> PaymentResult:
        """
        查询支付状态

        Args:
            payment_id: 支付ID

        Returns:
            PaymentResult: 支付结果
        """
        pass

    @abstractmethod
    async def create_refund(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None,
    ) -> RefundResult:
        """
        创建退款

        Args:
            payment_id: 支付ID
            amount: 退款金额 (None表示全额退款)
            reason: 退款原因

        Returns:
            RefundResult: 退款结果
        """
        pass

    @abstractmethod
    async def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        创建客户

        Args:
            email: 客户邮箱
            name: 客户名称
            metadata: 额外元数据

        Returns:
            str: 客户ID
        """
        pass

    @abstractmethod
    async def attach_payment_method(
        self,
        customer_id: str,
        payment_method_id: str,
    ) -> bool:
        """
        关联支付方式到客户

        Args:
            customer_id: 客户ID
            payment_method_id: 支付方式ID

        Returns:
            bool: 是否成功
        """
        pass

    @abstractmethod
    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        创建订阅

        Args:
            customer_id: 客户ID
            price_id: 价格ID
            trial_days: 试用天数
            metadata: 额外元数据

        Returns:
            Dict: 订阅信息
        """
        pass

    @abstractmethod
    async def cancel_subscription(
        self,
        subscription_id: str,
        immediately: bool = False,
    ) -> bool:
        """
        取消订阅

        Args:
            subscription_id: 订阅ID
            immediately: 是否立即取消

        Returns:
            bool: 是否成功
        """
        pass

    @abstractmethod
    async def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
    ) -> bool:
        """
        验证webhook签名

        Args:
            payload: 请求体
            signature: 签名

        Returns:
            bool: 签名是否有效
        """
        pass


class PaymentGatewayFactory:
    """支付网关工厂"""

    _gateways: Dict[PaymentProvider, type[PaymentGateway]] = {}

    @classmethod
    def register(cls, provider: PaymentProvider, gateway_class: type[PaymentGateway]):
        """注册支付网关"""
        cls._gateways[provider] = gateway_class

    @classmethod
    def create(cls, config: PaymentGatewayConfig) -> PaymentGateway:
        """创建支付网关实例"""
        gateway_class = cls._gateways.get(config.provider)
        if not gateway_class:
            raise PaymentGatewayException(f"Unsupported payment provider: {config.provider}")
        return gateway_class(config)
