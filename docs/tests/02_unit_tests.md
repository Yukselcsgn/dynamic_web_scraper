# 02. Unit Tests

## Overview

Unit tests form the **foundation** of our testing pyramid. They validate individual components in complete isolation, ensuring that each piece of the scraper works correctly before integration.

---

## Philosophy

### Core Principles

1. **Isolation**: Each test runs independently without external dependencies
2. **Speed**: Target < 100ms per test for rapid feedback
3. **Focus**: Test one thing at a time
4. **Clarity**: Test names describe what they validate
5. **Determinism**: Same input always produces same output

### The FIRST Principles

- **Fast**: Run quickly to enable frequent execution
- **Isolated**: Independent of other tests and external state
- **Repeatable**: Consistent results every time
- **Self-Validating**: Clear pass/fail without manual inspection
- **Timely**: Written alongside or before production code (TDD)

---

## Directory Structure

```
tests/unit/
├── analytics/          # Analytics and metrics collection
├── anti_bot/           # Anti-bot detection and evasion
├── comparison/         # Site comparison utilities
├── core/               # Core scraper functionality
├── css_selectors/      # CSS selector parsing
├── customization/      # Configuration and customization
├── data_parsers/       # HTML, JSON, XML parsing
├── data_processing/    # Data transformation pipelines
├── exceptions/         # Custom exception handling
├── export/             # Data export (JSON, CSV, Excel)
├── logging_manager/    # Logging infrastructure
├── plugins/            # Plugin system architecture
├── proxy_manager/      # Proxy rotation and management
├── reporting/          # Report generation
├── site_detection/     # Automatic site detection
├── user_agent_manager/ # User agent rotation
└── utils/              # Utility functions and helpers
```

---

## Module-Specific Testing Strategies

### 1. Core Module (`unit/core/`)

**Tests**: Core scraper orchestration, initialization, configuration

#### Key Test Areas
- Scraper initialization with various configurations
- URL validation and preprocessing
- Browser management lifecycle
- Method fallback logic (requests → Selenium → Playwright)
- Error handling and recovery

#### Example Tests
```python
def test_scraper_initialization_with_defaults():
    """Unit: Scraper initializes with default configuration."""
    scraper = Scraper()

    assert scraper.config is not None
    assert scraper.browser_config.headless is True
    assert scraper.timeout == 30

def test_scraper_validates_url_format():
    """Unit: Scraper validates URL formats correctly."""
    scraper = Scraper()

    assert scraper._validate_url("https://example.com") is True
    assert scraper._validate_url("http://example.com") is True
    assert scraper._validate_url("ftp://example.com") is False
    assert scraper._validate_url("not-a-url") is False

def test_scraper_method_fallback_on_failure():
    """Unit: Scraper falls back to next method on failure."""
    with patch('scraper.core.scraper.requests.get') as mock_requests:
        mock_requests.side_effect = requests.ConnectionError()

        scraper = Scraper()
        # Should fall back to Selenium
        result = scraper.fetch("https://example.com")

        assert result.method_used == "selenium"
```

---

### 2. Data Parsers (`unit/data_parsers/`)

**Tests**: HTML, JSON, XML parsing logic

#### Key Test Areas
- HTML parsing with BeautifulSoup/lxml
- JSON data extraction and validation
- CSS selector accuracy
- XPath expression handling
- Malformed input handling

#### Example Tests
```python
def test_parse_product_price_with_various_formats():
    """Unit: Price parser handles multiple currency formats."""
    from scraper.parsers import parse_price

    test_cases = [
        ("$19.99", 19.99),
        ("€25.50", 25.50),
        ("£10.00", 10.00),
        ("¥1000", 1000.0),
        ("19.99 USD", 19.99),
        ("FREE", 0.0),
    ]

    for input_price, expected in test_cases:
        assert parse_price(input_price) == expected

def test_html_parser_extracts_meta_tags():
    """Unit: HTML parser extracts meta tags correctly."""
    html = '''
    <html>
    <head>
        <meta name="description" content="Test description">
        <meta property="og:title" content="Test Title">
    </head>
    </html>
    '''

    parser = HTMLParser(html)

    assert parser.get_meta("description") == "Test description"
    assert parser.get_meta("og:title") == "Test Title"

def test_css_selector_validation():
    """Unit: CSS selector validator identifies invalid selectors."""
    from scraper.parsers import validate_css_selector

    assert validate_css_selector("div.class") is True
    assert validate_css_selector("#id") is True
    assert validate_css_selector("[data-attr='value']") is True
    assert validate_css_selector("invalid..selector") is False
```

---

### 3. Proxy Manager (`unit/proxy_manager/`)

**Tests**: Proxy rotation, validation, failure handling

#### Key Test Areas
- Proxy pool management
- Rotation strategies (round-robin, random, performance-based)
- Proxy validation and health checks
- Failure detection and removal
- Authentication handling

