# 04. End-to-End  (E2E) Tests

## Overview

End-to-end tests simulate **complete user journeys** through the application, validating that all components work together seamlessly from start to finish.

---

## Philosophy

> "E2E tests validate that the system works the way users expect it to, not just how developers think it should."

### Core Principles
1. **User-Centric**: Test from the user's perspective
2. **Realistic**: Use real browsers, real data flows
3. **Complete Workflows**: Cover entire journeys, not just features
4. **Production-Like**: Test in environments similar to production
5. **Valuable**: Focus on critical user paths

---

## E2E Test Scenarios

```
tests/e2e/
├── test_complete_scraping_cycle.py  # Full scraping lifecycle
├── test_dashboard_workflow.py       # Dashboard user workflows
├── test_multi_site_comparison.py    # Multi-site scraping
└── test_real_site_scraping.py       # Real-world site testing
```

---

## Scenario 1: Complete Scraping Cycle

**File**: `test_complete_scraping_cycle.py`

**User Journey**: User provides URL → Scraper executes → Data extracted → Data exported

### Complete Test Example
```python
def test_full_scraping_lifecycle_with_json_export():
    """E2E: Complete scraping from URL input to JSON export."""
    # Step 1: User configures scraper
    config = {
        "timeout": 30,
        "headless": True,
        "user_agent_rotation": True
    }
    scraper = Scraper(config=config)

    # Step 2: User provides target URL
    target_url = "https://books.toscrape.com/catalogue/page-1.html"

    # Step 3: Scraper executes
    result = scraper.scrape_url(target_url)

    # Step 4: Verify data extracted
    assert result.status == "success"
    assert len(result.data) > 0
    assert result.data[0].get("title") is not None

    # Step 5: User exports to JSON
    output_path = "test_output.json"
    scraper.export_to_json(result.data, output_path)

    # Step 6: Verify export
    assert os.path.exists(output_path)

    with open(output_path, "r") as f:
        exported_data = json.load(f)

    assert len(exported_data) == len(result.data)
    assert exported_data[0]["title"] == result.data[0]["title"]

    # Cleanup
    os.remove(output_path)

def test_scraping_with_authentication():
    """E2E: Scraping protected content with authentication."""
    scraper = Scraper()

    # User provides credentials
    scraper.set_authentication(
        username="testuser",
        password="testpass"
    )

    # Scrape protected page
    result = scraper.scrape_url("https://example.com/protected")

    assert result.status == "success"
    assert "Login required" not in result.html

def test_scraping_with_pagination():
    """E2E: Scraping multiple pages automatically."""
    scraper = Scraper()

    # Configure pagination
    scraper.set_pagination(
        next_button_selector=".next",
        max_pages=5
    )

    # Scrape with automatic pagination
    results = scraper.scrape_url("https://example.com/products")

    # Verify data from multiple pages
    assert len(results.pages_scraped) == 5
    assert len(results.data) > 50  # More than one page worth
```

---

## Scenario 2: Dashboard Workflow

**File**: `test_dashboard_workflow.py`

**User Journey**: Launch dashboard → Create job → Monitor → View results → Export

### Dashboard Test Example
```python
def test_complete_dashboard_workflow():
    """E2E: Complete dashboard user workflow."""
    from scraper.dashboard import create_app
    from selenium import webdriver

    # Step 1: Launch dashboard
    app = create_app()
    app_process = start_app_in_background()

    # Step 2: User opens dashboard in browser
    driver = webdriver.Chrome()
    driver.get("http://localhost:5000")

    # Step 3: User creates scraping job
    driver.find_element_by_id("url-input").send_keys("https://example.com")
    driver.find_element_by_id("config-selector").click()
    driver.find_element_by_xpath("//option[text()='E-commerce']").click()
    driver.find_element_by_id("start-button").click()

    # Step 4: Verify job created
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "job-card"))
    )

    # Step 5: Monitor progress
    job_status = driver.find_element_by_class_name("job-status").text
    assert job_status in ["Running", "Completed"]

    # Wait for completion
    WebDriverWait(driver, 60).until(
        lambda d: d.find_element_by_class_name("job-status").text == "Completed"
    )

    # Step 6: View results
    driver.find_element_by_class_name("view-results-btn").click()

    # Verify results displayed
    results_table = driver.find_element_by_id("results-table")
    rows = results_table.find_elements_by_tag_name("tr")
    assert len(rows) > 1  # Header + data rows

    # Step 7: Export results
    driver.find_element_by_id("export-json-btn").click()

    # Verify download triggered
    WebDriverWait(driver, 5).until(
        lambda d: len(os.listdir("downloads")) > 0
    )

    # Cleanup
    driver.quit()
    app_process.terminate()
```

