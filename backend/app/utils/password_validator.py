"""
密码强度验证工具
实施强密码策略，防止弱密码导致的账户被破解
"""

import re
from typing import Tuple

# 常用弱密码黑名单（部分）
COMMON_PASSWORDS = {
    "123456",
    "password",
    "12345678",
    "qwerty",
    "123456789",
    "12345",
    "1234",
    "111111",
    "1234567",
    "dragon",
    "123123",
    "baseball",
    "iloveyou",
    "trustno1",
    "1234567890",
    "superman",
    "qwertyuiop",
    "1qaz2wsx",
    "monkey",
    "shadow",
    "master",
    "666666",
    "qazwsx",
    "123qwe",
    "letmein",
    "admin",
    "admin123",
    "root",
    "toor",
    "pass",
    "password123",
    "password1",
    "welcome",
    "abc123",
    "football",
    # 中文常用弱密码
    "woaini",
    "woshishui",
    "nimabi",
    "wodemima",
    "123456a",
}


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    验证密码强度

    要求:
    - 至少8个字符
    - 至少1个大写字母
    - 至少1个小写字母
    - 至少1个数字
    - 至少1个特殊字符
    - 不在常用密码黑名单中

    Args:
        password: 待验证的密码

    Returns:
        (is_valid, message): 是否通过验证和消息
    """
    # 检查长度
    if len(password) < 8:
        return False, "密码至少需要8个字符"

    if len(password) > 128:
        return False, "密码不能超过128个字符"

    # 检查是否在弱密码黑名单中
    if password.lower() in COMMON_PASSWORDS:
        return False, "密码过于常见，请使用更复杂的密码"

    # 检查是否包含常见模式
    if re.match(r"^[0-9]+$", password):
        return False, "密码不能全是数字"

    if re.match(r"^[a-zA-Z]+$", password):
        return False, "密码不能全是字母"

    # 检查是否包含大写字母
    if not re.search(r"[A-Z]", password):
        return False, "密码需要至少1个大写字母"

    # 检查是否包含小写字母
    if not re.search(r"[a-z]", password):
        return False, "密码需要至少1个小写字母"

    # 检查是否包含数字
    if not re.search(r"\d", password):
        return False, "密码需要至少1个数字"

    # 检查是否包含特殊字符
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\\/;'`~]", password):
        return False, "密码需要至少1个特殊字符 (!@#$%^&*等)"

    # 检查是否包含过多重复字符（如 aaaa, 1111）
    if re.search(r"(.)\1{3,}", password):
        return False, "密码不应包含4个或更多连续重复字符"

    return True, "密码强度良好"


def calculate_password_strength(password: str) -> int:
    """
    计算密码强度分数（0-100）

    Args:
        password: 密码

    Returns:
        强度分数 (0-100)
    """
    score = 0

    # 长度分数（最多30分）
    if len(password) >= 8:
        score += 10
    if len(password) >= 12:
        score += 10
    if len(password) >= 16:
        score += 10

    # 字符类型分数（每种10分，最多40分）
    if re.search(r"[a-z]", password):
        score += 10
    if re.search(r"[A-Z]", password):
        score += 10
    if re.search(r"\d", password):
        score += 10
    if re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\\/;'`~]", password):
        score += 10

    # 复杂度分数（最多30分）
    unique_chars = len(set(password))
    if unique_chars >= 5:
        score += 10
    if unique_chars >= 8:
        score += 10
    if unique_chars >= 12:
        score += 10

    # 扣分项
    if password.lower() in COMMON_PASSWORDS:
        score -= 50
    if re.match(r"^[0-9]+$", password):
        score -= 30
    if re.search(r"(.)\1{2,}", password):
        score -= 20

    return max(0, min(100, score))


def get_password_strength_label(score: int) -> str:
    """
    根据分数返回强度标签

    Args:
        score: 密码强度分数

    Returns:
        强度标签
    """
    if score < 30:
        return "弱"
    elif score < 60:
        return "中等"
    elif score < 80:
        return "强"
    else:
        return "非常强"


# 用于Pydantic validator的便捷函数
def validate_password_field(password: str) -> str:
    """
    Pydantic field validator

    Args:
        password: 密码

    Returns:
        验证通过的密码

    Raises:
        ValueError: 如果密码不符合要求
    """
    is_valid, message = validate_password_strength(password)
    if not is_valid:
        raise ValueError(message)
    return password
