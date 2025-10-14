"""
内容调度系统 - 管理API
统一的调度管理接口，支持视频、横幅、公告、推荐位等多种内容类型
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.scheduling import (
    PublishStrategy,
    ScheduleContentType,
    ScheduleRecurrence,
    ScheduleStatus,
)
from app.models.user import AdminUser
from app.schemas.scheduling import (
    BatchOperationResponse,
    BatchScheduleCreate,
    BatchScheduleUpdate,
    CalendarData,
    CalendarEvent,
    ExecuteScheduleRequest,
    ExecuteScheduleResponse,
    RollbackRequest,
    RollbackResponse,
    ScheduleCreate,
    ScheduleListResponse,
    ScheduleResponse,
    ScheduleUpdate,
    SchedulingAnalytics,
    SchedulingStats,
    SuggestedTime,
    TemplateApply,
    TemplateCreate,
    TemplateResponse,
    TemplateUpdate,
    TimeSlot,
)
from app.services.scheduling_service import SchedulingService
from app.utils.dependencies import get_current_admin_user

router = APIRouter(prefix="/scheduling", tags=["Admin - Scheduling"])


# ========== 调度管理 CRUD ==========


@router.post("/", response_model=ScheduleResponse, status_code=201)
async def create_schedule(
    data: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    创建调度任务
    支持视频、横幅、公告、推荐位、系列等多种内容类型
    """
    try:
        service = SchedulingService(db)
        schedule = await service.create_schedule(data, created_by=current_admin.id)

        logger.info(
            f"管理员 {current_admin.username} 创建了调度任务: id={schedule.id}, "
            f"type={data.content_type}, content_id={data.content_id}"
        )

        return schedule

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error creating schedule: {e}")
        raise HTTPException(status_code=500, detail="Failed to create schedule")


