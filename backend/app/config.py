from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "VideoSite"
    DEBUG: bool = False  # 生产环境必须为False，开发时可通过.env覆盖
    SECRET_KEY: str
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str
    DATABASE_URL_SYNC: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    # 生产环境应该通过环境变量覆盖这个默认值
    # 示例: BACKEND_CORS_ORIGINS='["https://yourdomain.com","https://admin.yourdomain.com"]'
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3003",  # Admin frontend port
        "http://localhost:5173",
    ]

    # File Storage (MinIO)
    # 警告：生产环境必须在.env中设置强密码，不要使用默认值！
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str = "videos"
    MINIO_SECURE: bool = False  # 生产环境应设为True
    MINIO_PUBLIC_URL: str

    # Elasticsearch
    ELASTICSEARCH_URL: str = "http://localhost:9200"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Pagination
    PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Upload
    MAX_UPLOAD_SIZE: int = 5368709120  # 5GB
    ALLOWED_VIDEO_EXTENSIONS: str = ".mp4,.avi,.mkv,.mov,.flv"
    ALLOWED_IMAGE_EXTENSIONS: str = ".jpg,.jpeg,.png,.webp"

    # Email (optional)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""

    # Payment Gateways
    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # PayPal
    PAYPAL_CLIENT_ID: str = ""
    PAYPAL_CLIENT_SECRET: str = ""
    PAYPAL_ENVIRONMENT: str = "sandbox"  # sandbox or live

    # Alipay
    ALIPAY_APP_ID: str = ""
    ALIPAY_PRIVATE_KEY: str = ""  # RSA private key
    ALIPAY_PUBLIC_KEY: str = ""  # Alipay public key
    ALIPAY_GATEWAY_URL: str = "https://openapi.alipaydev.com/gateway.do"  # sandbox URL

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()  # type: ignore[call-arg]


def get_settings() -> Settings:
    """Get application settings"""
    return settings
