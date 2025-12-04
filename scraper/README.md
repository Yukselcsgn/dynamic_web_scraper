# Scraper Package

The `scraper` package is the main package containing all scraping functionality and advanced features.

## Main Entry Points

- **`main.py`**: Command-line entry point for direct scraping
- **`adaptive_config_manager.py`**: Adaptive configuration management
- **`universal_extractor.py`**: Universal data extraction engine
- **`config.py`**: Configuration management

## Sub-Packages

The scraper is organized into specialized sub-packages:

### Core Components
- [`analytics/`](analytics/README.md) - Data analysis and visualization
- [`core/`](core/README.md) - Core scraping functionality
- [`export/`](export/README.md) - Multi-format export capabilities

### Intelligence & Detection
- [`anti_bot/`](anti_bot/README.md) - Anti-bot evasion and stealth
- [`site_detection/`](site_detection/README.md) - Site type and structure detection
- [`css_selectors/`](css_selectors/README.md) - Dynamic selector generation

### Data Processing
- [`data_parsers/`](data_parsers/README.md) - Data parsing utilities
- [`data_processing/`](data_processing/README.md) - Data enrichment and cleaning

### Analysis & Comparison
- [`comparison/`](comparison/README.md) - Cross-site price comparison
- [`reporting/`](reporting/README.md) - Automated report generation

### Infrastructure
- [`distributed/`](distributed/README.md) - Distributed job processing
- [`dashboard/`](dashboard/README.md) - Web-based monitoring
- [`logging_manager/`](logging_manager/README.md) - Centralized logging
- [`exceptions/`](exceptions/README.md) - Custom exception handling

### Utilities & Management
- [`customization/`](customization/README.md) - Configuration management
- [`plugins/`](plugins/README.md) - Plugin system
- [`proxy_manager/`](proxy_manager/README.md) - Proxy rotation
- [`user_agent_manager/`](user_agent_manager/README.md) - User agent management
- [`utils/`](utils/README.md) - Common utilities

## Architecture

The scraper follows a modular architecture where each sub-package handles specific responsibilities. Components communicate through well-defined interfaces, making the system maintainable and extensible.

## Features

- **Intelligent scraping** with automatic site detection
- **Advanced anti-bot evasion** with multiple stealth profiles
- **Comprehensive data analysis** and visualization
- **Distributed processing** for scalability
- **Plugin system** for extensibility
- **Multi-format export** capabilities
- **Web dashboard** for monitoring and management
