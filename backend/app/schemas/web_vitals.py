"""
Web Vitals Pydantic Schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WebVitalCreate(BaseModel):
    """Web Vital metric from frontend"""

    name: str = Field(..., description="Metric name (CLS, INP, FCP, LCP, TTFB)")
    value: float = Field(..., description="Metric value")
    rating: str = Field(..., description="Performance rating")
    delta: Optional[float] = Field(None, description="Delta from previous")
    id: Optional[str] = Field(None, description="Metric instance ID")
    url: str = Field(..., description="Page URL")
    userAgent: str = Field(..., description="User agent string")
    timestamp: str = Field(..., description="ISO timestamp")


class PagePerformanceCreate(BaseModel):
    """Page performance metrics from Navigation Timing API"""

    url: str
    userAgent: Optional[str] = None
    pageLoadTime: Optional[float] = None
    dnsTime: Optional[float] = None
    tcpTime: Optional[float] = None
    requestTime: Optional[float] = None
    responseTime: Optional[float] = None
    domProcessing: Optional[float] = None
    domContentLoaded: Optional[float] = None


class WebVitalResponse(BaseModel):
    """Response after storing Web Vital"""

    success: bool = True
    message: str = "Metric recorded successfully"

    model_config = {"from_attributes": True}