---

## Scenario 3: Multi-Site Comparison

**File**: `test_multi_site_comparison.py`

**User Journey**: Configure multiple sites → Scrape all → Compare → Generate report

### Multi-Site Test Example
```python
def test_price_comparison_across_multiple_sites():
    """E2E: Compare product prices across multiple e-commerce sites."""
    # Step 1: Configure comparison
    comparison_scraper = ComparisonScraper()

    sites = [
        {
            "name": "Amazon",
            "url": "https://amazon.com/product/B08N5WRWNW",
            "config": "amazon_config"
        },
        {
            "name": "BestBuy",
            "url": "https://bestbuy.com/product/6428324",
            "config": "bestbuy_config"
        },
        {
            "name": "Walmart",
            "url": "https://walmart.com/product/123456",
            "config": "walmart_config"
        }
    ]

    # Step 2: Scrape all sites
    results = comparison_scraper.scrape_all(sites)

    # Step 3: Verify all sites scraped
    assert len(results) == 3
    for result in results:
        assert result.status == "success"
        assert result.data.get("price") is not None

    # Step 4: Compare prices
    comparison = comparison_scraper.compare(results, field="price")

    # Step 5: Find best deal
    best_deal = comparison.get_lowest("price")
    assert best_deal.site_name in ["Amazon", "BestBuy", "Walmart"]
    assert best_deal.price < max(r.data["price"] for r in results)

    # Step 6: Generate comparison report
    report = comparison_scraper.generate_report(comparison, format="html")

    # Verify report
    assert "<table" in report
    assert "Amazon" in report
    assert "BestBuy" in report
    assert "Walmart" in report
```

---

## Scenario 4: Real Site Scraping

**File**: `test_real_site_scraping.py`

**User Journey**: Scrape real production websites with real challenges

> **⚠️ IMPORTANT**: These tests hit real websites. Run sparingly, respect robots.txt, implement rate limiting.

### Real Site Test Examples
```python
@pytest.mark.slow
@pytest.mark.real_site
def test_scrape_books_toscrape():
    """E2E: Scrape real test website (books.toscrape.com)."""
    scraper = Scraper()

    result = scraper.scrape_url("https://books.toscrape.com/")

    # Verify realistic data
    assert len(result.data) >= 20  # At least 20 books

    # Verify required fields
    for book in result.data:
        assert "title" in book
        assert "price" in book
        assert book["price"] > 0

@pytest.mark.slow
@pytest.mark.real_site
@pytest.mark.cloudflare
def test_scrape_cloudflare_protected_site():
    """E2E: Handle Cloudflare-protected sites."""
    scraper = Scraper(stealth_mode=True)

    # Attempt to scrape Cloudflare-protected site
    result = scraper.scrape_url("https://example-with-cloudflare.com")

    # Should either succeed or gracefully fail
    if result.status == "cloudflare_challenge":
        assert result.challenge_solved in [True, False]
    else:
        assert result.status == "success"
        assert len(result.data) > 0

@pytest.mark.slow
@pytest.mark.real_site
def test_scrape_javascript_heavy_site():
    """E2E: Scrape JavaScript-heavy SPA."""
    scraper = Scraper(browser="playwright")

    result = scraper.scrape_url("https://example-spa.com")

    # Wait for JS to load
    scraper.wait_for_selector(".product-item", timeout=10)

    # Verify dynamic content loaded
    assert len(result.data) > 0
    assert result.rendering_engine == "playwright"
```

