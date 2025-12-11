# 03. Integration Tests

## Overview

Integration tests validate that **multiple components work together correctly**, focusing on interactions, data flow, and API contracts between modules.

---

## Philosophy

> "Integration tests verify that components can talk to each other without getting lost in translation."

### Key Principles
1. **Component Interaction**: Test how 2-5 components work together
2. **Data Flow**: Validate information passes correctly between modules
3. **API Contracts**: Ensure modules honor their interfaces
4. **Realistic Scenarios**: Use minimal mocking for realistic behavior
5. **Moderate Scope**: Not full E2E, but more than unit tests

---

## Test Organization

```
tests/integration/
├── test_analytics_generation.py     # Analytics pipeline
├── test_anti_bot_flow.py            # Bot evasion workflow
├── test_dashboard_integration.py    # Dashboard + backend
├── test_data_pipeline.py            # Scraping → processing → storage
├── test_distributed_scraping.py     # Multi-worker coordination
├── test_export_pipeline.py          # Data → export formats
├── test_plugin_integration.py       # Plugin system
├── test_proxy_rotation_flow.py      # Proxy management workflow
├── test_scraper_workflow.py         # Core scraping flow
└── test_site_detection_flow.py      # Auto-detection logic
```

---

## Integration Workflows

### 1. Analytics Generation (`test_analytics_generation.py`)

**Workflow**: Data Collection → Processing → Metrics Calculation → Report Generation

```python
def test_complete_analytics_pipeline():
    """Integration: Full analytics workflow from scraping to report."""
    # Arrange: Setup components
    scraper = Scraper(config=test_config)
    analytics_engine = AnalyticsEngine()
    report_generator = ReportGenerator()

    # Act: Execute complete workflow
    raw_data = scraper.scrape_url("https://test-site.com/products")
    processed_data = analytics_engine.process(raw_data)
    metrics = analytics_engine.calculate_metrics(processed_data)
    report = report_generator.generate(metrics, format="html")

    # Assert: Validate end-to-end results
    assert len(processed_data) > 0
    assert "total_items" in metrics
    assert "average_price" in metrics
    assert report.format == "html"
    assert "<html>" in report.content

def test_analytics_handles_empty_dataset():
    """Integration: Analytics pipeline handles empty data gracefully."""
    analytics_engine = AnalyticsEngine()
    report_generator = ReportGenerator()

    metrics = analytics_engine.calculate_metrics([])
    report = report_generator.generate(metrics)

    assert metrics["total_items"] == 0
    assert "No data available" in report.content
```

---

### 2. Proxy Rotation Flow (`test_proxy_rotation_flow.py`)

**Workflow**: Proxy Selection → Request → Failure Detection → Rotation → Retry

```python
def test_proxy_rotation_with_failures():
    """Integration: Proxy rotation handles failures and retries."""
    # Arrange
    proxy_manager = ProxyManager([
        "http://proxy1.com:8080",
        "http://proxy2.com:8080",
        "http://proxy3.com:8080"
    ])
    scraper = Scraper(proxy_manager=proxy_manager)

    # Mock first proxy to fail
    with patch('requests.get') as mock_get:
        mock_get.side_effect = [
            requests.ConnectionError("Proxy 1 failed"),
            Mock(status_code=200, text="<html>Success</html>")
        ]

        # Act: Attempt scrape with failing proxy
        result = scraper.fetch_url("https://example.com")

        # Assert: Verify rotation occurred
        assert mock_get.call_count == 2
        assert proxy_manager.current_proxy != "http://proxy1.com:8080"
        assert result.status_code == 200

def test_proxy_health_check_integration():
    """Integration: Proxy health checks work with scraper."""
    proxy_manager = ProxyManager(proxies, health_check=True)
    scraper = Scraper(proxy_manager=proxy_manager)

    # Health check should remove bad proxies
    proxy_manager.run_health_checks()

    available = proxy_manager.get_available_proxies()
    assert len(available) < len(proxies)  # Some removed

    # Scraper should only use healthy proxies
    result = scraper.fetch_url("https://example.com")
    assert result.proxy_used in available
```

---

### 3. Export Pipeline (`test_export_pipeline.py`)

**Workflow**: Data Extraction → Transformation → Validation → Multi-Format Export

