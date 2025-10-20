"""
Analytics API - Web Vitals and Performance Monitoring
Public endpoint (no auth required) for collecting frontend metrics
"""

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.web_vitals import PagePerformance, WebVital
from app.schemas.web_vitals import (
    PagePerformanceCreate,
    WebVitalCreate,
    WebVitalResponse,
)

router = APIRouter()


@router.post("/web-vitals", response_model=WebVitalResponse)
async def record_web_vital(
    metric: WebVitalCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Record a Web Vital metric from the frontend

    This endpoint receives Core Web Vitals metrics:
    - CLS (Cumulative Layout Shift)
    - INP (Interaction to Next Paint)
    - FCP (First Contentful Paint)
    - LCP (Largest Contentful Paint)
    - TTFB (Time to First Byte)
    """
    try:
        web_vital = WebVital(
            name=metric.name,
            value=metric.value,
            rating=metric.rating,
            delta=metric.delta,
            metric_id=metric.id,
            url=metric.url,
            user_agent=metric.userAgent,
            timestamp=datetime.fromisoformat(metric.timestamp.replace("Z", "+00:00")),
        )

        db.add(web_vital)
        await db.commit()

        return WebVitalResponse()

    except Exception as e:
        # Silently fail to not disrupt user experience
        # Log error for monitoring but return success
        print(f"Failed to record Web Vital: {e}")
        return WebVitalResponse()


@router.post("/page-performance", response_model=WebVitalResponse)
async def record_page_performance(
    metrics: PagePerformanceCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Record page performance metrics from Navigation Timing API

    Captures detailed performance breakdown:
    - Page load time
    - DNS lookup time
    - TCP connection time
    - Request/response times
    - DOM processing time
    """
    try:
        performance = PagePerformance(
            url=metrics.url,
            user_agent=metrics.userAgent,
            page_load_time=metrics.pageLoadTime,
            dns_time=metrics.dnsTime,
            tcp_time=metrics.tcpTime,
            request_time=metrics.requestTime,
            response_time=metrics.responseTime,
            dom_processing=metrics.domProcessing,
            dom_content_loaded=metrics.domContentLoaded,
        )

        db.add(performance)
        await db.commit()

        return WebVitalResponse()

    except Exception as e:
        print(f"Failed to record page performance: {e}")
        return WebVitalResponse()
