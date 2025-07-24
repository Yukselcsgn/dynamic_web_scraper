# Tests for Dynamic Web Scraper

## Overview
This directory contains unit and integration tests for all major modules:
- utils (e.g., html_utils)
- css_selectors
- site_detection
- Scraper integration

## Running Tests
To run all tests:
```bash
python -m unittest discover tests
# or
pytest
```

## Notes
- Tests use Python's built-in unittest and unittest.mock.
- Integration tests mock network requests for reliability. 