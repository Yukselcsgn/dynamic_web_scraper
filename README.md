
# 🚀 Dynamic Web Scraper - Enterprise-Grade Data Intelligence Platform

## 📋 **Overview**

Dynamic Web Scraper is a **sophisticated, enterprise-grade** Python platform for extracting, analyzing, and visualizing data from dynamic websites. It has evolved from a basic scraper into a comprehensive **data intelligence platform** with advanced features including intelligent site detection, automated data enrichment, price analysis, comparative analysis, and interactive dashboards.

---

## ✨ **Key Features**

### 🧠 **Intelligent Site Detection & Adaptation**
- **Automatic site type detection** (e-commerce, blog, news, etc.)
- **Dynamic CSS selector generation** based on site patterns
- **Smart product element detection** (titles, prices, images, links)
- **Site-specific rule caching** for improved performance
- **Anti-bot measure detection** and adaptive responses

### 🎯 **Advanced Data Processing & Enrichment**
- **Automatic data cleaning** and normalization
- **Price normalization** across different currencies and formats
- **Contact information extraction** from product descriptions
- **Category classification** using intelligent algorithms
- **Quality scoring** and outlier detection
- **Data validation** and integrity checks

### 📊 **Comprehensive Analytics & Visualization**
- **Interactive data visualization** with Plotly charts
- **Price distribution analysis** with statistical insights
- **Trend detection** with time-series analysis
- **Comparative analysis** across sources and categories
- **Heatmap visualizations** for pattern recognition
- **Summary dashboards** with comprehensive metrics
- **Export capabilities** for reports and presentations

### 🛡️ **Advanced Anti-Bot Evasion**
- **Multiple stealth profiles** (stealth, mobile, aggressive)
- **Browser fingerprint spoofing** and header manipulation
- **Human-like timing delays** and behavior simulation
- **Undetected ChromeDriver** integration for maximum stealth
- **Session persistence** and cookie management
- **CAPTCHA detection** and handling capabilities
- **Automatic browser automation** fallback for JavaScript-heavy sites

### 🔄 **Distributed Scraping & Processing**
- **Job Queue System** with priority-based scheduling
- **Worker Pool Management** for parallel processing
- **Thread-safe Operations** with persistent storage
- **Real-time Monitoring** and statistics
- **Automatic Retry Logic** and error recovery
- **Scalable Architecture** for enterprise use

### 🎨 **Plugin System & Extensibility**
- **Plugin System** with multiple plugin types (data processors, validators, custom scrapers)
- **Configuration Management** with multi-format support (JSON, YAML, TOML)
- **Environment Variable Overrides** for flexible deployment
- **Template Generation** for easy plugin development
- **Runtime Configuration** management and validation

### 📈 **Price Analysis & Time Series**
- **Statistical analysis** (mean, median, std dev, skewness)
- **Trend detection** (linear regression, moving averages)
- **Seasonality analysis** (autocorrelation, pattern recognition)
- **Anomaly detection** (Z-score, IQR, rolling statistics)
- **Price prediction** with confidence intervals
- **Intelligent recommendations** based on analysis

### 🔍 **Comparative Analysis & Deal Discovery**
- **Cross-site price comparison** with comprehensive analysis
- **Intelligent product matching** using similarity algorithms
- **Brand and model extraction** for accurate identification
- **Deal scoring and classification** with savings analysis
- **Best deal discovery** with ranking and recommendations
- **Price variance analysis** with statistical insights

### 📧 **Automated Reporting & Alerts**
- **Scheduled reports** with daily and weekly automation
- **Email notifications** for price changes and anomalies
- **Configurable alert thresholds** for price drops and increases
- **Statistical anomaly detection** using z-score analysis
- **HTML email templates** with detailed alert information
- **Background scheduling** with automated report generation

### 🌐 **Interactive Web Dashboard**
- **Real-time monitoring** of scraping jobs
- **Interactive charts and statistics**
- **Site analysis and visualization**
- **Job queue management**
- **Results viewing and export**
- **Responsive interface** with modern design

### 📦 **Multi-Format Export & Sharing**
- **Multiple output formats** (JSON, CSV, Excel, ZIP)
- **Comprehensive data packaging** with metadata
- **Export history tracking** and management
- **Automatic file cleanup** and maintenance
- **Slack integration** for automated sharing
- **Batch export capabilities** for multiple formats

---

## 🛠 **Requirements**

- **Python 3.8 or later**
- **Google Chrome or Firefox** (for Selenium)
- **All dependencies are version-pinned** in `requirements.txt`

---

## 📦 **Installation**

