# Exceptions Package

The `exceptions` package defines custom exceptions for error handling.

## Modules

### Scraper Exceptions (`scraper_exceptions.py`)
Custom exception classes with logging and suggestions.

**Key Classes:**
- **`ScraperException`**: Base exception class
- **`ProxyError`**: Proxy-related errors
- **`UserAgentError`**: User agent issues
- **`InvalidURLError`**: Invalid URL errors
- **`ParsingError`**: Data parsing failures
- **`RateLimitExceededError`**: Rate limit violations
- **`AuthenticationError`**: Authentication failures
- **`DataNotFoundError`**: Missing data errors
- **`ConfigurationError`**: Configuration problems

## Features

- Automatic error logging to file
- User-friendly error messages
- Contextual suggestions for resolution
- Detailed error context (URL, proxy, element, etc.)

## Usage

These exceptions provide clear error reporting and help diagnose scraping issues with actionable suggestions for fixing problems.
