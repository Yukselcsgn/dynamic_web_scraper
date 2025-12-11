# 09. Writing New Tests

## Overview

This style guide establishes standards for writing clear, maintainable, and effective tests for the Dynamic Web Scraper project.

---

## General Principles

### The CORRECT Framework

**C** - **Complete**: Test all relevant scenarios
**O** - **Organized**: Follow consistent structure
**R** - **Readable**: Clear intent and expectations
**R** - **Repeatable**: Deterministic results
**E** - **Efficient**: Fast execution
**C** - **Clear Failures**: Informative error messages
**T** - **Thorough**: Edge cases included

---

## Naming Conventions

### Test File Names

```
test_<module_name>.py
```

**Examples**:
- `test_proxy_manager.py`
- `test_data_parser.py`
- `test_scraper.py`

### Test Function Names

```
test_<what>_<conditions>_<expected_result>
```

**Pattern**: `test_<component>_<action>_<context>`

**Examples**:
```python
# Good
def test_parse_price_with_currency_symbol_returns_float():
def test_proxy_rotation_with_failed_proxy_skips_to_next():
def test_scraper_initialization_without_config_uses_defaults():

# Bad
def test_1():  # Not descriptive
def test_parser():  # Too vague
def test_this_thing_does_stuff():  # Unclear
```

### Test Class Names

```python
class Test<ComponentName>:
    """Tests for <ComponentName>."""
```

**Example**:
```python
class TestProxyManager:
    """Tests for ProxyManager class."""

    def test_round_robin_rotation(self):
        pass

    def test_proxy_failure_handling(self):
        pass
```

---

## Test Structure: AAA Pattern

**A** rrange - **A** ct - **A** ssert

```python
def test_example():
    """Test that demonstrates AAA pattern."""
    # Arrange: Set up test conditions
    scraper = Scraper()
    html = "<html><body><h1>Title</h1></body></html>"

    # Act: Execute the code being tested
    result = scraper.parse_html(html)

    # Assert: Verify expected outcomes
    assert result["title"] == "Title"
```

### Given-When-Then (Alternative)

```python
def test_with_given_when_then():
    """Test using Given-When-Then structure."""
    # Given: A configured scraper with proxies
    proxy_manager = ProxyManager(["proxy1", "proxy2"])
    scraper = Scraper(proxy_manager=proxy_manager)

    # When: The first proxy fails
    mock_failure(proxy="proxy1")
    result = scraper.fetch_url("https://example.com")

    # Then: The second proxy is used
    assert result.proxy_used == "proxy2"
```

---

## Docstrings

### Test Docstring Format

```python
def test_function_name():
    """<Test Type>: <What is being tested>.

    Optional longer description if needed.
    Edge cases, special conditions, or rationale.
    """
```

**Examples**:
```python
def test_parse_price_with_currency():
    """Unit: Price parser handles multiple currency symbols."""

def test_complete_scraping_workflow():
    """E2E: Full scraping cycle from URL input to data export."""

def test_issue_123_proxy_crash():
    """Regression: Issue #123 - Proxy manager crash on None value."""

def test_concurrent_scraping_performance():
    """QA/Performance: Handle 10 concurrent scraping tasks efficiently."""
```

---

## Parametrization

### Using `pytest.mark.parametrize`

```python
@pytest.mark.parametrize("input_price,expected", [
    ("$19.99", 19.99),
    ("€25.50", 25.50),
    ("£10.00", 10.00),
    ("¥1000", 1000.0),
    ("FREE", 0.0),
])
def test_parse_price_various_formats(input_price, expected):
    """Unit: Price parser handles various currency formats."""
    result = parse_price(input_price)
    assert result == expected
```

### Multiple Parameters

```python
@pytest.mark.parametrize("browser,headless", [
    ("chrome", True),
    ("chrome", False),
    ("firefox", True),
    ("firefox", False),
])
def test_browser_configurations(browser, headless):
    """Integration: Test various browser configurations."""
    scraper = Scraper(browser=browser, headless=headless)
    result = scraper.scrape_url("https://example.com")
    assert result.status == "success"
```

---

## Assertions

### Clear Assertions

```python
# Good: Clear what is being tested
assert result.status == "success"
assert len(data) == 10
assert "title" in product
assert product["price"] > 0

# Bad: Unclear expectations
assert result
assert data
assert product
```

### Multiple Assertions (When Appropriate)

```python
def test_product_structure():
    """Unit: Product has required fields with correct types."""
    product = parse_product(html)

    # Related assertions on same object
    assert "title" in product
    assert "price" in product
    assert "url" in product

    assert isinstance(product["title"], str)
    assert isinstance(product["price"], float)
    assert isinstance(product["url"], str)
```

### Custom Assertions

```python
from tests.helpers.assertions import assert_valid_scraped_data

def test_scraping_returns_valid_data():
    """Unit: Scraper returns properly structured data."""
    scraper = Scraper()
    result = scraper.scrape_url("https://example.com")

    # More readable than multiple asserts
    assert_valid_scraped_data(result.data)
```