### **Quick Start**
```bash
# Clone the repository
git clone <repository-url>
cd dynamic_web_scraper

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Mac/Linux

# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt

# Setup and test the scraper
python setup_and_test.py
```

### **Development Setup**
```bash
# Install all dependencies including development tools
pip install -r requirements.txt -r requirements-dev.txt

# Run the comprehensive test suite
python tests/run_tests.py --all --coverage

# Format and lint the code
black scraper/
flake8 scraper/
```

---

## 🚀 **Quick Start**

### **Option 1: Web Dashboard (Recommended)**
```bash
# Start the web dashboard
python run_dashboard.py
```
The dashboard will automatically open in your browser at `http://localhost:5000`

### **Option 2: Command Line**
```bash
# Run the scraper directly
python scraper/main.py
```

---

## ⚙ **Configuration**

All settings are managed in `config.json`:

```json
{
  "user_agents": [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)..."
  ],
  "proxies": [
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080"
  ],
  "use_proxy": true,
  "max_retries": 3,
  "retry_delay": 2,
  "rate_limiting": {
    "requests_per_minute": 60
  }
}
```

---

## 🎯 **Usage**

### **🚀 Automatic Workflow with All Advanced Features**

The scraper now automatically uses all advanced features in a comprehensive workflow:

#### **Step 1: Smart Site Detection**
- Automatically detects site type and anti-bot measures
- Generates optimal CSS selectors
- Adapts to different site structures

#### **Step 2: Data Extraction & Enrichment**
- Extracts raw data with intelligent parsing
- Cleans and normalizes data
- Adds quality scores and metadata
- Extracts contact information and categories

#### **Step 3: Advanced Analysis**
- **Price Analysis**: Statistical analysis, outlier detection, trend analysis
- **Comparative Analysis**: Cross-site price comparison, deal scoring
- **Time Series Analysis**: Trend detection, seasonality, predictions
- **Data Visualization**: Interactive charts and dashboards

#### **Step 4: Automated Reporting**
- Generates comprehensive reports
- Sends email alerts for anomalies
- Creates interactive dashboards
- Exports data in multiple formats

#### **Step 5: Plugin Processing**
- Applies custom data processors
- Validates data quality
- Enhances data with external sources

#### **Step 6: Distributed Processing**
- Queues jobs for parallel processing
- Manages worker pools
- Handles large-scale operations

### **📊 What You Get Automatically**
- **Raw data** in multiple formats
- **Enriched data** with quality scores and metadata
- **Price analysis** with statistical insights
- **Cross-site comparisons** and best deals
- **Interactive visualizations** and dashboards
- **Automated reports** with alerts and recommendations
- **Multiple export formats** for different use cases

### **Web Dashboard Features**

#### **1. Dashboard Overview**
- **Real-time statistics** (total jobs, success rate, results count)
- **Interactive charts** (success rate trends, job status distribution)
- **Recent jobs list** with status indicators
- **Active jobs monitoring** with live duration tracking

#### **2. Start Scraping**
- **URL input** with validation
- **Output format selection** (CSV, JSON, Excel)
- **Advanced options** (proxy rotation, Selenium)
- **Site analysis** before scraping
- **Real-time feedback** and progress tracking

#### **3. Job Management**
- **Job status tracking** (pending, running, completed, failed)
- **Results viewing** with pagination
- **Error handling** and debugging information
- **Export capabilities** for scraped data

#### **4. Site Analysis**
- **Automatic site type detection**
- **E-commerce pattern recognition**
- **CSS selector generation**
- **Confidence scoring**

### **Command Line Usage**

```bash
# Basic usage
python scraper/main.py

# You will be prompted for:
# - Target URL
# - Output file path (default: data/all_listings.csv)
```

---

## 🏗 **Project Structure**

