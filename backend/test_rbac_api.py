#!/usr/bin/env python3
"""
Quick test script to verify RBAC API endpoints
"""
import asyncio
import sys
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Add backend to path
sys.path.insert(0, '/home/eric/video/backend')

from app.database import async_session_maker
from app.models.admin import Role, Permission, RolePermission
from app.models.user import AdminUser


async def test_rbac_tables():
    """Test if RBAC tables exist and can be queried"""
    async with async_session_maker() as session:
        try:
            # Test permissions table
            result = await session.execute(select(Permission))
            permissions = result.scalars().all()
            print(f"✓ Permissions table exists: {len(permissions)} permissions found")

            # Test roles table
            result = await session.execute(select(Role))
            roles = result.scalars().all()
            print(f"✓ Roles table exists: {len(roles)} roles found")

            # Test role_permissions table
            result = await session.execute(select(RolePermission))
            role_perms = result.scalars().all()
            print(f"✓ Role_permissions table exists: {len(role_perms)} associations found")

            # Test admin_users with role relationship
            result = await session.execute(select(AdminUser))
            admins = result.scalars().all()
            print(f"✓ Admin_users table exists: {len(admins)} admin users found")

            print("\n✅ All RBAC tables are present and accessible!")

            # Show some details
            if permissions:
                print(f"\nSample permissions:")
                for perm in permissions[:5]:
                    print(f"  - {perm.name} ({perm.code})")

            if roles:
                print(f"\nSample roles:")
                for role in roles[:5]:
                    print(f"  - {role.name}")

            return True

        except Exception as e:
            print(f"❌ Error accessing RBAC tables: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    success = asyncio.run(test_rbac_tables())
    sys.exit(0 if success else 1)
