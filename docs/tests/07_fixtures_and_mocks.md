# 07. Fixtures and Mocks

## Overview

Test fixtures and mocks are the foundation of deterministic, fast, and reliable testing. This document explains our testing infrastructure and how to use it effectively.

---

## Directory Structure

```
tests/
├── fixtures/              # Test data and samples
│   ├── csv_samples/       # Sample CSV files
│   ├── html_samples/      # Mock HTML documents
│   ├── json_samples/      # Sample JSON data
│   ├── mock_responses/    # Pre-recorded HTTP responses
│   └── test_configs/      # Sample configuration files
│
└── helpers/               # Test utilities
    ├── assertions/        # Custom assertions
    ├── factories/         # Object factories
    ├── mocks/             # Mock implementations
    ├── mock_server.py     # HTTP mock server
    ├── selenium_helper.py # Selenium utilities
    └── test_database_manager.py  # DB test utilities
```

---

## Fixtures (`tests/fixtures/`)

### 1. HTML Samples (`fixtures/html_samples/`)

**Purpose**: Provide realistic HTML documents for testing parsers without hitting real websites.

**Organization**:
- `ecommerce_product_list.html` - Product listing pages
- `ecommerce_product_detail.html` - Product detail pages
- `news_article.html` - News article pages
- `blog_post.html` - Blog post pages
- `search_results.html` - Search result pages
- `cloudflare_challenge.html` - Cloudflare challenge page
- `malformed.html` - Intentionally broken HTML

**Usage Example**:
```python
from pathlib import Path

def load_fixture(filename):
    """Load HTML fixture by filename."""
    fixture_path = Path(__file__).parent / "fixtures" / "html_samples" / filename
    return fixture_path.read_text(encoding="utf-8")

def test_parse_product_listing():
    """Test parsing product listing page."""
    html = load_fixture("ecommerce_product_list.html")
    parser = HTMLParser(html)

    products = parser.extract_products()
    assert len(products) == 20  # Known fixture count
    assert products[0]["title"] == "Product Title"
```

### 2. JSON Samples (`fixtures/json_samples/`)

**Purpose**: Provide API response samples for testing data processing.

**Files**:
- `products_api_response.json` - Product API data
- `search_results.json` - Search API results
- `error_response.json` - API error responses
- `paginated_response.json` - Paginated API data

**Usage**:
```python
import json

def load_json_fixture(filename):
    """Load JSON fixture."""
    with open(f"tests/fixtures/json_samples/{filename}") as f:
        return json.load(f)

def test_process_api_response():
    """Test processing API responses."""
    api_data = load_json_fixture("products_api_response.json")
    processor = APIDataProcessor()

    result = processor.process(api_data)
    assert len(result) > 0
```

### 3. CSV Samples (`fixtures/csv_samples/`)

**Purpose**: Test CSV import/export functionality.

**Files**:
- `products.csv` - Product export sample
- `large_dataset.csv` - Performance testing
- `unicode_data.csv` - Unicode character handling
- `malformed.csv` - Error handling

### 4. Mock Responses (`fixtures/mock_responses/`)

**Purpose**: Pre-recorded HTTP responses for deterministic testing.

**Structure**:
```
mock_responses/
├── successful_200.json
├── not_found_404.json
├── server_error_500.json
├── timeout_response.json
└── headers_example.json
```

**Usage**:
```python
import responses

@responses.activate
def test_with_mock_response():
    """Test using pre-recorded response."""
    mock_data = load_json_fixture("mock_responses/successful_200.json")

    responses.add(
        responses.GET,
        "https://api.example.com/products",
        json=mock_data["body"],
        status=mock_data["status"],
        headers=mock_data["headers"]
    )

    scraper = Scraper()
    result = scraper.fetch("https://api.example.com/products")
    assert result.status_code == 200
```

### 5. Test Configs (`fixtures/test_configs/`)

**Purpose**: Sample configurations for testing config loading.

**Files**:
- `default_config.json` - Standard configuration
- `minimal_config.json` - Minimal required fields
- `advanced_config.json` - All options enabled
- `invalid_config.json` - Test error handling

---

## Helpers (`tests/helpers/`)

### 1. Custom Assertions (`helpers/assertions/`)

**Purpose**: Make tests more readable with domain-specific assertions.

**Example Assertions**:
```python
# helpers/assertions/scraping_assertions.py

def assert_valid_scraped_data(data):
    """Assert scraped data is valid."""
    assert data is not None, "Data should not be None"
    assert isinstance(data, list), "Data should be a list"
    assert len(data) > 0, "Data should not be empty"

    for item in data:
        assert isinstance(item, dict), "Each item should be a dictionary"
        assert "title" in item or "name" in item, "Item should have title/name"

def assert_valid_url(url):
    """Assert URL is properly formatted."""
    assert url is not None
    assert url.startswith("http://") or url.startswith("https://")
    assert len(url) > 10

def assert_html_contains_elements(html, selector, min_count=1):
    """Assert HTML contains elements matching selector."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    elements = soup.select(selector)
    assert len(elements) >= min_count, \
        f"Expected at least {min_count} elements for '{selector}', found {len(elements)}"
```

