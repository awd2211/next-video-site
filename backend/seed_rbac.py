"""
RBAC 种子数据脚本
用于初始化角色和权限数据
"""
import asyncio
from sqlalchemy import select
from app.database import async_session_maker
from app.models.admin import Permission, Role, RolePermission
from loguru import logger


# 定义权限数据
PERMISSIONS = [
    # 视频管理权限
    {"name": "查看视频", "code": "video.view", "module": "video", "description": "查看视频列表和详情"},
    {"name": "创建视频", "code": "video.create", "module": "video", "description": "上传和创建新视频"},
    {"name": "编辑视频", "code": "video.update", "module": "video", "description": "编辑视频信息"},
    {"name": "删除视频", "code": "video.delete", "module": "video", "description": "删除视频"},
    {"name": "视频审核", "code": "video.review", "module": "video", "description": "审核待发布的视频"},
    {"name": "视频转码", "code": "video.transcode", "module": "video", "description": "管理视频转码任务"},

    # 用户管理权限
    {"name": "查看用户", "code": "user.view", "module": "user", "description": "查看用户列表和详情"},
    {"name": "编辑用户", "code": "user.update", "module": "user", "description": "编辑用户信息"},
    {"name": "删除用户", "code": "user.delete", "module": "user", "description": "删除用户账号"},
    {"name": "封禁用户", "code": "user.ban", "module": "user", "description": "封禁和解封用户"},
    {"name": "用户VIP管理", "code": "user.vip", "module": "user", "description": "管理用户VIP状态"},

    # 评论管理权限
    {"name": "查看评论", "code": "comment.view", "module": "comment", "description": "查看评论列表"},
    {"name": "审核评论", "code": "comment.moderate", "module": "comment", "description": "审核、删除评论"},
    {"name": "置顶评论", "code": "comment.pin", "module": "comment", "description": "置顶评论"},

    # 分类和标签权限
    {"name": "管理分类", "code": "category.manage", "module": "category", "description": "创建、编辑、删除分类"},
    {"name": "管理标签", "code": "tag.manage", "module": "tag", "description": "创建、编辑、删除标签"},
    {"name": "管理演员", "code": "actor.manage", "module": "actor", "description": "管理演员信息"},
    {"name": "管理导演", "code": "director.manage", "module": "director", "description": "管理导演信息"},

    # 内容管理权限
    {"name": "管理公告", "code": "announcement.manage", "module": "announcement", "description": "创建和管理系统公告"},
    {"name": "管理横幅", "code": "banner.manage", "module": "banner", "description": "管理首页横幅广告"},
    {"name": "管理推荐", "code": "recommendation.manage", "module": "recommendation", "description": "管理推荐内容"},

    # 系统管理权限
    {"name": "查看日志", "code": "log.view", "module": "system", "description": "查看系统操作日志"},
    {"name": "查看统计", "code": "stats.view", "module": "system", "description": "查看统计数据"},
    {"name": "系统设置", "code": "settings.manage", "module": "system", "description": "修改系统设置"},
    {"name": "系统健康监控", "code": "health.view", "module": "system", "description": "查看系统健康状态"},
    {"name": "AI管理", "code": "ai.manage", "module": "system", "description": "管理AI服务配置"},

    # RBAC权限管理
    {"name": "管理角色", "code": "role.manage", "module": "rbac", "description": "创建、编辑、删除角色"},
    {"name": "管理权限", "code": "permission.manage", "module": "rbac", "description": "管理权限定义"},
    {"name": "分配角色", "code": "role.assign", "module": "rbac", "description": "为管理员分配角色"},

    # 报表权限
    {"name": "查看报表", "code": "report.view", "module": "report", "description": "查看各类统计报表"},
    {"name": "导出报表", "code": "report.export", "module": "report", "description": "导出报表数据"},

    # OAuth管理
    {"name": "OAuth设置", "code": "oauth.manage", "module": "oauth", "description": "管理OAuth第三方登录配置"},
]