---

## E2E Testing Best Practices

### 1. Use Page Object Pattern

```python
class ProductPage:
    """Page object for product listing pages."""

    def __init__(self, driver):
        self.driver = driver

    def get_product_titles(self):
        elements = self.driver.find_elements_by_class_name("product-title")
        return [el.text for el in elements]

    def get_product_prices(self):
        elements = self.driver.find_elements_by_class_name("product-price")
        return [parse_price(el.text) for el in elements]

def test_product_page_extraction():
    """E2E: Extract products using page object."""
    driver = webdriver.Chrome()
    driver.get("https://example.com/products")

    page = ProductPage(driver)
    titles = page.get_product_titles()
    prices = page.get_product_prices()

    assert len(titles) > 0
    assert len(prices) == len(titles)
```

### 2. Handle Waits Properly

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_scraping_with_dynamic_content():
    """E2E: Wait for dynamic content to load."""
    driver = webdriver.Chrome()
    driver.get("https://spa-example.com")

    # Explicit wait for specific element
    wait = WebDriverWait(driver, 10)
    products = wait.until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "product"))
    )

    assert len(products) > 0
```

### 3. Clean Up Resources

```python
@pytest.fixture
def browser():
    """Provide browser instance with automatic cleanup."""
    driver = webdriver.Chrome()
    yield driver
    driver.quit()

def test_with_browser(browser):
    """E2E: Test using browser fixture."""
    browser.get("https://example.com")
    # Test code here
    # Browser automatically closes after test
```

### 4. Capture Screenshots on Failure

```python
@pytest.fixture(autouse=True)
def screenshot_on_failure(request, browser):
    """Capture screenshot if test fails."""
    yield
    if request.node.rep_call.failed:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"screenshots/failure_{request.node.name}_{timestamp}.png"
        browser.save_screenshot(screenshot_path)
```

---

## Running E2E Tests

### Run All E2E Tests
```bash
python tests/run_e2e_tests.py
# or
pytest tests/e2e/ -v
```

### Run Specific Scenario
```bash
pytest tests/e2e/test_complete_scraping_cycle.py -v
```

### Skip Real Site Tests (Faster)
```bash
pytest tests/e2e/ -m "not real_site" -v
```

### Run Only Real  Site Tests
```bash
pytest tests/e2e/ -m "real_site" -v
```

### Run With Headed Browser (Visual)
```bash
HEADLESS=false pytest tests/e2e/ -v
```

---

## E2E vs Integration Tests

| Aspect | Integration Tests | E2E Tests |
|--------|------------------|-----------|
| Scope | 2-5 components | Entire system |
| Browser | Not typically | Always |
| External Services | Mocked | Real (or realistic) |
| Speed | Seconds | Minutes |
| Purpose | Component interaction | User journey |
| Frequency | Every commit | Pre-release |

---

## Common Challenges and Solutions

### 1. Flaky Tests

**Problem**: Tests pass/fail randomly

**Solutions**:
- Use explicit waits instead of sleep()
- Wait for elements instead of fixed timeouts
- Handle network variability gracefully

```python
# BAD: Flaky
def test_flaky():
    driver.get(url)
    time.sleep(5)  # Might not be enough
    element = driver.find_element_by_id("result")

# GOOD: Reliable
def test_reliable():
    driver.get(url)
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "result"))
    )
```

### 2. Slow Execution

**Problem**: E2E tests take too long

**Solutions**:
- Run in parallel
- Use headless browsers
- Cache authentication sessions
- Limit data set size in tests

### 3. Environment Dependencies

**Problem**: Tests work locally but fail in CI

**Solutions**:
- Use Docker for consistent environments
- Pin browser versions
- Handle different screen sizes
- Mock external APIs

---

## Next Steps

- **QA Tests**: [05. QA Tests](05_qa_tests.md)
- **Running Tests**: [08. Running Tests](08_running_tests.md)
- **Best Practices**: [11. Best Practices](11_best_practices.md)