**Usage**:
```python
from tests.helpers.assertions import assert_valid_scraped_data

def test_scraping_returns_valid_data():
    scraper = Scraper()
    result = scraper.scrape_url("https://example.com")

    # Readable assertion
    assert_valid_scraped_data(result.data)
```

### 2. Factories (`helpers/factories/`)

**Purpose**: Create test objects with sensible defaults.

**Factory Files**:
- `scraper_factory.py` - Create Scraper instances
- `data_factory.py` - Generate test data
- `config_factory.py` - Build configurations
- `response_factory.py` - Mock HTTP responses

**Example Factory**:
```python
# helpers/factories/scraper_factory.py

class ScraperFactory:
    """Factory for creating Scraper instances."""

    @staticmethod
    def create(headless=True, **kwargs):
        """Create scraper with sensible test defaults."""
        defaults = {
            "timeout": 10,
            "headless": headless,
            "user_agent_rotation": False,
            "logging_level": "ERROR"
        }
        defaults.update(kwargs)
        return Scraper(**defaults)

    @staticmethod
    def create_with_proxy():
        """Create scraper with proxy configured."""
        proxy_manager = ProxyManager(["http://test-proxy:8080"])
        return Scraper(proxy_manager=proxy_manager)

    @staticmethod
    def create_stealth():
        """Create scraper in stealth mode."""
        return Scraper(stealth_mode=True, user_agent_rotation=True)

# Usage
from tests.helpers.factories import ScraperFactory

def test_with_factory():
    scraper = ScraperFactory.create()
    # Test with clean scraper instance
```

**Data Factory Example**:
```python
# helpers/factories/data_factory.py

class ProductFactory:
    """Generate test product data."""

    @staticmethod
    def create(**kwargs):
        """Create single product."""
        defaults = {
            "id": 1,
            "title": "Test Product",
            "price": 19.99,
            "url": "https://example.com/product/1"
        }
        defaults.update(kwargs)
        return defaults

    @staticmethod
    def create_batch(count=10):
        """Create multiple products."""
        return [
            ProductFactory.create(id=i, title=f"Product {i}")
            for i in range(count)
        ]

# Usage
def test_data_processing():
    products = ProductFactory.create_batch(100)
    processor = DataProcessor()
    result = processor.process(products)
    assert len(result) == 100
```

### 3. Mocks (`helpers/mocks/`)

**Purpose**: Mock external dependencies and components.

**Mock Files**:
- `mock_browser.py` - Browser mocks
- `mock_http_client.py` - HTTP client mocks
- `mock_database.py` - Database mocks
- `mock_proxy_manager.py` - Proxy manager mocks
- `mock_logger.py` - Logger mocks

**Example Mock**:
```python
# helpers/mocks/mock_browser.py

class MockBrowser:
    """Mock browser for testing without real browser."""

    def __init__(self):
        self.current_url = None
        self.page_source = ""
        self.cookies = {}

    def get(self, url):
        """Mock navigation."""
        self.current_url = url
        self.page_source = f"<html><body>Mock page for {url}</body></html>"

    def find_elements_by_css_selector(self, selector):
        """Mock element finding."""
        return [MockElement(text=f"Element {i}") for i in range(3)]

    def quit(self):
        """Mock cleanup."""
        pass

class MockElement:
    def __init__(self, text=""):
        self.text = text

    def get_attribute(self, name):
        return f"mock-{name}"

# Usage
def test_with_mock_browser():
    scraper = Scraper()
    scraper.browser = MockBrowser()  # Inject mock

    scraper.navigate("https://example.com")
    assert scraper.browser.current_url == "https://example.com"
```

### 4. Mock Server (`helpers/mock_server.py`)

**Purpose**: Lightweight HTTP server for integration tests.

**Example**:
```python
# helpers/mock_server.py

from flask import Flask, jsonify
from threading import Thread

class MockServer:
    """Simple HTTP server for testing."""

    def __init__(self, port=5555):
        self.port = port
        self.app = Flask(__name__)
        self.thread = None
        self._setup_routes()

    def _setup_routes(self):
        @self.app.route("/products")
        def products():
            return jsonify([
                {"id": 1, "name": "Product 1"},
                {"id": 2, "name": "Product 2"}
            ])

        @self.app.route("/error")
        def error():
            return "Server Error", 500

    def start(self):
        """Start server in background thread."""
        self.thread = Thread(target=self.app.run, kwargs={
            "port": self.port,
            "debug": False
        })
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """Stop server."""
        # Cleanup logic
        pass

# Usage
import pytest

@pytest.fixture
def mock_server():
    """Provide mock HTTP server."""
    server = MockServer()
    server.start()
    yield server
    server.stop()

def test_with_mock_server(mock_server):
    scraper = Scraper()
    result = scraper.fetch_url("http://localhost:5555/products")
    assert len(result.data) == 2
```

