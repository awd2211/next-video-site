"""
PDF生成服务

使用ReportLab生成发票PDF
"""

from io import BytesIO
from datetime import datetime
from decimal import Decimal
from typing import Optional

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.pdfgen import canvas

from app.models.invoice import Invoice
from app.models.user import User
from app.config import settings


class PDFGenerator:
    """PDF生成器"""

    @staticmethod
    def generate_invoice_pdf(invoice: Invoice, user: User) -> BytesIO:
        """
        生成发票PDF

        Args:
            invoice: 发票对象
            user: 用户对象

        Returns:
            BytesIO: PDF文件流
        """
        buffer = BytesIO()

        # 创建PDF文档
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch,
        )

        # 准备内容
        elements = []
        styles = getSampleStyleSheet()

        # 自定义样式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=30,
            alignment=TA_LEFT,
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#3b82f6'),
            spaceAfter=12,
            spaceBefore=20,
        )

        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#374151'),
        )

        # 1. 公司信息和发票标题
        title_data = [
            [
                Paragraph('<b>VideoSite</b><br/>Premium Video Streaming', title_style),
                Paragraph(f'<b>INVOICE</b><br/>{invoice.invoice_number}', heading_style)
            ]
        ]

        title_table = Table(title_data, colWidths=[4*inch, 3*inch])
        title_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        elements.append(title_table)
        elements.append(Spacer(1, 0.3*inch))

        # 2. 发票日期和状态
        status_color = {
            'draft': colors.grey,
            'pending': colors.orange,
            'paid': colors.green,
            'void': colors.red,
            'uncollectible': colors.red,
        }.get(invoice.status.value, colors.grey)

        info_data = [
            ['Invoice Date:', invoice.created_at.strftime('%B %d, %Y')],
            ['Due Date:', invoice.payment_due_date.strftime('%B %d, %Y') if invoice.payment_due_date else 'N/A'],
            ['Status:', invoice.status.value.upper()],
        ]

        info_table = Table(info_data, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1f2937')),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(info_table)
        elements.append(Spacer(1, 0.4*inch))

        # 3. 账单地址
        elements.append(Paragraph('Bill To:', heading_style))

        bill_to_data = [
            [Paragraph(f'<b>{invoice.billing_name or user.username}</b>', normal_style)],
            [Paragraph(invoice.billing_email, normal_style)],
        ]

        if invoice.billing_address:
            bill_to_data.append([Paragraph(invoice.billing_address, normal_style)])

        bill_to_table = Table(bill_to_data, colWidths=[6*inch])
        bill_to_table.setStyle(TableStyle([
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))

        elements.append(bill_to_table)
        elements.append(Spacer(1, 0.4*inch))

        # 4. 项目明细
        elements.append(Paragraph('Items:', heading_style))

        # 项目表头
        items_data = [
            ['Description', 'Quantity', 'Unit Price', 'Amount']
        ]

        # 解析line_items
        if invoice.line_items:
            import json
            try:
                line_items = json.loads(invoice.line_items) if isinstance(invoice.line_items, str) else invoice.line_items
            except:
                line_items = []

            for item in line_items:
                items_data.append([
                    item.get('description', ''),
                    str(item.get('quantity', 1)),
                    f"${float(item.get('unit_price', 0)):.2f}",
                    f"${float(item.get('amount', 0)):.2f}"
                ])
        else:
            # 默认项目
            items_data.append([
                f'Subscription - {invoice.created_at.strftime("%B %Y")}',
                '1',
                f"${float(invoice.subtotal):.2f}",
                f"${float(invoice.subtotal):.2f}"
            ])

        items_table = Table(items_data, colWidths=[3.5*inch, 0.8*inch, 1.2*inch, 1.2*inch])
        items_table.setStyle(TableStyle([
            # 表头样式
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),

            # 内容样式
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#374151')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),

            # 对齐
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),

            # 边框
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#d1d5db')),
            ('LINEBELOW', (0, 1), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ]))

        elements.append(items_table)
        elements.append(Spacer(1, 0.3*inch))

        # 5. 总计
        totals_data = [
            ['', 'Subtotal:', f"${float(invoice.subtotal):.2f}"],
        ]

        if float(invoice.tax) > 0:
            totals_data.append(['', 'Tax:', f"${float(invoice.tax):.2f}"])

        if float(invoice.discount) > 0:
            totals_data.append(['', 'Discount:', f"-${float(invoice.discount):.2f}"])

        totals_data.append(['', 'Total:', f"${float(invoice.total):.2f}"])

        if float(invoice.amount_paid) > 0:
            totals_data.append(['', 'Amount Paid:', f"${float(invoice.amount_paid):.2f}"])
            totals_data.append(['', 'Amount Due:', f"${float(invoice.amount_due):.2f}"])

        totals_table = Table(totals_data, colWidths=[3.3*inch, 2*inch, 1.4*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#6b7280')),
            ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#1f2937')),
            ('FONTNAME', (1, 0), (1, -3), 'Helvetica'),
            ('FONTNAME', (2, 0), (2, -3), 'Helvetica'),
            ('FONTSIZE', (1, 0), (2, -3), 10),

            # 总计行加粗
            ('FONTNAME', (1, -3), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (1, -3), (-1, -1), 12),
            ('LINEABOVE', (1, -3), (-1, -3), 2, colors.HexColor('#d1d5db')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(totals_table)
        elements.append(Spacer(1, 0.5*inch))

        # 6. 付款说明
        if invoice.status.value != 'paid':
            elements.append(Paragraph('Payment Information:', heading_style))
            payment_info = Paragraph(
                'Please make payment by the due date. '
                'Thank you for your business!',
                normal_style
            )
            elements.append(payment_info)
            elements.append(Spacer(1, 0.3*inch))

        # 7. 页脚
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#9ca3af'),
            alignment=TA_CENTER,
        )

        footer_text = f'''
        <br/><br/>
        <b>VideoSite Inc.</b><br/>
        Thank you for your business!<br/>
        For questions, contact support@videosite.com
        '''

        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph(footer_text, footer_style))

        # 构建PDF
        doc.build(elements)

        # 重置buffer指针
        buffer.seek(0)

        return buffer

    @staticmethod
    def save_invoice_pdf(invoice: Invoice, user: User, filepath: str) -> str:
        """
        保存发票PDF到文件

        Args:
            invoice: 发票对象
            user: 用户对象
            filepath: 文件路径

        Returns:
            str: 文件路径
        """
        pdf_buffer = PDFGenerator.generate_invoice_pdf(invoice, user)

        with open(filepath, 'wb') as f:
            f.write(pdf_buffer.read())

        return filepath
