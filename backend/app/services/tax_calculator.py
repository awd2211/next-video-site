"""
税收计算服务

根据用户地区计算销售税
"""

from decimal import Decimal
from typing import Dict, Optional
from enum import Enum


class TaxRegion(str, Enum):
    """税收地区"""
    US = "US"  # 美国
    EU = "EU"  # 欧盟
    CA = "CA"  # 加拿大
    GB = "GB"  # 英国
    AU = "AU"  # 澳大利亚
    CN = "CN"  # 中国
    OTHER = "OTHER"  # 其他地区


# 美国各州税率（示例 - 实际应从数据库或API获取）
US_STATE_TAX_RATES = {
    "CA": Decimal("0.0725"),  # California
    "NY": Decimal("0.0400"),  # New York
    "TX": Decimal("0.0625"),  # Texas
    "FL": Decimal("0.0600"),  # Florida
    "IL": Decimal("0.0625"),  # Illinois
    "WA": Decimal("0.0650"),  # Washington
    "MA": Decimal("0.0625"),  # Massachusetts
    # 其他州...
}

# 欧盟国家VAT税率（示例）
EU_VAT_RATES = {
    "DE": Decimal("0.19"),  # Germany
    "FR": Decimal("0.20"),  # France
    "IT": Decimal("0.22"),  # Italy
    "ES": Decimal("0.21"),  # Spain
    "NL": Decimal("0.21"),  # Netherlands
    "BE": Decimal("0.21"),  # Belgium
    "IE": Decimal("0.23"),  # Ireland
    "AT": Decimal("0.20"),  # Austria
    # 其他国家...
}

# 其他国家税率
OTHER_TAX_RATES = {
    "CA": Decimal("0.05"),   # Canada GST (simplified)
    "GB": Decimal("0.20"),   # UK VAT
    "AU": Decimal("0.10"),   # Australia GST
    "CN": Decimal("0.06"),   # China VAT (simplified)
}


class TaxCalculator:
    """税收计算器"""

    @staticmethod
    def calculate_tax(
        amount: Decimal,
        country_code: str,
        state_code: Optional[str] = None,
        tax_exempt: bool = False,
    ) -> Dict[str, any]:
        """
        计算税额

        Args:
            amount: 税前金额
            country_code: 国家代码 (ISO 3166-1 alpha-2)
            state_code: 州/省代码 (用于美国、加拿大等)
            tax_exempt: 是否免税

        Returns:
            dict: {
                'tax_rate': Decimal,  # 税率
                'tax_amount': Decimal,  # 税额
                'total_amount': Decimal,  # 含税总额
                'tax_name': str,  # 税种名称
                'is_inclusive': bool,  # 是否为含税价
            }
        """
        if tax_exempt:
            return {
                'tax_rate': Decimal("0"),
                'tax_amount': Decimal("0"),
                'total_amount': amount,
                'tax_name': 'Tax Exempt',
                'is_inclusive': False,
            }

        country_code = country_code.upper()
        tax_rate = Decimal("0")
        tax_name = "Tax"
        is_inclusive = False

        # 美国
        if country_code == "US":
            if state_code and state_code.upper() in US_STATE_TAX_RATES:
                tax_rate = US_STATE_TAX_RATES[state_code.upper()]
                tax_name = f"Sales Tax ({state_code.upper()})"
            else:
                tax_rate = Decimal("0")  # 无州代码或未知州，不征税
                tax_name = "No Tax"

        # 欧盟
        elif country_code in EU_VAT_RATES:
            tax_rate = EU_VAT_RATES[country_code]
            tax_name = f"VAT ({country_code})"
            is_inclusive = True  # 欧盟通常显示含税价

        # 其他国家
        elif country_code in OTHER_TAX_RATES:
            tax_rate = OTHER_TAX_RATES[country_code]

            if country_code == "CA":
                tax_name = "GST"
            elif country_code == "GB":
                tax_name = "VAT"
                is_inclusive = True
            elif country_code == "AU":
                tax_name = "GST"
                is_inclusive = True
            elif country_code == "CN":
                tax_name = "VAT"
                is_inclusive = True
            else:
                tax_name = "Tax"

        # 计算税额
        if is_inclusive:
            # 含税价：从总额中提取税额
            # 例如：总额 = 100, 税率 = 20%, 则 税前 = 100/1.2 = 83.33, 税额 = 16.67
            tax_amount = amount - (amount / (1 + tax_rate))
            total_amount = amount
        else:
            # 不含税价：在金额上加税
            tax_amount = amount * tax_rate
            total_amount = amount + tax_amount

        return {
            'tax_rate': tax_rate,
            'tax_amount': tax_amount.quantize(Decimal("0.01")),
            'total_amount': total_amount.quantize(Decimal("0.01")),
            'tax_name': tax_name,
            'is_inclusive': is_inclusive,
        }

    @staticmethod
    def get_tax_info(country_code: str, state_code: Optional[str] = None) -> Dict[str, any]:
        """
        获取税收信息（不计算金额）

        Args:
            country_code: 国家代码
            state_code: 州/省代码

        Returns:
            dict: {
                'tax_rate': Decimal,
                'tax_name': str,
                'is_inclusive': bool,
            }
        """
        result = TaxCalculator.calculate_tax(
            amount=Decimal("100"),
            country_code=country_code,
            state_code=state_code
        )

        return {
            'tax_rate': result['tax_rate'],
            'tax_name': result['tax_name'],
            'is_inclusive': result['is_inclusive'],
        }

    @staticmethod
    def is_tax_applicable(country_code: str) -> bool:
        """
        检查是否适用税收

        Args:
            country_code: 国家代码

        Returns:
            bool: 是否需要征税
        """
        country_code = country_code.upper()
        return (
            country_code == "US" or
            country_code in EU_VAT_RATES or
            country_code in OTHER_TAX_RATES
        )

    @staticmethod
    def calculate_reverse_tax(
        total_amount: Decimal,
        country_code: str,
        state_code: Optional[str] = None,
    ) -> Dict[str, any]:
        """
        反向计算（从含税总额计算税前金额）

        Args:
            total_amount: 含税总额
            country_code: 国家代码
            state_code: 州/省代码

        Returns:
            dict: {
                'subtotal': Decimal,  # 税前金额
                'tax_amount': Decimal,  # 税额
                'tax_rate': Decimal,  # 税率
            }
        """
        tax_info = TaxCalculator.get_tax_info(country_code, state_code)
        tax_rate = tax_info['tax_rate']

        if tax_info['is_inclusive']:
            # 含税价
            subtotal = total_amount / (1 + tax_rate)
        else:
            # 不含税价
            subtotal = total_amount / (1 + tax_rate)

        tax_amount = total_amount - subtotal

        return {
            'subtotal': subtotal.quantize(Decimal("0.01")),
            'tax_amount': tax_amount.quantize(Decimal("0.01")),
            'tax_rate': tax_rate,
        }


# 便捷函数
def calculate_sales_tax(
    amount: Decimal,
    country: str,
    state: Optional[str] = None
) -> Decimal:
    """
    计算销售税（简化版）

    Returns:
        Decimal: 税额
    """
    result = TaxCalculator.calculate_tax(amount, country, state)
    return result['tax_amount']


def get_total_with_tax(
    amount: Decimal,
    country: str,
    state: Optional[str] = None
) -> Decimal:
    """
    获取含税总额（简化版）

    Returns:
        Decimal: 含税总额
    """
    result = TaxCalculator.calculate_tax(amount, country, state)
    return result['total_amount']
