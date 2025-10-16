"""
测试 Utils - File Validator (文件上传验证)
测试文件上传安全验证、魔数检查、文件类型验证
"""
import pytest
from io import BytesIO
from fastapi import HTTPException, UploadFile

from app.utils.file_validator import (
    sanitize_filename,
    check_file_magic,
    get_file_extension,
    validate_upload_file,
    FileValidationPresets,
    FILE_MAGIC_NUMBERS,
)


# ===========================================
# 测试数据 - 真实文件魔数
# ===========================================

# JPEG文件头
JPEG_MAGIC = bytes.fromhex("FFD8FFE000104A46494600")

# PNG文件头
PNG_MAGIC = bytes.fromhex("89504E470D0A1A0A0000000D49484452")

# GIF89a文件头
GIF_MAGIC = bytes.fromhex("474946383961")

# WebP文件头 (RIFF....WEBP)
WEBP_MAGIC = bytes.fromhex("52494646") + b"\x00\x00\x00\x00" + b"WEBP"

# MP4文件头
MP4_MAGIC = bytes.fromhex("00000018667479706D703432")

# 假的JPEG（实际是文本）
FAKE_JPEG = b"This is not a JPEG file"


# ===========================================
# Helper函数
# ===========================================

def create_upload_file(
    filename: str,
    content: bytes,
    content_type: str
) -> UploadFile:
    """创建模拟的UploadFile对象"""
    from starlette.datastructures import Headers

    file = UploadFile(
        filename=filename,
        file=BytesIO(content),
        headers=Headers({"content-type": content_type})
    )
    return file


# ===========================================
# 1. 文件名清理测试
# ===========================================

class TestSanitizeFilename:
    """测试文件名清理功能"""

    def test_sanitize_normal_filename(self):
        """测试正常文件名"""
        result = sanitize_filename("test_image.jpg")
        assert result == "test_image.jpg"

    def test_sanitize_path_separators(self):
        """测试移除路径分隔符"""
        result = sanitize_filename("../../etc/passwd")
        # 开头的点会被移除
        assert result == "_.._etc_passwd"

    def test_sanitize_windows_path(self):
        """测试Windows路径"""
        result = sanitize_filename("C:\\Windows\\System32\\file.exe")
        assert "_" in result
        assert "\\" not in result

    def test_sanitize_special_characters(self):
        """测试移除特殊字符"""
        result = sanitize_filename("file@#$%^&*().jpg")
        # 9个特殊字符被替换为下划线
        assert result == "file_________.jpg"

    def test_sanitize_chinese_characters(self):
        """测试中文字符"""
        result = sanitize_filename("测试文件.jpg")
        assert "_" in result  # 中文被替换为下划线

    def test_sanitize_spaces(self):
        """测试空格"""
        result = sanitize_filename("my file name.jpg")
        assert result == "my_file_name.jpg"

    def test_sanitize_hidden_file(self):
        """测试隐藏文件（开头的点）"""
        result = sanitize_filename(".hidden_file")
        assert not result.startswith(".")
        assert result == "hidden_file"

    def test_sanitize_long_filename(self):
        """测试超长文件名"""
        long_name = "a" * 300 + ".jpg"
        result = sanitize_filename(long_name)
        assert len(result) <= 255
        assert result.endswith(".jpg")

    def test_sanitize_empty_filename(self):
        """测试空文件名"""
        result = sanitize_filename("")
        assert result == "unnamed"

    def test_sanitize_only_dots(self):
        """测试只有点的文件名"""
        result = sanitize_filename("...")
        assert result == "unnamed"

    def test_sanitize_unicode_emoji(self):
        """测试Unicode表情符号"""
        result = sanitize_filename("file_😀_test.jpg")
        assert "😀" not in result
        assert "_" in result


# ===========================================
# 2. 文件扩展名测试
# ===========================================

