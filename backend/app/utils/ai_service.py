"""
AI Service Layer - 统一的AI提供商接口
支持: OpenAI, Grok (xAI), Google AI
"""

import time
from typing import Any, Optional

from loguru import logger

try:
    from openai import OpenAI, AsyncOpenAI
except ImportError:
    OpenAI = None
    AsyncOpenAI = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class AIServiceError(Exception):
    """AI服务异常"""

    pass


class AIService:
    """统一的AI服务接口"""

    @staticmethod
    def _get_openai_client(api_key: str, base_url: Optional[str] = None):
        """获取OpenAI客户端"""
        if OpenAI is None:
            raise AIServiceError("OpenAI SDK not installed. Run: pip install openai")

        return OpenAI(api_key=api_key, base_url=base_url)

    @staticmethod
    def _get_grok_client(api_key: str, base_url: Optional[str] = None):
        """获取Grok (xAI) 客户端 - 使用OpenAI兼容接口"""
        if OpenAI is None:
            raise AIServiceError("OpenAI SDK not installed. Run: pip install openai")

        # Grok API 使用 OpenAI 兼容接口
        grok_base_url = base_url or "https://api.x.ai/v1"
        return OpenAI(api_key=api_key, base_url=grok_base_url)

    @staticmethod
    def _get_google_client(api_key: str):
        """配置Google AI客户端"""
        if genai is None:
            raise AIServiceError(
                "Google Generative AI SDK not installed. Run: pip install google-generativeai"
            )

        genai.configure(api_key=api_key)
        return genai

    @staticmethod
    async def test_connection(
        provider_type: str,
        api_key: str,
        base_url: Optional[str] = None,
        model_name: str = "gpt-3.5-turbo",
    ) -> dict[str, Any]:
        """
        测试AI提供商连接

        Returns:
            dict: {success: bool, message: str, latency_ms: int}
        """
        start_time = time.time()

        try:
            if provider_type == "openai":
                client = AIService._get_openai_client(api_key, base_url)
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=10,
                )
                latency_ms = int((time.time() - start_time) * 1000)
                return {
                    "success": True,
                    "message": f"Connected successfully. Model: {response.model}",
                    "latency_ms": latency_ms,
                }

            elif provider_type == "grok":
                client = AIService._get_grok_client(api_key, base_url)
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=10,
                )
                latency_ms = int((time.time() - start_time) * 1000)
                return {
                    "success": True,
                    "message": f"Connected successfully. Model: {response.model}",
                    "latency_ms": latency_ms,
                }

            elif provider_type == "google":
                google_client = AIService._get_google_client(api_key)
                model = google_client.GenerativeModel(model_name)
                response = model.generate_content("Hello")
                latency_ms = int((time.time() - start_time) * 1000)
                return {
                    "success": True,
                    "message": f"Connected successfully. Model: {model_name}",
                    "latency_ms": latency_ms,
                }

            else:
                return {
                    "success": False,
                    "message": f"Unsupported provider type: {provider_type}",
                    "latency_ms": 0,
                }

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error(f"AI connection test failed: {str(e)}")
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}",
                "latency_ms": latency_ms,
            }

    @staticmethod
    async def chat_completion(
        provider_type: str,
        api_key: str,
        model_name: str,
        messages: list[dict[str, str]],
        base_url: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        **kwargs,
    ) -> dict[str, Any]:
        """
        统一的聊天完成接口

        Returns:
            dict: {success: bool, response: str, tokens_used: int, latency_ms: int, error: str}
        """
        start_time = time.time()

        try:
            if provider_type == "openai":
                client = AIService._get_openai_client(api_key, base_url)
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty,
                )
                latency_ms = int((time.time() - start_time) * 1000)
                return {
                    "success": True,
                    "response": response.choices[0].message.content,
                    "tokens_used": response.usage.total_tokens if response.usage else 0,
                    "latency_ms": latency_ms,
                    "model": response.model,
                }

            elif provider_type == "grok":
                client = AIService._get_grok_client(api_key, base_url)
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty,
                )
                latency_ms = int((time.time() - start_time) * 1000)
                return {
                    "success": True,
                    "response": response.choices[0].message.content,
                    "tokens_used": response.usage.total_tokens if response.usage else 0,
                    "latency_ms": latency_ms,
                    "model": response.model,
                }

            elif provider_type == "google":
                google_client = AIService._get_google_client(api_key)
                model = google_client.GenerativeModel(model_name)

                # 转换消息格式 (Google AI 使用不同的格式)
                # 简化处理: 将所有消息合并成一个prompt
                prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

                # 配置生成参数
                generation_config = {
                    "temperature": temperature,
                    "top_p": top_p,
                    "max_output_tokens": max_tokens,
                }

                response = model.generate_content(prompt, generation_config=generation_config)
                latency_ms = int((time.time() - start_time) * 1000)

                # Google AI 的token计数需要额外处理
                tokens_used = 0
                if hasattr(response, "usage_metadata"):
                    tokens_used = (
                        response.usage_metadata.prompt_token_count
                        + response.usage_metadata.candidates_token_count
                    )

                return {
                    "success": True,
                    "response": response.text,
                    "tokens_used": tokens_used,
                    "latency_ms": latency_ms,
                    "model": model_name,
                }

            else:
                return {
                    "success": False,
                    "error": f"Unsupported provider type: {provider_type}",
                    "tokens_used": 0,
                    "latency_ms": 0,
                }

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error(f"AI chat completion failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "tokens_used": 0,
                "latency_ms": latency_ms,
            }

    @staticmethod
    def get_available_models(provider_type: str) -> list[dict[str, Any]]:
        """
        获取可用的模型列表

        Returns:
            list: [{"id": str, "name": str, "description": str, "context_window": int}]
        """
        if provider_type == "openai":
            return [
                {
                    "id": "gpt-4-turbo-preview",
                    "name": "GPT-4 Turbo Preview",
                    "description": "Most capable model, 128K context",
                    "context_window": 128000,
                    "max_output_tokens": 4096,
                },
                {
                    "id": "gpt-4",
                    "name": "GPT-4",
                    "description": "High performance, 8K context",
                    "context_window": 8192,
                    "max_output_tokens": 4096,
                },
                {
                    "id": "gpt-3.5-turbo",
                    "name": "GPT-3.5 Turbo",
                    "description": "Fast and efficient, 16K context",
                    "context_window": 16385,
                    "max_output_tokens": 4096,
                },
                {
                    "id": "gpt-4o",
                    "name": "GPT-4o",
                    "description": "Multimodal flagship model, 128K context",
                    "context_window": 128000,
                    "max_output_tokens": 4096,
                },
                {
                    "id": "gpt-4o-mini",
                    "name": "GPT-4o Mini",
                    "description": "Affordable small model, 128K context",
                    "context_window": 128000,
                    "max_output_tokens": 16384,
                },
            ]

        elif provider_type == "grok":
            return [
                {
                    "id": "grok-beta",
                    "name": "Grok Beta",
                    "description": "xAI's Grok model, 128K context",
                    "context_window": 128000,
                    "max_output_tokens": 4096,
                },
                {
                    "id": "grok-2-latest",
                    "name": "Grok 2 Latest",
                    "description": "Latest Grok 2 model",
                    "context_window": 128000,
                    "max_output_tokens": 4096,
                },
                {
                    "id": "grok-2-1212",
                    "name": "Grok 2 (2024-12-12)",
                    "description": "Grok 2 snapshot from December 2024",
                    "context_window": 128000,
                    "max_output_tokens": 4096,
                },
            ]

        elif provider_type == "google":
            return [
                {
                    "id": "gemini-pro",
                    "name": "Gemini Pro",
                    "description": "Best for text-only tasks",
                    "context_window": 32768,
                    "max_output_tokens": 2048,
                },
                {
                    "id": "gemini-pro-vision",
                    "name": "Gemini Pro Vision",
                    "description": "Best for text and image tasks",
                    "context_window": 16384,
                    "max_output_tokens": 2048,
                },
                {
                    "id": "gemini-1.5-pro",
                    "name": "Gemini 1.5 Pro",
                    "description": "Latest Gemini model, 1M context",
                    "context_window": 1000000,
                    "max_output_tokens": 8192,
                },
                {
                    "id": "gemini-1.5-flash",
                    "name": "Gemini 1.5 Flash",
                    "description": "Fast and efficient, 1M context",
                    "context_window": 1000000,
                    "max_output_tokens": 8192,
                },
            ]

        return []
