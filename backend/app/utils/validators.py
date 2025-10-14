"""
通用的Pydantic validators
可在多个schema中复用
"""

from typing import Optional

from app.utils.path_validator import is_safe_url


def validate_safe_url(v: Optional[str]) -> Optional[str]:
    """
    验证URL是否安全
    
    用于Pydantic field_validator
    
    Args:
        v: URL字符串
        
    Returns:
        验证通过的URL
        
    Raises:
        ValueError: 如果URL不安全
    """
    if v is None:
        return v
        
    if not v.strip():
        return None
        
    if not is_safe_url(v):
        raise ValueError(
            "Invalid or unsafe URL. Must start with http:// or https:// "
            "and cannot point to internal/private IP addresses"
        )
    
    return v


def validate_text_length(
    v: Optional[str], max_length: int, field_name: str = "Text"
) -> Optional[str]:
    """
    验证文本长度
    
    Args:
        v: 文本内容
        max_length: 最大长度
        field_name: 字段名（用于错误消息）
        
    Returns:
        验证通过的文本
        
    Raises:
        ValueError: 如果超过长度限制
    """
    if v is None:
        return v
        
    if len(v) > max_length:
        raise ValueError(f"{field_name} cannot exceed {max_length} characters")
    
    return v


def validate_html_safe(v: Optional[str]) -> Optional[str]:
    """
    验证文本不包含危险的HTML标签
    
    Args:
        v: 文本内容
        
    Returns:
        验证通过的文本
        
    Raises:
        ValueError: 如果包含危险标签
    """
    if v is None:
        return v
        
    # 检查危险的HTML标签
    dangerous_tags = [
        "<script",
        "</script",
        "<iframe",
        "</iframe",
        "javascript:",
        "onerror=",
        "onclick=",
        "onload=",
    ]
    
    v_lower = v.lower()
    for tag in dangerous_tags:
        if tag in v_lower:
            raise ValueError(f"Text contains dangerous content: {tag}")
    
    return v


def validate_no_control_chars(v: Optional[str]) -> Optional[str]:
    """
    验证文本不包含控制字符
    
    Args:
        v: 文本内容
        
    Returns:
        验证通过的文本
        
    Raises:
        ValueError: 如果包含控制字符
    """
    if v is None:
        return v
        
    # 检查控制字符（除了常见的\n \r \t）
    for char in v:
        code = ord(char)
        # 允许 \t(9) \n(10) \r(13)
        if code < 32 and code not in (9, 10, 13):
            raise ValueError(f"Text contains invalid control character (code: {code})")
        # 检查其他控制字符范围
        if 127 <= code <= 159:
            raise ValueError(f"Text contains invalid control character (code: {code})")
    
    return v


def validate_ip_address(v: str) -> str:
    """
    验证IP地址格式
    
    Args:
        v: IP地址字符串
        
    Returns:
        验证通过的IP地址
        
    Raises:
        ValueError: 如果格式不正确
    """
    import re
    
    # 检查IPv4格式
    ipv4_pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    
    if not re.match(ipv4_pattern, v):
        raise ValueError("Invalid IP address format")
    
    return v


def validate_hex_color(v: str) -> str:
    """
    验证十六进制颜色格式
    
    Args:
        v: 颜色字符串
        
    Returns:
        验证通过的颜色（大写）
        
    Raises:
        ValueError: 如果格式不正确
    """
    import re
    
    if not re.match(r"^#[0-9A-Fa-f]{6}$", v):
        raise ValueError("Color must be in hex format (e.g., #FFFFFF)")
    
    return v.upper()

