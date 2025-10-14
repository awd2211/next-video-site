"""
测试Pydantic Schemas的验证规则
"""
# pyright: reportCallIssue=false
# pyright: reportArgumentType=false

import pytest
from pydantic import ValidationError

from app.schemas.auth import UserRegister
from app.schemas.comment import CommentCreate
from app.schemas.danmaku import DanmakuCreate
from app.schemas.rating import RatingCreate
from app.schemas.person import ActorBase
from app.schemas.video import VideoCreate
from app.schemas.series import SeriesCreate


class TestAuthSchemas:
    """测试认证相关schemas"""

    def test_user_register_valid(self):
        """测试有效的注册数据"""
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "Strong@Pass123",
            "captcha_id": "abc123",
            "captcha_code": "1234",
        }
        user = UserRegister(**data)
        assert user.email == "test@example.com"
        assert user.username == "testuser"

    def test_user_register_invalid_email(self):
        """测试无效邮箱"""
        data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "Strong@Pass123",
            "captcha_id": "abc",
            "captcha_code": "1234",
        }
        with pytest.raises(ValidationError):
            UserRegister(**data)

    def test_user_register_password_too_short(self):
        """测试密码太短"""
        data = {
            "email": "test@example.com",
            "username": "test",
            "password": "Short1!",
            "captcha_id": "abc",
            "captcha_code": "1234",
        }
        with pytest.raises(ValidationError):
            UserRegister(**data)

    def test_user_register_weak_password(self):
        """测试弱密码"""
        data = {
            "email": "test@example.com",
            "username": "test",
            "password": "password123",  # 常见弱密码
            "captcha_id": "abc",
            "captcha_code": "1234",
        }
        with pytest.raises(ValidationError):
            UserRegister(**data)

    def test_user_register_username_too_short(self):
        """测试用户名太短"""
        data = {
            "email": "test@example.com",
            "username": "ab",  # 少于3个字符
            "password": "Strong@Pass123",
            "captcha_id": "abc",
            "captcha_code": "1234",
        }
        with pytest.raises(ValidationError):
            UserRegister(**data)

    def test_captcha_code_invalid_length(self):
        """测试验证码长度无效"""
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "Strong@Pass123",
            "captcha_id": "abc",
            "captcha_code": "123",  # 少于4位
        }
        with pytest.raises(ValidationError):
            UserRegister(**data)


class TestCommentSchemas:
    """测试评论schemas"""

    def test_comment_create_valid(self):
        """测试有效评论"""
        data = {"video_id": 1, "content": "Great video!"}
        comment = CommentCreate(**data)
        assert comment.video_id == 1
        assert comment.content == "Great video!"

    def test_comment_content_too_long(self):
        """测试评论内容过长"""
        data = {"video_id": 1, "content": "x" * 1001}  # 超过1000
        with pytest.raises(ValidationError):
            CommentCreate(**data)

    def test_comment_empty_content(self):
        """测试空内容"""
        data = {"video_id": 1, "content": ""}
        with pytest.raises(ValidationError):
            CommentCreate(**data)

    def test_comment_invalid_video_id(self):
        """测试无效视频ID"""
        data = {"video_id": 0, "content": "test"}  # 必须>0
        with pytest.raises(ValidationError):
            CommentCreate(**data)


class TestDanmakuSchemas:
    """测试弹幕schemas"""

    def test_danmaku_create_valid(self):
        """测试有效弹幕"""
        data = {
            "video_id": 1,
            "content": "测试弹幕",
            "time": 10.5,
            "color": "#FFFFFF",
        }
        danmaku = DanmakuCreate(**data)
        assert danmaku.video_id == 1
        assert danmaku.content == "测试弹幕"

    def test_danmaku_content_too_long(self):
        """测试弹幕内容过长"""
        data = {
            "video_id": 1,
            "content": "x" * 101,  # 超过100
            "time": 10.0,
        }
        with pytest.raises(ValidationError):
            DanmakuCreate(**data)

    def test_danmaku_invalid_color(self):
        """测试无效颜色格式"""
        data = {"video_id": 1, "content": "test", "time": 10.0, "color": "white"}
        with pytest.raises(ValidationError):
            DanmakuCreate(**data)

    def test_danmaku_font_size_out_of_range(self):
        """测试字体大小超出范围"""
        data = {
            "video_id": 1,
            "content": "test",
            "time": 10.0,
            "font_size": 50,  # 超过36
        }
        with pytest.raises(ValidationError):
            DanmakuCreate(**data)


