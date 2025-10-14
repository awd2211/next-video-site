"""
角色模板系统
预定义常用角色配置,快速创建角色
"""

from typing import Dict, List

# 角色模板定义
ROLE_TEMPLATES: Dict[str, dict] = {
    "content_editor": {
        "name": "内容编辑",
        "name_en": "Content Editor",
        "description": "负责视频内容的创建、编辑和管理",
        "permissions": [
            # 视频管理
            "video.create",
            "video.read",
            "video.update",
            # 演员导演管理
            "actor.manage",
            "director.manage",
            # 标签分类管理
            "tag.manage",
            "category.manage",
            # 系列管理
            # "series.manage",  # 如果有此权限
        ],
        "icon": "✏️",
        "color": "#1890ff",
    },
    "content_moderator": {
        "name": "内容审核员",
        "name_en": "Content Moderator",
        "description": "负责内容审核和评论管理",
        "permissions": [
            # 视频审核
            "video.read",
            "video.review",
            # 评论管理
            "comment.read",
            "comment.moderate",
            "comment.delete",
            "comment.pin",
            # 用户查看
            "user.read",
        ],
        "icon": "🔍",
        "color": "#52c41a",
    },
    "user_manager": {
        "name": "用户管理员",
        "name_en": "User Manager",
        "description": "负责用户管理和权限分配",
        "permissions": [
            # 用户管理
            "user.read",
            "user.create",
            "user.update",
            "user.ban",
            "user.vip",
            # 评论查看
            "comment.read",
        ],
        "icon": "👥",
        "color": "#722ed1",
    },
    "system_admin": {
        "name": "系统管理员",
        "name_en": "System Administrator",
        "description": "负责系统设置和配置管理",
        "permissions": [
            # 系统设置
            "system.read",
            "system.update",
            "settings.manage",
            # 日志查看
            "log.view",
            # 统计查看
            "stats.view",
            # AI管理
            "ai.manage",
            # 系统健康
            "health.view",
        ],
        "icon": "⚙️",
        "color": "#fa8c16",
    },
    "operations_manager": {
        "name": "运营管理",
        "name_en": "Operations Manager",
        "description": "负责运营内容管理(横幅、公告、推荐)",
        "permissions": [
            # 运营内容
            "banner.manage",
            "announcement.manage",
            "recommendation.manage",
            # OAuth设置
            "oauth.manage",
            # 报表查看
            "report.view",
            "report.export",
            # 统计查看
            "stats.view",
        ],
        "icon": "📊",
        "color": "#eb2f96",
    },
    "viewer": {
        "name": "只读查看员",
        "name_en": "Viewer",
        "description": "只能查看内容,不能进行修改操作",
        "permissions": [
            # 只读权限
            "video.read",
            "user.read",
            "comment.read",
            "system.read",
            "stats.view",
            "log.view",
        ],
        "icon": "👁️",
        "color": "#13c2c2",
    },
    "full_admin": {
        "name": "完整管理员",
        "name_en": "Full Administrator",
        "description": "拥有除超级管理员外的所有权限",
        "permissions": [
            # 视频管理(全部)
            "video.create",
            "video.read",
            "video.update",
            "video.delete",
            "video.review",
            "video.transcode",
            # 用户管理(全部)
            "user.create",
            "user.read",
            "user.update",
            "user.delete",
            "user.ban",
            "user.vip",
            # 评论管理(全部)
            "comment.read",
            "comment.delete",
            "comment.moderate",
            "comment.pin",
            # 内容管理
            "actor.manage",
            "director.manage",
            "tag.manage",
            "category.manage",
            "banner.manage",
            "announcement.manage",
            "recommendation.manage",
            # 系统管理
            "system.read",
            "system.update",
            "settings.manage",
            "log.view",
            "stats.view",
            "ai.manage",
            "health.view",
            "report.view",
            "report.export",
            "oauth.manage",
        ],
        "icon": "👑",
        "color": "#f5222d",
    },
}


def get_role_templates() -> Dict[str, dict]:
    """获取所有角色模板"""
    return ROLE_TEMPLATES


def get_role_template(template_key: str) -> dict:
    """获取指定的角色模板"""
    return ROLE_TEMPLATES.get(template_key, {})


def get_template_permissions(template_key: str) -> List[str]:
    """获取模板的权限列表"""
    template = get_role_template(template_key)
    return template.get("permissions", [])


def expand_wildcard_permissions(permissions: List[str], all_permissions: List[str]) -> List[str]:
    """
    展开通配符权限

    Args:
        permissions: 包含通配符的权限列表
        all_permissions: 所有可用权限列表

    Returns:
        展开后的权限列表
    """
    expanded = []

    for perm in permissions:
        if "*" not in perm:
            # 非通配符,直接添加
            expanded.append(perm)
        elif perm == "*":
            # 所有权限
            expanded.extend(all_permissions)
        elif perm.endswith(".*"):
            # 模块级通配符 (video.*)
            module = perm[:-2]
            matching = [p for p in all_permissions if p.startswith(f"{module}.")]
            expanded.extend(matching)
        elif perm.startswith("*."):
            # 操作级通配符 (*.read)
            operation = perm[2:]
            matching = [p for p in all_permissions if p.endswith(f".{operation}")]
            expanded.extend(matching)

    # 去重并排序
    return sorted(list(set(expanded)))


def get_template_list() -> List[dict]:
    """
    获取模板列表(用于前端显示)

    Returns:
        [
            {
                "key": "content_editor",
                "name": "内容编辑",
                "name_en": "Content Editor",
                "description": "...",
                "permission_count": 7,
                "icon": "✏️",
                "color": "#1890ff"
            },
            ...
        ]
    """
    return [
        {
            "key": key,
            "name": template["name"],
            "name_en": template.get("name_en", template["name"]),
            "description": template["description"],
            "permission_count": len(template["permissions"]),
            "icon": template.get("icon", "🔧"),
            "color": template.get("color", "#1890ff"),
        }
        for key, template in ROLE_TEMPLATES.items()
    ]


def validate_template_permissions(template_key: str, available_permissions: List[str]) -> dict:
    """
    验证模板权限是否有效

    Args:
        template_key: 模板key
        available_permissions: 系统中可用的权限列表

    Returns:
        {
            "valid": True/False,
            "missing_permissions": [...],
            "available_permissions": [...]
        }
    """
    template = get_role_template(template_key)
    if not template:
        return {"valid": False, "error": "模板不存在"}

    template_perms = set(template["permissions"])
    available_perms = set(available_permissions)

    # 找出模板中不存在的权限
    missing = template_perms - available_perms

    return {
        "valid": len(missing) == 0,
        "missing_permissions": list(missing),
        "available_permissions": list(template_perms & available_perms),
    }