```python
def test_export_pipeline_multiple_formats():
    """Integration: Data exports correctly to multiple formats."""
    # Arrange
    scraper = Scraper()
    data_processor = DataProcessor()
    exporter = DataExporter()

    # Act: Complete pipeline
    raw_data = scraper.scrape_html(load_fixture("products.html"))
    processed_data = data_processor.clean(raw_data)

    json_output = exporter.to_json(processed_data, "output.json")
    csv_output = exporter.to_csv(processed_data, "output.csv")
    excel_output = exporter.to_excel(processed_data, "output.xlsx")

    # Assert: All formats created successfully
    assert os.path.exists("output.json")
    assert os.path.exists("output.csv")
    assert os.path.exists("output.xlsx")

    # Validate JSON content
    with open("output.json") as f:
        json_data = json.load(f)
    assert len(json_data) == len(processed_data)

    # Validate CSV content
    with open("output.csv") as f:
        csv_reader = csv.DictReader(f)
        csv_data = list(csv_reader)
    assert len(csv_data) == len(processed_data)
```

---

### 4. Data Pipeline (`test_data_pipeline.py`)

**Workflow**: Scraping → Parsing → Processing → Storage

```python
def test_complete_data_pipeline():
    """Integration: Full data pipeline from scrape to storage."""
    # Arrange
    scraper = Scraper()
    parser = DataParser()
    processor = DataProcessor()
    storage = DataStorage(connection=test_db)

    # Act: Execute full pipeline
    html = scraper.fetch_url("https://example.com/products")
    raw_items = parser.extract_items(html.text)
    processed_items = processor.transform(raw_items)
    storage.save_batch(processed_items)

    # Assert: Data stored correctly
    saved_items = storage.get_all()
    assert len(saved_items) == len(processed_items)
    assert saved_items[0]["price"] == processed_items[0]["price"]

def test_pipeline_data_consistency():
    """Integration: Data remains consistent through pipeline stages."""
    scraper = Scraper()
    parser = DataParser()
    processor = DataProcessor()

    # Generate checksum at each stage
    html = scraper.fetch_url("https://example.com/products")
    raw_items = parser.extract_items(html.text)

    # Verify item count preserved
    processed_items = processor.transform(raw_items)
    assert len(processed_items) == len(raw_items)

    # Verify essential fields preserved
    for raw, processed in zip(raw_items, processed_items):
        assert raw["id"] == processed["id"]
```

---

### 5. Plugin Integration (`test_plugin_integration.py`)

**Workflow**: Plugin Discovery → Loading → Hook Registration → Execution

```python
def test_plugin_system_integration():
    """Integration: Plugin system integrates with scraper."""
    # Arrange
    plugin_manager = PluginManager(plugin_dir="tests/fixtures/plugins")
    scraper = Scraper(plugin_manager=plugin_manager)

    # Act: Load plugins
    plugin_manager.discover_plugins()
    plugin_manager.load_all()

    # Execute scraping with plugins
    result = scraper.scrape_url("https://example.com")

    # Assert: Plugins executed
    assert plugin_manager.get_loaded_count() > 0
    assert result.metadata["plugins_executed"] > 0

def test_plugin_hooks_fire_at_correct_stages():
    """Integration: Plugin hooks fire in correct order."""
    execution_log = []

    class TestPlugin(Plugin):
        def on_before_scrape(self, url):
            execution_log.append("before_scrape")

        def on_after_scrape(self, result):
            execution_log.append("after_scrape")

        def on_data_extracted(self, data):
            execution_log.append("data_extracted")

    plugin_manager = PluginManager()
    plugin_manager.register(TestPlugin())
    scraper = Scraper(plugin_manager=plugin_manager)

    scraper.scrape_url("https://example.com")

    assert execution_log == [
        "before_scrape",
        "data_extracted",
        "after_scrape"
    ]
```

---

### 6. Site Detection Flow (`test_site_detection_flow.py`)

**Workflow**: URL Analysis → Pattern Matching → Config Selection → Validation

```python
def test_site_detection_selects_correct_config():
    """Integration: Site detector selects appropriate config."""
    # Arrange
    detector = SiteDetector()
    config_manager = ConfigManager()
    scraper = Scraper()

    # Act: Detect site type
    site_type = detector.detect("https://amazon.com/product/123")
    config = config_manager.get_config_for_site(site_type)
    scraper.apply_config(config)

    # Assert: Correct config applied
    assert site_type == "amazon"
    assert config.selectors["title"] == ".product-title"
    assert scraper.config.selectors["title"] == ".product-title"

def test_site_detection_fallback_to_generic():
    """Integration: Unknown sites fall back to generic config."""
    detector = SiteDetector()
    config_manager = ConfigManager()

    site_type = detector.detect("https://unknown-site.com")
    config = config_manager.get_config_for_site(site_type)

    assert site_type == "generic"
    assert config.selectors is not None
```

---

### 7. Anti-Bot Flow (`test_anti_bot_flow.py`)

**Workflow**: Detection → Evasion Tactics → Stealth Mode → Verification

