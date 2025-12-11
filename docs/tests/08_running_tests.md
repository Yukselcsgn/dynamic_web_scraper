# 08. Running Tests

## Overview

This guide provides comprehensive documentation on test execution strategies, runner scripts, pytest configuration, and CI/CD integration.

---

## Test Runner Scripts

The project provides 8 specialized test runner scripts for different scenarios:

### 1. `run_full_suite.py` - Complete Test Suite

**Purpose**: Execute all tests (unit, integration, e2e, qa, regression, smoke, benchmark)

```bash
python tests/run_full_suite.py
```

**When to Use**:
- Before merging to main branch
- Before creating releases
- Nightly CI/CD builds
- Comprehensive validation

**Estimated Time**: 40-85 minutes

---

### 2. `run_smoke_tests.py` - Quick Sanity Check

**Purpose**: Run only critical smoke tests

```bash
python tests/run_smoke_tests.py
```

**When to Use**:
- First step in CI/CD pipelines
- Quick sanity checks during development
- After major refactoring
- Before running longer test suites

**Estimated Time**: < 1 minute

---

### 3. `run_unit_tests.py` - Unit Tests Only

**Purpose**: Execute all unit tests

```bash
python tests/run_unit_tests.py
```

**When to Use**:
- During active development (most frequent)
- After modifying individual modules
- Rapid feedback loops
- TDD workflow

**Estimated Time**: 1-2 minutes

---

### 4. `run_integration_tests.py` - Integration Tests

**Purpose**: Run integration tests

```bash
python tests/run_integration_tests.py
```

**When to Use**:
- After modifying multiple related components
- Before feature completion
- Mid-level validation in CI/CD

**Estimated Time**: 5-10 minutes

---

### 5. `run_e2e_tests.py` - End-to-End Tests

**Purpose**: Execute E2E tests

```bash
python tests/run_e2e_tests.py
```

**When to Use**:
- Before releases
- After major feature additions
- Pre-production validation
- User acceptance testing

**Estimated Time**: 10-20 minutes

---

### 6. `run_qa_tests.py` - QA Test Suite

**Purpose**: Run comprehensive QA tests

```bash
python tests/run_qa_tests.py
```

**When to Use**:
- Before major releases
- Performance validation
- Security audits
- Cross-platform testing

**Estimated Time**: 20-40 minutes

---

### 7. `run_quick_tests.py` - Fast Test Subset

**Purpose**: Run subset of fast tests

```bash
python tests/run_quick_tests.py
```

**When to Use**:
- During active development
- Before committing changes
- Quick validation during debugging

**Estimated Time**: < 2 minutes

---

### 8. `run_tests.py` - General Runner

**Purpose**: Flexible test runner with options

```bash
python tests/run_tests.py [options]
```

**Options**:
```bash
--unit          # Run unit tests only
--integration   # Run integration tests only
--e2e           # Run e2e tests only
--coverage      # Generate coverage report
--verbose       # Verbose output
--parallel      # Run tests in parallel
```

---

## Direct Pytest Usage

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific directory
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run specific file
pytest tests/unit/proxy_manager/test_rotation.py

# Run specific test
pytest tests/unit/test_parser.py::test_parse_price

# Run tests matching pattern
pytest -k "proxy"  # All tests with 'proxy' in name
pytest -k "test_parse"  # All parsing tests
```

### Markers

```bash
# Run by marker
pytest -m "smoke"  # Smoke tests only
pytest -m "slow"  # Slow tests only
pytest -m "not slow"  # Skip slow tests
pytest -m "integration"  # Integration tests
pytest -m "e2e"  # E2E tests
pytest -m "real_site"  # Real site tests
pytest -m "not real_site"  # Skip real site tests

# Combine markers
pytest -m "integration and not slow"
```

### Coverage Reports

```bash
# Generate coverage report
pytest --cov=scraper

# HTML coverage report
pytest --cov=scraper --cov-report=html

# Terminal coverage report
pytest --cov=scraper --cov-report=term

# XML coverage report (for CI)
pytest --cov=scraper --cov-report=xml

# Generate multiple report formats
pytest --cov=scraper --cov-report=html --cov-report=xml --cov-report=term
```

### Parallel Execution

```bash
# Auto-detect CPU count
pytest -n auto

# Specific number of workers
pytest -n 4

# Parallel with coverage
pytest -n auto --cov=scraper
```

### Debugging

```bash
# Stop on first failure
pytest -x

# Drop into debugger on failure
pytest --pdb

# Show local variables on failure
pytest -l

# Verbose output with local variables
pytest -vv -l

# Show print statements
pytest -s

# Run last failed tests
pytest --lf

# Run failed tests first, then others
pytest --ff
```

### Output Control

```bash
# Quiet mode (minimal output)
pytest -q

# Show test duration
pytest --durations=10  # Show 10 slowest tests
pytest --durations=0  # Show all durations

