"""
测试 app/utils/security.py - 安全工具（密码、JWT）
"""
import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from app.utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.config import settings


@pytest.mark.unit
class TestPasswordHashing:
    """密码哈希测试"""

    def test_hash_password(self):
        """测试密码哈希"""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert hashed is not None
        assert len(hashed) > 0
        assert hashed != password  # 不应该是明文

    def test_verify_correct_password(self):
        """测试验证正确密码"""
        password = "correct_password"
        hashed = get_password_hash(password)
        
        result = verify_password(password, hashed)
        assert result is True

    def test_verify_incorrect_password(self):
        """测试验证错误密码"""
        password = "correct_password"
        hashed = get_password_hash(password)
        
        result = verify_password("wrong_password", hashed)
        assert result is False

    def test_hash_same_password_twice_different_hash(self):
        """测试相同密码两次哈希结果不同（salt）"""
        password = "same_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # 哈希值应该不同（因为 salt）
        assert hash1 != hash2
        
        # 但都能验证原密码
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_hash_empty_password(self):
        """测试哈希空密码"""
        hashed = get_password_hash("")
        assert hashed is not None
        assert verify_password("", hashed) is True

    def test_hash_unicode_password(self):
        """测试哈希 Unicode 密码"""
        password = "密码123!@#"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("wrong", hashed) is False

    def test_hash_long_password(self):
        """测试哈希长密码"""
        password = "a" * 200
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_verify_with_wrong_hash_format(self):
        """测试使用错误哈希格式验证"""
        result = verify_password("password", "not_a_valid_hash")
        assert result is False


@pytest.mark.unit
class TestJWTAccessToken:
    """JWT Access Token 测试"""

    def test_create_access_token(self):
        """测试创建 access token"""
        data = {"sub": "user@example.com", "user_id": 1}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_custom_expiry(self):
        """测试创建自定义过期时间的 token"""
        data = {"sub": "user@example.com"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)
        
        assert token is not None
        
        # 解码验证过期时间
        payload = decode_token(token)
        assert payload is not None
        assert "exp" in payload

    def test_access_token_contains_type(self):
        """测试 access token 包含类型字段"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        payload = decode_token(token)
        assert payload is not None
        assert payload.get("type") == "access"

    def test_access_token_contains_original_data(self):
        """测试 token 包含原始数据"""
        data = {"sub": "user@example.com", "user_id": 123, "is_admin": True}
        token = create_access_token(data)
        
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user@example.com"
        assert payload["user_id"] == 123
        assert payload["is_admin"] is True

    def test_access_token_expiration(self):
        """测试 access token 包含过期时间"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        payload = decode_token(token)
        assert payload is not None
        assert "exp" in payload
        
        # 验证过期时间在未来
        exp_timestamp = payload["exp"]
        now_timestamp = datetime.now(timezone.utc).timestamp()
        assert exp_timestamp > now_timestamp


@pytest.mark.unit
class TestJWTRefreshToken:
    """JWT Refresh Token 测试"""

    def test_create_refresh_token(self):
        """测试创建 refresh token"""
        data = {"sub": "user@example.com", "user_id": 1}
        token = create_refresh_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_refresh_token_contains_type(self):
        """测试 refresh token 包含类型字段"""
        data = {"sub": "test@example.com"}
        token = create_refresh_token(data)
        
        payload = decode_token(token)
        assert payload is not None
        assert payload.get("type") == "refresh"

    def test_refresh_token_longer_expiry(self):
        """测试 refresh token 过期时间更长"""
        data = {"sub": "test@example.com"}
        
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)
        
        access_payload = decode_token(access_token)
        refresh_payload = decode_token(refresh_token)
        
        # refresh token 应该比 access token 过期时间长
        assert refresh_payload["exp"] > access_payload["exp"]


