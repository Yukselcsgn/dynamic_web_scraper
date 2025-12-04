# API Reference Index

Complete API documentation for all modules in the Dynamic Web Scraper.

## Core Modules

### Scraper
Main scraping interface.

**Scraper Class**
```python
Scraper(url: str, config: Dict, max_retries: int = 3, retry_delay: int = 2)
```

**Methods:**
- `fetch_data(enable_smart_detection=True, enable_enrichment=True, enable_analysis=True) -> Dict`
- `save_data(data: List[Dict], file_name: str, format: str = "csv") -> bool`
- `parse_html(response_text: str) -> BeautifulSoup`

[See detailed Core API documentation →](core.md)

## Analytics Modules

### DataVisualizer
Interactive data visualization.

**DataVisualizer Class**
```python
DataVisualizer(output_directory: str = "data/visualizations")
```

**Methods:**
- `create_price_distribution_chart(data, output_file) -> str`
- `create_trend_analysis_chart(data, output_file) -> str`
- `create_summary_dashboard(data, output_file) -> str`

### PriceAnalyzer
Statistical price analysis.

**PriceAnalyzer Class**
```python
PriceAnalyzer()
```

**Methods:**
- `analyze_prices(data, category_field, price_field, date_field) -> PriceAnalysis`
- `create_visualizations(analysis, save_path) -> None`

### TimeSeriesAnalyzer
Time series analysis and forecasting.

**TimeSeriesAnalyzer Class**
```python
TimeSeriesAnalyzer(data_directory: str = "data/time_series")
```

**Methods:**
- `prepare_time_series_data(data, product_id) -> DataFrame`
- `detect_trends(df, window) -> TrendAnalysis`
- `analyze_seasonality(df, period) -> SeasonalityAnalysis`
- `detect_anomalies(df, method, threshold) -> AnomalyDetection`
- `predict_prices(df, horizon, method) -> PricePrediction`

[See detailed Analytics API documentation →](analytics.md)

## Anti-Bot Modules

### StealthManager
Anti-bot evasion and stealth.

**StealthManager Class**
```python
StealthManager(config: Dict = None)
```

**Methods:**
- `select_profile(url, site_type) -> StealthProfile`
- `fetch_with_stealth(url, method, data, use_browser) -> Response`

[See detailed Anti-Bot API documentation →](anti-bot.md)

## Export Modules

### ExportManager
Multi-format data export.

**ExportManager Class**
```python
ExportManager(data_directory: str = "data", export_config: ExportConfig = None)
```

**Methods:**
- `export_data(data, format, filename) -> ExportResult`
- `share_via_slack(file_path, message) -> ExportResult`
- `get_export_history(days_back) -> List[Dict]`

[See detailed Export API documentation →](export.md)

## Distributed Processing

### JobQueue
Distributed job queue system.

**JobQueue Class**
```python
JobQueue(storage_path: str = "data/job_queue")
```

**Methods:**
- `add_job(url, config, priority, tags, metadata) -> str`
- `get_job(worker_id) -> ScrapingJob`
- `complete_job(job_id, result) -> None`
- `get_stats() -> Dict`

[See detailed Distributed API documentation →](distributed.md)

## Plugin System

### PluginManager
Plugin management and loading.

**PluginManager Class**
```python
PluginManager(plugins_directory: str = "plugins")
```

**Methods:**
- `load_plugins() -> None`
- `get_plugins(plugin_type) -> List[Plugin]`
- `register_plugin(plugin) -> None`

[See detailed Plugin API documentation →](plugins.md)

## Configuration

### ConfigManager
Configuration management.

**ConfigManager Class**
```python
ConfigManager(config_file: str = "config.json")
```

**Methods:**
- `get(key, default) -> Any`
- `set(key, value) -> None`
- `save_config(file_path) -> None`

[See detailed Configuration API documentation →](configuration.md)

## Data Classes

### PriceAnalysis
```python
@dataclass
class PriceAnalysis:
    basic_stats: Dict[str, float]
    price_distribution: Dict[str, Any]
    outliers: List[Dict[str, Any]]
    trends: Dict[str, Any]
    recommendations: List[str]
    analysis_timestamp: str
```

### ScrapingJob
```python
@dataclass
class ScrapingJob:
    id: str
    url: str
    config: Dict[str, Any]
    priority: JobPriority
    status: JobStatus
    created_at: datetime
```

## Complete Module List

- `scraper.core` - Core scraping functionality
- `scraper.analytics` - Data analysis and visualization
- `scraper.anti_bot` - Anti-bot evasion
- `scraper.comparison` - Cross-site comparison
- `scraper.customization` - Configuration management
- `scraper.dashboard` - Web dashboard
- `scraper.data_parsers` - Data parsing
- `scraper.data_processing` - Data enrichment
- `scraper.distributed` - Distributed processing
- `scraper.exceptions` - Custom exceptions
- `scraper.export` - Export capabilities
- `scraper.logging_manager` - Logging
- `scraper.plugins` - Plugin system
- `scraper.proxy_manager` - Proxy management
- `scraper.reporting` - Automated reporting
- `scraper.site_detection` - Site detection
- `scraper.user_agent_manager` - User agent management
- `scraper.utils` - Utility functions

## Usage Examples

See individual module documentation for detailed examples and code samples.

---

For package-level documentation, see the [Package READMEs](../../scraper/).
