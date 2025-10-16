"""
测试 Utils - Validators (数据验证器)
测试所有 Pydantic 验证器和工具函数
"""
import pytest

from app.utils.validators import (
    validate_safe_url,
    validate_text_length,
    validate_html_safe,
    validate_no_control_chars,
    validate_ip_address,
    validate_hex_color,
)


# ===========================================
# 1. validate_safe_url 测试
# ===========================================

class TestValidateSafeUrl:
    """测试安全 URL 验证"""

    def test_validate_safe_url_valid_http(self):
        """测试有效的 HTTP URL"""
        url = "http://example.com/path"
        result = validate_safe_url(url)
        assert result == url

    def test_validate_safe_url_valid_https(self):
        """测试有效的 HTTPS URL"""
        url = "https://example.com/path?query=value"
        result = validate_safe_url(url)
        assert result == url

    def test_validate_safe_url_none(self):
        """测试 None 值"""
        result = validate_safe_url(None)
        assert result is None

    def test_validate_safe_url_empty_string(self):
        """测试空字符串"""
        result = validate_safe_url("")
        assert result is None

    def test_validate_safe_url_whitespace(self):
        """测试纯空白字符串"""
        result = validate_safe_url("   ")
        assert result is None

    def test_validate_safe_url_invalid_scheme(self):
        """测试无效的协议"""
        with pytest.raises(ValueError) as exc_info:
            validate_safe_url("ftp://example.com")
        assert "Invalid or unsafe URL" in str(exc_info.value)

    def test_validate_safe_url_no_scheme(self):
        """测试没有协议的 URL"""
        with pytest.raises(ValueError) as exc_info:
            validate_safe_url("example.com")
        assert "Invalid or unsafe URL" in str(exc_info.value)

    def test_validate_safe_url_private_ip(self):
        """测试私有 IP 地址"""
        with pytest.raises(ValueError) as exc_info:
            validate_safe_url("http://192.168.1.1")
        assert "Invalid or unsafe URL" in str(exc_info.value)

    def test_validate_safe_url_localhost(self):
        """测试 localhost"""
        with pytest.raises(ValueError) as exc_info:
            validate_safe_url("http://localhost:8000")
        assert "Invalid or unsafe URL" in str(exc_info.value)

    def test_validate_safe_url_loopback(self):
        """测试 127.0.0.1"""
        with pytest.raises(ValueError) as exc_info:
            validate_safe_url("http://127.0.0.1")
        assert "Invalid or unsafe URL" in str(exc_info.value)


# ===========================================
# 2. validate_text_length 测试
# ===========================================

class TestValidateTextLength:
    """测试文本长度验证"""

    def test_validate_text_length_within_limit(self):
        """测试在长度限制内"""
        text = "Hello World"
        result = validate_text_length(text, max_length=100)
        assert result == text

    def test_validate_text_length_exact_limit(self):
        """测试正好等于长度限制"""
        text = "A" * 50
        result = validate_text_length(text, max_length=50)
        assert result == text

    def test_validate_text_length_exceed_limit(self):
        """测试超过长度限制"""
        text = "A" * 101
        with pytest.raises(ValueError) as exc_info:
            validate_text_length(text, max_length=100)
        assert "cannot exceed 100 characters" in str(exc_info.value)

    def test_validate_text_length_custom_field_name(self):
        """测试自定义字段名"""
        text = "A" * 101
        with pytest.raises(ValueError) as exc_info:
            validate_text_length(text, max_length=100, field_name="Comment")
        assert "Comment cannot exceed 100 characters" in str(exc_info.value)

    def test_validate_text_length_none(self):
        """测试 None 值"""
        result = validate_text_length(None, max_length=100)
        assert result is None

    def test_validate_text_length_empty_string(self):
        """测试空字符串"""
        result = validate_text_length("", max_length=100)
        assert result == ""

    def test_validate_text_length_unicode(self):
        """测试 Unicode 字符"""
        text = "你好世界" * 30  # 120 个字符
        with pytest.raises(ValueError):
            validate_text_length(text, max_length=100)


# ===========================================
# 3. validate_html_safe 测试
# ===========================================

