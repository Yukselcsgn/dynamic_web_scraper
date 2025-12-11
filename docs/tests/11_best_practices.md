# 11. Best Practices

## Overview

This document provides long-term maintenance strategies, anti-patterns to avoid, and guidelines for keeping tests reliable, maintainable, and valuable over time.

---

## Core Best Practices

### 1. Keep Tests Deterministic

**Principle**: Tests should produce the same result every time they run.

✅ **DO**:
```python
def test_deterministic():
    """Test with fixed data."""
    data = {"timestamp": "2025-01-01T00:00:00Z"}
    result = process(data)
    assert result["date"] == "2025-01-01"
```

❌ **DON'T**:
```python
def test_non_deterministic():
    """Test with current time - result changes."""
    data = {"timestamp": datetime.now()}  # Changes every run!
    result = process(data)
    assert result["date"] == "2025-01-01"  # Will fail tomorrow
```

**Strategies**:
- Mock time/date functions
- Use fixed test data
- Avoid random number generation (or seed it)
- Don't depend on external APIs

---

### 2. Tests Should Be Independent

**Principle**: Each test should run successfully in isolation and in any order.

✅ **DO**:
```python
def test_a():
    """Independent test."""
    scraper = Scraper()  # Fresh instance
    result = scraper.scrape(url)
    assert result is not None

def test_b():
    """Independent test."""
    scraper = Scraper()  # Another fresh instance
    result = scraper.scrape(url)
    assert result is not None
```

❌ **DON'T**:
```python
# Global state shared between tests
shared_scraper = None

def test_a():
    global shared_scraper
    shared_scraper = Scraper()  # Creates shared state

def test_b():
    # Depends on test_a running first!
    assert shared_scraper is not None  # Fragile!
```

---

### 3. Fast Tests Are Better Tests

**Principle**: Keep tests fast to encourage frequent running.

**Speed Targets**:
- Unit tests: < 100ms each
- Integration tests: < 30s each
- E2E tests: < 10min each

**Strategies**:
```python
# Use in-memory databases
@pytest.fixture
def test_db():
    return Database(":memory:")  # Fast!

# Mock slow operations
@patch('time.sleep')
def test_without_waiting(mock_sleep):
    # No actual waiting
    pass

# Use smaller datasets
def test_with_small_data():
    data = ProductFactory.create_batch(10)  # Not 10,000!
```

---

### 4. Test One Thing at a Time

**Principle**: Each test should verify a single behavior.

✅ **DO**:
```python
def test_parser_extracts_title():
    """Test title extraction only."""
    assert parser.extract_title(html) == "Expected Title"

def test_parser_extracts_price():
    """Test price extraction only."""
    assert parser.extract_price(html) == 19.99
```

❌ **DON'T**:
```python
def test_parser_everything():
    """Test too many things."""
    result = parser.parse(html)
    assert result["title"] == "Title"  # Different concern
    assert result["price"] == 19.99    # Different concern
    assert result["url"] == "url"      # Different concern
    assert len(result) > 0             # Different concern
```

---

### 5. Write Tests Before Fixing Bugs

**Principle**: TDD for bug fixes - write failing test, then fix.

**Process**:
```python
# Step 1: Write test that reproduces bug
def test_issue_123_proxy_crash():
    """Regression: Issue #123 - Crash on None proxy."""
    manager = ProxyManager([None, "proxy1"])
    # This SHOULD fail with the bug
    proxy = manager.get_next()  # Crashes!

# Step 2: Fix the code until test passes
# Step 3: Test stays as regression prevention
```

---

## Maintaining Test Data

### Fixture Lifecycle

**Keep fixtures up-to-date with code changes**:

```python
# When data structure changes, update fixtures
# OLD:
{"name": "Product", "price": 19.99}

# NEW (added currency field):
{"name": "Product", "price": 19.99, "currency": "USD"}

# Update ALL fixtures and factories
```

### Mock Data vs Real Data

| Use Mock Data When | Use Real Data When |
|-------------------|--------------------|
| Testing parser logic | E2E tests |
| Unit testing components | Validation tests |
| Fast execution needed | Real-world verification |
| Determinism required | Integration with external services |

---

## Avoiding Flaky Tests

### Common Causes and Solutions

#### 1. **Timing Issues**

