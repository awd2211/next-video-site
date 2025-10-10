"""
操作日志中间件
自动记录管理员的重要操作
"""
import json
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.database import async_session_maker
from app.models.admin import OperationLog
import re


# 需要记录日志的路由模式
LOG_PATTERNS = [
    # 视频管理
    (r"^/api/v1/admin/videos$", "POST", "video", "create", "创建视频"),
    (r"^/api/v1/admin/videos/\d+$", "PUT", "video", "update", "更新视频"),
    (r"^/api/v1/admin/videos/\d+$", "DELETE", "video", "delete", "删除视频"),
    (r"^/api/v1/admin/videos/\d+/status$", "PUT", "video", "update_status", "更新视频状态"),

    # 用户管理
    (r"^/api/v1/admin/users$", "POST", "user", "create", "创建用户"),
    (r"^/api/v1/admin/users/\d+$", "PUT", "user", "update", "更新用户信息"),
    (r"^/api/v1/admin/users/\d+$", "DELETE", "user", "delete", "删除用户"),
    (r"^/api/v1/admin/users/\d+/ban$", "POST", "user", "ban", "封禁用户"),
    (r"^/api/v1/admin/users/\d+/unban$", "POST", "user", "unban", "解封用户"),

    # 评论管理
    (r"^/api/v1/admin/comments/\d+$", "DELETE", "comment", "delete", "删除评论"),
    (r"^/api/v1/admin/comments/\d+/approve$", "POST", "comment", "approve", "审核通过评论"),
    (r"^/api/v1/admin/comments/\d+/reject$", "POST", "comment", "reject", "拒绝评论"),
    (r"^/api/v1/admin/comments/batch-delete$", "POST", "comment", "batch_delete", "批量删除评论"),

    # 分类管理
    (r"^/api/v1/admin/categories$", "POST", "category", "create", "创建分类"),
    (r"^/api/v1/admin/categories/\d+$", "PUT", "category", "update", "更新分类"),
    (r"^/api/v1/admin/categories/\d+$", "DELETE", "category", "delete", "删除分类"),

    # 公告管理
    (r"^/api/v1/admin/announcements/announcements$", "POST", "announcement", "create", "创建公告"),
    (r"^/api/v1/admin/announcements/announcements/\d+$", "PUT", "announcement", "update", "更新公告"),
    (r"^/api/v1/admin/announcements/announcements/\d+$", "DELETE", "announcement", "delete", "删除公告"),

    # 横幅管理
    (r"^/api/v1/admin/banners$", "POST", "banner", "create", "创建横幅"),
    (r"^/api/v1/admin/banners/\d+$", "PUT", "banner", "update", "更新横幅"),
    (r"^/api/v1/admin/banners/\d+$", "DELETE", "banner", "delete", "删除横幅"),

    # 系统设置
    (r"^/api/v1/admin/system-settings$", "POST", "system", "update_settings", "更新系统设置"),
    (r"^/api/v1/admin/email/config$", "PUT", "system", "update_email", "更新邮件配置"),

    # 角色权限
    (r"^/api/v1/admin/roles$", "POST", "role", "create", "创建角色"),
    (r"^/api/v1/admin/roles/\d+$", "PUT", "role", "update", "更新角色"),
    (r"^/api/v1/admin/roles/\d+$", "DELETE", "role", "delete", "删除角色"),
    (r"^/api/v1/admin/roles/\d+/permissions$", "PUT", "role", "update_permissions", "更新角色权限"),
]


def should_log_operation(path: str, method: str):
    """判断是否应该记录此操作"""
    for pattern, log_method, module, action, desc in LOG_PATTERNS:
        if method == log_method and re.match(pattern, path):
            return True, module, action, desc
    return False, None, None, None


class OperationLogMiddleware(BaseHTTPMiddleware):
    """操作日志中间件"""

    async def dispatch(self, request: Request, call_next):
        # 执行请求
        response = await call_next(request)

        # 只记录管理员API的操作
        if not request.url.path.startswith("/api/v1/admin/"):
            return response

        # 只记录特定的操作
        should_log, module, action, description = should_log_operation(
            request.url.path, request.method
        )

        if not should_log:
            return response

        # 只记录成功的操作（2xx状态码）
        if response.status_code < 200 or response.status_code >= 300:
            return response

        # 异步创建日志（不阻塞响应）
        try:
            # 从请求中获取管理员ID
            admin_user_id = None
            if hasattr(request.state, "user"):
                admin_user_id = request.state.user.id

            # 如果没有管理员ID，跳过日志记录
            if not admin_user_id:
                return response

            # 获取请求数据
            request_data = None
            if request.method in ["POST", "PUT", "PATCH"]:
                # 注意：body已经被消费了，这里无法再次读取
                # 如果需要记录请求体，需要在之前的中间件中缓存
                request_data = {"note": "Request body not captured"}

            # 创建后台任务记录日志
            async def log_operation():
                async with async_session_maker() as db:
                    log = OperationLog(
                        admin_user_id=admin_user_id,
                        module=module,
                        action=action,
                        description=description,
                        ip_address=request.client.host if request.client else None,
                        user_agent=request.headers.get("user-agent"),
                        request_method=request.method,
                        request_url=str(request.url),
                        request_data=json.dumps(request_data, ensure_ascii=False) if request_data else None,
                    )
                    db.add(log)
                    await db.commit()

            # 启动后台任务
            import asyncio
            asyncio.create_task(log_operation())

        except Exception as e:
            # 日志记录失败不应影响主业务
            print(f"Failed to log operation: {e}")

        return response
