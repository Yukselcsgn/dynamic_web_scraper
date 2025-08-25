"""
Customization Module

This module provides customization capabilities for the scraper, including
configuration management, user preferences, and extensibility features.
"""

from .config_manager import (
    ConfigManager,
    ScraperConfig,
    get_config,
    get_config_manager,
    get_setting,
    set_setting,
)

__all__ = [
    "ConfigManager",
    "ScraperConfig",
    "get_config_manager",
    "get_config",
    "get_setting",
    "set_setting",
]