#### Example Tests
```python
def test_proxy_manager_round_robin_rotation():
    """Unit: ProxyManager rotates proxies in round-robin order."""
    proxies = ["proxy1.com", "proxy2.com", "proxy3.com"]
    manager = ProxyManager(proxies, strategy="round-robin")

    assert manager.get_next() == "proxy1.com"
    assert manager.get_next() == "proxy2.com"
    assert manager.get_next() == "proxy3.com"
    assert manager.get_next() == "proxy1.com"  # Cycles back

def test_proxy_manager_removes_failing_proxy():
    """Unit: ProxyManager removes proxy after consecutive failures."""
    manager = ProxyManager(["proxy1.com", "proxy2.com"])

    # Simulate failures
    for _ in range(3):  # threshold = 3
        manager.report_failure("proxy1.com")

    available = manager.get_available_proxies()
    assert "proxy1.com" not in available
    assert "proxy2.com" in available

def test_proxy_authentication_formatting():
    """Unit: Proxy auth credentials formatted correctly."""
    proxy = ProxyConfig(
        host="proxy.com",
        port=8080,
        username="user",
        password="pass"
    )

    assert proxy.to_url() == "http://user:pass@proxy.com:8080"
```

---

### 4. Data Processing (`unit/data_processing/`)

**Tests**: Data transformation, cleaning, normalization

#### Key Test Areas
- Data cleaning and normalization
- Type conversion
- Missing data handling
- Deduplication logic
- Data validation

#### Example Tests
```python
def test_normalize_whitespace():
    """Unit: Normalizer removes extra whitespace."""
    from scraper.processing import normalize_whitespace

    input_text = "  Multiple   spaces\n\nand\tlines  "
    expected = "Multiple spaces and lines"

    assert normalize_whitespace(input_text) == expected

def test_deduplicate_items_by_key():
    """Unit: Deduplicator removes duplicates based on key."""
    items = [
        {"id": 1, "name": "Product A"},
        {"id": 2, "name": "Product B"},
        {"id": 1, "name": "Product A Duplicate"},
    ]

    result = deduplicate(items, key="id")

    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[1]["id"] == 2

def test_type_coercion_handles_invalid_input():
    """Unit: Type coercer returns None for invalid conversions."""
    from scraper.processing import coerce_type

    assert coerce_type("123", int) == 123
    assert coerce_type("invalid", int) is None
    assert coerce_type("true", bool) is True
    assert coerce_type("19.99", float) == 19.99
```

---

### 5. Export Module (`unit/export/`)

**Tests**: Data export to various formats

#### Key Test Areas
- JSON export formatting
- CSV export with proper escaping
- Excel export with sheets
- XML export structure
- Custom format support

#### Example Tests
```python
def test_export_to_json_with_pretty_print():
    """Unit: JSON exporter uses pretty printing."""
    data = [{"name": "Product", "price": 19.99}]
    exporter = JSONExporter(pretty=True)

    result = exporter.export(data)

    assert isinstance(result, str)
    assert "\n" in result  # Pretty printed
    assert "  " in result  # Indentation

def test_csv_export_escapes_commas_in_values():
    """Unit: CSV exporter properly escapes comma values."""
    data = [{"description": "Product, with commas"}]
    exporter = CSVExporter()

    result = exporter.export(data)

    assert '\"Product, with commas\"' in result

def test_excel_export_creates_multiple_sheets():
    """Unit: Excel exporter supports multiple sheets."""
    data = {
        "Products": [{"name": "A"}],
        "Orders": [{"order_id": 1}]
    }

    exporter = ExcelExporter()
    workbook = exporter.export(data)

    assert "Products" in workbook.sheetnames
    assert "Orders" in workbook.sheetnames
```

---

### 6. Anti-Bot Module (`unit/anti_bot/`)

**Tests**: Bot detection evasion, stealth techniques

#### Key Test Areas
- User agent rotation
- Header manipulation
- Browser fingerprint randomization
- Behavior randomization (delays, mouse movements)
- Detection of bot challenges

#### Example Tests
```python
def test_user_agent_rotation():
    """Unit: Anti-bot rotates user agents."""
    anti_bot = AntiBotManager()

    ua1 = anti_bot.get_user_agent()
    ua2 = anti_bot.get_user_agent()

    assert ua1 != ua2

def test_stealth_headers_include_realistic_values():
    """Unit: Stealth headers look like real browser."""
    headers = generate_stealth_headers()

    assert "User-Agent" in headers
    assert "Accept-Language" in headers
    assert "Accept-Encoding" in headers
    assert headers["DNT"] == "1"

def test_detect_cloudflare_challenge():
    """Unit: Detector identifies Cloudflare challenges."""
    html_with_challenge = load_fixture("cloudflare_challenge.html")

    assert detect_bot_challenge(html_with_challenge) == "cloudflare"
```

---

### 7. Exception Handling (`unit/exceptions/`)

**Tests**: Custom exceptions, error messages, error recovery

