"""
Plugin System Module

This module provides a plugin system for extending the scraper with custom
functionality, allowing users to add their own data processors, validators,
and custom scraping logic.
"""

from .plugin_manager import (
    BasePlugin,
    CustomScraperPlugin,
    DataProcessorPlugin,
    PluginInfo,
    PluginManager,
    ValidatorPlugin,
)

__all__ = [
    "PluginManager",
    "BasePlugin",
    "DataProcessorPlugin",
    "ValidatorPlugin",
    "CustomScraperPlugin",
    "PluginInfo",
]