❌ **Problem**:
```python
def test_flaky():
    driver.get(url)
    time.sleep(2)  # Might not be enough!
    element = driver.find_element_by_id("result")
```

✅ **Solution**:
```python
def test_reliable():
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "result"))
    )
```

#### 2. **External Dependencies**

❌ **Problem**:
```python
def test_flaky():
    # Real API call - might fail if API is down
    result = fetch_from_api("https://api.example.com")
```

✅ **Solution**:
```python
@patch('requests.get')
def test_reliable(mock_get):
    mock_get.return_value.json.return_value = {"data": "test"}
    result = fetch_from_api("https://api.example.com")
```

#### 3. **Test Order Dependencies**

❌ **Problem**:
```python
def test_a():
    global cache
    cache = load_data()

def test_b():
    # Depends on test_a running first!
    assert cache is not None
```

✅ **Solution**:
```python
@pytest.fixture
def cache():
    return load_data()

def test_a(cache):
    assert cache is not None

def test_b(cache):
    assert cache is not None
```

---

## Selector Maintenance

### Strategies for Evolving Websites

**Problem**: Websites change, selectors break.

**Solutions**:

#### 1. **Centralize Selectors**
```python
# config/selectors.py
SELECTORS = {
    "amazon": {
        "product_title": "#productTitle",
        "product_price": ".a-price-whole",
        "add_to_cart": "#add-to-cart-button"
    }
}

# Easy to update in one place!
```

#### 2. **Use Multiple Selectors (Fallback)**
```python
def find_title(html):
    """Try multiple selectors."""
    selectors = [
        "#productTitle",      # Primary
        ".product-title",     # Fallback 1
        "h1.title",           # Fallback 2
    ]

    for selector in selectors:
        result = html.select_one(selector)
        if result:
            return result.text

    return None
```

#### 3. **Test with Multiple HTML Versions**
```python
# fixtures/html_samples/
# ├── amazon_product_2025_01.html  # January version
# ├── amazon_product_2025_02.html  # February version
# └── amazon_product_2025_03.html  # March version

@pytest.mark.parametrize("fixture", [
    "amazon_product_2025_01.html",
    "amazon_product_2025_02.html",
    "amazon_product_2025_03.html",
])
def test_parser_works_across_versions(fixture):
    """Test parser handles different HTML versions."""
    html = load_fixture(fixture)
    result = parse_product(html)
    assert result["title"] is not None
```

---

## Version Pinning and Dependencies

### Test Dependency Management

```python
# requirements-test.txt
pytest==8.0.0           # Pin exact version
pytest-cov==4.1.0       # Pin exact version
pytest-xdist==3.5.0     # Parallel execution
pytest-timeout==2.2.0   # Timeout support

# Pin browser drivers
selenium==4.16.0
webdriver-manager==4.0.1

# Why pin?
# - Reproducible test results
# - Avoid breaking changes
# - Consistent CI/CD environment
```

### Updating Test Dependencies

```bash
# 1. Check for updates
pip list --outdated

# 2. Update one at a time
pip install --upgrade pytest

# 3. Run full test suite
python tests/run_full_suite.py

# 4. If pass, update requirements-test.txt
# 5. If fail, investigate and fix or revert
```

---

## Test Coverage Guidelines

### Don't Chase 100% Coverage

**80% coverage is better than 90% with bad tests.**

✅ **DO Cover**:
- Public APIs
- Business logic
- Error paths
- Edge cases
- Complex algorithms

❌ **DON'T Obsess Over**:
- Getters/setters
- Simple property access
- Third-party code
- Configuration files

### Meaningful Coverage

```python
# BAD: High coverage, low value
def test_getter():
    obj = MyClass()
    assert obj.name is not None  # Meaningless test!

# GOOD: Lower coverage, high value
def test_complex_calculation():
    """Test edge case in complex algorithm."""
    input_data = create_edge_case()
    result = complex_algorithm(input_data)
    assert result == expected_edge_case_output
```

---

## Refactoring Tests

### When to Refactor Tests

✅ **Refactor when**:
- Tests are duplicated
- Setup code is repeated
- Tests are hard to understand
- Tests are slow without reason

**Refactoring Example**:

