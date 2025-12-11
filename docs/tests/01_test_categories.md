# 01. Test Categories

## Overview

The Dynamic Web Scraper employs **seven distinct test categories**, each designed to validate different aspects of the application. This document provides comprehensive explanations of each category, their purposes, scopes, and how they interconnect.

---

## Test Categories Matrix

| Category | Purpose | Speed | Dependencies | CI/CD Stage | Coverage |
|----------|---------|-------|--------------|-------------|----------|
| **Smoke** | Quick sanity check | < 1 min | Minimal | Stage 1 (First) | Critical paths only |
| **Unit** | Component isolation | Milliseconds | None (mocked) | Stage 1 | 17 functional domains |
| **Integration** | Multi-component interaction | Seconds | Some real | Stage 2 | 10 workflows |
| **E2E** | Full workflow validation | Minutes | Real browsers | Stage 3 | 4 scenarios |
| **QA** | Non-functional quality | Variable | Platform-specific | Stage 4 | 6 dimensions |
| **Regression** | Bug prevention | Variable | Minimal | Stage 3 | Historical issues |
| **Benchmark** | Performance tracking | Seconds | Consistent env | Periodic | Performance-critical ops |

---

## 1. Smoke Tests

### Purpose
Provide **rapid validation** that the most critical functionality is working. Smoke tests act as a first line of defense before running more comprehensive test suites.

### Philosophy
> "If smoke tests fail, nothing else matters — the build is fundamentally broken."

### Characteristics
- ⚡ **Speed**: Complete suite runs in < 1 minute
- 🎯 **Scope**: Only the most critical paths
- 🔧 **Dependencies**: Minimal external dependencies
- 📊 **Coverage**: Essential features only

### What Smoke Tests Validate
1. **Application startup**: Can the scraper initialize?
2. **Core scraping**: Can a basic scrape operation complete?
3. **Data extraction**: Can data be extracted from simple HTML?
4. **Export**: Can data be exported to at least one format?
5. **Configuration loading**: Can configuration files be read?

### When to Run
- ✅ First step in every CI/CD pipeline
- ✅ After major refactoring
- ✅ Before running longer test suites
- ✅ Quick sanity check during development

### Example Test Structure
```python
def test_smoke_scraper_initialization():
    """Smoke test: Verify scraper can be initialized."""
    scraper = Scraper()
    assert scraper is not None
    assert scraper.config is not None

def test_smoke_basic_scrape():
    """Smoke test: Verify basic scraping works."""
    scraper = Scraper()
    html = "<html><body><h1>Test</h1></body></html>"
    result = scraper.scrape_html(html)
    assert result is not None
    assert len(result) > 0
```

---

## 2. Unit Tests

### Purpose
Validate the **correctness of individual components** in complete isolation from the rest of the system.

### Philosophy
> "Unit tests verify that each piece works correctly on its own before we combine them."

### Characteristics
- ⚡ **Speed**: Milliseconds per test (target: < 100ms each)
- 🎯 **Scope**: Single function, class, or module
- 🔧 **Dependencies**: None — everything external is mocked
- 📊 **Coverage**: Target >85% line coverage for core modules

### Organization (17 Functional Domains)

#### **Core Logic**
- `unit/core/` - Core scraper logic, main orchestration
- `unit/exceptions/` - Custom exception handling
- `unit/utils/` - Utility functions and helpers

#### **Data Processing**
- `unit/data_parsers/` - HTML, JSON, XML parsing
- `unit/data_processing/` - Data transformation pipelines
- `unit/css_selectors/` - CSS selector validation and parsing

#### **Infrastructure**
- `unit/proxy_manager/` - Proxy rotation and management
- `unit/user_agent_manager/` - User agent rotation
- `unit/logging_manager/` - Logging infrastructure

#### **Anti-Detection**
- `unit/anti_bot/` - Anti-bot evasion mechanisms
- `unit/site_detection/` - Automatic site detection logic

#### **Export & Reporting**
- `unit/export/` - Data export (JSON, CSV, Excel, etc.)
- `unit/reporting/` - Report generation
- `unit/analytics/` - Analytics and metrics

#### **Extensibility**
- `unit/plugins/` - Plugin system
- `unit/customization/` - Configuration and customization
- `unit/comparison/` - Site comparison utilities

