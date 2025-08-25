"""
Pytest configuration and shared fixtures for Dynamic Web Scraper tests.

This file contains common fixtures, test data, and configuration
that can be used across all test modules.
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scraper.config import load_config
from scraper.logging_manager.logging_manager import setup_logging


@pytest.fixture(scope="session")
def test_config():
    """Load test configuration."""
    return load_config()


@pytest.fixture(scope="session")
def test_data_dir():
    """Create temporary test data directory."""
    temp_dir = tempfile.mkdtemp(prefix="scraper_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="session")
def test_logs_dir():
    """Create temporary logs directory."""
    temp_dir = tempfile.mkdtemp(prefix="scraper_logs_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def setup_logging_fixture(test_logs_dir):
    """Setup logging for individual tests."""
    log_file = os.path.join(test_logs_dir, "test.log")
    setup_logging(log_file)
    return log_file


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return [
        {
            "title": "Test Product 1",
            "price": 100.0,
            "currency": "USD",
            "url": "https://example.com/product1",
            "source": "test_site",
            "category": "electronics",
            "description": "Test product description",
        },
        {
            "title": "Test Product 2",
            "price": 200.0,
            "currency": "USD",
            "url": "https://example.com/product2",
            "source": "test_site",
            "category": "electronics",
            "description": "Another test product",
        },
    ]


@pytest.fixture
def sample_site_config():
    """Sample site configuration for testing."""
    return {
        "name": "test_site",
        "base_url": "https://example.com",
        "selectors": {
            "product_container": ".product",
            "title": ".product-title",
            "price": ".product-price",
            "url": ".product-link",
        },
        "anti_bot_measures": ["user_agent_check", "rate_limiting"],
        "rate_limit": {"requests_per_minute": 60},
    }


@pytest.fixture
def mock_response():
    """Mock HTTP response for testing."""
    mock = Mock()
    mock.status_code = 200
    mock.text = """
    <html>
        <body>
            <div class="product">
                <h2 class="product-title">Test Product</h2>
                <span class="product-price">$100</span>
                <a class="product-link" href="/product/1">View Product</a>
            </div>
        </body>
    </html>
    """
    mock.url = "https://example.com"
    return mock


@pytest.fixture
def mock_session():
    """Mock requests session for testing."""
    with patch("requests.Session") as mock_session:
        session = mock_session.return_value
        session.headers = {}
        yield session


@pytest.fixture
def test_urls():
    """Common test URLs."""
    return {
        "amazon": "https://www.amazon.com/s?k=laptop",
        "ebay": "https://www.ebay.com/sch/i.html?_nkw=laptop",
        "example": "https://example.com/products",
        "sahibinden": "https://www.sahibinden.com/arama?query=laptop",
    }


@pytest.fixture(scope="session")
def test_environment():
    """Setup test environment variables."""
    original_env = os.environ.copy()

    # Set test environment variables
    os.environ["SCRAPER_TEST_MODE"] = "true"
    os.environ["SCRAPER_LOG_LEVEL"] = "DEBUG"

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "e2e: marks tests as end-to-end tests")
    config.addinivalue_line("markers", "performance: marks tests as performance tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    for item in items:
        # Mark tests based on their location
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "e2e" in item.nodeid:
            item.add_marker(pytest.mark.e2e)
        elif "performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)
