# Developer Guide - Dynamic Web Scraper

Comprehensive guide for developers working on the Dynamic Web Scraper codebase.

## Table of Contents

1. [Development Setup](#development-setup)
2. [Project Architecture](#project-architecture)
3. [Code Organization](#code-organization)
4. [Development Workflow](#development-workflow)
5. [Testing](#testing)
6. [Code Style](#code-style)
7. [Adding New Features](#adding-new-features)
8. [Debugging](#debugging)
9. [Best Practices](#best-practices)

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- IDE (VS Code, PyCharm recommended)
- Basic understanding of web scraping concepts

### Initial Setup

```bash
# Clone repository
git clone https://github.com/Yukselcsgn/dynamic_web_scraper.git
cd dynamic_web_scraper

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests to verify setup
pytest
```

### Development Tools

```bash
# Code formatting
black scraper/

# Linting
flake8 scraper/

# Type checking
mypy scraper/

# Run all quality checks
pre-commit run --all-files
```

## Project Architecture

### High-Level Structure

```
scraper/
├── core/           # Core scraping engine
├── analytics/      # Data analysis
├── anti_bot/       # Anti-bot evasion
├── comparison/     # Cross-site comparison
├── dashboard/      # Web interface
├── distributed/    # Distributed processing
└── utils/          # Shared utilities
```

### Key Design Patterns

#### 1. Strategy Pattern
Used in `StealthManager` for different evasion strategies:
```python
class StealthProfile:
    def apply_strategy(self, driver):
        # Implementation
        pass
```

#### 2. Factory Pattern
Used in plugin system for dynamic plugin loading:
```python
def create_plugin(plugin_type):
    # Return appropriate plugin instance
    pass
```

#### 3. Observer Pattern
Used in distributed job queue for status updates:
```python
class JobQueue:
    def notify_observers(self, job_status):
        # Notify all registered observers
        pass
```

## Code Organization

### Module Structure

Each package follows this structure:
```
package_name/
├── __init__.py          # Public API
├── main_module.py       # Core functionality
├── helpers.py           # Helper functions
└── README.md            # Package documentation
```

### Import Conventions

```python
# Standard library
import os
import sys
from typing import Dict, List

# Third-party
import requests
import pandas as pd

# Local
from scraper.core import Scraper
from scraper.utils import helpers
```

## Development Workflow

### 1. Creating a Feature Branch

```bash
git checkout -b feature/new-feature-name
```

### 2. Making Changes

```python
# scraper/new_module.py
from typing import Dict, List

class NewFeature:
    """
    New feature implementation.

    Args:
        config: Configuration dictionary
    """

    def __init__(self, config: Dict):
        self.config = config

    def process(self, data: List[Dict]) -> List[Dict]:
        """Process data with new feature."""
        # Implementation
        return processed_data
```

### 3. Adding Tests

```python
# tests/test_new_module.py
import pytest
from scraper.new_module import NewFeature

class TestNewFeature:
    """Test cases for NewFeature."""

    def test_initialization(self):
        """Test feature initialization."""
        feature = NewFeature(config={})
        assert feature.config is not None

    def test_process(self):
        """Test data processing."""
        feature = NewFeature(config={})
        result = feature.process([{"test": "data"}])
        assert len(result) > 0
```

### 4. Documentation

```python
def new_function(param1: str, param2: int = 10) -> Dict:
    """
    Brief description of function.

    Detailed explanation of what the function does,
    including any important notes or warnings.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 10)

    Returns:
        Dictionary containing processed results

    Raises:
        ValueError: If param1 is empty
        TypeError: If param2 is not an integer

    Example:
        >>> result = new_function("test", 20)
        >>> print(result)
        {'status': 'success'}
    """
    if not param1:
        raise ValueError("param1 cannot be empty")

    return {"status": "success", "data": param1}
```

### 5. Committing Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add: New feature for XYZ functionality"

# Push to repository
git push origin feature/new-feature-name
```

## Testing

### Running Tests

```bash
# All tests
pytest

# Specific category
pytest tests/core/

# With coverage
pytest --cov=scraper --cov-report=html

# Specific test
pytest tests/test_scraper.py::TestScraper::test_initialization
```

### Writing Tests

#### Unit Tests

```python
def test_price_extraction():
    """Test price extraction from text."""
    from scraper.data_processing.data_enricher import DataEnricher

    enricher = DataEnricher()
    price, currency = enricher._extract_price("$99.99")

    assert price == 99.99
    assert currency == "USD"
```

#### Integration Tests

```python
@pytest.mark.integration
def test_complete_workflow():
    """Test complete scraping workflow."""
    scraper = Scraper(url="https://httpbin.org/html", config={})
    result = scraper.fetch_data()

    assert result is not None
    assert 'raw_data' in result
```

### Test Fixtures

```python
# conftest.py
@pytest.fixture
def sample_config():
    """Provide sample configuration."""
    return {
        "use_proxy": False,
        "max_retries": 3
    }

@pytest.fixture
def scraper_instance(sample_config):
    """Provide scraper instance."""
    return Scraper(url="https://example.com", config=sample_config)
```

## Code Style

### Formatting

We use **Black** for Python formatting:
```bash
black scraper/
```

### Linting

We use **flake8** for linting:
```bash
flake8 scraper/
```

### Type Hints

Always use type hints:
```python
from typing import Dict, List, Optional

def process_data(
    data: List[Dict[str, any]],
    config: Optional[Dict] = None
) -> List[Dict]:
    """Process data with optional config."""
    return processed_data
```

### Docstrings

Use Google-style docstrings:
```python
def calculate_statistics(prices: List[float]) -> Dict[str, float]:
    """
    Calculate statistical measures for prices.

    Args:
        prices: List of price values

    Returns:
        Dictionary with statistics:
            - mean: Average price
            - median: Median price
            - std: Standard deviation

    Raises:
        ValueError: If prices list is empty
    """
    pass
```

## Adding New Features

### 1. Plan the Feature

- Define the problem it solves
- Sketch the API
- Consider edge cases
- Plan testing strategy

### 2. Create Feature Branch

```bash
git checkout -b feature/feature-name
```

### 3. Implement Feature

```python
# scraper/new_feature/feature.py
class NewFeature:
    """Implementation of new feature."""

    def __init__(self, config: Dict):
        self.config = config
        self._validate_config()

    def _validate_config(self):
        """Validate configuration."""
        required_keys = ['key1', 'key2']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config: {key}")
```

### 4. Add Tests

```python
# tests/test_new_feature.py
class TestNewFeature:
    def test_feature_works(self):
        feature = NewFeature(config={'key1': 'val1', 'key2': 'val2'})
        result = feature.execute()
        assert result is not None
```

### 5. Document Feature

Create `README.md` in the feature package:
```markdown
# New Feature

Description of the feature.

## Usage

\`\`\`python
from scraper.new_feature import NewFeature

feature = NewFeature(config={})
result = feature.execute()
\`\`\`
```

### 6. Submit Pull Request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for PR guidelines.

## Debugging

### Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
```

### Debugging with pdb

```python
import pdb

def problematic_function():
    data = fetch_data()
    pdb.set_trace()  # Breakpoint
    processed = process(data)
    return processed
```

### VS Code Debugging

Create `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        }
    ]
}
```

## Best Practices

### 1. Code Quality

- Write self-documenting code
- Keep functions small and focused
- Use meaningful variable names
- Add comments for complex logic

### 2. Error Handling

```python
from scraper.exceptions import ScraperException

try:
    result = risky_operation()
except ScraperException as e:
    logger.error(f"Operation failed: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise ScraperException("Operation failed") from e
```

### 3. Performance

- Use generators for large datasets
- Cache expensive operations
- Profile code to find bottlenecks
- Use async for I/O-bound operations

### 4. Security

- Never commit secrets
- Validate all inputs
- Sanitize user data
- Use environment variables for configuration

### 5. Documentation

- Keep README files updated
- Document all public APIs
- Provide usage examples
- Maintain CHANGELOG

## Common Tasks

### Adding a New Package

```bash
mkdir scraper/new_package
touch scraper/new_package/__init__.py
touch scraper/new_package/main.py
touch scraper/new_package/README.md
```

### Running Quality Checks

```bash
# Format code
black scraper/

# Check linting
flake8 scraper/

# Type checking
mypy scraper/

# Run tests
pytest

# All checks
pre-commit run --all-files
```

### Updating Dependencies

```bash
# Update requirements.txt
pip freeze > requirements.txt

# Install updated dependencies
pip install -r requirements.txt
```

## Resources

- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Type Hints (PEP 484)](https://www.python.org/dev/peps/pep-0484/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Project Architecture](architecture/overview.md)

## Getting Help

- Review [architecture documentation](architecture/overview.md)
- Check [API reference](api/index.md)
- Ask questions in GitHub Discussions
- Join development meetings

---

**Happy coding!** 🚀