### Testing Patterns

#### **Pure Logic Testing**
```python
def test_parse_price_with_currency_symbol():
    """Unit test: Price parser handles currency symbols."""
    from scraper.parsers import parse_price

    assert parse_price("$19.99") == 19.99
    assert parse_price("€25.50") == 25.50
    assert parse_price("£10.00") == 10.00
```

#### **Mocking External Dependencies**
```python
from unittest.mock import Mock, patch

def test_scraper_handles_network_error():
    """Unit test: Scraper handles network errors gracefully."""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.ConnectionError("Network error")

        scraper = Scraper()
        result = scraper.fetch_url("http://example.com")

        assert result is None
        assert scraper.errors[-1].type == "NetworkError"
```

### When to Run
- ✅ During active development (constantly)
- ✅ Every commit
- ✅ First stage of CI/CD pipeline
- ✅ When modifying any individual module

---

## 3. Integration Tests

### Purpose
Validate that **multiple components work together correctly**, focusing on interactions, data flow, and API contracts.

### Philosophy
> "Integration tests verify that components can talk to each other without getting lost in translation."

### Characteristics
- ⚡ **Speed**: Seconds per test (target: < 30s each)
- 🎯 **Scope**: 2-5 components working together
- 🔧 **Dependencies**: Mix of real and mocked (databases, minimal external calls)
- 📊 **Coverage**: 10 major integration workflows

### Key Integration Workflows

#### **1. Analytics Generation Flow** (`test_analytics_generation.py`)
**Tests**: Data collection → Processing → Metrics calculation → Report generation

```python
def test_complete_analytics_pipeline():
    """Integration: Full analytics workflow."""
    # Setup
    scraper = Scraper()
    analytics_engine = AnalyticsEngine()
    report_generator = ReportGenerator()

    # Execute workflow
    data = scraper.scrape(url)
    metrics = analytics_engine.calculate_metrics(data)
    report = report_generator.generate(metrics)

    # Validate
    assert report.contains_metric("total_items")
    assert report.format == "html"
```

#### **2. Proxy Rotation Flow** (`test_proxy_rotation_flow.py`)
**Tests**: Proxy pool → Selection → Rotation → Failure handling → Retry

#### **3. Export Pipeline** (`test_export_pipeline.py`)
**Tests**: Data extraction → Transformation → Validation → Export (multiple formats)

#### **4. Plugin Integration** (`test_plugin_integration.py`)
**Tests**: Plugin discovery → Loading → Execution → Hook system

#### **5. Data Pipeline** (`test_data_pipeline.py`)
**Tests**: Scraping → Parsing → Processing → Storage

#### **6. Anti-Bot Flow** (`test_anti_bot_flow.py`)
**Tests**: Detection → Evasion tactics → Stealth mode → Verification

#### **7. Site Detection Flow** (`test_site_detection_flow.py`)
**Tests**: URL analysis → Pattern matching → Config selection → Validation

#### **8. Dashboard Integration** (`test_dashboard_integration.py`)
**Tests**: Backend API → Frontend rendering → User interactions

#### **9. Distributed Scraping** (`test_distributed_scraping.py`)
**Tests**: Task distribution → Worker coordination → Result aggregation

#### **10. Scraper Workflow** (`test_scraper_workflow.py`)
**Tests**: Configuration → Initialization → Execution → Cleanup

### When to Run
- ✅ After modifying multiple related components
- ✅ Before feature completion
- ✅ Second stage of CI/CD pipeline
- ✅ Pre-merge validation

---

## 4. End-to-End (E2E) Tests

### Purpose
Simulate **real-world user scenarios** by testing the complete application workflow from start to finish.

### Philosophy
> "E2E tests validate that the entire system works as users expect it to."

### Characteristics
- ⚡ **Speed**: Minutes per test (target: 2-10 min each)
- 🎯 **Scope**: Complete user journeys
- 🔧 **Dependencies**: Real browsers (Selenium, Playwright), external services
- 📊 **Coverage**: 4 comprehensive scenarios

### E2E Scenarios

#### **1. Complete Scraping Cycle** (`test_complete_scraping_cycle.py`)
**Journey**: Initialize → Configure → Scrape → Process → Export → Verify