class TestValidateHtmlSafe:
    """测试 HTML 安全验证"""

    def test_validate_html_safe_plain_text(self):
        """测试纯文本"""
        text = "This is plain text"
        result = validate_html_safe(text)
        assert result == text

    def test_validate_html_safe_safe_html(self):
        """测试安全的 HTML（基本标签）"""
        text = "<p>Hello <b>World</b></p>"
        result = validate_html_safe(text)
        assert result == text

    def test_validate_html_safe_none(self):
        """测试 None 值"""
        result = validate_html_safe(None)
        assert result is None

    def test_validate_html_safe_script_tag(self):
        """测试 script 标签"""
        text = "Hello <script>alert('xss')</script>"
        with pytest.raises(ValueError) as exc_info:
            validate_html_safe(text)
        assert "dangerous content" in str(exc_info.value)
        assert "<script" in str(exc_info.value)

    def test_validate_html_safe_script_uppercase(self):
        """测试大写 SCRIPT 标签"""
        text = "Hello <SCRIPT>alert('xss')</SCRIPT>"
        with pytest.raises(ValueError) as exc_info:
            validate_html_safe(text)
        assert "dangerous content" in str(exc_info.value)

    def test_validate_html_safe_iframe(self):
        """测试 iframe 标签"""
        text = '<iframe src="evil.com"></iframe>'
        with pytest.raises(ValueError) as exc_info:
            validate_html_safe(text)
        assert "dangerous content" in str(exc_info.value)

    def test_validate_html_safe_javascript_protocol(self):
        """测试 javascript: 协议"""
        text = '<a href="javascript:alert()">Click</a>'
        with pytest.raises(ValueError) as exc_info:
            validate_html_safe(text)
        assert "dangerous content" in str(exc_info.value)

    def test_validate_html_safe_onerror(self):
        """测试 onerror 事件"""
        text = '<img src="x" onerror="alert()">'
        with pytest.raises(ValueError) as exc_info:
            validate_html_safe(text)
        assert "dangerous content" in str(exc_info.value)

    def test_validate_html_safe_onclick(self):
        """测试 onclick 事件"""
        text = '<button onclick="alert()">Click</button>'
        with pytest.raises(ValueError) as exc_info:
            validate_html_safe(text)
        assert "dangerous content" in str(exc_info.value)

    def test_validate_html_safe_onload(self):
        """测试 onload 事件"""
        text = '<body onload="alert()">'
        with pytest.raises(ValueError) as exc_info:
            validate_html_safe(text)
        assert "dangerous content" in str(exc_info.value)


# ===========================================
# 4. validate_no_control_chars 测试
# ===========================================

class TestValidateNoControlChars:
    """测试控制字符验证"""

    def test_validate_no_control_chars_plain_text(self):
        """测试纯文本"""
        text = "Hello World 123"
        result = validate_no_control_chars(text)
        assert result == text

    def test_validate_no_control_chars_none(self):
        """测试 None 值"""
        result = validate_no_control_chars(None)
        assert result is None

    def test_validate_no_control_chars_newline(self):
        """测试换行符（允许）"""
        text = "Line1\nLine2"
        result = validate_no_control_chars(text)
        assert result == text

    def test_validate_no_control_chars_carriage_return(self):
        """测试回车符（允许）"""
        text = "Line1\rLine2"
        result = validate_no_control_chars(text)
        assert result == text

    def test_validate_no_control_chars_tab(self):
        """测试制表符（允许）"""
        text = "Col1\tCol2"
        result = validate_no_control_chars(text)
        assert result == text

    def test_validate_no_control_chars_null(self):
        """测试 NULL 字符"""
        text = "Hello\x00World"
        with pytest.raises(ValueError) as exc_info:
            validate_no_control_chars(text)
        assert "invalid control character" in str(exc_info.value)

    def test_validate_no_control_chars_bell(self):
        """测试 BELL 字符"""
        text = "Hello\x07World"
        with pytest.raises(ValueError) as exc_info:
            validate_no_control_chars(text)
        assert "invalid control character" in str(exc_info.value)

    def test_validate_no_control_chars_escape(self):
        """测试 ESC 字符"""
        text = "Hello\x1bWorld"
        with pytest.raises(ValueError) as exc_info:
            validate_no_control_chars(text)
        assert "invalid control character" in str(exc_info.value)

    def test_validate_no_control_chars_delete(self):
        """测试 DELETE 字符（127-159 范围）"""
        text = "Hello\x7fWorld"
        with pytest.raises(ValueError) as exc_info:
            validate_no_control_chars(text)
        assert "invalid control character" in str(exc_info.value)

    def test_validate_no_control_chars_unicode(self):
        """测试 Unicode 字符（正常）"""
        text = "你好世界 🌍"
        result = validate_no_control_chars(text)
        assert result == text


# ===========================================
# 5. validate_ip_address 测试
# ===========================================