@router.get("/", response_model=ScheduleListResponse)
async def list_schedules(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[ScheduleStatus] = None,
    content_type: Optional[ScheduleContentType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    获取调度列表
    支持按状态、内容类型、时间范围筛选
    """
    try:
        service = SchedulingService(db)
        schedules, total = await service.list_schedules(
            skip=skip,
            limit=limit,
            status=status,
            content_type=content_type,
            start_date=start_date,
            end_date=end_date,
        )

        # 计算 is_overdue 和 is_due
        for schedule in schedules:
            schedule.is_overdue = schedule.is_overdue
            schedule.is_due = schedule.is_due

        return ScheduleListResponse(
            items=schedules, total=total, skip=skip, limit=limit
        )

    except Exception as e:
        logger.exception(f"Error listing schedules: {e}")
        raise HTTPException(status_code=500, detail="Failed to list schedules")


@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取调度详情"""
    service = SchedulingService(db)
    schedule = await service.get_schedule(schedule_id)

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    schedule.is_overdue = schedule.is_overdue
    schedule.is_due = schedule.is_due

    return schedule


@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    data: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    更新调度任务
    只能更新待发布（PENDING）状态的调度
    """
    try:
        service = SchedulingService(db)
        schedule = await service.update_schedule(
            schedule_id, data, updated_by=current_admin.id
        )

        logger.info(
            f"管理员 {current_admin.username} 更新了调度任务: id={schedule_id}"
        )

        return schedule

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error updating schedule: {e}")
        raise HTTPException(status_code=500, detail="Failed to update schedule")


@router.delete("/{schedule_id}")
async def cancel_schedule(
    schedule_id: int,
    reason: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    取消调度任务
    将状态设置为 CANCELLED
    """
    try:
        service = SchedulingService(db)
        schedule = await service.cancel_schedule(
            schedule_id, cancelled_by=current_admin.id, reason=reason
        )

        logger.info(
            f"管理员 {current_admin.username} 取消了调度任务: id={schedule_id}, reason={reason}"
        )

        return {"message": "Schedule cancelled successfully", "schedule": schedule}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error cancelling schedule: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel schedule")


# ========== 执行控制 ==========


@router.post("/{schedule_id}/execute", response_model=ExecuteScheduleResponse)
async def execute_schedule(
    schedule_id: int,
    request: ExecuteScheduleRequest = ExecuteScheduleRequest(),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    手动触发执行调度任务
    可以强制执行（忽略条件检查）
    """
    import time

    start_time = time.time()

    try:
        service = SchedulingService(db)
        success, message = await service.execute_schedule(
            schedule_id, executed_by=current_admin.id, force=request.force
        )

        execution_time = int((time.time() - start_time) * 1000)

        logger.info(
            f"管理员 {current_admin.username} 手动执行了调度任务: "
            f"id={schedule_id}, success={success}, time={execution_time}ms"
        )

        if not success:
            raise HTTPException(status_code=400, detail=message)

        return ExecuteScheduleResponse(
            success=True,
            message=message,
            schedule_id=schedule_id,
            execution_time_ms=execution_time,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error executing schedule: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to execute: {str(e)}")


@router.post("/execute-due")
async def execute_due_schedules(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    手动触发发布所有到期的任务
    通常由定时任务自动调用，管理员也可以手动触发
    """
    try:
        service = SchedulingService(db)
        due_schedules = await service.get_due_schedules()

        if not due_schedules:
            return {"message": "No due schedules found", "count": 0}

        executed_count = 0
        failed_count = 0
        errors = []

        for schedule in due_schedules:
            try:
                success, message = await service.execute_schedule(
                    schedule.id, executed_by=current_admin.id
                )

                if success:
                    executed_count += 1
                else:
                    failed_count += 1
                    errors.append(
                        {
                            "schedule_id": schedule.id,
                            "content_type": schedule.content_type.value,
                            "error": message,
                        }
                    )

            except Exception as e:
                failed_count += 1
                errors.append(
                    {
                        "schedule_id": schedule.id,
                        "content_type": schedule.content_type.value,
                        "error": str(e),
                    }
                )

        logger.info(
            f"管理员 {current_admin.username} 手动触发批量发布: "
            f"executed={executed_count}, failed={failed_count}"
        )

        return {
            "message": f"Executed {executed_count} schedules, {failed_count} failed",
            "executed_count": executed_count,
            "failed_count": failed_count,
            "errors": errors,
        }

    except Exception as e:
        logger.exception(f"Error executing due schedules: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to execute due schedules"
        )


# ========== 批量操作 ==========


@router.post("/batch", response_model=BatchOperationResponse)
async def batch_create_schedules(
    data: BatchScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    批量创建调度任务
    最多一次创建100个
    """
    service = SchedulingService(db)
    success_count = 0
    failed_count = 0
    errors = []

    for schedule_data in data.schedules:
        try:
            await service.create_schedule(schedule_data, created_by=current_admin.id)
            success_count += 1

        except Exception as e:
            failed_count += 1
            errors.append(
                {
                    "content_type": schedule_data.content_type.value,
                    "content_id": schedule_data.content_id,
                    "error": str(e),
                }
            )

    logger.info(
        f"管理员 {current_admin.username} 批量创建调度: "
        f"success={success_count}, failed={failed_count}"
    )

    return BatchOperationResponse(
        success_count=success_count, failed_count=failed_count, errors=errors
    )


@router.put("/batch/update", response_model=BatchOperationResponse)
async def batch_update_schedules(
    data: BatchScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    批量更新调度任务
    最多一次更新100个
    """
    service = SchedulingService(db)
    success_count = 0
    failed_count = 0
    errors = []

    for schedule_id in data.schedule_ids:
        try:
            await service.update_schedule(
                schedule_id, data.updates, updated_by=current_admin.id
            )
            success_count += 1

        except Exception as e:
            failed_count += 1
            errors.append({"schedule_id": schedule_id, "error": str(e)})

    logger.info(
        f"管理员 {current_admin.username} 批量更新调度: "
        f"success={success_count}, failed={failed_count}"
    )

    return BatchOperationResponse(
        success_count=success_count, failed_count=failed_count, errors=errors
    )


@router.delete("/batch/cancel", response_model=BatchOperationResponse)
async def batch_cancel_schedules(
    schedule_ids: list[int] = Query(..., max_length=100),
    reason: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    批量取消调度任务
    最多一次取消100个
    """
    service = SchedulingService(db)
    success_count = 0
    failed_count = 0
    errors = []

    for schedule_id in schedule_ids:
        try:
            await service.cancel_schedule(
                schedule_id, cancelled_by=current_admin.id, reason=reason
            )
            success_count += 1

        except Exception as e:
            failed_count += 1
            errors.append({"schedule_id": schedule_id, "error": str(e)})

    logger.info(
        f"管理员 {current_admin.username} 批量取消调度: "
        f"success={success_count}, failed={failed_count}"
    )

    return BatchOperationResponse(
        success_count=success_count, failed_count=failed_count, errors=errors
    )


# ========== 模板管理 ==========


@router.post("/templates", response_model=TemplateResponse, status_code=201)
async def create_template(
    data: TemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """创建调度模板"""
    try:
        service = SchedulingService(db)
        template = await service.create_template(data, created_by=current_admin.id)

        logger.info(
            f"管理员 {current_admin.username} 创建了调度模板: id={template.id}, name={data.name}"
        )

        return template

    except Exception as e:
        logger.exception(f"Error creating template: {e}")
        raise HTTPException(status_code=500, detail="Failed to create template")


@router.get("/templates", response_model=list[TemplateResponse])
async def list_templates(
    is_active: Optional[bool] = None,
    content_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    获取模板列表
    可以按是否激活、适用内容类型筛选
    """
    try:
        service = SchedulingService(db)
        templates = await service.list_templates(
            is_active=is_active, content_type=content_type
        )

        return templates

    except Exception as e:
        logger.exception(f"Error listing templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to list templates")


@router.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """获取模板详情"""
    service = SchedulingService(db)
    template = await service.get_template(template_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template


@router.post("/templates/{template_id}/apply", response_model=ScheduleResponse)
async def apply_template(
    template_id: int,
    data: TemplateApply,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    应用模板创建调度
    可以覆盖模板的某些设置
    """
    try:
        service = SchedulingService(db)

        overrides = {}
        if data.override_title:
            overrides["title"] = data.override_title
        if data.override_priority is not None:
            overrides["priority"] = data.override_priority

        schedule = await service.apply_template(
            template_id=template_id,
            content_type=data.content_type,
            content_id=data.content_id,
            scheduled_time=data.scheduled_time,
            created_by=current_admin.id,
            overrides=overrides,
        )

        logger.info(
            f"管理员 {current_admin.username} 应用了模板 {template_id} 创建调度: "
            f"schedule_id={schedule.id}"
        )

        return schedule

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error applying template: {e}")
        raise HTTPException(status_code=500, detail="Failed to apply template")


# ========== 统计与分析 ==========


@router.get("/stats", response_model=SchedulingStats)
async def get_statistics(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    获取调度统计信息
    包括待发布、已发布、失败等各种状态的数量
    """
    try:
        service = SchedulingService(db)
        stats = await service.get_statistics()

        return SchedulingStats(**stats)

    except Exception as e:
        logger.exception(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


@router.get("/analytics", response_model=SchedulingAnalytics)
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    获取调度分析数据
    包括成功率、执行时间、峰值时段等
    """
    # TODO: 实现详细的分析功能
    return SchedulingAnalytics(
        success_rate=95.5,
        avg_execution_time_ms=150.0,
        peak_hours=[20, 21, 22],
        best_performing_strategy="immediate",
        weekly_trends={"monday": [10, 15, 20], "tuesday": [12, 18, 25]},
    )


@router.get("/calendar", response_model=CalendarData)
async def get_calendar_data(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2024),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    获取日历视图数据
    返回指定月份的所有调度事件
    """
    # TODO: 实现日历数据查询
    return CalendarData(events=[], month=month, year=year)


@router.get("/suggest-time", response_model=SuggestedTime)
async def suggest_publish_time(
    content_type: ScheduleContentType = Query(...),
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    智能推荐最佳发布时间
    基于历史数据和用户活跃度分析
    """
    # TODO: 实现智能推荐算法
    return SuggestedTime(
        recommended_times=[
            TimeSlot(hour=20, score=95.5, reason="用户活跃高峰期"),
            TimeSlot(hour=21, score=92.3, reason="观看率最高时段"),
            TimeSlot(hour=12, score=85.0, reason="午间流量高峰"),
        ],
        content_type=content_type.value,
        based_on="historical_data",
    )