```
dynamic_web_scraper/
├── scraper/                          # Core scraping logic
│   ├── main.py                      # Command line entry point
│   ├── Scraper.py                   # Main scraper class with all features
│   ├── config.py                    # Configuration management
│   ├── dashboard/                   # Web dashboard
│   │   ├── app.py                   # Flask application
│   │   └── templates/               # HTML templates
│   ├── analytics/                   # Data analysis and visualization
│   │   ├── data_visualizer.py       # Interactive charts and dashboards
│   │   ├── price_analyzer.py        # Price analysis and statistics
│   │   └── time_series_analyzer.py  # Time series analysis and prediction
│   ├── comparison/                  # Cross-site comparison
│   │   └── site_comparator.py       # Product matching and deal analysis
│   ├── reporting/                   # Automated reporting
│   │   └── automated_reporter.py    # Reports, alerts, and notifications
│   ├── export/                      # Data export and sharing
│   │   └── export_manager.py        # Multi-format export capabilities
│   ├── plugins/                     # Plugin system
│   │   └── plugin_manager.py        # Plugin management and extensibility
│   ├── distributed/                 # Distributed processing
│   │   ├── job_queue.py             # Job queue system
│   │   └── worker_pool.py           # Worker pool management
│   ├── anti_bot/                    # Anti-bot evasion
│   │   └── stealth_manager.py       # Stealth and anti-detection
│   ├── site_detection/              # Intelligent site detection
│   │   ├── site_detector.py         # Site structure detection
│   │   ├── html_analyzer.py         # HTML analysis
│   │   └── css_selector_builder.py  # Selector building
│   ├── css_selectors/               # Dynamic selector system
│   │   ├── css_selector_generator.py # Selector generation
│   │   ├── css_rules.py             # Rule management
│   │   └── dynamic_selector.py      # Site adaptation
│   ├── data_parsers/                # Data processing
│   ├── proxy_manager/               # Proxy handling
│   ├── user_agent_manager/          # User agent management
│   ├── logging_manager/             # Logging system
│   └── exceptions/                  # Custom exceptions
├── tests/                           # Comprehensive test suite
│   ├── core/                        # Core functionality tests
│   ├── analytics/                   # Analytics and visualization tests
│   ├── site_detection/              # Site detection tests
│   ├── utils/                       # Utility function tests
│   ├── integration/                 # Integration tests
│   ├── conftest.py                  # Pytest configuration and fixtures
│   └── run_tests.py                 # Test runner script
├── data/                            # Output data storage
├── logs/                            # Log files
├── config.json                      # Configuration
├── requirements.txt                 # Production dependencies
├── requirements-dev.txt             # Development dependencies
├── pytest.ini                      # Pytest configuration
├── run_dashboard.py                 # Dashboard launcher
└── README.md                        # Documentation
```

---

## 🧪 **Testing**

The project includes a **comprehensive, organized test suite** with professional structure:

### **Run All Tests**
```bash
# Run the complete test suite
python tests/run_tests.py --all

# Run with coverage
python tests/run_tests.py --all --coverage

# Run with HTML report
python tests/run_tests.py --all --html
```

### **Run Specific Test Categories**
```bash
# Core functionality tests
python tests/run_tests.py --category core

# Analytics and visualization tests
python tests/run_tests.py --category analytics

# Site detection tests
python tests/run_tests.py --category site_detection

# Utility function tests
python tests/run_tests.py --category utils

# Integration tests
python tests/run_tests.py --category integration
```

### **Quick Tests (Unit Tests Only)**
```bash
# Run only unit tests (fast)
python tests/run_tests.py --quick
```

### **Test Categories Available**
| Category | Location | Purpose |
|----------|----------|---------|
| **core** | `tests/core/` | Basic scraper functionality and integration |
| **analytics** | `tests/analytics/` | Data analysis and visualization |
| **site_detection** | `tests/site_detection/` | Site detection and CSS selector generation |
| **utils** | `tests/utils/` | Utility functions |
| **integration** | `tests/integration/` | Complete workflow testing |

### **Direct Pytest Commands**
```bash
# Run all tests
pytest tests/

# Run specific category
pytest tests/analytics/

# Run with markers
pytest -m "not slow"
pytest -m integration
```

---

## 📊 **Example Output**

### **CSV Output**
```csv
title,price,image,link,quality_score,category,source
iPhone 13 Pro,$999.99,https://example.com/iphone.jpg,https://example.com/iphone,0.95,electronics,amazon
Samsung Galaxy S21,$899.99,https://example.com/samsung.jpg,https://example.com/samsung,0.92,electronics,ebay
```

### **JSON Output with Enrichment**
```json
[
  {
    "title": "iPhone 13 Pro",
    "price": 999.99,
    "currency": "USD",
    "image": "https://example.com/iphone.jpg",
    "link": "https://example.com/iphone",
    "quality_score": 0.95,
    "category": "electronics",
    "source": "amazon",
    "extracted_contacts": [],
    "price_analysis": {
      "is_outlier": false,
      "price_percentile": 75,
      "trend": "stable"
    }
  }
]
```

### **Interactive Dashboard**
- **Real-time charts** and visualizations
- **Interactive filtering** by source, category, date
- **Price distribution analysis** with histograms
- **Trend analysis** with moving averages
- **Comparative analysis** across sources

---

