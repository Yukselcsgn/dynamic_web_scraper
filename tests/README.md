# Tests Package

The `tests/` package contains the comprehensive test suite for the Dynamic Web Scraper project.

## Test Structure

```
tests/
├── conftest.py                      # Pytest configuration and shared fixtures
├── run_tests.py                     # Test runner script
├── core/                            # Core functionality tests
├── analytics/                       # Analytics tests
├── site_detection/                  # Site detection tests
├── utils/                           # Utility tests
└── integration/                     # Integration tests
```

## Test Categories

### Core Tests (`core/`)
Tests for basic scraper functionality:
- `test_scraper_basic.py` - Basic scraping operations
- `test_scraper_integration.py` - Integration tests

### Analytics Tests (`analytics/`)
Tests for data analysis and visualization:
- `test_data_visualizer.py` - Chart creation and visualization

### Site Detection Tests (`site_detection/`)
Tests for site detection and selector generation:
- `test_css_selectors.py` - CSS selector generation
- `test_site_detector.py` - Site detector functionality
- `test_html_analyzer.py` - HTML analysis
- Additional selector and rule tests

### Utils Tests (`utils/`)
Tests for utility functions:
- `test_request_utils.py` - HTTP request utilities
- `test_html_utils.py` - HTML processing utilities

### Integration Tests (`integration/`)
End-to-end workflow tests:
- `test_complete_workflow.py` - Complete scraping workflows

## Running Tests

### Run All Tests
```bash
python tests/run_tests.py --all
```

### Run Specific Categories
```bash
# Core tests
python tests/run_tests.py --category core

# Analytics tests
python tests/run_tests.py --category analytics

# Site detection tests
python tests/run_tests.py --category site_detection
```

### Quick Tests (Unit Tests Only)
```bash
python tests/run_tests.py --quick
```

### With Coverage
```bash
python tests/run_tests.py --all --coverage
```

### With HTML Report
```bash
python tests/run_tests.py --all --html
```

## Test Markers

Defined in `pytest.ini`:
- `slow` - Slow-running tests
- `integration` - Integration tests
- `e2e` - End-to-end tests
- `performance` - Performance tests
- `stress` - Stress tests
- `unit` - Unit tests
- `smoke` - Smoke tests

## Configuration

- **pytest.ini**: Pytest configuration
- **conftest.py**: Shared fixtures and test setup
- **run_tests.py**: Custom test runner script

## Writing Tests

Follow these guidelines:
1. Place tests in appropriate category directories
2. Name test files with `test_` prefix
3. Use descriptive test function names
4. Leverage shared fixtures from `conftest.py`
5. Add appropriate test markers
6. Document complex test scenarios

## Test Coverage

Run tests with coverage to ensure code quality:
```bash
pytest --cov=scraper --cov-report=html
```

View coverage reports in `htmlcov/index.html`.
