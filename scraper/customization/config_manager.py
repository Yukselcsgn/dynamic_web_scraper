#!/usr/bin/env python3
"""
Configuration Manager

This module provides a comprehensive configuration management system that allows
users to customize the scraper behavior through configuration files, environment
variables, and runtime settings.
"""

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import toml
import yaml


@dataclass
class ScraperConfig:
    """Main configuration class for the scraper."""

    # Basic settings
    name: str = "Dynamic Web Scraper"
    version: str = "2.2.0"
    debug_mode: bool = False
    test_mode: bool = False

    # Logging settings
    log_level: str = "INFO"
    log_file: str = "logs/scraper.log"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_rotation: bool = True
    log_max_size: int = 10 * 1024 * 1024  # 10MB
    log_backup_count: int = 5

    # Request settings
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 2.0
    rate_limiting: bool = True
    requests_per_minute: int = 60

    # User agent and proxy settings
    user_agent_rotation: bool = True
    proxy_rotation: bool = False
    use_proxy: bool = False
    proxy_timeout: int = 10

    # Selenium settings
    selenium_timeout: int = 30
    headless: bool = True
    browser_window_size: str = "1920x1080"

    # Data processing settings
    enable_smart_detection: bool = True
    enable_data_enrichment: bool = True
    enable_price_analysis: bool = True
    enable_plugin_system: bool = True

    # Output settings
    output_formats: List[str] = field(default_factory=lambda: ["csv", "json"])
    default_output_format: str = "csv"
    output_directory: str = "data"
    create_backup: bool = True

    # Anti-bot settings
    stealth_mode: bool = True
    humanize_timing: bool = True
    browser_fingerprint: bool = True
    session_persistence: bool = True

    # Distributed settings
    enable_distributed: bool = False
    num_workers: int = 4
    job_queue_path: str = "data/job_queue"
    max_jobs_per_worker: int = 100

    # Plugin settings
    plugins_directory: str = "plugins"
    auto_load_plugins: bool = True
    plugin_config: Dict[str, Any] = field(default_factory=dict)

    # Custom settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScraperConfig":
        """Create config from dictionary."""
        return cls(**data)