## 🔧 **Advanced Features**

### **Intelligent Site Detection**
The scraper automatically:
- **Detects site type** (e-commerce, blog, news, etc.)
- **Identifies product patterns** (shopping cart, prices, add to cart buttons)
- **Generates appropriate CSS selectors**
- **Adapts to different site structures**
- **Caches site analysis** for improved performance

### **Dynamic CSS Selector Generation**
- **Smart selector strategies** based on element attributes
- **Fallback mechanisms** for when primary selectors fail
- **Validation and optimization** of generated selectors
- **Site-specific caching** for improved performance
- **Multiple selector types** (ID, class, smart, path-based)

### **Anti-Detection Measures**
- **User agent rotation** from a large pool of realistic browsers
- **Proxy rotation** with automatic failover
- **Rate limiting** with random delays
- **Request header randomization**
- **Browser fingerprint spoofing**
- **Human-like behavior simulation**

### **Robust Error Handling**
- **Retry logic** with exponential backoff
- **Graceful degradation** when selectors fail
- **Comprehensive logging** for debugging
- **Custom exceptions** with helpful error messages
- **Automatic recovery** from common failures

---

## 🚀 **Performance & Scalability**

### **Optimizations**
- **Asynchronous processing** for multiple jobs
- **Database caching** for site analysis results
- **Efficient memory usage** with streaming data processing
- **Background job processing** with queue management
- **Parallel processing** with worker pools

### **Monitoring**
- **Real-time job status** tracking
- **Performance metrics** and statistics
- **Error rate monitoring**
- **Resource usage tracking**
- **Comprehensive logging** and debugging

---

## 🔒 **Security & Privacy**

- **No sensitive data logging** (credentials, API keys)
- **Input validation** and sanitization
- **Secure configuration** management
- **Respect for robots.txt** (configurable)
- **Data encryption** for sensitive information
- **Access control** and authentication

---

## 🤝 **Contributing**

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### **Development Setup**
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run the comprehensive test suite
python tests/run_tests.py --all --coverage

# Format code
black scraper/

# Lint code
flake8 scraper/

# Type checking
mypy scraper/
```

### **Code Quality**
- **Pre-commit hooks** for automatic code formatting
- **Comprehensive testing** with pytest
- **Code coverage** reporting
- **Static analysis** with mypy and flake8
- **Security scanning** with bandit

---

## 📝 **Logging & Troubleshooting**

### **Log Files**
- **Main logs**: `logs/scraper.log`
- **Error logs**: `logs/error_YYYY-MM-DD.log`
- **Dashboard logs**: Console output
- **Test logs**: `logs/test_YYYY-MM-DD.log`

### **Common Issues**

#### **Import Errors**
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt
```

#### **Selenium Issues**
```bash
# Install webdriver-manager
pip install webdriver-manager

# The scraper will automatically download drivers
```

#### **Proxy Issues**
```bash
# Check proxy configuration in config.json
# Disable proxy rotation if needed
```

#### **Test Issues**
```bash
# Run tests with verbose output
python tests/run_tests.py --all --verbose

# Check test configuration
python tests/run_tests.py --list
```

---

## 📄 **License**

This project is licensed under the Apache License 2.0 — see the [LICENSE](LICENSE) file for details.

---

## 🎉 **What's New in This Version**

### **v0.9 - Enterprise Data Intelligence Platform**
- ✅ **Complete Test Organization** - Professional test suite with organized structure
- ✅ **Integrated Advanced Features** - All features working together seamlessly
- ✅ **Comprehensive Analytics** - Data visualization, price analysis, time series
- ✅ **Distributed Processing** - Job queues, worker pools, parallel processing
- ✅ **Plugin System** - Extensible architecture with custom plugins
- ✅ **Automated Reporting** - Scheduled reports, email alerts, notifications
- ✅ **Comparative Analysis** - Cross-site price comparison and deal discovery
- ✅ **Multi-Format Export** - JSON, CSV, Excel, ZIP with metadata
- ✅ **Interactive Dashboards** - Web-based data exploration and visualization
- ✅ **Advanced Anti-Bot Evasion** - Multiple stealth profiles and detection avoidance

---

## 🎯 **Ready to Get Started?**

1. **Quick Start**: Run `python run_dashboard.py` for the web interface
2. **Command Line**: Use `python scraper/main.py` for direct scraping
3. **Testing**: Run `python tests/run_tests.py --all` to verify everything works
4. **Development**: Install dev dependencies with `pip install -r requirements-dev.txt`

**🚀 Transform your web scraping into a comprehensive data intelligence platform!**
