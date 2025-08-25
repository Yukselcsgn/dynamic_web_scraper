"""
Reporting Module

This module provides automated reporting and alerting capabilities for the Dynamic Web Scraper,
including scheduled reports, email notifications, and alert management.
"""

from .automated_reporter import AlertConfig, AutomatedReporter, ReportConfig

__all__ = ["AutomatedReporter", "AlertConfig", "ReportConfig"]
