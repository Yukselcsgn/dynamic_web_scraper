# 06. Regression Tests

## Overview

Regression tests ensure that **previously fixed bugs don't resurface** and that deprecated features continue to work during the deprecation period.

---

## Philosophy

> "Regression tests are our insurance policy against repeating past mistakes."

### Core Principles
1. **Bug Memory**: Each fixed bug gets a permanent test
2. **Historical Context**: Tests reference issue numbers and dates
3. **Backward Compatibility**: Deprecated features keep working until removal
4. **Never Delete**: Only remove tests when features are fully removed
5. **Documentation**: Tests document what went wrong and how it was fixed

---

## Directory Structure

```
tests/regression/
├── test_bug_fixes.py              # Specific bug scenarios
└── test_deprecated_features.py   # Backward compatibility
```

---

## Bug Fixes (`test_bug_fixes.py`)

Each test addresses a specific historical issue with full documentation.

### Test Template

```python
def test_issue_XXX_brief_description():
    """Regression: Issue #XXX - Full issue description.

    Bug: What was broken
    Symptoms: How it manifested
    Cause: Root cause if known
    Fixed: Date fixed
    Related: PR numbers, commit hashes

    This test ensures the fix remains in place.
    """
    # Test code that would fail with the original bug
    # But passes with the fix
```

### Examples

```python
def test_issue_123_proxy_rotation_crash_on_none():
    """Regression: Issue #123 - ProxyManager crashes when proxy list contains None.

    Bug: ProxyManager.get_next_proxy() crashed with AttributeError when None in list
    Symptoms: Scraper would crash instead of skipping invalid proxies
    Cause: Missing null check in rotation logic
    Fixed: 2025-11-15
    Related: PR #456, commit a1b2c3d
    """
    proxy_manager = ProxyManager()

    # Add proxies with None values (should not crash)
    proxy_manager.add_proxies([
        None,
        "http://proxy1.com:8080",
        None,
        "http://proxy2.com:8080"
    ])

    # Should skip None values without crashing
    proxy = proxy_manager.get_next_proxy()
    assert proxy is not None
    assert proxy in ["http://proxy1.com:8080", "http://proxy2.com:8080"]

def test_issue_234_empty_data_considered_success():
    """Regression: Issue #234 - HTTP 200 with empty data marked as success.

    Bug: Scraper marked attempts as successful even when no data extracted
    Symptoms: Fallback methods never tried, silent failures on JS-heavy sites
    Cause: Success determined by HTTP code, not data extraction
    Fixed: 2025-12-08
    Related: PR #567, Issue #234

    This bug prevented Playwright fallback from executing when Selenium
    returned empty results on Cloudflare-protected sites.
    """
    scraper = Scraper()

    # Mock empty data response
    with patch.object(scraper, '_fetch_selenium') as mock_selenium:
        mock_selenium.return_value = ScrapingResult(
            status_code=200,
            html="<html><body></body></html>",
            data=[]  # Empty data
        )

        # Should trigger fallback to Playwright
        result = scraper.scrape_url("https://example.com")

        # Verify fallback occurred
        assert result.method_used != "selenium"
        assert result.fallback_triggered is True

def test_issue_345_unicode_encoding_in_csv_export():
    """Regression: Issue #345 - Unicode characters corrupted in CSV export.

    Bug: Non-ASCII characters became garbled in CSV exports
    Symptoms: Product names with accents/emojis displayed as �
    Cause: CSV writer not using UTF-8 encoding
    Fixed: 2025-10-20
    Related: PR #678
    """
    data = [
        {"name": "Café Français", "price": 19.99},
        {"name": "Piñata 🎉", "price": 25.00}
    ]

    exporter = CSVExporter()
    csv_content = exporter.export(data)

    # Verify unicode preserved
    assert "Café" in csv_content
    assert "Français" in csv_content
    assert "Piñata" in csv_content
    assert "🎉" in csv_content or "\\U0001f389" in csv_content

def test_issue_456_infinite_loop_on_circular_pagination():
    """Regression: Issue #456 - Infinite loop with circular pagination.

    Bug: Scraper enters infinite loop when pagination links form a circle
    Symptoms: Script never completes, uses 100% CPU
    Cause: No tracking of visited pages
    Fixed: 2025-09-15
    Related: PR #789
    """
    scraper = Scraper()

    # Mock circular pagination (page1 → page2 → page1)
    responses = {
        "page1": '<a class="next" href="page2">Next</a>',
        "page2": '<a class="next" href="page1">Next</a>'
    }

    def mock_fetch(url):
        return Mock(text=responses.get(url, ""))

    with patch.object(scraper, 'fetch_url', side_effect=mock_fetch):
        scraper.set_pagination(next_selector=".next", max_pages=10)

        # Should detect cycle and stop (not loop infinitely)
        results = scraper.scrape_url("page1")

        # Should have visited both pages but stopped
        assert len(results.pages_visited) == 2
        assert results.circular_pagination_detected is True
```

