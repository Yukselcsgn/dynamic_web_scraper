
# Dynamic Web Scraper

## 🚀 **Overview**
Dynamic Web Scraper is a **sophisticated, enterprise-grade** Python tool for extracting data from dynamic websites, especially e-commerce platforms. It features **intelligent site detection**, **automatic CSS selector generation**, **proxy rotation**, **Selenium integration**, and a **beautiful web dashboard** for monitoring and control.

---

## ✨ **Key Features**

### 🧠 **Intelligent Site Detection**
- **Automatic site type detection** (e-commerce, blog, news, etc.)
- **Dynamic CSS selector generation** based on site patterns
- **Smart product element detection** (titles, prices, images, links)
- **Site-specific rule caching** for improved performance

### 🎯 **Advanced CSS Selector System**
- **Multiple selector strategies** (ID, class, smart, path-based)
- **Selector validation and optimization**
- **Dynamic class filtering** to avoid breaking selectors
- **Fallback mechanisms** for when primary selectors fail

### 🌐 **Web Dashboard**
- **Real-time monitoring** of scraping jobs
- **Interactive charts and statistics**
- **Site analysis and visualization**
- **Job queue management**
- **Results viewing and export**

### 🔄 **Robust Scraping Engine**
- **User-Agent and Proxy Rotation** (from config.json)
- **Dynamic Content Handling** (Selenium)
- **Retry logic with exponential backoff**
- **Rate limiting and anti-detection measures**

### 📊 **Data Processing & Export**
- **Multiple output formats** (CSV, JSON, Excel)
- **Data cleaning and validation**
- **Database storage with SQLAlchemy**
- **Real-time progress tracking**

---

## 🛠 **Requirements**
- **Python 3.8 or later**
- **Google Chrome or Firefox** (for Selenium)
- **All dependencies are version-pinned** in `requirements.txt`

---

## 📦 **Installation**

```bash
# Clone the repository
git clone <repository-url>
cd dynamic_web_scraper

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Setup and test the scraper
python setup_and_test.py
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
  "retry_delay": 2
}
```

---

## 🎯 **Usage**

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
│   ├── Scraper.py                   # Main scraper class
│   ├── config.py                    # Configuration management
│   ├── dashboard/                   # Web dashboard
│   │   ├── app.py                   # Flask application
│   │   └── templates/               # HTML templates
│   ├── css_selectors/               # Dynamic selector system
│   │   ├── css_selector_generator.py # Selector generation
│   │   ├── css_rules.py             # Rule management
│   │   └── dynamic_selector.py      # Site adaptation
│   ├── site_detection/              # Intelligent site detection
│   │   ├── site_detector.py         # Site structure detection
│   │   ├── html_analyzer.py         # HTML analysis
│   │   └── css_selector_builder.py  # Selector building
│   ├── data_parsers/                # Data processing
│   ├── proxy_manager/               # Proxy handling
│   ├── user_agent_manager/          # User agent management
│   ├── logging_manager/             # Logging system
│   └── exceptions/                  # Custom exceptions
├── tests/                           # Comprehensive test suite
├── data/                            # Output data storage
├── logs/                            # Log files
├── config.json                      # Configuration
├── requirements.txt                 # Dependencies
├── run_dashboard.py                 # Dashboard launcher
└── README.md                        # Documentation
```

---

## 🧪 **Testing**

```bash
# Run all tests
python -m pytest

# Run specific test modules
python -m pytest tests/test_css_selectors.py -v
python -m pytest tests/test_Scraper.py -v

# Run with coverage
python -m pytest --cov=scraper
```

---

## 📊 **Example Output**

### **CSV Output**
```csv
title,price,image,link
iPhone 13 Pro,$999.99,https://example.com/iphone.jpg,https://example.com/iphone
Samsung Galaxy S21,$899.99,https://example.com/samsung.jpg,https://example.com/samsung
```

### **JSON Output**
```json
[
  {
    "title": "iPhone 13 Pro",
    "price": "$999.99",
    "image": "https://example.com/iphone.jpg",
    "link": "https://example.com/iphone"
  }
]
```

---

## 🔧 **Advanced Features**

### **Intelligent Site Detection**
The scraper automatically:
- **Detects site type** (e-commerce, blog, news, etc.)
- **Identifies product patterns** (shopping cart, prices, add to cart buttons)
- **Generates appropriate CSS selectors**
- **Adapts to different site structures**

### **Dynamic CSS Selector Generation**
- **Smart selector strategies** based on element attributes
- **Fallback mechanisms** for when primary selectors fail
- **Validation and optimization** of generated selectors
- **Site-specific caching** for improved performance

### **Anti-Detection Measures**
- **User agent rotation** from a large pool of realistic browsers
- **Proxy rotation** with automatic failover
- **Rate limiting** with random delays
- **Request header randomization**

### **Robust Error Handling**
- **Retry logic** with exponential backoff
- **Graceful degradation** when selectors fail
- **Comprehensive logging** for debugging
- **Custom exceptions** with helpful error messages

---

## 🚀 **Performance & Scalability**

### **Optimizations**
- **Asynchronous processing** for multiple jobs
- **Database caching** for site analysis results
- **Efficient memory usage** with streaming data processing
- **Background job processing** with queue management

### **Monitoring**
- **Real-time job status** tracking
- **Performance metrics** and statistics
- **Error rate monitoring**
- **Resource usage tracking**

---

## 🔒 **Security & Privacy**

- **No sensitive data logging** (credentials, API keys)
- **Input validation** and sanitization
- **Secure configuration** management
- **Respect for robots.txt** (configurable)

---

## 🤝 **Contributing**

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### **Development Setup**
```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest

# Format code
black scraper/

# Lint code
flake8 scraper/
```

---

## 📝 **Logging & Troubleshooting**

### **Log Files**
- **Main logs**: `logs/scraper.log`
- **Error logs**: `logs/error_YYYY-MM-DD.log`
- **Dashboard logs**: Console output

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

---

## 📄 **License**

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🎉 **What's New in This Version**

### **v2.0 - Advanced Features**
- ✅ **Web Dashboard** with real-time monitoring
- ✅ **Intelligent Site Detection** with automatic adaptation
- ✅ **Dynamic CSS Selector Generation**
- ✅ **Comprehensive HTML Analysis**
- ✅ **Advanced Error Handling** and recovery
- ✅ **Database Integration** with SQLAlchemy
- ✅ **Background Job Processing**
- ✅ **Interactive Charts** and statistics
- ✅ **Site Analysis API** with confidence scoring
- ✅ **Professional UI/UX** with Bootstrap 5

### **v1.0 - Core Features**
- ✅ **Basic web scraping** functionality
- ✅ **Proxy and user agent rotation**
- ✅ **Data export** in multiple formats
- ✅ **Logging system** with rotation
- ✅ **Configuration management**
- ✅ **Comprehensive testing**

---

**🎯 Ready to scrape the web intelligently? Start with the web dashboard for the best experience!**
