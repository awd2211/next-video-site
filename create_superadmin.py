#!/usr/bin/env python3
"""
创建或重置超级管理员账户
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.models.user import AdminUser
from app.utils.security import get_password_hash
from app.config import settings

def create_or_reset_superadmin():
    """创建或重置超级管理员账户"""

    # 创建数据库连接
    engine = create_engine(settings.DATABASE_URL_SYNC)

    with Session(engine) as session:
        # 检查是否已存在 admin 账户
        stmt = select(AdminUser).where(AdminUser.username == 'admin')
        admin = session.execute(stmt).scalar_one_or_none()

        if admin:
            print(f"✓ 找到现有超级管理员账户: {admin.username}")
            print(f"  Email: {admin.email}")
            print(f"  ID: {admin.id}")
            print()

            # 重置密码
            new_password = "admin123456"
            admin.hashed_password = get_password_hash(new_password)
            admin.is_superadmin = True
            admin.is_active = True
            session.commit()

            print("✓ 密码已重置!")
            print()
            print("=" * 50)
            print("超级管理员账户信息:")
            print("=" * 50)
            print(f"用户名: {admin.username}")
            print(f"邮箱:   {admin.email}")
            print(f"密码:   {new_password}")
            print("=" * 50)

        else:
            # 创建新的超级管理员
            print("未找到 admin 账户，创建新的超级管理员...")

            new_password = "admin123456"
            new_admin = AdminUser(
                username='admin',
                email='admin@videosite.com',
                full_name='系统管理员',
                hashed_password=get_password_hash(new_password),
                is_superadmin=True,
                is_active=True
            )

            session.add(new_admin)
            session.commit()
            session.refresh(new_admin)

            print("✓ 超级管理员账户创建成功!")
            print()
            print("=" * 50)
            print("超级管理员账户信息:")
            print("=" * 50)
            print(f"用户名: {new_admin.username}")
            print(f"邮箱:   {new_admin.email}")
            print(f"密码:   {new_password}")
            print(f"ID:     {new_admin.id}")
            print("=" * 50)

        print()
        print("你可以使用以上信息登录管理后台:")
        print("http://localhost:3001")
        print()

if __name__ == '__main__':
    try:
        create_or_reset_superadmin()
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