---

## Deprecated Features (`test_deprecated_features.py`)

Tests ensure backward compatibility during deprecation periods.

### Deprecation Timeline

1. **Announcement**: Feature marked deprecated, warning added
2. **Deprecation Period**: 3-6 months (version dependent)
3. **Removal**: Feature removed in next major version

### Test Template

```python
def test_deprecated_FEATURE_NAME():
    """Regression: Deprecated 'feature_name' still works.

    Deprecated: YYYY-MM-DD (version X.Y.Z)
    Remove: YYYY-MM-DD (version A.B.C)
    Replacement: new_feature_name
    Migration Guide: docs/migration.md#feature-name
    """
    import warnings

    with warnings.catch_warnings(record=True) as w:
        # Use deprecated feature
        result = deprecated_function()

        # Verify deprecation warning raised
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "deprecated" in str(w[0].message).lower()

        # But feature still works
        assert result is not None
```

### Examples

```python
def test_deprecated_headless_parameter():
    """Regression: Deprecated 'headless' parameter still works.

    Deprecated: 2025-12-01 (version 2.0.0)
    Remove: 2026-06-01 (version 3.0.0)
    Replacement: Use browser_config={'headless': True}
    Migration Guide: docs/migration.md#headless
    """
    import warnings

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        # Use deprecated parameter
        scraper = Scraper(headless=True)

        # Verify warning raised
        assert len(w) == 1
        assert issubclass(w[-1].category, DeprecationWarning)
        assert "headless" in str(w[-1].message).lower()
        assert "browser_config" in str(w[-1].message).lower()

        # But parameter still works
        assert scraper.browser_config.headless is True

def test_deprecated_scrape_method_with_string():
    """Regression: Deprecated scrape(url_string) still works.

    Deprecated: 2025-11-01 (version 1.9.0)
    Remove: 2026-05-01 (version 2.5.0)
    Replacement: Use scrape_url(url_string)
    Migration Guide: docs/migration.md#scrape-method
    """
    with warnings.catch_warnings(record=True) as w:
        scraper = Scraper()

        # Deprecated: scrape() with string
        result = scraper.scrape("https://example.com")

        # Warning should be raised
        assert any("scrape_url" in str(warning.message) for warning in w)

        # But still works
        assert result is not None

def test_deprecated_json_export_method():
    """Regression: Deprecated to_json() method still works.

    Deprecated: 2025-10-15 (version 1.8.0)
    Remove: 2026-04-15 (version 2.4.0)
    Replacement: Use export_to_json()
    """
    scraper = Scraper()
    data = [{"item": "test"}]

    with warnings.catch_warnings(record=True):
        # Deprecated method
        json_output = scraper.to_json(data)

        # Still works
        assert json_output is not None
        assert "test" in json_output
```

---

## Edge Cases and Historical Bugs

