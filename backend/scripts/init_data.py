"""
数据初始化脚本
创建初始管理员账户、测试用户、分类、国家等基础数据
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.user import User, AdminUser
from app.models.admin import Role, Permission, RolePermission
from app.models.video import Category, Country, Tag
from app.utils.security import get_password_hash


async def create_permissions(db: AsyncSession):
    """创建权限"""
    permissions_data = [
        {"name": "查看视频", "code": "video.read", "module": "video", "description": "查看视频列表和详情"},
        {"name": "创建视频", "code": "video.create", "module": "video", "description": "创建新视频"},
        {"name": "编辑视频", "code": "video.update", "module": "video", "description": "编辑视频信息"},
        {"name": "删除视频", "code": "video.delete", "module": "video", "description": "删除视频"},

        {"name": "查看用户", "code": "user.read", "module": "user", "description": "查看用户列表和详情"},
        {"name": "创建用户", "code": "user.create", "module": "user", "description": "创建新用户"},
        {"name": "编辑用户", "code": "user.update", "module": "user", "description": "编辑用户信息"},
        {"name": "删除用户", "code": "user.delete", "module": "user", "description": "删除用户"},

        {"name": "查看评论", "code": "comment.read", "module": "comment", "description": "查看评论列表"},
        {"name": "审核评论", "code": "comment.moderate", "module": "comment", "description": "审核评论"},
        {"name": "删除评论", "code": "comment.delete", "module": "comment", "description": "删除评论"},

        {"name": "查看系统设置", "code": "system.read", "module": "system", "description": "查看系统设置"},
        {"name": "修改系统设置", "code": "system.update", "module": "system", "description": "修改系统设置"},
    ]

    permissions = []
    for perm_data in permissions_data:
        perm = Permission(**perm_data)
        db.add(perm)
        permissions.append(perm)

    await db.flush()
    print(f"✓ 创建了 {len(permissions)} 个权限")
    return permissions


async def create_roles(db: AsyncSession, permissions: list):
    """创建角色"""
    # 超级管理员角色（所有权限）
    super_admin = Role(name="super_admin", description="超级管理员")
    db.add(super_admin)
    await db.flush()

    for perm in permissions:
        role_perm = RolePermission(role_id=super_admin.id, permission_id=perm.id)
        db.add(role_perm)

    # 普通管理员角色（部分权限）
    admin = Role(name="admin", description="管理员")
    db.add(admin)
    await db.flush()

    admin_perms = [p for p in permissions if p.module != "system"]
    for perm in admin_perms:
        role_perm = RolePermission(role_id=admin.id, permission_id=perm.id)
        db.add(role_perm)

    # 编辑角色（只能编辑内容）
    editor = Role(name="editor", description="编辑")
    db.add(editor)
    await db.flush()

    editor_perms = [p for p in permissions if "read" in p.code or p.code in ["video.create", "video.update"]]
    for perm in editor_perms:
        role_perm = RolePermission(role_id=editor.id, permission_id=perm.id)
        db.add(role_perm)

    await db.flush()
    print(f"✓ 创建了 3 个角色：超级管理员、管理员、编辑")
    return {"super_admin": super_admin, "admin": admin, "editor": editor}


async def create_admin_users(db: AsyncSession, roles: dict):
    """创建管理员账户"""
    admin_users_data = [
        {
            "username": "admin",
            "email": "admin@videosite.com",
            "password": "admin123456",
            "full_name": "系统管理员",
            "role_id": roles["super_admin"].id,
        },
        {
            "username": "editor",
            "email": "editor@videosite.com",
            "password": "editor123456",
            "full_name": "内容编辑",
            "role_id": roles["editor"].id,
        },
    ]

    for user_data in admin_users_data:
        password = user_data.pop("password")
        admin_user = AdminUser(
            **user_data,
            hashed_password=get_password_hash(password),
            is_active=True,
        )
        db.add(admin_user)

    await db.flush()
    print(f"✓ 创建了 {len(admin_users_data)} 个管理员账户")
    print("  - admin / admin123456 (超级管理员)")
    print("  - editor / editor123456 (内容编辑)")


async def create_test_users(db: AsyncSession):
    """创建测试用户"""
    test_users_data = [
        {
            "username": "testuser",
            "email": "test@example.com",
            "password": "test123456",
            "full_name": "测试用户",
        },
        {
            "username": "john",
            "email": "john@example.com",
            "password": "john123456",
            "full_name": "John Doe",
        },
    ]

    for user_data in test_users_data:
        password = user_data.pop("password")
        user = User(
            **user_data,
            hashed_password=get_password_hash(password),
            is_active=True,
        )
        db.add(user)

    await db.flush()
    print(f"✓ 创建了 {len(test_users_data)} 个测试用户")
    print("  - testuser / test123456")
    print("  - john / john123456")


async def create_categories(db: AsyncSession):
    """创建视频分类"""
    categories_data = [
        {"name": "电影", "slug": "movie", "description": "各类电影作品"},
        {"name": "电视剧", "slug": "tv-series", "description": "连续剧集"},
        {"name": "综艺", "slug": "variety", "description": "综艺节目"},
        {"name": "动漫", "slug": "anime", "description": "动画作品"},
        {"name": "纪录片", "slug": "documentary", "description": "纪录片"},
    ]

    for cat_data in categories_data:
        category = Category(**cat_data, sort_order=0)
        db.add(category)

    await db.flush()
    print(f"✓ 创建了 {len(categories_data)} 个视频分类")


async def create_countries(db: AsyncSession):
    """创建国家/地区"""
    countries_data = [
        {"name": "中国大陆", "code": "CN"},
        {"name": "中国香港", "code": "HK"},
        {"name": "中国台湾", "code": "TW"},
        {"name": "韩国", "code": "KR"},
        {"name": "日本", "code": "JP"},
        {"name": "美国", "code": "US"},
        {"name": "英国", "code": "GB"},
        {"name": "泰国", "code": "TH"},
        {"name": "印度", "code": "IN"},
        {"name": "其他", "code": "OT"},
    ]

    for country_data in countries_data:
        country = Country(**country_data)
        db.add(country)

    await db.flush()
    print(f"✓ 创建了 {len(countries_data)} 个国家/地区")


async def create_tags(db: AsyncSession):
    """创建标签"""
    tags_data = [
        ("动作", "action"), ("喜剧", "comedy"), ("爱情", "romance"), ("科幻", "scifi"),
        ("悬疑", "mystery"), ("惊悚", "thriller"), ("恐怖", "horror"), ("战争", "war"),
        ("剧情", "drama"), ("犯罪", "crime"), ("奇幻", "fantasy"), ("冒险", "adventure"),
        ("家庭", "family"), ("传记", "biography"), ("历史", "history"), ("武侠", "wuxia"),
        ("都市", "urban"), ("古装", "period"), ("校园", "school"), ("职场", "workplace"),
        ("穿越", "time-travel"), ("重生", "rebirth"), ("宫斗", "palace"), ("仙侠", "xianxia"),
        ("谍战", "spy"), ("刑侦", "detective"), ("医疗", "medical"), ("军旅", "military"),
        ("农村", "rural"), ("年代", "era"), ("青春", "youth"), ("励志", "inspirational"),
    ]

    for tag_name, slug in tags_data:
        tag = Tag(name=tag_name, slug=slug)
        db.add(tag)

    await db.flush()
    print(f"✓ 创建了 {len(tags_data)} 个标签")


async def main():
    """主函数"""
    print("=" * 60)
    print("开始初始化数据...")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        try:
            # 1. 创建权限
            print("\n[1/7] 创建权限...")
            permissions = await create_permissions(db)

            # 2. 创建角色
            print("\n[2/7] 创建角色...")
            roles = await create_roles(db, permissions)

            # 3. 创建管理员账户
            print("\n[3/7] 创建管理员账户...")
            await create_admin_users(db, roles)

            # 4. 创建测试用户
            print("\n[4/7] 创建测试用户...")
            await create_test_users(db)

            # 5. 创建视频分类
            print("\n[5/7] 创建视频分类...")
            await create_categories(db)

            # 6. 创建国家/地区
            print("\n[6/7] 创建国家/地区...")
            await create_countries(db)

            # 7. 创建标签
            print("\n[7/7] 创建标签...")
            await create_tags(db)

            # 提交所有更改
            await db.commit()

            print("\n" + "=" * 60)
            print("✓ 数据初始化完成！")
            print("=" * 60)
            print("\n登录信息：")
            print("\n【管理后台】http://localhost:3001")
            print("  超级管理员: admin / admin123456")
            print("  内容编辑:   editor / editor123456")
            print("\n【用户前端】http://localhost:3000")
            print("  测试用户:   testuser / test123456")
            print("  测试用户:   john / john123456")
            print("=" * 60)

        except Exception as e:
            await db.rollback()
            print(f"\n✗ 初始化失败: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
