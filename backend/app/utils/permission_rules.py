"""
权限规则引擎 / Permission Rules Engine

提供权限验证规则、冲突检测、依赖检查等功能
Provides permission validation rules, conflict detection, dependency checking, etc.
"""

from typing import List, Dict, Set, Tuple


# 权限冲突规则 / Permission Conflict Rules
# 定义互斥的权限组合 / Define mutually exclusive permission combinations
PERMISSION_CONFLICTS: List[Tuple[str, str]] = [
    # 只读与编辑权限冲突 / Read-only conflicts with edit permissions
    ("video.read_only", "video.update"),
    ("video.read_only", "video.delete"),
    ("user.view_only", "user.update"),
    ("user.view_only", "user.delete"),

    # 临时封禁与永久封禁冲突 / Temporary ban conflicts with permanent ban
    ("user.ban.temporary", "user.ban.permanent"),
]


# 权限依赖规则 / Permission Dependency Rules
# 格式: (依赖权限, 必需权限) / Format: (dependent permission, required permission)
PERMISSION_DEPENDENCIES: List[Tuple[str, str]] = [
    # 视频权限依赖 / Video permission dependencies
    ("video.create", "video.read"),
    ("video.update", "video.read"),
    ("video.update.basic", "video.read"),
    ("video.update.status", "video.read"),
    ("video.update.sensitive", "video.read"),
    ("video.delete", "video.read"),
    ("video.delete.all", "video.read"),
    ("video.delete.own", "video.read"),
    ("video.review", "video.read"),

    # 用户权限依赖 / User permission dependencies
    ("user.update", "user.read"),
    ("user.delete", "user.read"),
    ("user.ban", "user.read"),
    ("user.ban.temporary", "user.read"),
    ("user.ban.permanent", "user.read"),

    # 评论权限依赖 / Comment permission dependencies
    ("comment.update", "comment.read"),
    ("comment.delete", "comment.read"),
    ("comment.moderate", "comment.read"),

    # 系统管理权限依赖 / System management permission dependencies
    ("settings.update", "settings.read"),
    ("ai.update", "ai.read"),
]


# 权限推荐规则 / Permission Recommendation Rules
# 当拥有某权限时，建议同时拥有的其他权限 / When having a permission, suggest other permissions
PERMISSION_RECOMMENDATIONS: Dict[str, List[str]] = {
    "video.create": ["video.read", "video.update.basic", "tag.manage", "category.manage"],
    "video.review": ["video.read", "video.update.status", "comment.read"],
    "video.delete": ["video.read"],

    "user.ban": ["user.read", "comment.read", "log.view"],
    "user.ban.temporary": ["user.read", "comment.read"],
    "user.ban.permanent": ["user.read", "comment.read", "log.view"],

    "comment.moderate": ["comment.read", "comment.delete", "user.read"],
    "comment.delete": ["comment.read"],

    "system.manage": ["settings.read", "log.view", "stats.view", "health.view"],
    "settings.update": ["settings.read", "log.view"],
}


# 细粒度权限定义 / Fine-grained Permission Definitions
FINE_GRAINED_PERMISSIONS = {
    # 视频权限细分 / Video permission breakdown
    "video": {
        "video.read": "查看视频",
        "video.read_only": "只读模式(不能修改)",
        "video.create": "创建视频",
        "video.update": "更新视频(所有字段)",
        "video.update.basic": "更新基本信息(标题、描述、封面)",
        "video.update.status": "更新状态(发布、下架、推荐)",
        "video.update.sensitive": "更新敏感信息(分类、标签、年龄限制)",
        "video.delete": "删除视频(所有)",
        "video.delete.own": "删除自己创建的视频",
        "video.delete.all": "删除所有视频(包括他人)",
        "video.review": "审核视频",
        "video.import": "批量导入视频",
        "video.export": "导出视频数据",
    },

    # 用户权限细分 / User permission breakdown
    "user": {
        "user.read": "查看用户",
        "user.view_only": "只读模式(不能修改)",
        "user.create": "创建用户",
        "user.update": "更新用户信息",
        "user.update.basic": "更新基本信息",
        "user.update.sensitive": "更新敏感信息(邮箱、手机)",
        "user.delete": "删除用户",
        "user.ban": "封禁用户",
        "user.ban.temporary": "临时封禁用户",
        "user.ban.permanent": "永久封禁用户",
        "user.unban": "解封用户",
    },

    # 评论权限细分 / Comment permission breakdown
    "comment": {
        "comment.read": "查看评论",
        "comment.create": "发表评论",
        "comment.update": "编辑评论",
        "comment.delete": "删除评论",
        "comment.delete.own": "删除自己的评论",
        "comment.delete.all": "删除所有评论",
        "comment.moderate": "审核评论",
        "comment.pin": "置顶评论",
    },

    # 系统权限细分 / System permission breakdown
    "system": {
        "system.read": "查看系统信息",
        "system.manage": "管理系统",
        "system.backup": "备份系统",
        "system.restore": "恢复系统",
        "system.maintenance": "系统维护模式",
    },

    # 设置权限细分 / Settings permission breakdown
    "settings": {
        "settings.read": "查看设置",
        "settings.update": "更新设置",
        "settings.update.basic": "更新基本设置",
        "settings.update.security": "更新安全设置",
        "settings.update.email": "更新邮件设置",
    },
}