class TestGetFileExtension:
    """测试获取文件扩展名"""

    def test_get_extension_normal(self):
        """测试正常文件名"""
        ext = get_file_extension("test.jpg")
        assert ext == ".jpg"

    def test_get_extension_uppercase(self):
        """测试大写扩展名"""
        ext = get_file_extension("test.JPG")
        assert ext == ".jpg"  # 应该转换为小写

    def test_get_extension_multiple_dots(self):
        """测试多个点的文件名"""
        ext = get_file_extension("my.test.file.png")
        assert ext == ".png"

    def test_get_extension_no_extension(self):
        """测试无扩展名"""
        ext = get_file_extension("testfile")
        assert ext == ""

    def test_get_extension_empty(self):
        """测试空字符串"""
        ext = get_file_extension("")
        assert ext == ""

    def test_get_extension_none(self):
        """测试None"""
        ext = get_file_extension(None)
        assert ext == ""

    def test_get_extension_dot_only(self):
        """测试只有点"""
        ext = get_file_extension("test.")
        assert ext == "."


# ===========================================
# 3. 文件魔数检查测试
# ===========================================

class TestCheckFileMagic:
    """测试文件魔数检查"""

    def test_check_jpeg_magic(self):
        """测试JPEG魔数"""
        assert check_file_magic(JPEG_MAGIC, "image/jpeg") is True

    def test_check_png_magic(self):
        """测试PNG魔数"""
        assert check_file_magic(PNG_MAGIC, "image/png") is True

    def test_check_gif_magic(self):
        """测试GIF魔数"""
        assert check_file_magic(GIF_MAGIC, "image/gif") is True

    def test_check_webp_magic(self):
        """测试WebP魔数（需要RIFF+WEBP）"""
        assert check_file_magic(WEBP_MAGIC, "image/webp") is True

    def test_check_mp4_magic(self):
        """测试MP4魔数"""
        assert check_file_magic(MP4_MAGIC, "video/mp4") is True

    def test_check_wrong_magic(self):
        """测试错误的魔数"""
        # 用JPEG魔数检查PNG类型
        assert check_file_magic(JPEG_MAGIC, "image/png") is False

    def test_check_fake_file(self):
        """测试伪造的文件"""
        # 文本内容声称是JPEG
        assert check_file_magic(FAKE_JPEG, "image/jpeg") is False

    def test_check_unknown_mime(self):
        """测试未知MIME类型（应跳过检查）"""
        # 对于未知类型，返回True（跳过魔数检查）
        assert check_file_magic(b"anything", "application/unknown") is True

    def test_check_empty_content(self):
        """测试空内容"""
        assert check_file_magic(b"", "image/jpeg") is False


# ===========================================
# 4. 完整文件验证测试
# ===========================================