### 5. Selenium Helper (`helpers/selenium_helper.py`)

**Purpose**: Selenium testing utilities.

**Features**:
```python
# helpers/selenium_helper.py

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SeleniumHelper:
    """Utilities for Selenium testing."""

    @staticmethod
    def wait_for_element(driver, selector, timeout=10):
        """Wait for element to be present."""
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )

    @staticmethod
    def wait_for_text(driver, selector, text, timeout=10):
        """Wait for element to contain text."""
        def element_has_text(driver):
            element = driver.find_element_by_css_selector(selector)
            return text in element.text

        WebDriverWait(driver, timeout).until(element_has_text)

    @staticmethod
    def scroll_to_bottom(driver):
        """Scroll to bottom of page."""
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    @staticmethod
    def take_screenshot_on_failure(driver, test_name):
        """Capture screenshot if test fails."""
        screenshot_path = f"screenshots/{test_name}.png"
        driver.save_screenshot(screenshot_path)
        return screenshot_path

# Usage
def test_with_selenium_helper():
    driver = webdriver.Chrome()
    helper = SeleniumHelper()

    driver.get("https://example.com")
    element = helper.wait_for_element(driver, ".product-title")
    assert element is not None
```

### 6. Test Database Manager (`helpers/test_database_manager.py`)

**Purpose**: Manage test databases with automatic cleanup.

**Example**:
```python
# helpers/test_database_manager.py

class TestDatabaseManager:
    """Manage test databases."""

    def __init__(self, db_name=":memory:"):
        self.db_name = db_name
        self.connection = None

    def setup(self):
        """Create test database with schema."""
        self.connection = sqlite3.connect(self.db_name)
        self._create_schema()

    def _create_schema(self):
        """Create database tables."""
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT,
                price REAL
            )
        """)

    def insert_test_data(self):
        """Insert sample data."""
        self.connection.execute(
            "INSERT INTO products (name, price) VALUES (?, ?)",
            ("Test Product", 19.99)
        )
        self.connection.commit()

    def teardown(self):
        """Clean up database."""
        if self.connection:
            self.connection.close()

# Usage
@pytest.fixture
def test_db():
    """Provide test database."""
    db = TestDatabaseManager()
    db.setup()
    db.insert_test_data()
    yield db
    db.teardown()

def test_with_database(test_db):
    storage = DataStorage(test_db.connection)
    products = storage.get_all_products()
    assert len(products) > 0
```

---

## Pytest Fixtures

### Built-in Pytest Fixtures

```python
# conftest.py

import pytest

@pytest.fixture
def sample_html():
    """Provide sample HTML for tests."""
    return load_fixture("ecommerce_product_list.html")

@pytest.fixture
def scraper():
    """Provide fresh Scraper instance."""
    return ScraperFactory.create()

@pytest.fixture
def mock_scraper():
    """Provide Scraper with mocked dependencies."""
    scraper = Scraper()
    scraper.browser = MockBrowser()
    scraper.http_client = MockHTTPClient()
    return scraper

@pytest.fixture(scope="session")
def test_server():
    """Provide mock server for entire test session."""
    server = MockServer()
    server.start()
    yield server
    server.stop()

@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Automatically clean up temp files after each test."""
    yield
    # Cleanup code runs after test
    for file in Path("temp").glob("*.tmp"):
        file.unlink()
```

---

## Best Practices

### 1. Use Fixtures for Setup/Teardown

```python
@pytest.fixture
def configured_scraper():
    """Setup scraper with config."""
    scraper = Scraper(config="test_config.json")
    yield scraper
    # Teardown
    scraper.close()
```

### 2. Parametrize Fixture Variations

```python
@pytest.fixture(params=["chrome", "firefox"])
def browser_scraper(request):
    """Test with multiple browsers."""
    return Scraper(browser=request.param)
```

### 3. Keep Fixtures Focused

```python
# GOOD: Single responsibility
@pytest.fixture
def test_database():
    db = Database(":memory:")
    yield db
    db.close()

# BAD: Too much responsibility
@pytest.fixture
def everything():
    db = Database()
    scraper = Scraper()
    server = MockServer()
    # Too complex
```

---

## Next Steps

- **Running Tests**: [08. Running Tests](08_running_tests.md)
- **Writing New Tests**: [09. Writing New Tests](09_writing_new_tests.md)
- **Best Practices**: [11. Best Practices](11_best_practices.md)