```python
def test_full_scraping_lifecycle():
    """E2E: Complete scraping from URL to exported data."""
    # User provides URL and configuration
    scraper = Scraper(config="config.json")

    # Execute scraping
    result = scraper.scrape_url("https://example.com/products")

    # Process and export
    scraper.export_to_json(result, "output.json")
    scraper.export_to_csv(result, "output.csv")

    # Validate exported files
    assert os.path.exists("output.json")
    assert os.path.exists("output.csv")

    # Validate data integrity
    with open("output.json") as f:
        data = json.load(f)
    assert len(data) > 0
    assert "title" in data[0]
```

#### **2. Dashboard Workflow** (`test_dashboard_workflow.py`)
**Journey**: Launch dashboard → Create job → Monitor progress → View results → Export

#### **3. Multi-Site Comparison** (`test_multi_site_comparison.py`)
**Journey**: Configure multiple sites → Scrape all → Compare data → Generate report

#### **4. Real Site Scraping** (`test_real_site_scraping.py`)
**Journey**: Scrape production sites → Handle real challenges (Cloudflare, JS-heavy, etc.)

### When to Run
- ✅ Before releases
- ✅ After major feature additions
- ✅ Pre-production validation
- ✅ User acceptance testing
- ✅ Third stage of CI/CD pipeline

---

## 5. QA Tests (Quality Assurance)

### Purpose
Validate **non-functional requirements** across six critical quality dimensions.

### Philosophy
> "QA tests ensure the application meets production-level quality standards beyond just functional correctness."

### Characteristics
- ⚡ **Speed**: Variable (seconds to minutes)
- 🎯 **Scope**: Quality attributes (performance, security, etc.)
- 🔧 **Dependencies**: Platform-specific, monitoring tools
- 📊 **Coverage**: 6 specialized categories

### QA Categories

#### **1. Compatibility** (`qa/compatibility/`)
**Ensures**: Works across browsers, platforms, Python versions

- Browser compatibility (Chrome, Firefox, Safari, Edge)
- Platform compatibility (Windows, macOS, Linux)
- Python version compatibility (3.8-3.12)
- Selenium version compatibility

#### **2. Performance** (`qa/performance/`)
**Measures**: Speed, throughput, resource usage

- Concurrent request handling
- Database performance
- Large dataset processing
- Memory usage and leak detection
- Scraping speed benchmarks

#### **3. Reliability** (`qa/reliability/`)
**Validates**: Graceful failure handling, recovery

- Connection stability under poor networks
- Data consistency across sessions
- Error recovery mechanisms
- Retry logic correctness
- Timeout handling

#### **4. Scalability** (`qa/scalability/`)
**Tests**: Behavior under increasing load

- Load handling capacity
- Queue scalability with many tasks
- Worker scaling (horizontal)

#### **5. Security** (`qa/security/`)
**Prevents**: Common vulnerabilities

- Input sanitization
- Proxy credential security
- Sensitive data handling
- SQL injection prevention
- XSS prevention

#### **6. Usability** (`qa/usability/`)
**Evaluates**: Developer experience

- API ergonomics
- Error message clarity
- Configuration ease
- Documentation completeness

### When to Run
- ✅ Before major releases
- ✅ Performance validation
- ✅ Security audits
- ✅ Cross-platform testing
- ✅ Fourth stage of CI/CD (nightly builds)

---

## 6. Regression Tests

### Purpose
Ensure that **previously fixed bugs don't resurface** and deprecated features continue working during the deprecation period.

### Philosophy
> "Regression tests are our insurance policy against repeating past mistakes."

### Characteristics
- ⚡ **Speed**: Variable
- 🎯 **Scope**: Historical issues and edge cases
- 🔧 **Dependencies**: Minimal
- 📊 **Coverage**: All fixed bugs, deprecated features

### Test Organization

#### **Bug Fixes** (`test_bug_fixes.py`)
Each test addresses a specific historical issue:

