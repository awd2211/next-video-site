"""
发票服务

处理发票生成、PDF 创建等业务逻辑
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.models.invoice import Invoice, InvoiceStatus
from app.models.payment import Payment
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate


class InvoiceService:
    """发票服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_invoice_number(self) -> str:
        """生成唯一的发票编号"""
        # 格式: INV-YYYYMMDD-XXXXX
        today = datetime.now().strftime("%Y%m%d")

        # 查询今天已有的发票数量
        result = await self.db.execute(
            select(Invoice).where(
                Invoice.invoice_number.like(f"INV-{today}-%")
            )
        )
        count = len(list(result.scalars().all()))

        sequence = count + 1
        return f"INV-{today}-{sequence:05d}"

    async def create_invoice(
        self, user_id: int, invoice_data: InvoiceCreate
    ) -> Invoice:
        """
        创建发票

        Args:
            user_id: 用户ID
            invoice_data: 发票数据

        Returns:
            Invoice: 新创建的发票
        """
        # 验证支付记录
        payment_result = await self.db.execute(
            select(Payment).where(
                and_(
                    Payment.id == invoice_data.payment_id,
                    Payment.user_id == user_id,
                )
            )
        )
        payment = payment_result.scalar_one_or_none()

        if not payment:
            raise ValueError("Payment not found")

        # 检查是否已有发票
        existing_result = await self.db.execute(
            select(Invoice).where(Invoice.payment_id == invoice_data.payment_id)
        )
        existing = existing_result.scalar_one_or_none()

        if existing:
            raise ValueError("Invoice already exists for this payment")

        # 生成发票编号
        invoice_number = await self.generate_invoice_number()

        # 计算总额
        total = invoice_data.subtotal + invoice_data.tax - invoice_data.discount

        # 创建发票
        invoice = Invoice(
            user_id=user_id,
            payment_id=invoice_data.payment_id,
            invoice_number=invoice_number,
            status=InvoiceStatus.PENDING,
            subtotal=invoice_data.subtotal,
            tax=invoice_data.tax,
            discount=invoice_data.discount,
            total=total,
            currency=invoice_data.currency,
            billing_name=invoice_data.billing_name,
            billing_email=invoice_data.billing_email,
            billing_address=invoice_data.billing_address,
            tax_id=invoice_data.tax_id,
            description=invoice_data.description,
            items=invoice_data.items,
            issue_date=datetime.now(),
            due_date=datetime.now() + timedelta(days=30),  # 30天支付期限
        )

        self.db.add(invoice)
        await self.db.commit()
        await self.db.refresh(invoice)

        # 异步生成 PDF (实际应该使用后台任务)
        # await self._generate_pdf(invoice)

        return invoice

    async def get_invoice(self, user_id: int, invoice_id: int) -> Optional[Invoice]:
        """获取发票"""
        result = await self.db.execute(
            select(Invoice).where(
                and_(Invoice.id == invoice_id, Invoice.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()

    async def get_invoice_by_number(
        self, user_id: int, invoice_number: str
    ) -> Optional[Invoice]:
        """根据发票号获取发票"""
        result = await self.db.execute(
            select(Invoice).where(
                and_(
                    Invoice.invoice_number == invoice_number,
                    Invoice.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_user_invoices(
        self, user_id: int, skip: int = 0, limit: int = 20
    ) -> tuple[List[Invoice], int]:
        """获取用户的发票列表"""
        # 查询总数
        count_result = await self.db.execute(
            select(Invoice).where(Invoice.user_id == user_id)
        )
        total = len(list(count_result.scalars().all()))

        # 查询列表
        result = await self.db.execute(
            select(Invoice)
            .where(Invoice.user_id == user_id)
            .order_by(desc(Invoice.created_at))
            .offset(skip)
            .limit(limit)
        )
        invoices = list(result.scalars().all())

        return invoices, total

    async def update_invoice(
        self, user_id: int, invoice_id: int, update_data: InvoiceUpdate
    ) -> Invoice:
        """更新发票"""
        invoice = await self.get_invoice(user_id, invoice_id)
        if not invoice:
            raise ValueError("Invoice not found")

        # 只能更新草稿或待支付状态的发票
        if invoice.status not in [InvoiceStatus.DRAFT, InvoiceStatus.PENDING]:
            raise ValueError("Cannot update paid or voided invoice")

        # 更新字段
        if update_data.status is not None:
            invoice.status = update_data.status

        if update_data.billing_name is not None:
            invoice.billing_name = update_data.billing_name

        if update_data.billing_email is not None:
            invoice.billing_email = update_data.billing_email

        if update_data.billing_address is not None:
            invoice.billing_address = update_data.billing_address

        if update_data.tax_id is not None:
            invoice.tax_id = update_data.tax_id

        if update_data.description is not None:
            invoice.description = update_data.description

        await self.db.commit()
        await self.db.refresh(invoice)

        return invoice

    async def mark_as_paid(self, invoice_id: int) -> Invoice:
        """标记发票为已支付"""
        result = await self.db.execute(
            select(Invoice).where(Invoice.id == invoice_id)
        )
        invoice = result.scalar_one_or_none()

        if not invoice:
            raise ValueError("Invoice not found")

        invoice.status = InvoiceStatus.PAID
        invoice.paid_at = datetime.now()

        await self.db.commit()
        await self.db.refresh(invoice)

        return invoice

    async def void_invoice(self, user_id: int, invoice_id: int) -> Invoice:
        """作废发票"""
        invoice = await self.get_invoice(user_id, invoice_id)
        if not invoice:
            raise ValueError("Invoice not found")

        if invoice.status == InvoiceStatus.PAID:
            raise ValueError("Cannot void paid invoice")

        invoice.status = InvoiceStatus.VOID

        await self.db.commit()
        await self.db.refresh(invoice)

        return invoice

    async def generate_pdf(self, invoice_id: int) -> str:
        """
        生成发票 PDF

        Args:
            invoice_id: 发票ID

        Returns:
            str: PDF URL

        注意: 这是一个简化实现
        实际应该使用 ReportLab 或 WeasyPrint 生成 PDF
        """
        result = await self.db.execute(
            select(Invoice).where(Invoice.id == invoice_id)
        )
        invoice = result.scalar_one_or_none()

        if not invoice:
            raise ValueError("Invoice not found")

        # 实际应该:
        # 1. 使用模板引擎渲染 HTML (Jinja2)
        # 2. 将 HTML 转换为 PDF (WeasyPrint)
        # 3. 上传到 MinIO
        # 4. 返回公开 URL

        # 简化实现: 返回假 URL
        pdf_url = f"https://storage.example.com/invoices/{invoice.invoice_number}.pdf"

        invoice.pdf_url = pdf_url

        await self.db.commit()
        await self.db.refresh(invoice)

        return pdf_url

    async def _generate_pdf(self, invoice: Invoice) -> None:
        """内部方法: 异步生成 PDF"""
        # 实际实现:
        # 1. 使用 Celery 任务队列
        # 2. 调用 PDF 生成服务
        # 3. 更新 invoice.pdf_url

        pass

    async def send_invoice_email(self, invoice_id: int) -> bool:
        """
        发送发票邮件

        Args:
            invoice_id: 发票ID

        Returns:
            bool: 是否成功

        注意: 这是一个简化实现
        实际应该使用邮件服务发送
        """
        result = await self.db.execute(
            select(Invoice).where(Invoice.id == invoice_id)
        )
        invoice = result.scalar_one_or_none()

        if not invoice:
            raise ValueError("Invoice not found")

        # 实际应该:
        # 1. 渲染邮件模板
        # 2. 附加 PDF 文件
        # 3. 通过 SMTP 发送

        # 简化实现: 返回成功
        return True

    async def calculate_statistics(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> dict:
        """
        计算发票统计数据

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            dict: 统计数据
        """
        query = select(Invoice)

        if start_date:
            query = query.where(Invoice.created_at >= start_date)

        if end_date:
            query = query.where(Invoice.created_at <= end_date)

        result = await self.db.execute(query)
        invoices = list(result.scalars().all())

        total_amount = sum(inv.total for inv in invoices)
        paid_amount = sum(
            inv.total for inv in invoices if inv.status == InvoiceStatus.PAID
        )
        pending_amount = sum(
            inv.total for inv in invoices if inv.status == InvoiceStatus.PENDING
        )

        return {
            "total_invoices": len(invoices),
            "paid_invoices": len(
                [inv for inv in invoices if inv.status == InvoiceStatus.PAID]
            ),
            "pending_invoices": len(
                [inv for inv in invoices if inv.status == InvoiceStatus.PENDING]
            ),
            "void_invoices": len(
                [inv for inv in invoices if inv.status == InvoiceStatus.VOID]
            ),
            "total_amount": float(total_amount),
            "paid_amount": float(paid_amount),
            "pending_amount": float(pending_amount),
        }
