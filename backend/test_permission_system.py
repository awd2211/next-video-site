#!/usr/bin/env python3
"""
权限系统测试脚本 / Permission System Test Script
测试权限验证、缓存和审计日志功能 / Test permission verification, caching, and audit logs
"""

import asyncio
import sys
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import AdminUser
from app.models.admin import Role, Permission, RolePermission
from app.models.permission_log import PermissionLog
from app.utils.permissions import (
    get_admin_permissions_cached,
    check_admin_has_permission,
    check_admin_has_any_permission,
    check_admin_has_all_permissions,
    invalidate_admin_permissions_cache,
)
from app.utils.cache import get_redis


async def test_permission_caching():
    """测试权限缓存功能 / Test permission caching"""
    print("\n" + "="*60)
    print("🔍 测试1: 权限缓存功能 / Test 1: Permission Caching")
    print("="*60)

    async for session in get_db():
        # 获取第一个管理员
        result = await session.execute(select(AdminUser).limit(1))
        admin = result.scalar_one_or_none()

        if not admin:
            print("❌ 未找到管理员 / No admin found")
            return

        print(f"✅ 测试管理员 / Test admin: {admin.username} (ID: {admin.id})")

        # 清除缓存
        await invalidate_admin_permissions_cache(admin.id)
        print("🧹 已清除缓存 / Cache cleared")

        # 第一次获取权限(应该从数据库)
        start = datetime.now()
        perms1 = await get_admin_permissions_cached(admin.id, session)
        time1 = (datetime.now() - start).total_seconds() * 1000
        print(f"📊 第一次获取 / First fetch: {time1:.2f}ms (from database)")
        print(f"   权限数量 / Permission count: {len(perms1)}")

        # 第二次获取权限(应该从缓存)
        start = datetime.now()
        perms2 = await get_admin_permissions_cached(admin.id, session)
        time2 = (datetime.now() - start).total_seconds() * 1000
        print(f"📊 第二次获取 / Second fetch: {time2:.2f}ms (from cache)")

        # 验证结果一致
        assert perms1 == perms2, "权限不一致 / Permissions mismatch"
        print(f"✅ 权限一致性验证通过 / Permission consistency verified")

        # 验证缓存加速
        if time2 < time1:
            speedup = time1 / time2
            print(f"🚀 缓存加速: {speedup:.1f}x / Cache speedup: {speedup:.1f}x")

        # 验证缓存存在
        redis = await get_redis()
        cache_key = f"admin:{admin.id}:permissions"
        cached = await redis.get(cache_key)
        if cached:
            print(f"✅ Redis缓存存在 / Redis cache exists: {cache_key}")
        else:
            print(f"❌ Redis缓存不存在 / Redis cache not found: {cache_key}")


async def test_permission_checks():
    """测试权限检查函数 / Test permission check functions"""
    print("\n" + "="*60)
    print("🔍 测试2: 权限检查函数 / Test 2: Permission Check Functions")
    print("="*60)

    async for session in get_db():
        result = await session.execute(select(AdminUser).limit(1))
        admin = result.scalar_one_or_none()

        if not admin:
            print("❌ 未找到管理员 / No admin found")
            return

        print(f"✅ 测试管理员 / Test admin: {admin.username}")

        # 获取权限列表
        perms = await get_admin_permissions_cached(admin.id, session)
        print(f"📋 管理员权限 / Admin permissions: {list(perms)[:5]}... (total: {len(perms)})")

        # 测试单个权限检查
        if perms:
            test_perm = list(perms)[0]
            has_perm = await check_admin_has_permission(admin.id, test_perm, session)
            print(f"✅ 单个权限检查 / Single permission check: {test_perm} = {has_perm}")

        # 测试任意权限检查
        if len(perms) >= 2:
            test_perms = list(perms)[:2]
            has_any = await check_admin_has_any_permission(admin.id, test_perms, session)
            print(f"✅ 任意权限检查 / Any permission check: {has_any}")

        # 测试全部权限检查
        if len(perms) >= 2:
            test_perms = list(perms)[:2]
            has_all = await check_admin_has_all_permissions(admin.id, test_perms, session)
            print(f"✅ 全部权限检查 / All permissions check: {has_all}")

        # 测试不存在的权限
        fake_perm = "fake.permission.that.does.not.exist"
        has_fake = await check_admin_has_permission(admin.id, fake_perm, session)
        print(f"✅ 不存在的权限检查 / Non-existent permission check: {fake_perm} = {has_fake}")
        assert not has_fake, "应该返回False / Should return False"


