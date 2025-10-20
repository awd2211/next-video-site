"""
Web Vitals and Performance Metrics Model
Stores real user monitoring (RUM) data from frontend
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.database import Base


class WebVital(Base):
    """
    Stores Web Vitals metrics (CLS, INP, FCP, LCP, TTFB)
    Following Google's Core Web Vitals standards
    """

    __tablename__ = "web_vitals"

    id = Column(Integer, primary_key=True, index=True)

    # Metric details
    name = Column(String(50), nullable=False, index=True)  # CLS, INP, FCP, LCP, TTFB
    value = Column(Float, nullable=False)  # Metric value in ms or score
    rating = Column(String(20))  # good, needs-improvement, poor
    delta = Column(Float, nullable=True)  # Change from previous measurement
    metric_id = Column(String(100), nullable=True)  # Unique ID for this metric instance

    # Context
    url = Column(Text, nullable=False)  # Page URL where metric was captured
    user_agent = Column(Text, nullable=True)  # Browser/device info

    # Timestamps
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self):
        return f"<WebVital {self.name}={self.value:.2f} ({self.rating})>"


class PagePerformance(Base):
    """
    Stores detailed page performance metrics
    Using Navigation Timing API data
    """

    __tablename__ = "page_performance"

    id = Column(Integer, primary_key=True, index=True)

    # Page info
    url = Column(Text, nullable=False, index=True)
    user_agent = Column(Text, nullable=True)

    # Performance timing metrics (all in milliseconds)
    page_load_time = Column(Float, nullable=True)  # Total page load
    dns_time = Column(Float, nullable=True)  # DNS lookup duration
    tcp_time = Column(Float, nullable=True)  # TCP connection time
    request_time = Column(Float, nullable=True)  # Request duration
    response_time = Column(Float, nullable=True)  # Response duration
    dom_processing = Column(Float, nullable=True)  # DOM processing time
    dom_content_loaded = Column(Float, nullable=True)  # DOMContentLoaded time

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    def __repr__(self):
        return f"<PagePerformance url={self.url[:50]} load_time={self.page_load_time:.2f}ms>"
