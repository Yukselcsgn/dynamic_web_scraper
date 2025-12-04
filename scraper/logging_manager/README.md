# Logging Manager Package

The `logging_manager` package provides centralized logging functionality.

## Modules

### Logging Manager (`logging_manager.py`)
Centralized logging setup and message handling.

**Key Functions:**
- `setup_logging()`: Initialize logging configuration
- `log_message(level, message)`: Log messages with standardized formatting

## Features

- File-based logging to `logs/` directory
- Multiple log levels (INFO, WARNING, ERROR, DEBUG)
- Consistent log formatting across all modules
- Centralized configuration

## Usage

All scraper components use this logging manager for consistent log output, making it easy to track operations and debug issues.