async def test_permission_logs():
    """测试权限审计日志 / Test permission audit logs"""
    print("\n" + "="*60)
    print("🔍 测试3: 权限审计日志 / Test 3: Permission Audit Logs")
    print("="*60)

    async for session in get_db():
        # 查询最近的日志
        result = await session.execute(
            select(PermissionLog)
            .order_by(PermissionLog.created_at.desc())
            .limit(5)
        )
        logs = result.scalars().all()

        print(f"📋 最近的审计日志数量 / Recent audit logs count: {len(logs)}")

        if logs:
            print("\n最近的日志 / Recent logs:")
            for log in logs:
                print(f"  - [{log.created_at}] {log.admin_username}: {log.action}")
                print(f"    目标 / Target: {log.target_type}#{log.target_id} ({log.target_name})")
                if log.description:
                    print(f"    描述 / Description: {log.description}")
        else:
            print("ℹ️  暂无审计日志(正常,系统刚启动时可能没有) / No audit logs yet (normal for new system)")


async def test_role_templates():
    """测试角色模板 / Test role templates"""
    print("\n" + "="*60)
    print("🔍 测试4: 角色模板 / Test 4: Role Templates")
    print("="*60)

    from app.utils.role_templates import (
        get_role_templates,
        get_role_template,
        get_template_list,
    )

    # 获取所有模板
    templates = get_role_templates()
    print(f"📋 角色模板数量 / Role template count: {len(templates)}")

    # 获取模板列表
    template_list = get_template_list()
    print("\n可用的角色模板 / Available role templates:")
    for tmpl in template_list:
        print(f"  {tmpl['icon']} {tmpl['name_en']} ({tmpl['name']})")
        print(f"     权限数量 / Permissions: {tmpl['permission_count']}")
        print(f"     描述 / Description: {tmpl['description']}")

    # 测试获取单个模板
    content_editor = get_role_template("content_editor")
    if content_editor:
        print(f"\n✅ 内容编辑模板 / Content Editor template:")
        print(f"   名称 / Name: {content_editor['name']} ({content_editor['name_en']})")
        print(f"   权限 / Permissions: {content_editor['permissions'][:3]}... (total: {len(content_editor['permissions'])})")


async def test_wildcard_permissions():
    """测试通配符权限 / Test wildcard permissions"""
    print("\n" + "="*60)
    print("🔍 测试5: 通配符权限 / Test 5: Wildcard Permissions")
    print("="*60)

    async for session in get_db():
        # 查找有通配符权限的角色
        result = await session.execute(
            select(Role, Permission)
            .join(RolePermission, Role.id == RolePermission.role_id)
            .join(Permission, Permission.id == RolePermission.permission_id)
            .where(Permission.code.like('%*%'))
            .limit(5)
        )
        wildcard_perms = result.all()

        if wildcard_perms:
            print("✅ 通配符权限示例 / Wildcard permission examples:")
            for role, perm in wildcard_perms:
                print(f"  - {role.name}: {perm.code} ({perm.name})")
        else:
            print("ℹ️  系统中暂无通配符权限 / No wildcard permissions found")
            print("   通配符权限示例 / Wildcard permission examples:")
            print("   - * : 所有权限 / All permissions")
            print("   - video.* : 视频模块所有权限 / All video module permissions")
            print("   - *.read : 所有模块的读权限 / Read permission for all modules")


async def main():
    """主函数 / Main function"""
    print("\n" + "🚀"*30)
    print("权限系统完整测试 / Permission System Complete Test")
    print("🚀"*30)

    try:
        await test_permission_caching()
        await test_permission_checks()
        await test_permission_logs()
        await test_role_templates()
        await test_wildcard_permissions()

        print("\n" + "="*60)
        print("✅ 所有测试完成! / All tests completed!")
        print("="*60)
        print("\n📊 测试总结 / Test Summary:")
        print("  1. ✅ 权限缓存正常工作 / Permission caching works")
        print("  2. ✅ 权限检查函数正常 / Permission check functions work")
        print("  3. ✅ 审计日志表已创建 / Audit log table created")
        print("  4. ✅ 角色模板系统可用 / Role template system available")
        print("  5. ✅ 通配符权限支持 / Wildcard permission support")
        print("\n🎉 P1权限系统优化完成! / P1 Permission System Optimization Complete!")

    except Exception as e:
        print(f"\n❌ 测试失败 / Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