class TestValidateIpAddress:
    """测试 IP 地址验证"""

    def test_validate_ip_address_valid(self):
        """测试有效的 IP 地址"""
        ip = "192.168.1.1"
        result = validate_ip_address(ip)
        assert result == ip

    def test_validate_ip_address_valid_public(self):
        """测试公共 IP 地址"""
        ip = "8.8.8.8"
        result = validate_ip_address(ip)
        assert result == ip

    def test_validate_ip_address_valid_zero(self):
        """测试 0.0.0.0"""
        ip = "0.0.0.0"
        result = validate_ip_address(ip)
        assert result == ip

    def test_validate_ip_address_valid_255(self):
        """测试边界值 255"""
        ip = "255.255.255.255"
        result = validate_ip_address(ip)
        assert result == ip

    def test_validate_ip_address_invalid_format(self):
        """测试无效格式"""
        with pytest.raises(ValueError) as exc_info:
            validate_ip_address("192.168.1")
        assert "Invalid IP address format" in str(exc_info.value)

    def test_validate_ip_address_invalid_value(self):
        """测试数值超过 255"""
        with pytest.raises(ValueError) as exc_info:
            validate_ip_address("192.168.1.256")
        assert "Invalid IP address format" in str(exc_info.value)

    def test_validate_ip_address_invalid_chars(self):
        """测试包含非法字符"""
        with pytest.raises(ValueError) as exc_info:
            validate_ip_address("192.168.1.a")
        assert "Invalid IP address format" in str(exc_info.value)

    def test_validate_ip_address_ipv6(self):
        """测试 IPv6 格式（当前不支持）"""
        with pytest.raises(ValueError):
            validate_ip_address("2001:0db8:85a3:0000:0000:8a2e:0370:7334")

    def test_validate_ip_address_hostname(self):
        """测试域名（应该失败）"""
        with pytest.raises(ValueError):
            validate_ip_address("example.com")

    def test_validate_ip_address_localhost(self):
        """测试 localhost"""
        with pytest.raises(ValueError):
            validate_ip_address("localhost")


# ===========================================
# 6. validate_hex_color 测试
# ===========================================

class TestValidateHexColor:
    """测试十六进制颜色验证"""

    def test_validate_hex_color_valid_lowercase(self):
        """测试有效的小写颜色"""
        color = "#ffffff"
        result = validate_hex_color(color)
        assert result == "#FFFFFF"

    def test_validate_hex_color_valid_uppercase(self):
        """测试有效的大写颜色"""
        color = "#FFFFFF"
        result = validate_hex_color(color)
        assert result == "#FFFFFF"

    def test_validate_hex_color_valid_mixed(self):
        """测试混合大小写"""
        color = "#FfFfFf"
        result = validate_hex_color(color)
        assert result == "#FFFFFF"

    def test_validate_hex_color_valid_black(self):
        """测试黑色"""
        color = "#000000"
        result = validate_hex_color(color)
        assert result == "#000000"

    def test_validate_hex_color_valid_red(self):
        """测试红色"""
        color = "#ff0000"
        result = validate_hex_color(color)
        assert result == "#FF0000"

    def test_validate_hex_color_no_hash(self):
        """测试缺少 # 符号"""
        with pytest.raises(ValueError) as exc_info:
            validate_hex_color("ffffff")
        assert "hex format" in str(exc_info.value)

    def test_validate_hex_color_too_short(self):
        """测试长度不足"""
        with pytest.raises(ValueError) as exc_info:
            validate_hex_color("#fff")
        assert "hex format" in str(exc_info.value)

    def test_validate_hex_color_too_long(self):
        """测试长度过长"""
        with pytest.raises(ValueError) as exc_info:
            validate_hex_color("#fffffff")
        assert "hex format" in str(exc_info.value)

    def test_validate_hex_color_invalid_chars(self):
        """测试包含非法字符"""
        with pytest.raises(ValueError) as exc_info:
            validate_hex_color("#gggggg")
        assert "hex format" in str(exc_info.value)

    def test_validate_hex_color_rgb_format(self):
        """测试 RGB 格式（应该失败）"""
        with pytest.raises(ValueError):
            validate_hex_color("rgb(255,255,255)")

    def test_validate_hex_color_empty(self):
        """测试空字符串"""
        with pytest.raises(ValueError):
            validate_hex_color("")


# ===========================================
# 测试总结
# ===========================================

"""
测试覆盖：
✅ validate_safe_url - 10个测试用例
✅ validate_text_length - 7个测试用例
✅ validate_html_safe - 10个测试用例
✅ validate_no_control_chars - 10个测试用例
✅ validate_ip_address - 10个测试用例
✅ validate_hex_color - 11个测试用例

总计：58个测试用例

测试场景：
- URL 安全验证（HTTP/HTTPS、私有IP、localhost）
- 文本长度限制（边界值、Unicode）
- HTML 安全检查（XSS 防护）
- 控制字符过滤（允许的和禁止的）
- IP 地址格式验证（IPv4）
- 十六进制颜色验证（格式和大小写）
- None 值和空字符串处理
- 边界条件和异常情况
"""