# Capture method
pytest --capture=no  # Don't capture stdout
pytest -s  # Same as --capture=no
```

---

## Pytest Configuration

### `pytest.ini`

```ini
[pytest]
# Test discovery patterns
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Markers
markers =
    smoke: Quick smoke tests
    slow: Slow-running tests
    integration: Integration tests
    e2e: End-to-end tests
    real_site: Tests that hit real websites
    benchmark: Performance benchmark tests
    regression: Regression tests

# Coverage settings
addopts =
    --strict-markers
    --tb=short
    --disable-warnings

# Test paths
testpaths = tests

# Minimum Python version
minversion = 3.8
```

### `conftest.py` (Global Fixtures)

```python
# tests/conftest.py

import pytest

@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration."""
    return {
        "timeout": 10,
        "headless": True
    }

@pytest.fixture(autouse=True)
def reset_cache():
    """Clear cache before each test."""
    # Cleanup code
    yield
    # Teardown code

@pytest.fixture
def scraper(test_config):
    """Provide Scraper instance."""
    from scraper import Scraper
    return Scraper(**test_config)
```

### `.coveragerc` (Coverage Configuration)

```ini
[run]
source = scraper
omit =
    */tests/*
    */venv/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:

[html]
directory = tests/reports/coverage
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  smoke-and-unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      - name: Run smoke tests
        run: python tests/run_smoke_tests.py
      - name: Run unit tests
        run: python tests/run_unit_tests.py --coverage

  integration:
    needs: smoke-and-unit
    runs-on: ubuntu-latest
    steps:
      - name: Run integration tests
        run: python tests/run_integration_tests.py

  e2e:
    needs: integration
    runs-on: ubuntu-latest
    steps:
      - name: Install browsers
        run: |
          playwright install
      - name: Run E2E tests
        run: python tests/run_e2e_tests.py
```

### GitLab CI Example

```yaml
stages:
  - fast-feedback
  - integration
  - comprehensive

smoke-tests:
  stage: fast-feedback
  script:
    - python tests/run_smoke_tests.py

unit-tests:
  stage: fast-feedback
  script:
    - python tests/run_unit_tests.py
    - coverage report

integration-tests:
  stage: integration
  script:
    - python tests/run_integration_tests.py

e2e-tests:
  stage: comprehensive
  script:
    - python tests/run_e2e_tests.py
  only:
    - main
```

---

## Test Execution Strategies

### Development Workflow

```bash
# 1. During development - fast feedback
pytest tests/unit/module_im_working_on/ -v

# 2. Before commit - broader check
python tests/run_quick_tests.py

# 3. Before push - comprehensive
python tests/run_unit_tests.py
python tests/run_integration_tests.py
```

### Pre-Release Workflow

```bash
# 1. Full test suite
python tests/run_full_suite.py

# 2. Generate coverage report
pytest --cov=scraper --cov-report=html

# 3. Run QA tests
python tests/run_qa_tests.py

# 4. Performance benchmarks
pytest tests/benchmark/ --benchmark-only
```

### Continuous Integration

```
Stage 1: Fast Feedback (< 2 min)
├── Smoke tests
└── Unit tests

Stage 2: Integration (5-10 min)
├── Integration tests
└── Coverage analysis

Stage 3: Comprehensive (15-30 min)
├── E2E tests
├── Regression tests
└── Benchmark tests

Stage 4: QA (30-60 min)  [Nightly only]
├── Compatibility tests
├── Performance tests
├── Security tests
└── Scalability tests
```

---

## Common Test Execution Patterns

### Watch Mode (TDD)

```bash
# Install pytest-watch
pip install pytest-watch

# Run tests on file changes
ptw tests/unit/

# With coverage
ptw -- --cov=scraper
```

### Selective Re-runs

```bash
# Run only failed tests from last run
pytest --lf

# Run failed first, then others
pytest --ff

# Re-run specific test multiple times (flaky test detection)
pytest --count=10 tests/unit/test_specific.py
```

### Performance Profiling

```bash
# Profile test execution time
pytest --durations=20

# Profile with cProfile
pytest --profile

# Memory profiling
pytest --memprof
```

---

## Troubleshooting

### Tests Running Slowly

```bash
# Identify slow tests
pytest --durations=10

# Run in parallel
pytest -n auto

# Skip slow tests
pytest -m "not slow"
```

### Flaky Tests

```bash
# Re-run failed tests
pytest --lf --count=5

# Show test output
pytest -s -v

# Use debugger
pytest --pdb
```

### Coverage Issues

```bash
# Show missing lines
pytest --cov=scraper --cov-report=term-missing

# Focus on specific module
pytest --cov=scraper.parsers tests/unit/data_parsers/
```

---

## Best Practices

1. **Run smoke/unit tests frequently** - Fast feedback
2. **Run integration tests before commits**
3. **Run full suite before merging to main**
4. **Use markers** to organize and select tests
5. **Generate coverage reports** regularly
6. **Parallelize where possible** for speed
7. **Monitor test execution time** and optimize slowtests

---

## Next Steps

- **Writing New Tests**: [09. Writing New Tests](09_writing_new_tests.md)
- **Best Practices**: [11. Best Practices](11_best_practices.md)