#### Example Tests
```python
def test_scraping_error_captures_context():
    """Unit: ScrapingError captures URL and method."""
    try:
        raise ScrapingError(
            "Failed to scrape",
            url="https://example.com",
            method="selenium"
        )
    except ScrapingError as e:
        assert e.url == "https://example.com"
        assert e.method == "selenium"
        assert "Failed to scrape" in str(e)

def test_retry_exception_includes_attempt_count():
    """Unit: RetryExhaustedError tracks attempts."""
    error = RetryExhaustedError(max_retries=3)

    assert error.max_retries == 3
    assert "3" in str(error)
```

---

## Testing Patterns and Best Practices

### 1. AAA Pattern (Arrange-Act-Assert)

```python
def test_parse_product_title():
    """Unit: Parser extracts product title correctly."""
    # Arrange
    html = '<h1 class="title">Product Name</h1>'
    parser = HTMLParser(html)

    # Act
    title = parser.get_title()

    # Assert
    assert title == "Product Name"
```

### 2. Parametrized Testing

```python
@pytest.mark.parametrize("input,expected", [
    ("$19.99", 19.99),
    ("€25.50", 25.50),
    ("£10.00", 10.00),
    ("FREE", 0.0),
])
def test_price_parsing_various_formats(input, expected):
    """Unit: Price parser handles various currency formats."""
    assert parse_price(input) == expected
```

### 3. Fixture Usage

```python
@pytest.fixture
def sample_html():
    return load_fixture("sample_product.html")

@pytest.fixture
def parser(sample_html):
    return HTMLParser(sample_html)

def test_parser_extracts_price(parser):
    """Unit: Parser extracts price from fixture."""
    assert parser.get_price() == 19.99
```

### 4. Mocking External Dependencies

```python
def test_fetcher_retries_on_timeout():
    """Unit: Fetcher retries on timeout errors."""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = [
            requests.Timeout(),
            Mock(status_code=200, text="Success")
        ]

        fetcher = HttpFetcher(max_retries=2)
        result = fetcher.fetch("https://example.com")

        assert mock_get.call_count == 2
        assert result.text == "Success"
```

### 5. Testing Edge Cases

```python
def test_parser_handles_empty_input():
    """Unit: Parser handles empty input gracefully."""
    parser = HTMLParser("")

    assert parser.get_title() is None
    assert parser.get_links() == []

def test_parser_handles_malformed_html():
    """Unit: Parser handles malformed HTML."""
    parser = HTMLParser("<div><p>Unclosed tags")

    # Should not crash
    result = parser.get_text()
    assert isinstance(result, str)
```

---

## Running Unit Tests

### Run All Unit Tests
```bash
python tests/run_unit_tests.py
# or
pytest tests/unit/ -v
```

### Run Specific Module
```bash
pytest tests/unit/proxy_manager/ -v
pytest tests/unit/data_parsers/ -v
```

### Run With Coverage
```bash
pytest tests/unit/ --cov=scraper --cov-report=html
```

### Run Fast (Skip Slow Tests)
```bash
pytest tests/unit/ -m "not slow"
```

### Run With Watch Mode (TDD)
```bash
pytest-watch tests/unit/
```

---

## Coverage Goals

| Module | Target Coverage | Current | Priority |
|--------|----------------|---------|----------|
| core/ | 90% | - | Critical |
| data_parsers/ | 85% | - | High |
| proxy_manager/ | 85% | - | High |
| anti_bot/ | 80% | - | High |
| export/ | 85% | - | Medium |
| data_processing/ | 85% | - | Medium |
| utils/ | 90% | - | Medium |
| Others | 75% | - | Medium |

---

## Common Anti-Patterns to Avoid

❌ **Testing Implementation Details**
```python
# BAD: Testing internal implementation
def test_parser_uses_beautifulsoup():
    parser = HTMLParser(html)
    assert isinstance(parser._soup, BeautifulSoup)

# GOOD: Testing behavior
def test_parser_extracts_title():
    parser = HTMLParser(html)
    assert parser.get_title() == "Expected Title"
```

❌ **Multiple Assertions on Different Concerns**
```python
# BAD: Testing multiple unrelated things
def test_scraper():
    scraper = Scraper()
    assert scraper.timeout == 30
    assert scraper.parse_html(html) == data
    assert scraper.export_json(data) is not None

# GOOD: Separate tests
def test_scraper_default_timeout():
    assert Scraper().timeout == 30

def test_scraper_parses_html():
    assert Scraper().parse_html(html) == data
```

❌ **External Dependencies**
```python
# BAD: Real network call in unit test
def test_fetch_url():
    result = fetch("https://example.com")
    assert result.status_code == 200

# GOOD: Mocked dependency
def test_fetch_url():
    with patch('requests.get') as mock:
        mock.return_value.status_code = 200
        result = fetch("https://example.com")
        assert result.status_code == 200
```

---

## Next Steps

- **Integration Tests**: [03. Integration Tests](03_integration_tests.md)
- **Running Tests**: [08. Running Tests](08_running_tests.md)
- **Writing New Tests**: [09. Writing New Tests](09_writing_new_tests.md)
- **Fixtures and Mocks**: [07. Fixtures and Mocks](07_fixtures_and_mocks.md)
