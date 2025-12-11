# 05. QA Tests (Quality Assurance)

## Overview

QA tests validate **non-functional requirements** across six critical quality dimensions, ensuring production-level quality beyond correctness.

---

## QA Test Categories

```
tests/qa/
├── compatibility/       # Cross-platform, browser, version testing
├── performance/         # Speed, throughput, resource usage
├── reliability/         # Error handling, recovery, consistency
├── scalability/         # Load handling, horizontal scaling
├── security/            # Vulnerability prevention, data protection
└── usability/           # Developer experience, API ergonomics
```

---

## 1. Compatibility Tests

**Location**: `tests/qa/compatibility/`

**Purpose**: Ensure the scraper works across different browsers, platforms, and dependency versions.

### Test Files
- `test_browser_compatibility.py` - Chrome, Firefox, Safari, Edge
- `test_platform_compatibility.py` - Windows, macOS, Linux
- `test_python_versions.py` - Python 3.8-3.12
- `test_selenium_versions.py` - Selenium version compatibility

### Examples

```python
@pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
def test_scraper_works_across_browsers(browser):
    """QA/Compat: Scraper works on major browsers."""
    scraper = Scraper(browser=browser)
    result = scraper.scrape_url("https://example.com")

    assert result.status == "success"
    assert len(result.data) > 0

@pytest.mark.parametrize("python_version", ["3.8", "3.9", "3.10", "3.11", "3.12"])
def test_python_version_compatibility(python_version):
    """QA/Compat: Package works on supported Python versions."""
    # Run via tox or Docker with different Python versions
    subprocess.run(
        [f"python{python_version}", "-m", "pytest", "tests/unit/", "-x"],
        check=True
    )

@pytest.mark.parametrize("platform", ["linux", "darwin", "win32"])
def test_platform_specific_features(platform):
    """QA/Compat: Platform-specific code works correctly."""
    if sys.platform != platform:
        pytest.skip(f"Skipping {platform} test")

    scraper = Scraper()
    assert scraper.platform == platform
```

---

## 2. Performance Tests

**Location**: `tests/qa/performance/`

**Purpose**: Measure and validate performance characteristics under realistic workloads.

### Test Files
- `test_concurrent_requests.py` - Concurrent scraping performance
- `test_database_performance.py` - Database query/write speed
- `test_large_dataset_handling.py` - Large data processing
- `test_memory_usage.py` - Memory consumption & leaks
- `test_scraping_speed.py` - Scraping throughput

### Examples

```python
def test_concurrent_scraping_performance():
    """QA/Perf: Handle 10 concurrent scraping tasks."""
    import concurrent.futures
    import time

    urls = [f"https://example.com/page/{i}" for i in range(10)]
    scraper = Scraper()

    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(scraper.scrape_url, url) for url in urls]
        results = [f.result() for f in futures]

    elapsed = time.time() - start_time

    # Performance assertions
    assert all(r.status == "success" for r in results)
    assert elapsed < 60  # Should complete in < 1 minute

def test_memory_usage_stays_bounded():
    """QA/Perf: Memory usage doesn't grow unbounded."""
    import tracemalloc

    tracemalloc.start()
    scraper = Scraper()

    initial_memory = tracemalloc.get_traced_memory()[0]

    # Scrape 100 pages
    for i in range(100):
        scraper.scrape_url(f"https://example.com/page/{i}")
        scraper.clear_cache()  # Simulate memory cleanup

    current_memory = tracemalloc.get_traced_memory()[0]
    memory_growth = current_memory - initial_memory

    tracemalloc.stop()

    # Memory shouldn't grow more than 100MB
    assert memory_growth < 100 * 1024 * 1024

def test_large_dataset_processing_performance():
    """QA/Perf: Process large datasets efficiently."""
    # Generate large dataset
    large_dataset = [{"item": f"product_{i}"} for i in range(10000)]

    processor = DataProcessor()

    start = time.time()
    result = processor.process_batch(large_dataset)
    elapsed = time.time() - start

    assert len(result) == 10000
    assert elapsed < 5  # Target: < 5 seconds for 10k items
```

---

## 3. Reliability Tests

**Location**: `tests/qa/reliability/`

**Purpose**: Ensure graceful handling of failures, network issues, and unexpected conditions.

### Test Files
- `test_connection_stability.py` - Network instability handling
- `test_data_consistency.py` - Data integrity across sessions
- `test_error_recovery.py` - Recovery mechanisms
- `test_retry_mechanism.py` - Retry logic validation
- `test_timeout_handling.py` - Timeout handling

### Examples

```python
def test_scraper_handles_intermittent_network_failures():
    """QA/Reliability: Scraper retries on network failures."""
    with patch('requests.get') as mock_get:
        # Simulate intermittent failures
        mock_get.side_effect = [
            requests.ConnectionError("Network error"),
            requests.Timeout("Timeout"),
            Mock(status_code=200, text="<html>Success</html>")
        ]

        scraper = Scraper(max_retries=3)
        result = scraper.fetch_url("https://example.com")

        assert result.status_code == 200
        assert mock_get.call_count == 3

def test_data_consistency_across_crashes():
    """QA/Reliability: Data remains consistent after crashes."""
    storage = DataStorage("test.db")

    # Start transaction
    storage.begin_transaction()
    storage.insert({"item": "test1"})
    storage.insert({"item": "test2"})

    # Simulate crash before commit
    storage._connection.close()

    # Reopen database
    storage = DataStorage("test.db")

    # Data should NOT be there (transaction rolled back)
    assert storage.count() == 0

def test_graceful_degradation_on_partial_failures():
    """QA/Reliability: System continues despite partial failures."""
    scraper = Scraper()
    urls = [
        "https://valid-site.com",
        "https://invalid-site-404.com",
        "https://another-valid-site.com"
    ]

    results = scraper.scrape_batch(urls, skip_errors=True)

    # Should have 2 successful results despite 1 failure
    successful = [r for r in results if r.status == "success"]
    assert len(successful) == 2
```

