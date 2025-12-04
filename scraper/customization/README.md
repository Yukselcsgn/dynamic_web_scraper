# Customization Package

The `customization` package provides configuration management for customizing scraper behavior.

## Modules

### Config Manager (`config_manager.py`)
Comprehensive configuration management system.

**Key Classes:**
- **`ScraperConfig`**: Main configuration dataclass with all settings
- **`ConfigManager`**: Configuration loader and manager
  - **Features:**
    - Multi-source configuration (files, environment variables, user configs)
    - Support for JSON, YAML, and TOML formats
    - Configuration validation
    - Template config generation
    - Import/export functionality
    - Runtime configuration updates

## Usage

The config manager allows users to customize scraper behavior through configuration files or environment variables without modifying code.