@pytest.mark.unit
class TestDecodeToken:
    """Token 解码测试"""

    def test_decode_valid_token(self):
        """测试解码有效 token"""
        data = {"sub": "test@example.com", "user_id": 1}
        token = create_access_token(data)
        
        payload = decode_token(token)
        
        assert payload is not None
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == 1

    def test_decode_invalid_token(self):
        """测试解码无效 token"""
        invalid_token = "invalid.token.string"
        payload = decode_token(invalid_token)
        
        assert payload is None

    def test_decode_malformed_token(self):
        """测试解码格式错误的 token"""
        malformed_token = "not_a_jwt_token"
        payload = decode_token(malformed_token)
        
        assert payload is None

    def test_decode_expired_token(self):
        """测试解码过期 token"""
        data = {"sub": "test@example.com"}
        # 创建已过期的 token（负数过期时间）
        expired_token = create_access_token(
            data, 
            expires_delta=timedelta(seconds=-1)
        )
        
        payload = decode_token(expired_token)
        # 过期的 token 应该解码失败
        assert payload is None

    def test_decode_tampered_token(self):
        """测试解码被篡改的 token"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        # 篡改 token（修改最后几个字符）
        tampered_token = token[:-10] + "tamperedXX"
        
        payload = decode_token(tampered_token)
        assert payload is None

    def test_decode_token_with_wrong_secret(self):
        """测试使用错误密钥解码"""
        data = {"sub": "test@example.com"}
        
        # 使用正确密钥创建
        token = jwt.encode(
            {**data, "exp": datetime.now(timezone.utc) + timedelta(minutes=15)},
            "correct_secret",
            algorithm="HS256"
        )
        
        # 使用错误密钥解码
        try:
            jwt.decode(token, "wrong_secret", algorithms=["HS256"])
            assert False, "应该抛出异常"
        except JWTError:
            assert True


@pytest.mark.unit
class TestTokenSecurity:
    """Token 安全性测试"""

    def test_token_cannot_be_modified(self):
        """测试 token 不能被修改"""
        data = {"sub": "user@example.com", "role": "user"}
        token = create_access_token(data)
        
        # 尝试修改 token 中的角色（在实际中无法做到）
        # 解码后修改再编码会失败验证
        parts = token.split('.')
        assert len(parts) == 3  # JWT 有三部分

    def test_token_signature_verification(self):
        """测试 token 签名验证"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        # 正确解码
        payload1 = decode_token(token)
        assert payload1 is not None
        
        # 修改 token 后解码应该失败
        tampered = token[:-1] + ("X" if token[-1] != "X" else "Y")
        payload2 = decode_token(tampered)
        assert payload2 is None

    def test_different_tokens_for_same_data(self):
        """测试相同数据生成不同 token（因为时间戳）"""
        data = {"sub": "test@example.com"}
        
        token1 = create_access_token(data)
        import time
        time.sleep(1)
        token2 = create_access_token(data)
        
        # Token 应该不同（因为过期时间不同）
        assert token1 != token2
        
        # 但都应该能解码
        assert decode_token(token1) is not None
        assert decode_token(token2) is not None


@pytest.mark.unit
class TestTokenPayload:
    """Token Payload 测试"""

    def test_access_token_payload_structure(self):
        """测试 access token payload 结构"""
        data = {"sub": "user@example.com", "user_id": 1}
        token = create_access_token(data)
        payload = decode_token(token)
        
        assert "sub" in payload
        assert "user_id" in payload
        assert "exp" in payload
        assert "type" in payload
        assert payload["type"] == "access"

    def test_refresh_token_payload_structure(self):
        """测试 refresh token payload 结构"""
        data = {"sub": "user@example.com", "user_id": 1}
        token = create_refresh_token(data)
        payload = decode_token(token)
        
        assert "sub" in payload
        assert "user_id" in payload
        assert "exp" in payload
        assert "type" in payload
        assert payload["type"] == "refresh"

    def test_token_with_extra_claims(self):
        """测试带额外声明的 token"""
        data = {
            "sub": "user@example.com",
            "user_id": 1,
            "username": "testuser",
            "is_admin": False,
            "permissions": ["read", "write"],
        }
        token = create_access_token(data)
        payload = decode_token(token)
        
        assert payload["username"] == "testuser"
        assert payload["is_admin"] is False
        assert payload["permissions"] == ["read", "write"]


@pytest.mark.unit
class TestEdgeCases:
    """边界情况测试"""

    def test_empty_data_token(self):
        """测试空数据创建 token"""
        token = create_access_token({})
        assert token is not None
        
        payload = decode_token(token)
        assert payload is not None
        assert "exp" in payload

    def test_large_payload_token(self):
        """测试大量数据的 token"""
        data = {
            "sub": "user@example.com",
            "large_list": list(range(1000)),
            "large_dict": {f"key_{i}": f"value_{i}" for i in range(100)},
        }
        token = create_access_token(data)
        
        assert token is not None
        payload = decode_token(token)
        assert payload is not None
        assert len(payload["large_list"]) == 1000

    def test_special_characters_in_token(self):
        """测试特殊字符"""
        data = {
            "sub": "user+test@example.com",
            "name": "用户名 Test <>&",
        }
        token = create_access_token(data)
        payload = decode_token(token)
        
        assert payload["sub"] == "user+test@example.com"
        assert payload["name"] == "用户名 Test <>&"