class ConfigManager:
    """
    Manages configuration loading, validation, and customization.
    """

    def __init__(self, config_file: str = "config.json"):
        """
        Initialize the configuration manager.

        Args:
            config_file: Path to the main configuration file
        """
        self.config_file = Path(config_file)
        self.config = ScraperConfig()
        self.logger = logging.getLogger("ConfigManager")

        # Configuration sources (in order of precedence)
        self.config_sources = []

        # Load configuration
        self.load_configuration()

    def load_configuration(self):
        """Load configuration from all sources."""
        # 1. Load default configuration
        self._load_default_config()

        # 2. Load from config file
        if self.config_file.exists():
            self._load_from_file(self.config_file)

        # 3. Load from environment variables
        self._load_from_environment()

        # 4. Load from user config directory
        self._load_user_config()

        # 5. Validate configuration
        self._validate_config()

        self.logger.info("Configuration loaded successfully")

    def _load_default_config(self):
        """Load default configuration."""
        self.config = ScraperConfig()
        self.config_sources.append("default")

    def _load_from_file(self, file_path: Path):
        """Load configuration from a file."""
        try:
            if file_path.suffix.lower() == ".json":
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            elif file_path.suffix.lower() in [".yml", ".yaml"]:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
            elif file_path.suffix.lower() == ".toml":
                with open(file_path, "r", encoding="utf-8") as f:
                    data = toml.load(f)
            else:
                self.logger.warning(
                    f"Unsupported config file format: {file_path.suffix}"
                )
                return

            # Update config with file data
            self._update_config(data)
            self.config_sources.append(f"file:{file_path}")

        except Exception as e:
            self.logger.error(f"Failed to load config from {file_path}: {e}")

    def _load_from_environment(self):
        """Load configuration from environment variables."""
        env_mappings = {
            "SCRAPER_DEBUG_MODE": ("debug_mode", bool),
            "SCRAPER_LOG_LEVEL": ("log_level", str),
            "SCRAPER_TIMEOUT": ("timeout", int),
            "SCRAPER_MAX_RETRIES": ("max_retries", int),
            "SCRAPER_USE_PROXY": ("use_proxy", bool),
            "SCRAPER_HEADLESS": ("headless", bool),
            "SCRAPER_NUM_WORKERS": ("num_workers", int),
            "SCRAPER_ENABLE_DISTRIBUTED": ("enable_distributed", bool),
            "SCRAPER_STEALTH_MODE": ("stealth_mode", bool),
        }

        env_data = {}
        for env_var, (config_key, value_type) in env_mappings.items():
            if env_var in os.environ:
                try:
                    value = os.environ[env_var]
                    if value_type == bool:
                        value = value.lower() in ("true", "1", "yes", "on")
                    elif value_type == int:
                        value = int(value)
                    env_data[config_key] = value
                except (ValueError, TypeError) as e:
                    self.logger.warning(f"Invalid environment variable {env_var}: {e}")

        if env_data:
            self._update_config(env_data)
            self.config_sources.append("environment")

    def _load_user_config(self):
        """Load user-specific configuration."""
        user_config_dir = Path.home() / ".config" / "dynamic_web_scraper"
        user_config_file = user_config_dir / "config.json"

        if user_config_file.exists():
            self._load_from_file(user_config_file)

    def _update_config(self, data: Dict[str, Any]):
        """Update configuration with new data."""
        for key, value in data.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                # Store unknown keys in custom_settings
                self.config.custom_settings[key] = value

    def _validate_config(self):
        """Validate the configuration."""
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.config.log_level.upper() not in valid_log_levels:
            self.logger.warning(
                f"Invalid log level: {self.config.log_level}, using INFO"
            )
            self.config.log_level = "INFO"

        # Validate timeout values
        if self.config.timeout <= 0:
            self.logger.warning("Invalid timeout value, using 30")
            self.config.timeout = 30

        if self.config.max_retries < 0:
            self.logger.warning("Invalid max_retries value, using 3")
            self.config.max_retries = 3

        # Validate worker count
        if self.config.num_workers <= 0:
            self.logger.warning("Invalid num_workers value, using 4")
            self.config.num_workers = 4

        # Validate output formats
        valid_formats = ["csv", "json", "excel", "xml", "yaml"]
        invalid_formats = [
            fmt
            for fmt in self.config.output_formats
            if fmt.lower() not in valid_formats
        ]
        if invalid_formats:
            self.logger.warning(f"Invalid output formats: {invalid_formats}")
            self.config.output_formats = [
                fmt
                for fmt in self.config.output_formats
                if fmt.lower() in valid_formats
            ]

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        if hasattr(self.config, key):
            return getattr(self.config, key)
        elif key in self.config.custom_settings:
            return self.config.custom_settings[key]
        return default

    def set(self, key: str, value: Any):
        """
        Set a configuration value.

        Args:
            key: Configuration key
            value: Value to set
        """
        if hasattr(self.config, key):
            setattr(self.config, key, value)
        else:
            self.config.custom_settings[key] = value

    def save_config(self, file_path: Optional[str] = None):
        """
        Save current configuration to file.

        Args:
            file_path: Path to save config (uses default if None)
        """
        if file_path is None:
            file_path = self.config_file

        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            config_data = self.config.to_dict()

            if file_path.suffix.lower() == ".json":
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(config_data, f, indent=2, default=str)
            elif file_path.suffix.lower() in [".yml", ".yaml"]:
                with open(file_path, "w", encoding="utf-8") as f:
                    yaml.dump(config_data, f, default_flow_style=False)
            elif file_path.suffix.lower() == ".toml":
                with open(file_path, "w", encoding="utf-8") as f:
                    toml.dump(config_data, f)
            else:
                # Default to JSON
                with open(file_path.with_suffix(".json"), "w", encoding="utf-8") as f:
                    json.dump(config_data, f, indent=2, default=str)

            self.logger.info(f"Configuration saved to {file_path}")

        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")

    def create_template_config(self, file_path: str, format_type: str = "json"):
        """
        Create a template configuration file.

        Args:
            file_path: Path to create the template
            format_type: Format type (json, yaml, toml)
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Create template with all default values
        template_config = ScraperConfig()
        template_data = template_config.to_dict()

        try:
            if format_type.lower() == "json":
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(template_data, f, indent=2, default=str)
            elif format_type.lower() in ["yml", "yaml"]:
                with open(file_path, "w", encoding="utf-8") as f:
                    yaml.dump(template_data, f, default_flow_style=False)
            elif format_type.lower() == "toml":
                with open(file_path, "w", encoding="utf-8") as f:
                    toml.dump(template_data, f)
            else:
                raise ValueError(f"Unsupported format: {format_type}")

            self.logger.info(f"Template configuration created: {file_path}")

        except Exception as e:
            self.logger.error(f"Failed to create template configuration: {e}")

    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current configuration.

        Returns:
            Configuration summary
        """
        return {
            "name": self.config.name,
            "version": self.config.version,
            "debug_mode": self.config.debug_mode,
            "log_level": self.config.log_level,
            "timeout": self.config.timeout,
            "max_retries": self.config.max_retries,
            "use_proxy": self.config.use_proxy,
            "headless": self.config.headless,
            "enable_distributed": self.config.enable_distributed,
            "num_workers": self.config.num_workers,
            "stealth_mode": self.config.stealth_mode,
            "output_formats": self.config.output_formats,
            "config_sources": self.config_sources,
            "custom_settings_count": len(self.config.custom_settings),
        }

    def reset_to_defaults(self):
        """Reset configuration to default values."""
        self.config = ScraperConfig()
        self.config_sources = ["default"]
        self.logger.info("Configuration reset to defaults")

    def export_config(self, format_type: str = "json") -> str:
        """
        Export configuration as a string.

        Args:
            format_type: Export format (json, yaml, toml)

        Returns:
            Configuration as string
        """
        config_data = self.config.to_dict()

        try:
            if format_type.lower() == "json":
                return json.dumps(config_data, indent=2, default=str)
            elif format_type.lower() in ["yml", "yaml"]:
                return yaml.dump(config_data, default_flow_style=False)
            elif format_type.lower() == "toml":
                return toml.dumps(config_data)
            else:
                raise ValueError(f"Unsupported format: {format_type}")

        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")
            return ""

    def import_config(self, config_data: str, format_type: str = "json"):
        """
        Import configuration from a string.

        Args:
            config_data: Configuration data as string
            format_type: Import format (json, yaml, toml)
        """
        try:
            if format_type.lower() == "json":
                data = json.loads(config_data)
            elif format_type.lower() in ["yml", "yaml"]:
                data = yaml.safe_load(config_data)
            elif format_type.lower() == "toml":
                data = toml.loads(config_data)
            else:
                raise ValueError(f"Unsupported format: {format_type}")

            self._update_config(data)
            self.config_sources.append(f"imported:{format_type}")
            self._validate_config()

            self.logger.info("Configuration imported successfully")

        except Exception as e:
            self.logger.error(f"Failed to import configuration: {e}")


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> ScraperConfig:
    """Get the current configuration."""
    return get_config_manager().config


def get_setting(key: str, default: Any = None) -> Any:
    """Get a configuration setting."""
    return get_config_manager().get(key, default)


def set_setting(key: str, value: Any):
    """Set a configuration setting."""
    get_config_manager().set(key, value)