---

## 4. Scalability Tests

**Location**: `tests/qa/scalability/`

**Purpose**: Validate behavior under increasing load and resource demands.

### Test Files
- `test_load_handling.py` - High load scenarios
- `test_queue_scalability.py` - Large queue performance
- `test_worker_scaling.py` - Horizontal scaling

### Examples

```python
def test_worker_scaling():
    """QA/Scalability: Performance improves with more workers."""
    task_queue = TaskQueue()

    # Add 100 tasks
    for i in range(100):
        task_queue.add({"url": f"https://example.com/page/{i}"})

    # Test with different worker counts
    results = {}
    for worker_count in [1, 2, 4, 8]:
        coordinator = Coordinator(num_workers=worker_count)
        start = time.time()
        coordinator.process_queue(task_queue.copy())
        elapsed = time.time() - start
        results[worker_count] = elapsed

    # More workers should be faster (with diminishing returns)
    assert results[2] < results[1]
    assert results[4] < results[2]

def test_queue_scales_to_10000_tasks():
    """QA/Scalability: Queue handles large task counts."""
    queue = TaskQueue()

    # Add 10,000 tasks
    for i in range(10000):
        queue.add({"url": f"https://example.com/page/{i}"})

    assert queue.size() == 10000

    # Should be able to retrieve tasks quickly
    start = time.time()
    for _ in range(100):
        task = queue.pop()
    elapsed = time.time() - start

    assert elapsed < 1  # Sub-second for 100 pops
```

---

## 5. Security Tests

**Location**: `tests/qa/security/`

**Purpose**: Prevent common vulnerabilities and ensure secure data handling.

### Test Files
- `test_input_sanitization.py` - Input validation
- `test_proxy_security.py` - Proxy credential security
- `test_sensitive_data_handling.py` - Sensitive data protection
- `test_sql_injection_prevention.py` - SQL injection prevention
- `test_xss_prevention.py` - XSS prevention

### Examples

```python
def test_sql_injection_prevention():
    """QA/Security: SQL injection is prevented."""
    storage = DataStorage()

    # Attempt SQL injection
    malicious_input = "'; DROP TABLE products; --"

    # Should be safely escaped
    storage.insert({"name": malicious_input})

    # Verify data stored safely and table still exists
    assert storage.table_exists("products")
    item = storage.get_by_name(malicious_input)
    assert item["name"] == malicious_input

def test_xss_prevention_in_scraped_data():
    """QA/Security: XSS scripts are sanitized."""
    html = '<div class="product"><script>alert("XSS")</script>Product Name</div>'

    scraper = Scraper()
    result = scraper.parse_html(html)

    # Script tags should be removed/escaped
    assert "<script>" not in result["product_name"]
    assert result["product_name"] == "Product Name"

def test_sensitive_data_not_logged():
    """QA/Security: Sensitive data doesn't appear in logs."""
    import logging
    from io import StringIO

    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    logging.getLogger().addHandler(handler)

    scraper = Scraper(api_key="secret_key_12345")
    scraper.scrape_url("https://api.example.com")

    log_content = log_capture.getvalue()

    # API key should NOT appear in logs
    assert "secret_key_12345" not in log_content
```

---

## 6. Usability Tests

**Location**: `tests/qa/usability/`

**Purpose**: Ensure good developer experience and intuitive APIs.

### Examples

```python
def test_api_ergonomics():
    """QA/Usability: API is intuitive and easy to use."""
    # Should work with minimal configuration
    scraper = Scraper()
    result = scraper.scrape("https://example.com")

    assert result is not None

    # Should have helpful defaults
    assert scraper.timeout > 0
    assert scraper.user_agent is not None

def test_error_messages_are_helpful():
    """QA/Usability: Error messages guide users to solutions."""
    scraper = Scraper()

    try:
        scraper.scrape_url("invalid-url")
    except ValueError as e:
        error_msg = str(e)
        # Should explain the problem clearly
        assert "URL" in error_msg or "url" in error_msg
        # Should be actionable
        assert "http" in error_msg.lower() or "https" in error_msg.lower()

def test_configuration_validation():
    """QA/Usability: Invalid configurations are caught early."""
    with pytest.raises(ConfigurationError) as exc_info:
        Scraper(timeout=-1)  # Invalid timeout

    assert "timeout" in str(exc_info.value).lower()
    assert "positive" in str(exc_info.value).lower()
```

---

## Running QA Tests

### Run All QA Tests
```bash
python tests/run_qa_tests.py
# or
pytest tests/qa/ -v
```

### Run Specific Category
```bash
pytest tests/qa/performance/ -v
pytest tests/qa/security/ -v
pytest tests/qa/compatibility/ -v
```

### Run Performance Tests with Profiling
```bash
pytest tests/qa/performance/ --profile
```

### Run Security Tests with Coverage
```bash
pytest tests/qa/security/ --cov=scraper --cov-report=html
```

##---

## QA Test Metrics

| Category | Tests | Priority | Frequency |
|----------|-------|----------|-----------|
| Compatibility | ~10 | High | Per release |
| Performance | ~15 | High | Weekly |
| Reliability | ~12 | Critical | Every PR |
| Scalability | ~6 | Medium | Monthly |
| Security | ~15 | Critical | Every PR |
| Usability | ~8 | Medium | Per feature |

---

## Next Steps

- **Regression Tests**: [06. Regression Tests](06_regression_tests.md)
- **Running Tests**: [08. Running Tests](08_running_tests.md)
- **Best Practices**: [11. Best Practices](11_best_practices.md)