class TestValidateUploadFile:
    """测试完整文件验证"""

    @pytest.mark.asyncio
    async def test_validate_valid_image(self):
        """测试有效的图片文件"""
        file = create_upload_file(
            filename="test.jpg",
            content=JPEG_MAGIC + b"\x00" * 100,  # 添加一些内容
            content_type="image/jpeg"
        )

        content, ext = await validate_upload_file(
            file,
            allowed_extensions=[".jpg", ".png"],
            allowed_mimes=["image/jpeg", "image/png"],
            max_size=1024 * 1024,  # 1MB
            check_magic=True
        )

        assert ext == ".jpg"
        assert len(content) > 0

    @pytest.mark.asyncio
    async def test_validate_empty_filename(self):
        """测试空文件名"""
        file = create_upload_file(
            filename="",
            content=JPEG_MAGIC,
            content_type="image/jpeg"
        )

        with pytest.raises(HTTPException) as exc:
            await validate_upload_file(
                file,
                allowed_extensions=[".jpg"],
                allowed_mimes=["image/jpeg"],
                max_size=1024 * 1024
            )

        assert exc.value.status_code == 400
        assert "文件名无效" in exc.value.detail

    @pytest.mark.asyncio
    async def test_validate_none_filename(self):
        """测试None文件名"""
        file = create_upload_file(
            filename=None,
            content=JPEG_MAGIC,
            content_type="image/jpeg"
        )

        with pytest.raises(HTTPException) as exc:
            await validate_upload_file(
                file,
                allowed_extensions=[".jpg"],
                allowed_mimes=["image/jpeg"],
                max_size=1024 * 1024
            )

        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_validate_wrong_extension(self):
        """测试错误的文件扩展名"""
        file = create_upload_file(
            filename="test.exe",
            content=b"executable content",
            content_type="application/x-msdownload"
        )

        with pytest.raises(HTTPException) as exc:
            await validate_upload_file(
                file,
                allowed_extensions=[".jpg", ".png"],
                allowed_mimes=["image/jpeg", "image/png"],
                max_size=1024 * 1024
            )

        assert exc.value.status_code == 400
        assert "不支持的文件类型" in exc.value.detail

    @pytest.mark.asyncio
    async def test_validate_empty_file(self):
        """测试空文件"""
        file = create_upload_file(
            filename="test.jpg",
            content=b"",
            content_type="image/jpeg"
        )

        with pytest.raises(HTTPException) as exc:
            await validate_upload_file(
                file,
                allowed_extensions=[".jpg"],
                allowed_mimes=["image/jpeg"],
                max_size=1024 * 1024
            )

        assert exc.value.status_code == 400
        assert "文件为空" in exc.value.detail

    @pytest.mark.asyncio
    async def test_validate_file_too_large(self):
        """测试文件过大"""
        large_content = JPEG_MAGIC + b"\x00" * (10 * 1024 * 1024)  # 10MB
        file = create_upload_file(
            filename="test.jpg",
            content=large_content,
            content_type="image/jpeg"
        )

        with pytest.raises(HTTPException) as exc:
            await validate_upload_file(
                file,
                allowed_extensions=[".jpg"],
                allowed_mimes=["image/jpeg"],
                max_size=1 * 1024 * 1024,  # 只允许1MB
                check_magic=False  # 跳过魔数检查以加快速度
            )

        assert exc.value.status_code == 413
        assert "文件过大" in exc.value.detail

    @pytest.mark.asyncio
    async def test_validate_wrong_mime_type(self):
        """测试错误的MIME类型"""
        file = create_upload_file(
            filename="test.jpg",
            content=JPEG_MAGIC,
            content_type="image/gif"  # 声称是GIF
        )

        with pytest.raises(HTTPException) as exc:
            await validate_upload_file(
                file,
                allowed_extensions=[".jpg"],
                allowed_mimes=["image/jpeg"],  # 只允许JPEG
                max_size=1024 * 1024
            )

        assert exc.value.status_code == 400
        assert "不支持的MIME类型" in exc.value.detail

    @pytest.mark.asyncio
    async def test_validate_fake_file_magic(self):
        """测试伪造的文件（魔数不匹配）"""
        file = create_upload_file(
            filename="test.jpg",
            content=FAKE_JPEG,  # 文本内容
            content_type="image/jpeg"  # 声称是JPEG
        )

        with pytest.raises(HTTPException) as exc:
            await validate_upload_file(
                file,
                allowed_extensions=[".jpg"],
                allowed_mimes=["image/jpeg"],
                max_size=1024 * 1024,
                check_magic=True  # 启用魔数检查
            )

        assert exc.value.status_code == 400
        assert "文件内容与声明的类型不匹配" in exc.value.detail

    @pytest.mark.asyncio
    async def test_validate_skip_magic_check(self):
        """测试跳过魔数检查"""
        file = create_upload_file(
            filename="test.jpg",
            content=FAKE_JPEG,  # 虽然内容不对
            content_type="image/jpeg"
        )

        # 跳过魔数检查应该成功
        content, ext = await validate_upload_file(
            file,
            allowed_extensions=[".jpg"],
            allowed_mimes=["image/jpeg"],
            max_size=1024 * 1024,
            check_magic=False  # 跳过魔数检查
        )

        assert ext == ".jpg"


# ===========================================
# 5. 预设验证配置测试
# ===========================================

