#!/usr/bin/env python3
"""
Plugin Manager System

This module provides a plugin system for extending the scraper with custom
functionality, allowing users to add their own data processors, validators,
and custom scraping logic.
"""

import importlib
import importlib.util
import inspect
import logging
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type


@dataclass
class PluginInfo:
    """Information about a loaded plugin."""

    name: str
    version: str
    description: str
    author: str
    plugin_type: str
    file_path: str
    loaded_at: datetime
    enabled: bool = True
    config: Dict[str, Any] = None

    def __post_init__(self):
        if self.config is None:
            self.config = {}


class BasePlugin(ABC):
    """
    Base class for all scraper plugins.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the plugin.

        Args:
            config: Plugin configuration
        """
        self.config = config or {}
        self.logger = logging.getLogger(f"plugin.{self.__class__.__name__}")

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description."""
        pass

    @property
    @abstractmethod
    def author(self) -> str:
        """Plugin author."""
        pass

    @property
    @abstractmethod
    def plugin_type(self) -> str:
        """Plugin type (data_processor, validator, custom, etc.)."""
        pass

    def initialize(self) -> bool:
        """
        Initialize the plugin. Called when the plugin is loaded.

        Returns:
            True if initialization was successful
        """
        return True

    def cleanup(self):
        """Cleanup resources when the plugin is unloaded."""
        pass


class DataProcessorPlugin(BasePlugin):
    """
    Base class for data processing plugins.
    """

    @property
    def plugin_type(self) -> str:
        return "data_processor"

    @abstractmethod
    def process_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process the scraped data.

        Args:
            data: List of scraped data items

        Returns:
            Processed data
        """
        pass


class ValidatorPlugin(BasePlugin):
    """
    Base class for data validation plugins.
    """

    @property
    def plugin_type(self) -> str:
        return "validator"

    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate a data item.

        Args:
            data: Data item to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        pass


class CustomScraperPlugin(BasePlugin):
    """
    Base class for custom scraping logic plugins.
    """

    @property
    def plugin_type(self) -> str:
        return "custom_scraper"

    @abstractmethod
    def can_handle_url(self, url: str) -> bool:
        """
        Check if this plugin can handle the given URL.

        Args:
            url: URL to check

        Returns:
            True if the plugin can handle this URL
        """
        pass

    @abstractmethod
    def scrape_url(self, url: str, html_content: str) -> List[Dict[str, Any]]:
        """
        Custom scraping logic for the URL.

        Args:
            url: URL to scrape
            html_content: HTML content of the page

        Returns:
            List of scraped data items
        """
        pass