def validate_permissions(permission_codes: List[str]) -> Dict:
    """
    验证权限组合的有效性
    Validate permission combination validity

    Args:
        permission_codes: 权限代码列表 / List of permission codes

    Returns:
        dict: 包含验证结果、冲突、缺失依赖和推荐 / Contains validation results, conflicts, missing dependencies, and recommendations
    """
    perm_set = set(permission_codes)
    conflicts = []
    missing_dependencies = []
    recommendations = []

    # 检查权限冲突 / Check permission conflicts
    for p1, p2 in PERMISSION_CONFLICTS:
        if p1 in perm_set and p2 in perm_set:
            conflicts.append({
                "permission1": p1,
                "permission2": p2,
                "message": f"权限冲突: {p1} 与 {p2} 不能同时拥有"
            })

    # 检查权限依赖 / Check permission dependencies
    for dependent, required in PERMISSION_DEPENDENCIES:
        if dependent in perm_set and required not in perm_set:
            # 检查是否有通配符满足 / Check if wildcard satisfies
            module = required.split(".")[0]
            if f"{module}.*" not in perm_set and "*" not in perm_set:
                missing_dependencies.append({
                    "permission": dependent,
                    "requires": required,
                    "message": f"{dependent} 需要 {required} 权限"
                })

    # 生成权限推荐 / Generate permission recommendations
    for perm in perm_set:
        if perm in PERMISSION_RECOMMENDATIONS:
            recommended = PERMISSION_RECOMMENDATIONS[perm]
            missing_recommended = []

            for rec in recommended:
                # 检查是否已拥有(精确匹配或通配符) / Check if already has (exact match or wildcard)
                if rec not in perm_set:
                    module = rec.split(".")[0]
                    if f"{module}.*" not in perm_set and "*" not in perm_set:
                        missing_recommended.append(rec)

            if missing_recommended:
                recommendations.append({
                    "for_permission": perm,
                    "recommended": missing_recommended,
                    "reason": "这些权限通常一起使用，建议添加以获得完整功能"
                })

    # 判断是否有效 / Determine if valid
    is_valid = len(conflicts) == 0 and len(missing_dependencies) == 0

    return {
        "valid": is_valid,
        "conflicts": conflicts,
        "missing_dependencies": missing_dependencies,
        "recommendations": recommendations,
        "total_permissions": len(permission_codes),
        "message": "权限配置有效" if is_valid else "权限配置存在问题，请检查冲突和依赖"
    }


def check_permission_conflict(perm1: str, perm2: str) -> bool:
    """
    检查两个权限是否冲突
    Check if two permissions conflict

    Args:
        perm1: 权限1 / Permission 1
        perm2: 权限2 / Permission 2

    Returns:
        bool: 是否冲突 / Whether they conflict
    """
    return (perm1, perm2) in PERMISSION_CONFLICTS or (perm2, perm1) in PERMISSION_CONFLICTS


def get_required_permissions(permission: str) -> List[str]:
    """
    获取某权限所需的所有依赖权限
    Get all required permissions for a given permission

    Args:
        permission: 权限代码 / Permission code

    Returns:
        List[str]: 依赖权限列表 / List of required permissions
    """
    required = []
    for dependent, req in PERMISSION_DEPENDENCIES:
        if dependent == permission:
            required.append(req)
    return required


def get_recommended_permissions(permission: str) -> List[str]:
    """
    获取某权限的推荐权限
    Get recommended permissions for a given permission

    Args:
        permission: 权限代码 / Permission code

    Returns:
        List[str]: 推荐权限列表 / List of recommended permissions
    """
    return PERMISSION_RECOMMENDATIONS.get(permission, [])


def expand_wildcard_permissions(permissions: Set[str], all_permissions: List[str]) -> Set[str]:
    """
    展开通配符权限
    Expand wildcard permissions

    Args:
        permissions: 权限集合(可能包含通配符) / Permission set (may contain wildcards)
        all_permissions: 所有可用权限列表 / List of all available permissions

    Returns:
        Set[str]: 展开后的权限集合 / Expanded permission set
    """
    expanded = set()

    for perm in permissions:
        if perm == "*":
            # 全部权限 / All permissions
            expanded.update(all_permissions)
        elif perm.endswith(".*"):
            # 模块级通配符 / Module-level wildcard
            module = perm[:-2]
            expanded.update([p for p in all_permissions if p.startswith(f"{module}.")])
        else:
            # 普通权限 / Regular permission
            expanded.add(perm)

    return expanded


def get_permission_hierarchy() -> Dict:
    """
    获取权限层级结构
    Get permission hierarchy structure

    Returns:
        Dict: 权限层级树 / Permission hierarchy tree
    """
    hierarchy = {}

    for module, perms in FINE_GRAINED_PERMISSIONS.items():
        hierarchy[module] = {
            "name": module,
            "permissions": []
        }

        for code, desc in perms.items():
            parts = code.split(".")
            hierarchy[module]["permissions"].append({
                "code": code,
                "description": desc,
                "level": len(parts),
                "parent": ".".join(parts[:-1]) if len(parts) > 2 else module
            })

    return hierarchy


def suggest_permission_template(role_type: str) -> List[str]:
    """
    根据角色类型推荐权限模板
    Suggest permission template based on role type

    Args:
        role_type: 角色类型 / Role type

    Returns:
        List[str]: 推荐的权限列表 / List of recommended permissions
    """
    templates = {
        "content_creator": [
            "video.read", "video.create", "video.update.basic", "video.delete.own",
            "tag.manage", "category.manage", "actor.manage", "director.manage"
        ],
        "content_moderator": [
            "video.read", "video.review", "video.update.status",
            "comment.read", "comment.moderate", "comment.delete",
            "user.read", "user.ban.temporary"
        ],
        "user_manager": [
            "user.read", "user.update", "user.ban", "user.unban",
            "comment.read", "log.view"
        ],
        "system_admin": [
            "system.*", "settings.*", "log.view", "stats.view", "health.view", "ai.manage"
        ],
        "viewer": [
            "video.read", "user.read", "comment.read", "stats.view", "log.view"
        ]
    }

    return templates.get(role_type, [])