# 定义角色数据
ROLES = [
    {
        "name": "内容管理员",
        "description": "负责视频内容的日常管理和审核",
        "permissions": [
            "video.view", "video.create", "video.update", "video.review",
            "comment.view", "comment.moderate",
            "category.manage", "tag.manage", "actor.manage", "director.manage",
            "announcement.manage", "banner.manage",
            "stats.view",
        ]
    },
    {
        "name": "用户管理员",
        "description": "负责用户管理和客服工作",
        "permissions": [
            "user.view", "user.update", "user.ban", "user.vip",
            "comment.view", "comment.moderate",
            "stats.view", "log.view",
        ]
    },
    {
        "name": "运营管理员",
        "description": "负责运营推广和内容策划",
        "permissions": [
            "video.view", "video.update", "video.review",
            "recommendation.manage", "banner.manage", "announcement.manage",
            "stats.view", "report.view", "report.export",
        ]
    },
    {
        "name": "技术管理员",
        "description": "负责系统维护和技术支持",
        "permissions": [
            "video.view", "video.transcode",
            "log.view", "stats.view", "health.view",
            "settings.manage", "ai.manage",
        ]
    },
    {
        "name": "高级管理员",
        "description": "拥有大部分管理权限",
        "permissions": [
            "video.view", "video.create", "video.update", "video.delete", "video.review", "video.transcode",
            "user.view", "user.update", "user.ban", "user.vip",
            "comment.view", "comment.moderate", "comment.pin",
            "category.manage", "tag.manage", "actor.manage", "director.manage",
            "announcement.manage", "banner.manage", "recommendation.manage",
            "log.view", "stats.view", "report.view", "report.export",
            "settings.manage", "health.view", "ai.manage", "oauth.manage",
        ]
    },
    {
        "name": "只读管理员",
        "description": "仅具有查看权限，无修改权限",
        "permissions": [
            "video.view", "user.view", "comment.view",
            "log.view", "stats.view", "report.view", "health.view",
        ]
    },
]


async def seed_permissions(session):
    """创建权限数据"""
    logger.info("开始创建权限数据...")

    created_count = 0
    existing_count = 0

    for perm_data in PERMISSIONS:
        # 检查权限是否已存在
        result = await session.execute(
            select(Permission).where(Permission.code == perm_data["code"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            logger.debug(f"权限已存在: {perm_data['code']}")
            existing_count += 1
            continue

        # 创建新权限
        permission = Permission(**perm_data)
        session.add(permission)
        created_count += 1
        logger.info(f"创建权限: {perm_data['name']} ({perm_data['code']})")

        # 每次添加后立即提交，避免批量插入时的唯一约束冲突
        try:
            await session.commit()
        except Exception as e:
            logger.warning(f"提交权限 {perm_data['code']} 时出错: {e}")
            await session.rollback()
            existing_count += 1
            created_count -= 1

    logger.success(f"权限数据创建完成！新增: {created_count}, 已存在: {existing_count}")


async def seed_roles(session):
    """创建角色数据"""
    logger.info("开始创建角色数据...")

    # 获取所有权限，建立code到id的映射
    result = await session.execute(select(Permission))
    permissions = result.scalars().all()
    permission_map = {p.code: p.id for p in permissions}

    created_count = 0
    existing_count = 0

    for role_data in ROLES:
        # 检查角色是否已存在
        result = await session.execute(
            select(Role).where(Role.name == role_data["name"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            logger.debug(f"角色已存在: {role_data['name']}")
            existing_count += 1
            continue

        # 创建新角色
        role = Role(
            name=role_data["name"],
            description=role_data["description"],
            is_active=True
        )
        session.add(role)
        await session.flush()  # 获取role.id

        # 分配权限
        for perm_code in role_data["permissions"]:
            if perm_code in permission_map:
                role_perm = RolePermission(
                    role_id=role.id,
                    permission_id=permission_map[perm_code]
                )
                session.add(role_perm)
            else:
                logger.warning(f"权限不存在: {perm_code}")

        created_count += 1
        logger.info(f"创建角色: {role_data['name']} (权限数: {len(role_data['permissions'])})")

    await session.commit()
    logger.success(f"角色数据创建完成！新增: {created_count}, 已存在: {existing_count}")


async def main():
    """主函数"""
    logger.info("="*60)
    logger.info("开始初始化RBAC数据")
    logger.info("="*60)

    async with async_session_maker() as session:
        try:
            # 创建权限
            await seed_permissions(session)

            # 创建角色
            await seed_roles(session)

            logger.info("="*60)
            logger.success("RBAC数据初始化完成！")
            logger.info("="*60)

            # 显示统计信息
            result = await session.execute(select(Permission))
            perm_count = len(result.scalars().all())

            result = await session.execute(select(Role))
            role_count = len(result.scalars().all())

            logger.info(f"当前系统中共有 {perm_count} 个权限，{role_count} 个角色")

        except Exception as e:
            logger.error(f"初始化失败: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