class PluginManager:
    """
    Manages loading, unloading, and execution of plugins.
    """

    def __init__(self, plugins_directory: str = "plugins"):
        """
        Initialize the plugin manager.

        Args:
            plugins_directory: Directory containing plugin files
        """
        self.plugins_directory = Path(plugins_directory)
        self.plugins_directory.mkdir(exist_ok=True)

        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_info: Dict[str, PluginInfo] = {}
        self.plugin_modules: Dict[str, Any] = {}

        # Plugin type handlers
        self.data_processors: List[DataProcessorPlugin] = []
        self.validators: List[ValidatorPlugin] = []
        self.custom_scrapers: List[CustomScraperPlugin] = []

        self.logger = logging.getLogger("PluginManager")

    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in the plugins directory.

        Returns:
            List of discovered plugin file paths
        """
        plugin_files = []

        if not self.plugins_directory.exists():
            return plugin_files

        # Look for Python files in the plugins directory
        for file_path in self.plugins_directory.glob("*.py"):
            if file_path.name.startswith("_"):
                continue  # Skip private files

            plugin_files.append(str(file_path))

        # Also look in subdirectories
        for subdir in self.plugins_directory.iterdir():
            if subdir.is_dir() and not subdir.name.startswith("_"):
                for file_path in subdir.glob("*.py"):
                    if file_path.name.startswith("_"):
                        continue
                    plugin_files.append(str(file_path))

        self.logger.info(f"Discovered {len(plugin_files)} plugin files")
        return plugin_files

    def load_plugin(self, plugin_path: str) -> Optional[PluginInfo]:
        """
        Load a plugin from a file.

        Args:
            plugin_path: Path to the plugin file

        Returns:
            PluginInfo if successful, None otherwise
        """
        try:
            # Load the module
            module_name = f"plugin_{Path(plugin_path).stem}"
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find plugin classes in the module
            plugin_classes = []
            for name, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, BasePlugin)
                    and obj != BasePlugin
                ):
                    plugin_classes.append(obj)

            if not plugin_classes:
                self.logger.warning(f"No plugin classes found in {plugin_path}")
                return None

            # Load the first plugin class found
            plugin_class = plugin_classes[0]
            plugin_instance = plugin_class()

            # Create plugin info
            plugin_info = PluginInfo(
                name=plugin_instance.name,
                version=plugin_instance.version,
                description=plugin_instance.description,
                author=plugin_instance.author,
                plugin_type=plugin_instance.plugin_type,
                file_path=plugin_path,
                loaded_at=datetime.now(),
                config=getattr(plugin_instance, "config", {}),
            )

            # Initialize the plugin
            if not plugin_instance.initialize():
                self.logger.error(f"Failed to initialize plugin {plugin_info.name}")
                return None

            # Store the plugin
            self.plugins[plugin_info.name] = plugin_instance
            self.plugin_info[plugin_info.name] = plugin_info
            self.plugin_modules[plugin_info.name] = module

            # Register by type
            self._register_plugin_by_type(plugin_instance)

            self.logger.info(
                f"Loaded plugin: {plugin_info.name} v{plugin_info.version}"
            )
            return plugin_info

        except Exception as e:
            self.logger.error(f"Failed to load plugin from {plugin_path}: {e}")
            return None

    def _register_plugin_by_type(self, plugin: BasePlugin):
        """Register plugin by its type."""
        if isinstance(plugin, DataProcessorPlugin):
            self.data_processors.append(plugin)
        elif isinstance(plugin, ValidatorPlugin):
            self.validators.append(plugin)
        elif isinstance(plugin, CustomScraperPlugin):
            self.custom_scrapers.append(plugin)

    def load_all_plugins(self) -> List[PluginInfo]:
        """
        Load all discovered plugins.

        Returns:
            List of loaded plugin info
        """
        plugin_files = self.discover_plugins()
        loaded_plugins = []

        for plugin_path in plugin_files:
            plugin_info = self.load_plugin(plugin_path)
            if plugin_info:
                loaded_plugins.append(plugin_info)

        self.logger.info(f"Loaded {len(loaded_plugins)} plugins")
        return loaded_plugins

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin.

        Args:
            plugin_name: Name of the plugin to unload

        Returns:
            True if successful
        """
        if plugin_name not in self.plugins:
            return False

        try:
            plugin = self.plugins[plugin_name]

            # Cleanup the plugin
            plugin.cleanup()

            # Remove from type-specific lists
            if isinstance(plugin, DataProcessorPlugin):
                self.data_processors.remove(plugin)
            elif isinstance(plugin, ValidatorPlugin):
                self.validators.remove(plugin)
            elif isinstance(plugin, CustomScraperPlugin):
                self.custom_scrapers.remove(plugin)

            # Remove from main collections
            del self.plugins[plugin_name]
            del self.plugin_info[plugin_name]
            del self.plugin_modules[plugin_name]

            self.logger.info(f"Unloaded plugin: {plugin_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False

    def enable_plugin(self, plugin_name: str) -> bool:
        """
        Enable a plugin.

        Args:
            plugin_name: Name of the plugin to enable

        Returns:
            True if successful
        """
        if plugin_name in self.plugin_info:
            self.plugin_info[plugin_name].enabled = True
            self.logger.info(f"Enabled plugin: {plugin_name}")
            return True
        return False

    def disable_plugin(self, plugin_name: str) -> bool:
        """
        Disable a plugin.

        Args:
            plugin_name: Name of the plugin to disable

        Returns:
            True if successful
        """
        if plugin_name in self.plugin_info:
            self.plugin_info[plugin_name].enabled = False
            self.logger.info(f"Disabled plugin: {plugin_name}")
            return True
        return False

    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """
        Get a plugin instance.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Plugin instance or None
        """
        return self.plugins.get(plugin_name)

    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """
        Get plugin information.

        Args:
            plugin_name: Name of the plugin

        Returns:
            PluginInfo or None
        """
        return self.plugin_info.get(plugin_name)

    def list_plugins(self) -> List[PluginInfo]:
        """
        List all loaded plugins.

        Returns:
            List of plugin information
        """
        return list(self.plugin_info.values())

    def list_plugins_by_type(self, plugin_type: str) -> List[PluginInfo]:
        """
        List plugins by type.

        Args:
            plugin_type: Type of plugins to list

        Returns:
            List of plugin information
        """
        return [
            info
            for info in self.plugin_info.values()
            if info.plugin_type == plugin_type and info.enabled
        ]

    def process_data_with_plugins(
        self, data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Process data through all enabled data processor plugins.

        Args:
            data: Data to process

        Returns:
            Processed data
        """
        processed_data = data.copy()

        for processor in self.data_processors:
            plugin_info = self.plugin_info.get(processor.name)
            if plugin_info and plugin_info.enabled:
                try:
                    self.logger.debug(f"Processing data with plugin: {processor.name}")
                    processed_data = processor.process_data(processed_data)
                except Exception as e:
                    self.logger.error(f"Error in data processor {processor.name}: {e}")

        return processed_data

    def validate_data_with_plugins(
        self, data: Dict[str, Any]
    ) -> tuple[bool, List[str]]:
        """
        Validate data through all enabled validator plugins.

        Args:
            data: Data to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        all_errors = []
        is_valid = True

        for validator in self.validators:
            plugin_info = self.plugin_info.get(validator.name)
            if plugin_info and plugin_info.enabled:
                try:
                    self.logger.debug(f"Validating data with plugin: {validator.name}")
                    valid, errors = validator.validate_data(data)
                    if not valid:
                        is_valid = False
                        all_errors.extend(errors)
                except Exception as e:
                    self.logger.error(f"Error in validator {validator.name}: {e}")
                    is_valid = False
                    all_errors.append(f"Validator {validator.name} error: {e}")

        return is_valid, all_errors

    def find_custom_scraper_for_url(self, url: str) -> Optional[CustomScraperPlugin]:
        """
        Find a custom scraper plugin that can handle the given URL.

        Args:
            url: URL to find scraper for

        Returns:
            Custom scraper plugin or None
        """
        for scraper in self.custom_scrapers:
            plugin_info = self.plugin_info.get(scraper.name)
            if plugin_info and plugin_info.enabled:
                try:
                    if scraper.can_handle_url(url):
                        return scraper
                except Exception as e:
                    self.logger.error(f"Error in custom scraper {scraper.name}: {e}")

        return None

    def create_plugin_template(self, plugin_name: str, plugin_type: str) -> str:
        """
        Create a template for a new plugin.

        Args:
            plugin_name: Name for the new plugin
            plugin_type: Type of plugin (data_processor, validator, custom_scraper)

        Returns:
            Path to the created template file
        """
        template_content = self._get_plugin_template(plugin_name, plugin_type)

        # Create filename
        filename = f"{plugin_name.lower().replace(' ', '_')}.py"
        file_path = self.plugins_directory / filename

        # Write template
        with open(file_path, "w") as f:
            f.write(template_content)

        self.logger.info(f"Created plugin template: {file_path}")
        return str(file_path)

    def _get_plugin_template(self, plugin_name: str, plugin_type: str) -> str:
        """Get template content for a plugin type."""
        base_template = f'''#!/usr/bin/env python3
"""
{plugin_name} Plugin

This is a custom plugin for the Dynamic Web Scraper.
"""

from scraper.plugins.plugin_manager import {self._get_base_class(plugin_type)}


class {plugin_name.replace(' ', '')}Plugin({self._get_base_class(plugin_type)}):
    """
    {plugin_name} plugin implementation.
    """

    @property
    def name(self) -> str:
        return "{plugin_name}"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Custom {plugin_type} plugin"

    @property
    def author(self) -> str:
        return "Your Name"

    def initialize(self) -> bool:
        """
        Initialize the plugin.

        Returns:
            True if initialization was successful
        """
        # Add your initialization code here
        return True

    def cleanup(self):
        """Cleanup resources when the plugin is unloaded."""
        # Add your cleanup code here
        pass
'''

        if plugin_type == "data_processor":
            base_template += '''
    def process_data(self, data: list) -> list:
        """
        Process the scraped data.

        Args:
            data: List of scraped data items

        Returns:
            Processed data
        """
        # Add your data processing logic here
        processed_data = []

        for item in data:
            # Process each item
            processed_item = item.copy()
            # Add your processing logic here

            processed_data.append(processed_item)

        return processed_data
'''
        elif plugin_type == "validator":
            base_template += '''
    def validate_data(self, data: dict) -> tuple[bool, list]:
        """
        Validate a data item.

        Args:
            data: Data item to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Add your validation logic here
        # Example:
        # if not data.get('title'):
        #     errors.append("Missing title")

        return len(errors) == 0, errors
'''
        elif plugin_type == "custom_scraper":
            base_template += '''
    def can_handle_url(self, url: str) -> bool:
        """
        Check if this plugin can handle the given URL.

        Args:
            url: URL to check

        Returns:
            True if the plugin can handle this URL
        """
        # Add your URL matching logic here
        # Example:
        # return "example.com" in url

        return False

    def scrape_url(self, url: str, html_content: str) -> list:
        """
        Custom scraping logic for the URL.

        Args:
            url: URL to scrape
            html_content: HTML content of the page

        Returns:
            List of scraped data items
        """
        # Add your custom scraping logic here
        scraped_data = []

        # Parse HTML and extract data
        # Add your parsing logic here

        return scraped_data
'''

        return base_template

    def _get_base_class(self, plugin_type: str) -> str:
        """Get the base class name for a plugin type."""
        type_map = {
            "data_processor": "DataProcessorPlugin",
            "validator": "ValidatorPlugin",
            "custom_scraper": "CustomScraperPlugin",
        }
        return type_map.get(plugin_type, "BasePlugin")

    def shutdown(self):
        """Shutdown the plugin manager and cleanup all plugins."""
        for plugin_name in list(self.plugins.keys()):
            self.unload_plugin(plugin_name)

        self.logger.info("Plugin manager shutdown complete")