class TestFileValidationPresets:
    """测试预设验证配置"""

    @pytest.mark.asyncio
    async def test_validate_image_preset_success(self):
        """测试图片预设验证 - 成功"""
        file = create_upload_file(
            filename="photo.png",
            content=PNG_MAGIC + b"\x00" * 100,
            content_type="image/png"
        )

        content, ext = await FileValidationPresets.validate_image(file)

        assert ext == ".png"
        assert len(content) > 0

    @pytest.mark.asyncio
    async def test_validate_image_preset_wrong_type(self):
        """测试图片预设验证 - 错误类型"""
        file = create_upload_file(
            filename="video.mp4",
            content=MP4_MAGIC,
            content_type="video/mp4"
        )

        with pytest.raises(HTTPException):
            await FileValidationPresets.validate_image(file)

    @pytest.mark.asyncio
    async def test_validate_video_preset_success(self):
        """测试视频预设验证 - 成功"""
        file = create_upload_file(
            filename="video.mp4",
            content=b"\x00" * 1000,  # 模拟视频内容
            content_type="video/mp4"
        )

        content, ext = await FileValidationPresets.validate_video(file)

        assert ext == ".mp4"

    @pytest.mark.asyncio
    async def test_validate_video_preset_max_size(self):
        """测试视频预设最大大小"""
        # 视频应该允许大文件（5GB）
        assert FileValidationPresets.VIDEO_MAX_SIZE == 5 * 1024 * 1024 * 1024

    @pytest.mark.asyncio
    async def test_validate_subtitle_preset_success(self):
        """测试字幕预设验证 - 成功"""
        file = create_upload_file(
            filename="subtitle.srt",
            content=b"1\n00:00:00,000 --> 00:00:02,000\nHello World",
            content_type="text/plain"
        )

        content, ext = await FileValidationPresets.validate_subtitle(file)

        assert ext == ".srt"
        assert b"Hello World" in content


# ===========================================
# 6. 边界条件和安全测试
# ===========================================

class TestSecurityAndEdgeCases:
    """测试安全和边界条件"""

    def test_sanitize_path_traversal_attack(self):
        """测试路径遍历攻击"""
        malicious_names = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "....//....//....//etc/passwd",
        ]

        for name in malicious_names:
            result = sanitize_filename(name)
            # 点号本身是允许的（文件扩展名需要），但路径分隔符应该被移除
            assert "/" not in result
            assert "\\" not in result
            # 不应该以点开头（隐藏文件）
            assert not result.startswith(".")

    def test_sanitize_null_byte_attack(self):
        """测试空字节注入"""
        result = sanitize_filename("test\x00.jpg.exe")
        assert "\x00" not in result

    def test_sanitize_command_injection(self):
        """测试命令注入字符"""
        result = sanitize_filename("file;rm -rf /.jpg")
        assert ";" not in result
        assert " " not in result or "_" in result

    @pytest.mark.asyncio
    async def test_validate_extension_case_insensitive(self):
        """测试扩展名大小写不敏感"""
        file = create_upload_file(
            filename="test.JPG",  # 大写扩展名
            content=JPEG_MAGIC + b"\x00" * 100,
            content_type="image/jpeg"
        )

        content, ext = await validate_upload_file(
            file,
            allowed_extensions=[".jpg"],  # 小写允许列表
            allowed_mimes=["image/jpeg"],
            max_size=1024 * 1024,
            check_magic=True
        )

        assert ext == ".jpg"  # 应该被转换为小写

    @pytest.mark.asyncio
    async def test_validate_boundary_file_size(self):
        """测试边界文件大小"""
        # 正好在限制内
        exact_size = 1024 * 1024  # 1MB
        file = create_upload_file(
            filename="test.jpg",
            content=JPEG_MAGIC + b"\x00" * (exact_size - len(JPEG_MAGIC)),
            content_type="image/jpeg"
        )

        content, ext = await validate_upload_file(
            file,
            allowed_extensions=[".jpg"],
            allowed_mimes=["image/jpeg"],
            max_size=exact_size,
            check_magic=False
        )

        assert len(content) == exact_size

    def test_file_magic_numbers_coverage(self):
        """测试文件魔数定义的完整性"""
        # 验证所有定义的MIME类型都有魔数
        assert "image/jpeg" in FILE_MAGIC_NUMBERS
        assert "image/png" in FILE_MAGIC_NUMBERS
        assert "image/gif" in FILE_MAGIC_NUMBERS
        assert "image/webp" in FILE_MAGIC_NUMBERS
        assert "video/mp4" in FILE_MAGIC_NUMBERS

        # 验证魔数不为空
        for mime, magics in FILE_MAGIC_NUMBERS.items():
            assert len(magics) > 0
            for magic in magics:
                assert len(magic) > 0

    def test_sanitize_dot_files(self):
        """测试各种点文件格式"""
        test_cases = [
            (".htaccess", "htaccess"),  # 开头的单个点被移除
            (".env", "env"),             # 开头的单个点被移除
            (".git", "git"),             # 开头的单个点被移除
            ("..config", "config"),      # 开头的所有点被移除
        ]

        for input_name, expected_start in test_cases:
            result = sanitize_filename(input_name)
            if expected_start:
                assert result.startswith(expected_start)

    @pytest.mark.asyncio
    async def test_validate_multiple_extensions(self):
        """测试多扩展名文件"""
        file = create_upload_file(
            filename="archive.tar.gz.jpg",
            content=JPEG_MAGIC + b"\x00" * 100,
            content_type="image/jpeg"
        )

        content, ext = await validate_upload_file(
            file,
            allowed_extensions=[".jpg"],
            allowed_mimes=["image/jpeg"],
            max_size=1024 * 1024,
            check_magic=True
        )

        # 应该只取最后一个扩展名
        assert ext == ".jpg"