---

## Fixtures

### Use Fixtures for Setup

```python
@pytest.fixture
def configured_scraper():
    """Provide configured Scraper instance."""
    config = {
        "timeout": 10,
        "headless": True
    }
    scraper = Scraper(**config)
    yield scraper
    # Cleanup
    scraper.close()

def test_with_fixture(configured_scraper):
    """Test using scraper fixture."""
    result = configured_scraper.scrape_url("https://example.com")
    assert result is not None
```

### Fixture Scope

```python
@pytest.fixture(scope="function")  # Default: New instance per test
def test_scraper():
    return Scraper()

@pytest.fixture(scope="module")  # One instance per module
def shared_scraper():
    return Scraper()

@pytest.fixture(scope="session")  # One instance per test session
def mock_server():
    server = MockServer()
    server.start()
    yield server
    server.stop()
```

---

## Mocking

### When to Mock

✅ **Mock external dependencies**:
- HTTP requests
- Databases
- File system operations
- Time/date functions
- Random number generation

❌ **Don't mock**:
- Code under test
- Simple data structures
- Pure functions

### Mocking Examples

```python
from unittest.mock import Mock, patch, MagicMock

def test_with_mock():
    """Unit: Test with mocked HTTP request."""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "<html>Test</html>"

        scraper = Scraper()
        result = scraper.fetch_url("https://example.com")

        assert result.status_code == 200
        mock_get.assert_called_once()

def test_mock_return_values():
    """Unit: Mock with different return values."""
    with patch('ProxyManager.get_next_proxy') as mock:
        mock.side_effect = ["proxy1", "proxy2", "proxy3"]

        manager = ProxyManager()
        assert manager.get_next_proxy() == "proxy1"
        assert manager.get_next_proxy() == "proxy2"
        assert manager.get_next_proxy() == "proxy3"
```

---

## Test Organization

### Grouping Related Tests

```python
class TestProxyManager:
    """Tests for ProxyManager."""

    class TestRotation:
        """Tests for proxy rotation logic."""

        def test_round_robin(self):
            pass

        def test_random(self):
            pass

    class TestFailureHandling:
        """Tests for proxy failure handling."""

        def test_remove_failed_proxy(self):
            pass

        def test_retry_logic(self):
            pass
```

---

## Edge Cases and Error Conditions

### Test Both Happy and Unhappy Paths

```python
def test_parse_valid_html():
    """Unit: Parser handles valid HTML."""
    html = "<div class='product'>Test</div>"
    result = parse_html(html)
    assert result is not None

def test_parse_empty_html():
    """Unit: Parser handles empty HTML gracefully."""
    html = ""
    result = parse_html(html)
    assert result is None or result == []

def test_parse_malformed_html():
    """Unit: Parser handles malformed HTML without crashing."""
    html = "<div><p>Unclosed tags"
    result = parse_html(html)
    # Should not crash, return partial data
    assert isinstance(result, (dict, list, type(None)))

def test_parse_with_special_characters():
    """Unit: Parser handles special characters."""
    html = "<div>Test & <script>alert('XSS')</script></div>"
    result = parse_html(html)
    assert "<script>" not in result
```

---

## Performance Considerations

### Mark Slow Tests

```python
@pytest.mark.slow
def test_large_dataset_processing():
    """Performance: Process 10,000 items."""
    data = generate_large_dataset(10000)
    result = process(data)
    assert len(result) == 10000
```

### Set Timeouts

```python
@pytest.mark.timeout(5)  # Max 5 seconds
def test_should_complete_quickly():
    """Unit: Operation completes in < 5 seconds."""
    result = fast_operation()
    assert result is not None
```

---

## Test Data

### Use Fixtures for Test Data

```python
@pytest.fixture
def sample_products():
    """Provide sample product data."""
    return [
        {"name": "Product 1", "price": 19.99},
        {"name": "Product 2", "price": 29.99}
    ]

def test_with_sample_data(sample_products):
    """Test with fixture data."""
    processor = DataProcessor()
    result = processor.process(sample_products)
    assert len(result) == 2
```

### Use Factories for Complex Objects

```python
from tests.helpers.factories import ProductFactory

def test_with_factory():
    """Test using factory-generated data."""
    products = ProductFactory.create_batch(100)
    processor = DataProcessor()
    result = processor.process(products)
    assert len(result) == 100
```

---

## Documentation and Comments

### When to Add Comments

```python
def test_complex_scenario():
    """Unit: Complex multi-step validation."""
    # Step 1: Setup initial state
    scraper = Scraper()
    scraper.configure(max_retries=3)

    # Step 2: Simulate first failure
    with patch('requests.get') as mock:
        mock.side_effect = [ConnectionError(), Mock(status_code=200)]

        # Step 3: Verify retry logic
        result = scraper.fetch("https://example.com")

        # Verify retry occurred (2 calls = 1 failure + 1 success)
        assert mock.call_count == 2
```