```python
def test_issue_123_proxy_rotation_crash():
    """Regression: Issue #123 - Proxy rotation crash on None value.

    Bug: ProxyManager crashed when proxy list contained None
    Fixed: 2025-11-15
    Related: PR #456
    """
    proxy_manager = ProxyManager()
    proxy_manager.add_proxies([None, "http://proxy1.com", None])

    # Should not crash
    proxy = proxy_manager.get_next_proxy()
    assert proxy is not None
```

#### **Deprecated Features** (`test_deprecated_features.py`)
Ensures backward compatibility during deprecation:

```python
def test_deprecated_headless_parameter():
    """Regression: Deprecated 'headless' parameter still works.

    Deprecated: 2025-12-01
    Remove: 2026-06-01 (6 months)
    Migration: Use browser_config instead
    """
    import warnings

    with warnings.catch_warnings(record=True) as w:
        scraper = Scraper(headless=True)

        assert len(w) == 1
        assert "deprecated" in str(w[0].message).lower()
        assert scraper.browser_config.headless is True
```

### When to Run
- ✅ Every pull request
- ✅ Before releases
- ✅ Third stage of CI/CD pipeline

---

## 7. Benchmark Tests

### Purpose
**Measure and track performance metrics** over time to detect performance regressions.

### Philosophy
> "You can't improve what you don't measure."

### Characteristics
- ⚡ **Speed**: Seconds per benchmark
- 🎯 **Scope**: Performance-critical operations
- 🔧 **Dependencies**: Consistent test environment
- 📊 **Coverage**: Parsing, scraping, data processing

### Benchmark Categories

#### **Parsing Benchmarks** (`test_parsing_benchmarks.py`)
- HTML parsing speed (various sizes)
- JSON parsing performance
- CSS selector matching speed

#### **Scraping Benchmarks** (`test_scraping_benchmarks.py`)
- Requests-based scraping throughput
- Selenium scraping performance
- Playwright scraping speed
- Method comparison benchmarks

### Benchmark Format
```python
import pytest

@pytest.mark.benchmark(group="parsing")
def test_benchmark_html_parsing(benchmark):
    """Benchmark: HTML parsing performance."""
    html = load_fixture("large_product_page.html")

    result = benchmark(parse_html, html)

    # Performance assertions
    assert benchmark.stats.mean < 0.1  # Target: < 100ms average
```

### When to Run
- ✅ Periodically (nightly builds)
- ✅ Before performance optimization work
- ✅ After optimization to validate improvements
- ✅ Before releases to catch regressions

---

## Category Relationships

### Temporal Flow
```
Development Time:
Unit → Integration → E2E

Quality Validation:
E2E → QA → Regression

Performance Tracking:
Benchmark (periodic)

Quick Validation:
Smoke (always first)
```

### Dependency Hierarchy
```
┌─────────────┐
│    Smoke    │  ← Depends on nothing, validates basics
└──────┬──────┘
       │
┌──────▼──────┐
│    Unit     │  ← Isolated, no dependencies
└──────┬──────┘
       │
┌──────▼──────┐
│ Integration │  ← Depends on multiple units
└──────┬──────┘
       │
┌──────▼──────┐
│     E2E     │  ← Depends on full system
└─┬────┬────┬─┘
  │    │    │
  ▼    ▼    ▼
┌───┐ ┌───┐ ┌──────────┐
│ QA│ │Reg│ │Benchmark │
└───┘ └───┘ └──────────┘
```

---

## Summary Table

| Category | Files | Lines of Test Code | Avg Execution Time |
|----------|-------|-------------------|-------------------|
| Smoke | ~5 | ~200 | < 1 min |
| Unit | ~50+ | ~5000+ | 1-2 min |
| Integration | ~10 | ~2000 | 5-10 min |
| E2E | ~4 | ~1000 | 10-20 min |
| QA | ~25+ | ~3000+ | 20-40 min |
| Regression | ~2 | ~500 | 2-5 min |
| Benchmark | ~2 | ~300 | 2-5 min |
| **Total** | **~100+** | **~12000+** | **40-85 min (full suite)** |

---

## Next Steps

- **Deep Dive**: Read category-specific docs (02-06)
- **Running Tests**: See [08. Running Tests](08_running_tests.md)
- **Writing Tests**: See [09. Writing New Tests](09_writing_new_tests.md)
- **Best Practices**: See [11. Best Practices](11_best_practices.md)