**Before** (Duplication):
```python
def test_parse_product_a():
    html = "<div class='product'>Product A</div>"
    parser = HTMLParser(html)
    result = parser.extract_product()
    assert result["name"] == "Product A"

def test_parse_product_b():
    html = "<div class='product'>Product B</div>"
    parser = HTMLParser(html)
    result = parser.extract_product()
    assert result["name"] == "Product B"
```

**After** (Parametrized):
```python
@pytest.mark.parametrize("product_name", ["Product A", "Product B"])
def test_parse_product(product_name):
    html = f"<div class='product'>{product_name}</div>"
    parser = HTMLParser(html)
    result = parser.extract_product()
    assert result["name"] == product_name
```

---

## Snapshot Testing

### When to Use Snapshots

**Use for**:
- HTML output
- JSON responses
- Generated reports
- Complex data structures

**Example**:
```python
def test_report_generation(snapshot):
    """Test report matches snapshot."""
    report = generate_report(data)
    snapshot.assert_match(report, "report.html")

# First run: creates snapshot
# Subsequent runs: compare against snapshot
# If intentional change: update snapshot with --snapshot-update
```

---

## Documentation and Comments

### Test Documentation Standards

```python
def test_complex_scenario():
    """<Type>: <What is tested>.

    Context: Why this test exists
    Edge Case: What edge case is covered
    Related: Links to issues, PRs, documentation

    Example:
        result = function(edge_case_input)
        assert result == expected
    """
    # Implementation
```

### When to Add Comments

```python
def test_with_comments():
    """Test with helpful inline comments."""
    # Arrange: Create edge case that triggered Issue #123
    data = create_circular_reference()

    # Act: Should detect cycle and stop
    processor = DataProcessor(max_depth=10)
    result = processor.process(data)

    # Assert: Cycle was detected (no infinite loop)
    assert result.cycle_detected is True
    assert result.depth < 10
```

---

## CI/CD Best Practices

### Optimizing CI/CD Test Execution

**1. Parallelize Tests**
```yaml
# .github/workflows/test.yml
jobs:
  test:
    strategy:
      matrix:
        test-group: [unit, integration, e2e]
    steps:
      - run: pytest tests/${{ matrix.test-group }}
```

**2. Cache Dependencies**
```yaml
- name: Cache pip
  uses: actions/cache@v2
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

**3. Fail Fast**
```bash
# Stop on first failure in CI
pytest -x
```

**4. Retry Flaky Tests**
```bash
# Retry failed tests up to 3 times
pytest --reruns 3 --reruns-delay 1
```

---

## Monitoring Test Health

### Key Metrics to Track

| Metric | Target | Action if Off Target |
|--------|--------|---------------------|
| Test execution time | < 60 min | Parallelize or optimize |
| Flaky test rate | < 1% | Fix or quarantine |
| Test coverage | > 80% | Add tests for uncovered code |
| Test failure rate | < 5% | Investigate and fix |

### Quarantine Flaky Tests

```python
@pytest.mark.flaky  # Mark as known flaky
@pytest.mark.skip(reason="Flaky - see Issue #456")
def test_sometimes_fails():
    """Quarantined until fixed."""
    pass
```

---

## Anti-Patterns to Avoid

### 1. ❌ Testing Implementation Details

Focus on **behavior**, not **implementation**.

### 2. ❌ Brittle Tests

Tests shouldn't break from minor unrelated changes.

### 3. ❌ Slow Test Suites

If tests are slow, developers won't run them.

### 4. ❌ Meaningless Assertions

Every assertion should test something valuable.

### 5. ❌ Test Code Duplication

Use fixtures and helpers to reduce duplication.

---

## Summary: The Golden Rules

1. **Deterministic**: Same input → Same output
2. **Independent**: Tests don't affect each other
3. **Fast**: Quick execution encourages frequent running
4. **Focused**: One test, one behavior
5. **Maintainable**: Easy to understand and update
6. **Valuable**: Tests that catch real bugs
7. **Documented**: Clear purpose and context

---

## Resources

- [Overview](00_overview.md) - Test architecture overview
- [Writing New Tests](09_writing_new_tests.md) - Style guide
- [Running Tests](08_running_tests.md) - Execution guide
- [Fixtures and Mocks](07_fixtures_and_mocks.md) - Test infrastructure

---

**Remember**: Good tests are an investment that pays dividends in reliability, confidence, and development speed. Maintain them with the same care as production code.
