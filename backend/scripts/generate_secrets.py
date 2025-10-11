#!/usr/bin/env python3
"""
生成安全的随机密钥
用于.env配置文件
"""
import secrets


def generate_all_secrets():
    """生成所有需要的密钥"""
    print("=" * 60)
    print("VideoSite 安全密钥生成器")
    print("=" * 60)
    print()
    print("请将以下内容添加到你的 .env 文件中：")
    print()
    print("-" * 60)
    
    # 应用密钥
    secret_key = secrets.token_urlsafe(32)
    print(f"SECRET_KEY={secret_key}")
    
    # JWT密钥
    jwt_secret = secrets.token_urlsafe(32)
    print(f"JWT_SECRET_KEY={jwt_secret}")
    
    print()
    
    # MinIO凭据
    minio_access = secrets.token_urlsafe(20)
    minio_secret = secrets.token_urlsafe(40)
    print(f"MINIO_ACCESS_KEY={minio_access}")
    print(f"MINIO_SECRET_KEY={minio_secret}")
    
    print()
    print("-" * 60)
    print()
    print("⚠️  重要提示：")
    print("1. 请妥善保管这些密钥，不要分享给他人")
    print("2. 不要提交 .env 文件到版本控制")
    print("3. 生产环境建议使用 AWS Secrets Manager 等工具")
    print("4. 定期轮换密钥（建议每3-6个月）")
    print()
    print("=" * 60)


if __name__ == "__main__":
    generate_all_secrets()


