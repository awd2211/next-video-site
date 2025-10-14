"""
测试验证工具函数
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
from app.utils.password_validator import (
    validate_password_strength,
    calculate_password_strength,
    validate_password_field,
)
from app.utils.file_validator import sanitize_filename, get_file_extension
from app.utils.path_validator import is_safe_url, validate_video_id


class TestValidateSafeUrl:
    """测试URL安全验证"""

    def test_valid_http_url(self):
        """测试有效的HTTP URL"""
        url = "http://example.com/video.mp4"
        assert validate_safe_url(url) == url

    def test_valid_https_url(self):
        """测试有效的HTTPS URL"""
        url = "https://example.com/image.jpg"
        assert validate_safe_url(url) == url

    def test_none_value(self):
        """测试None值"""
        assert validate_safe_url(None) is None

    def test_empty_string(self):
        """测试空字符串"""
        assert validate_safe_url("") is None

    def test_invalid_protocol(self):
        """测试无效协议"""
        with pytest.raises(ValueError, match="Invalid or unsafe URL"):
            validate_safe_url("ftp://example.com")

    def test_localhost_blocked(self):
        """测试localhost被阻止"""
        with pytest.raises(ValueError):
            validate_safe_url("http://localhost/file")

    def test_private_ip_blocked(self):
        """测试私有IP被阻止"""
        with pytest.raises(ValueError):
            validate_safe_url("http://192.168.1.1/file")
        with pytest.raises(ValueError):
            validate_safe_url("http://10.0.0.1/file")


class TestValidateTextLength:
    """测试文本长度验证"""

    def test_valid_length(self):
        """测试有效长度"""
        text = "Hello World"
        assert validate_text_length(text, 20) == text

    def test_exact_max_length(self):
        """测试正好达到最大长度"""
        text = "x" * 100
        assert validate_text_length(text, 100) == text

    def test_exceeds_max_length(self):
        """测试超过最大长度"""
        text = "x" * 101
        with pytest.raises(ValueError, match="cannot exceed 100 characters"):
            validate_text_length(text, 100)

    def test_none_value(self):
        """测试None值"""
        assert validate_text_length(None, 100) is None


class TestValidateHtmlSafe:
    """测试HTML安全验证"""

    def test_safe_text(self):
        """测试安全文本"""
        text = "Hello <b>World</b>"
        # 目前只检测危险标签，不清理安全标签
        assert validate_html_safe(text) == text

    def test_script_tag_rejected(self):
        """测试script标签被拒绝"""
        text = "Hello <script>alert(1)</script>"
        with pytest.raises(ValueError, match="dangerous content"):
            validate_html_safe(text)

    def test_javascript_protocol_rejected(self):
        """测试javascript:协议被拒绝"""
        text = '<a href="javascript:alert(1)">Click</a>'
        with pytest.raises(ValueError, match="dangerous content"):
            validate_html_safe(text)

    def test_event_handler_rejected(self):
        """测试事件处理器被拒绝"""
        text = '<img src="x" onerror="alert(1)">'
        with pytest.raises(ValueError, match="dangerous content"):
            validate_html_safe(text)


class TestValidateNoControlChars:
    """测试控制字符验证"""

    def test_normal_text(self):
        """测试正常文本"""
        text = "Hello\nWorld\t!"
        assert validate_no_control_chars(text) == text

    def test_null_byte_rejected(self):
        """测试空字节被拒绝"""
        text = "Hello\x00World"
        with pytest.raises(ValueError, match="control character"):
            validate_no_control_chars(text)

    def test_other_control_char_rejected(self):
        """测试其他控制字符被拒绝"""
        text = "Hello\x1FWorld"
        with pytest.raises(ValueError, match="control character"):
            validate_no_control_chars(text)


class TestValidateIpAddress:
    """测试IP地址验证"""

    def test_valid_ipv4(self):
        """测试有效IPv4地址"""
        assert validate_ip_address("192.168.1.1") == "192.168.1.1"
        assert validate_ip_address("10.0.0.1") == "10.0.0.1"
        assert validate_ip_address("127.0.0.1") == "127.0.0.1"

    def test_invalid_format(self):
        """测试无效格式"""
        with pytest.raises(ValueError, match="Invalid IP address"):
            validate_ip_address("192.168.1")
        with pytest.raises(ValueError):
            validate_ip_address("not.an.ip.address")

    def test_out_of_range(self):
        """测试超出范围"""
        with pytest.raises(ValueError):
            validate_ip_address("256.1.1.1")


class TestValidateHexColor:
    """测试十六进制颜色验证"""

    def test_valid_color(self):
        """测试有效颜色"""
        assert validate_hex_color("#FFFFFF") == "#FFFFFF"
        assert validate_hex_color("#000000") == "#000000"
        assert validate_hex_color("#ff0000") == "#FF0000"  # 转大写

    def test_invalid_format(self):
        """测试无效格式"""
        with pytest.raises(ValueError, match="hex format"):
            validate_hex_color("FFFFFF")  # 缺少#
        with pytest.raises(ValueError):
            validate_hex_color("#FFF")  # 太短
        with pytest.raises(ValueError):
            validate_hex_color("#GGGGGG")  # 无效字符


class TestPasswordValidator:
    """测试密码验证器"""

    def test_strong_password(self):
        """测试强密码"""
        is_valid, msg = validate_password_strength("Strong@Pass123")
        assert is_valid is True

    def test_password_too_short(self):
        """测试密码太短"""
        is_valid, msg = validate_password_strength("Aa1!")
        assert is_valid is False
        assert "8个字符" in msg

    def test_password_no_uppercase(self):
        """测试缺少大写字母"""
        is_valid, msg = validate_password_strength("password123!")
        assert is_valid is False
        assert "大写字母" in msg

    def test_password_no_lowercase(self):
        """测试缺少小写字母"""
        is_valid, msg = validate_password_strength("PASSWORD123!")
        assert is_valid is False
        assert "小写字母" in msg

    def test_password_no_number(self):
        """测试缺少数字"""
        is_valid, msg = validate_password_strength("Password!")
        assert is_valid is False
        assert "数字" in msg

    def test_password_no_special(self):
        """测试缺少特殊字符"""
        is_valid, msg = validate_password_strength("MyPass123")  # 避免使用常见密码
        assert is_valid is False
        assert "特殊字符" in msg or "常见" in msg  # 可能触发其他规则

    def test_common_password(self):
        """测试常见弱密码"""
        is_valid, msg = validate_password_strength("password123")
        assert is_valid is False
        assert "常见" in msg

    def test_repeated_chars(self):
        """测试重复字符"""
        is_valid, msg = validate_password_strength("Aaaa1111!")
        assert is_valid is False
        assert "重复字符" in msg

    def test_calculate_strength(self):
        """测试密码强度计算"""
        assert calculate_password_strength("") == 0
        assert calculate_password_strength("weak") < 40
        assert calculate_password_strength("Medium1!") >= 40
        assert calculate_password_strength("Strong@Pass123") >= 60

    def test_validate_password_field_success(self):
        """测试Pydantic validator成功"""
        password = "Strong@Pass123"
        assert validate_password_field(password) == password

    def test_validate_password_field_failure(self):
        """测试Pydantic validator失败"""
        with pytest.raises(ValueError):
            validate_password_field("weak")


class TestPathValidator:
    """测试路径验证器"""

    def test_safe_url_https(self):
        """测试安全HTTPS URL"""
        assert is_safe_url("https://example.com") is True

    def test_safe_url_http(self):
        """测试安全HTTP URL"""
        assert is_safe_url("http://example.com/path") is True

    def test_unsafe_protocol(self):
        """测试不安全协议"""
        assert is_safe_url("ftp://example.com") is False
        assert is_safe_url("file:///etc/passwd") is False

    def test_localhost_blocked(self):
        """测试localhost被阻止"""
        assert is_safe_url("http://localhost") is False
        assert is_safe_url("http://127.0.0.1") is False

    def test_private_ip_blocked(self):
        """测试私有IP被阻止"""
        assert is_safe_url("http://192.168.1.1") is False
        assert is_safe_url("http://10.0.0.1") is False
        assert is_safe_url("http://172.16.0.1") is False

    def test_validate_video_id_valid(self):
        """测试有效视频ID"""
        assert validate_video_id(123) == 123
        assert validate_video_id("456") == 456

    def test_validate_video_id_invalid(self):
        """测试无效视频ID"""
        with pytest.raises(ValueError):
            validate_video_id(0)
        with pytest.raises(ValueError):
            validate_video_id(-1)
        with pytest.raises(ValueError):
            validate_video_id("invalid")


class TestFileValidator:
    """测试文件验证器"""

    def test_sanitize_filename_removes_slashes(self):
        """测试移除斜杠"""
        assert "/" not in sanitize_filename("test/file.txt")
        assert "\\" not in sanitize_filename("test\\file.txt")

    def test_sanitize_filename_removes_special_chars(self):
        """测试移除特殊字符"""
        filename = "test<file>.txt"
        result = sanitize_filename(filename)
        assert "<" not in result
        assert ">" not in result

    def test_sanitize_filename_limits_length(self):
        """测试限制长度"""
        long_name = "a" * 300 + ".txt"
        result = sanitize_filename(long_name)
        assert len(result) <= 255

    def test_get_file_extension(self):
        """测试获取文件扩展名"""
        assert get_file_extension("test.jpg") == ".jpg"
        assert get_file_extension("document.pdf") == ".pdf"
        assert get_file_extension("noext") == ""