class TestRatingSchemas:
    """测试评分schemas"""

    def test_rating_create_valid(self):
        """测试有效评分"""
        data = {"video_id": 1, "score": 8.5}
        rating = RatingCreate(**data)
        assert rating.video_id == 1
        assert rating.score == 8.5

    def test_rating_score_out_of_range(self):
        """测试评分超出范围"""
        with pytest.raises(ValidationError):
            RatingCreate(video_id=1, score=11.0)  # 超过10
        with pytest.raises(ValidationError):
            RatingCreate(video_id=1, score=-1.0)  # 小于0


class TestPersonSchemas:
    """测试演员/导演schemas"""

    def test_actor_base_valid(self):
        """测试有效演员数据"""
        data = {"name": "Tom Hanks", "biography": "Great actor"}
        actor = ActorBase(**data)
        assert actor.name == "Tom Hanks"

    def test_actor_name_too_long(self):
        """测试名字过长"""
        data = {"name": "x" * 201}  # 超过200
        with pytest.raises(ValidationError):
            ActorBase(**data)

    def test_actor_biography_too_long(self):
        """测试简介过长"""
        data = {"name": "Tom", "biography": "x" * 1001}  # 超过1000
        with pytest.raises(ValidationError):
            ActorBase(**data)

    def test_actor_unsafe_avatar_url(self):
        """测试不安全的头像URL"""
        data = {"name": "Tom", "avatar": "http://localhost/image.jpg"}
        with pytest.raises(ValidationError):
            ActorBase(**data)


class TestVideoSchemas:
    """测试视频schemas"""

    def test_video_create_valid(self):
        """测试有效视频数据"""
        data = {"title": "Test Video", "video_type": "movie"}
        video = VideoCreate(**data)
        assert video.title == "Test Video"

    def test_video_title_too_long(self):
        """测试标题过长"""
        data = {"title": "x" * 501, "video_type": "movie"}  # 超过500
        with pytest.raises(ValidationError):
            VideoCreate(**data)

    def test_video_description_too_long(self):
        """测试描述过长"""
        data = {
            "title": "Test",
            "video_type": "movie",
            "description": "x" * 2001,  # 超过2000
        }
        with pytest.raises(ValidationError):
            VideoCreate(**data)

    def test_video_year_out_of_range(self):
        """测试年份超出范围"""
        data = {"title": "Test", "video_type": "movie", "release_year": 1800}  # <1900
        with pytest.raises(ValidationError):
            VideoCreate(**data)

    def test_video_unsafe_url(self):
        """测试不安全的URL"""
        data = {
            "title": "Test",
            "video_type": "movie",
            "video_url": "http://192.168.1.1/video.mp4",
        }
        with pytest.raises(ValidationError):
            VideoCreate(**data)


class TestSeriesSchemas:
    """测试剧集schemas"""

    def test_series_create_valid(self):
        """测试有效剧集数据"""
        data = {"title": "Test Series"}
        series = SeriesCreate(**data)
        assert series.title == "Test Series"

    def test_series_title_too_long(self):
        """测试标题过长"""
        data = {"title": "x" * 501}  # 超过500
        with pytest.raises(ValidationError):
            SeriesCreate(**data)

    def test_series_description_too_long(self):
        """测试描述过长"""
        data = {"title": "Test", "description": "x" * 2001}  # 超过2000
        with pytest.raises(ValidationError):
            SeriesCreate(**data)

    def test_series_unsafe_cover_url(self):
        """测试不安全的封面URL"""
        data = {"title": "Test", "cover_image": "http://localhost/cover.jpg"}
        with pytest.raises(ValidationError):
            SeriesCreate(**data)