```python
def test_anti_bot_detection_and_evasion():
    """Integration: Anti-bot system detects and evades challenges."""
    # Arrange
    scraper = Scraper(stealth_mode=True)
    anti_bot_manager = AntiBotManager()

    # Mock Cloudflare challenge
    challenge_html = load_fixture("cloudflare_challenge.html")

    with patch.object(scraper, 'fetch_url') as mock_fetch:
        mock_fetch.return_value = Mock(text=challenge_html)

        # Act: Attempt to bypass
        result = scraper.scrape_with_anti_bot("https://protected-site.com")

        # Assert: Challenge detected and handled
        assert anti_bot_manager.challenge_detected
        assert result.evasion_attempted
```

---

### 8. Dashboard Integration (`test_dashboard_integration.py`)

**Workflow**: Backend API → Data Processing → Frontend Rendering

```python
def test_dashboard_api_integration():
    """Integration: Dashboard API integrates with backend."""
    from scraper.dashboard import create_app

    app = create_app(testing=True)
    client = app.test_client()

    # Create scraping job via API
    response = client.post('/api/jobs', json={
        "url": "https://example.com",
        "config": "default"
    })

    assert response.status_code == 201
    job_id = response.json["job_id"]

    # Check job status
    status_response = client.get(f'/api/jobs/{job_id}')
    assert status_response.status_code == 200
    assert status_response.json["status"] in ["pending", "running", "completed"]
```

---

### 9. Distributed Scraping (`test_distributed_scraping.py`)

**Workflow**: Task Distribution → Worker Coordination → Result Aggregation

```python
def test_distributed_scraping_with_multiple_workers():
    """Integration: Multiple workers process tasks correctly."""
    # Arrange
    task_queue = TaskQueue()
    workers = [Worker(id=i, queue=task_queue) for i in range(3)]
    coordinator = Coordinator(workers)

    # Add tasks
    urls = [f"https://example.com/page/{i}" for i in range(10)]
    for url in urls:
        task_queue.add_task({"url": url})

    # Act: Start workers
    coordinator.start_all()
    coordinator.wait_for_completion(timeout=30)

    # Assert: All tasks completed
    assert task_queue.pending_count() == 0
    assert coordinator.get_results_count() == 10
```

---

### 10. Scraper Workflow (`test_scraper_workflow.py`)

**Workflow**: Configuration → Initialization → Execution → Cleanup

```python
def test_complete_scraper_workflow():
    """Integration: Complete scraper lifecycle."""
    # Configuration phase
    config = ScraperConfig(
        timeout=30,
        retries=3,
        headless=True
    )

    # Initialization phase
    scraper = Scraper(config=config)
    assert scraper.is_ready()

    # Execution phase
    result = scraper.scrape_url("https://example.com")
    assert result.status == "success"
    assert len(result.data) > 0

    # Cleanup phase
    scraper.close()
    assert scraper.browser is None
```

---

## Running Integration Tests

### Run All Integration Tests
```bash
python tests/run_integration_tests.py
# or
pytest tests/integration/ -v
```

### Run Specific Workflow
```bash
pytest tests/integration/test_proxy_rotation_flow.py -v
pytest tests/integration/test_data_pipeline.py -v
```

### Run With Markers
```bash
pytest tests/integration/ -m "integration" -v
```

### Parallel Execution
```bash
pytest tests/integration/ -n auto
```

---

## Best Practices

### 1. Use Test Databases/Fixtures
```python
@pytest.fixture
def test_database():
    """Provide clean test database for each test."""
    db = Database(":memory:")  # SQLite in-memory
    db.setup_schema()
    yield db
    db.close()

def test_data_storage(test_database):
    storage = DataStorage(test_database)
    storage.save({"item": "test"})
    assert test_database.count() == 1
```

### 2. Mock External Services
```python
@pytest.fixture
def mock_external_api():
    with patch('requests.get') as mock:
        mock.return_value.json.return_value = {"status": "ok"}
        yield mock
```

### 3. Test Error Paths
```python
def test_pipeline_handles_partial_failures():
    """Integration: Pipeline continues despite individual failures."""
    processor = DataProcessor()
    items = [
        {"valid": "data"},
        {"invalid": None},  # Will cause error
        {"valid": "data2"}
    ]

    results = processor.process_batch(items, skip_errors=True)

    assert len(results) == 2  # One skipped
    assert processor.error_count == 1
```

---

## Next Steps

- **E2E Tests**: [04. E2E Tests](04_e2e_tests.md)
- **Running Tests**: [08. Running Tests](08_running_tests.md)
- **Fixtures and Mocks**: [07. Fixtures and Mocks](07_fixtures_and_mocks.md)