```python
def test_issue_567_timezone_aware_datetime_serialization():
    """Regression: Issue #567 - Timezone-aware datetimes fail JSON export.

    Bug: JSON export crashed with timezone-aware datetime objects
    Fixed: 2025-08-10
    """
    from datetime import datetime, timezone

    data = [{
        "timestamp": datetime.now(timezone.utc),
        "event": "scrape_completed"
    }]

    exporter = JSONExporter()

    # Should not crash
    json_output = exporter.export(data)
    assert json_output is not None
    assert "scrape_completed" in json_output

def test_issue_678_empty_css_selector_handling():
    """Regression: Issue #678 - Empty CSS selector causes browser crash.

    Bug: Empty or whitespace-only selectors crashed browser
    Fixed: 2025-07-05
    """
    scraper = Scraper()

    # Should handle gracefully, not crash
    result = scraper.find_elements("   ")  # Whitespace selector
    assert result == []

    result = scraper.find_elements("")  # Empty selector
    assert result == []

def test_issue_789_concurrent_browser_instances():
    """Regression: Issue #789 - Concurrent browser instances interfere.

    Bug: Multiple Scraper instances shared browser state
    Fixed: 2025-06-20
    """
    scraper1 = Scraper()
    scraper2 = Scraper()

    # Each should have independent browser
    scraper1.scrape_url("https://example1.com")
    scraper2.scrape_url("https://example2.com")

    # Browsers should be different instances
    assert scraper1.browser != scraper2.browser
    assert scraper1.browser.current_url != scraper2.browser.current_url
```

---

## Running Regression Tests

### Run All Regression Tests
```bash
pytest tests/regression/ -v
```

### Run Only Bug Fix Tests
```bash
pytest tests/regression/test_bug_fixes.py -v
```

### Run Only Deprecated Feature Tests
```bash
pytest tests/regression/test_deprecated_features.py -v
```

### Run Specific Issue Test
```bash
pytest tests/regression/test_bug_fixes.py::test_issue_123 -v
```

---

## When to Add Regression Tests

✅ **Always add when:**
- Fixing a bug that wasn't caught by existing tests
- Fixing a bug that affected users in production
- Implementing a complex bug fix
- Fixing a bug that could easily reoccur

✅ **Consider adding when:**
- Fixing a typo that caused issues
- Fixing an edge case
- User reported an issue

❌ **Don't need to add when:**
- The bug is already covered by existing tests
- It's a trivial fix with no risk of regression

---

## Best Practices

### 1. Document Thoroughly

```python
def test_issue_999_example():
    """Regression: Issue #999 - Full description.

    Bug: What broke
    Cause: Why it broke
    Impact: Who was affected
    Fixed: When fixed
    Links: GitHub issue, PR
    """
```

### 2. Make Tests Fail with the Bug

```python
# Test should demonstrate the bug would cause failure
def test_bug_fix():
    """This test would FAIL with the original bug."""
    # Code that triggers the bug path
    # With the fix, test passes
```

### 3. Keep Tests Simple

```python
# Focus on the specific bug, not everything
def test_specific_bug():
    # Minimal setup
    # Trigger bug condition
    # Assert fix works
```

### 4. Don't Delete Old Tests

```python
# Even for very old bugs
def test_issue_001_from_2020():
    """Still valuable to keep this."""
    # Old bugs can resurface
```

---

## Regression Test Metrics

| Metric | Target | Purpose |
|--------|--------|---------|
| Bug fix tests | 1 per reported bug | Prevent recurrence |
| Deprecated feature tests | 100% coverage | Ensure backward compat |
| Test execution time | < 5 minutes | Quick feedback |
| Test failure rate | 0% in CI | Always passing |

---

## Next Steps

- **Fixtures and Mocks**: [07. Fixtures and Mocks](07_fixtures_and_mocks.md)
- **Running Tests**: [08. Running Tests](08_running_tests.md)
- **Best Practices**: [11. Best Practices](11_best_practices.md)