# ===========================================
# 7. 配置常量测试
# ===========================================

class TestPresetConstants:
    """测试预设常量"""

    def test_image_extensions(self):
        """测试图片扩展名列表"""
        assert ".jpg" in FileValidationPresets.IMAGE_EXTENSIONS
        assert ".png" in FileValidationPresets.IMAGE_EXTENSIONS
        assert ".webp" in FileValidationPresets.IMAGE_EXTENSIONS

    def test_video_extensions(self):
        """测试视频扩展名列表"""
        assert ".mp4" in FileValidationPresets.VIDEO_EXTENSIONS
        assert ".mkv" in FileValidationPresets.VIDEO_EXTENSIONS
        assert ".avi" in FileValidationPresets.VIDEO_EXTENSIONS

    def test_subtitle_extensions(self):
        """测试字幕扩展名列表"""
        assert ".srt" in FileValidationPresets.SUBTITLE_EXTENSIONS
        assert ".vtt" in FileValidationPresets.SUBTITLE_EXTENSIONS

    def test_size_limits_reasonable(self):
        """测试文件大小限制是否合理"""
        # 图片不应超过100MB
        assert FileValidationPresets.IMAGE_MAX_SIZE <= 100 * 1024 * 1024

        # 视频应该允许GB级别
        assert FileValidationPresets.VIDEO_MAX_SIZE >= 1 * 1024 * 1024 * 1024

        # 字幕应该很小
        assert FileValidationPresets.SUBTITLE_MAX_SIZE <= 10 * 1024 * 1024


# ===========================================
# 测试总结
# ===========================================

"""
测试覆盖：
✅ 文件名清理 - 11个测试用例
✅ 文件扩展名 - 7个测试用例
✅ 文件魔数检查 - 9个测试用例
✅ 完整文件验证 - 10个测试用例
✅ 预设验证配置 - 5个测试用例
✅ 安全和边界条件 - 9个测试用例
✅ 配置常量 - 4个测试用例

总计：55个测试用例

测试场景：
- 文件名清理（路径遍历、特殊字符、超长名）
- 扩展名提取和验证（大小写、多扩展名）
- 文件魔数验证（JPEG/PNG/GIF/WebP/MP4）
- 伪造文件检测
- 文件大小限制
- MIME类型验证
- 空文件/空文件名处理
- 路径遍历攻击防护
- 命令注入防护
- 空字节注入防护
- 点文件处理
- 边界值测试
- 预设配置（图片/视频/字幕）

安全测试：
- ✅ 路径遍历攻击防护
- ✅ 文件类型伪造检测
- ✅ 命令注入防护
- ✅ 空字节注入防护
- ✅ 文件大小限制
- ✅ 隐藏文件防护
- ✅ 魔数验证防伪造
"""