---

## Common Anti-Patterns to Avoid

### ❌ Testing Implementation Details

```python
# BAD
def test_uses_beautifulsoup():
    parser = HTMLParser(html)
    assert isinstance(parser._soup, BeautifulSoup)

# GOOD
def test_extracts_title():
    parser = HTMLParser(html)
    assert parser.get_title() == "Expected Title"
```

### ❌ Excessive Mocking

```python
# BAD: Mocking everything
def test_too_many_mocks():
    with patch('module.ClassA'), \
         patch('module.ClassB'), \
         patch('module.ClassC'):
        # What are we even testing?
        pass

# GOOD: Mock only external dependencies
def test_appropriate_mocking():
    with patch('requests.get') as mock_get:
        scraper = Scraper()  # Real scraper
        result = scraper.fetch("url")  # Mocked HTTP
```

### ❌ Unclear Test Names

```python
# BAD
def test_1():
def test_stuff():
def test_works():

# GOOD
def test_get_price_from_html_returns_float():
def test_proxy_rotation_cycles_through_list():
```

### ❌ Tests with Side Effects

```python
# BAD: Modifies global state
def test_modifies_global():
    global_cache.clear()  # Affects other tests
    result = function_using_cache()

# GOOD: Use fixtures with cleanup
@pytest.fixture
def clean_cache():
    cache = Cache()
    yield cache
    cache.clear()

def test_with_clean_cache(clean_cache):
    result = function_using_cache(clean_cache)
```

---

## Coverage Guidelines

### Target Coverage Levels

| Component | Target Coverage |
|-----------|----------------|
| Core modules | 90%+ |
| Parsers | 85%+ |
| Utilities | 85%+ |
| Plugins | 75%+ |
| Scripts | 65%+ |

### What to Cover

✅ **Must cover**:
- Public API functions
- Critical business logic
- Error handling paths
- Edge cases

⚠️ **Consider covering**:
- Helper functions
- Internal methods (if complex)
- Configuration loading

❌ **Don't obsess over**:
- Simple getters/setters
- Third-party code
- Auto-generated code

---

## Review Checklist

Before submitting tests, verify:

- [ ] Test names are descriptive
- [ ] Docstrings explain what is tested
- [ ] AAA pattern is followed
- [ ] Edge cases are covered
- [ ] No hard-coded paths or URLs
- [ ] Uses appropriate fixtures
- [ ] External dependencies mocked
- [ ] Tests are independent
- [ ] Tests pass locally
- [ ] Coverage improved or maintained

---

## Example: Complete Test Module

```python
"""Tests for ProxyManager module."""

import pytest
from unittest.mock import Mock, patch
from scraper.proxy_manager import ProxyManager


class TestProxyManager:
    """Tests for ProxyManager class."""

    @pytest.fixture
    def proxy_list(self):
        """Provide test proxy list."""
        return [
            "http://proxy1.com:8080",
            "http://proxy2.com:8080",
            "http://proxy3.com:8080"
        ]

    @pytest.fixture
    def manager(self, proxy_list):
        """Provide ProxyManager instance."""
        return ProxyManager(proxies=proxy_list)

    def test_initialization_with_proxy_list(self, proxy_list):
        """Unit: ProxyManager initializes with proxy list."""
        manager = ProxyManager(proxies=proxy_list)
        assert manager.proxy_count() == 3

    def test_round_robin_rotation(self, manager):
        """Unit: get_next_proxy() rotates through proxies."""
        assert manager.get_next_proxy() == "http://proxy1.com:8080"
        assert manager.get_next_proxy() == "http://proxy2.com:8080"
        assert manager.get_next_proxy() == "http://proxy3.com:8080"
        assert manager.get_next_proxy() == "http://proxy1.com:8080"

    def test_remove_failed_proxy(self, manager):
        """Unit: report_failure() removes proxy after threshold."""
        # Report 3 failures for proxy1
        for _ in range(3):
            manager.report_failure("http://proxy1.com:8080")

        # Proxy1 should be removed
        assert manager.proxy_count() == 2
        assert "http://proxy1.com:8080" not in manager.get_all_proxies()

    @pytest.mark.parametrize("strategy", ["round-robin", "random"])
    def test_rotation_strategies(self, proxy_list, strategy):
        """Unit: Manager supports different rotation strategies."""
        manager = ProxyManager(proxies=proxy_list, strategy=strategy)
        proxy = manager.get_next_proxy()
        assert proxy in proxy_list
```

---

## Next Steps

- **Architecture Diagrams**: [10. Architecture Diagrams](10_architecture_diagram.md)
- **Best Practices**: [11. Best Practices](11_best_practices.md)
- **Running Tests**: [08. Running Tests](08_running_tests.md)
