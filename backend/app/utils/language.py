"""
语言处理工具
"""
from typing import Any, Dict
from fastapi import Request


class LanguageHelper:
    """语言助手"""

    SUPPORTED_LANGUAGES = ['zh-CN', 'en-US', 'ja-JP']
    DEFAULT_LANGUAGE = 'zh-CN'

    @staticmethod
    def get_language(request: Request) -> str:
        """
        从请求获取语言

        优先级:
        1. X-Language 自定义头
        2. Accept-Language 标准头
        3. 默认语言（zh-CN）
        """
        # 方法1: 自定义头（推荐，精确控制）
        custom_lang = request.headers.get("X-Language", "")
        if custom_lang in LanguageHelper.SUPPORTED_LANGUAGES:
            return custom_lang

        # 方法2: Accept-Language（浏览器自动发送）
        accept_lang = request.headers.get("Accept-Language", "")
        if accept_lang:
            # 解析: zh-CN,zh;q=0.9,en;q=0.8
            for lang_entry in accept_lang.split(','):
                lang_code = lang_entry.split(';')[0].strip()
                if lang_code in LanguageHelper.SUPPORTED_LANGUAGES:
                    return lang_code

                # 模糊匹配: zh -> zh-CN
                lang_prefix = lang_code.split('-')[0]
                for supported in LanguageHelper.SUPPORTED_LANGUAGES:
                    if supported.startswith(lang_prefix):
                        return supported

        # 默认语言
        return LanguageHelper.DEFAULT_LANGUAGE

    @staticmethod
    def get_localized_field(obj: Any, field: str, lang: str) -> str:
        """
        获取本地化字段值

        Args:
            obj: 数据库对象
            field: 字段名（如 'name'）
            lang: 语言代码

        Returns:
            翻译后的值，如果没有翻译则返回默认值

        Example:
            category = db.query(Category).first()
            name = get_localized_field(category, 'name', 'en-US')
            # 返回 category.name_en 或 category.name
        """
        # 如果是默认语言，直接返回
        if lang == LanguageHelper.DEFAULT_LANGUAGE:
            return getattr(obj, field, '')

        # 尝试获取翻译字段
        lang_suffix = lang.replace('-', '_').lower().split('_')[0]  # zh-CN -> zh, en-US -> en
        localized_field = f"{field}_{lang_suffix}"

        # 获取翻译值，如果没有则回退到默认语言
        value = getattr(obj, localized_field, None)
        return value if value else getattr(obj, field, '')

    @staticmethod
    def to_dict_with_locale(obj: Any, lang: str, fields: list[str]) -> Dict[str, Any]:
        """
        将对象转换为字典，包含本地化字段

        Args:
            obj: 数据库对象
            lang: 语言代码
            fields: 需要本地化的字段列表

        Returns:
            包含本地化值的字典
        """
        result = {}

        for field in fields:
            result[field] = LanguageHelper.get_localized_field(obj, field, lang)

        # 添加其他非翻译字段
        for attr in dir(obj):
            if not attr.startswith('_') and attr not in fields:
                value = getattr(obj, attr, None)
                if not callable(value):
                    result[attr] = value

        return result


# 依赖函数
async def get_language(request: Request) -> str:
    """获取请求语言（用作FastAPI依赖）"""
    return LanguageHelper.get_language(request)
