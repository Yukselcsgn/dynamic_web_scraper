# User Guide - Dynamic Web Scraper

Complete guide for end users of the Dynamic Web Scraper.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Using the Web Dashboard](#using-the-web-dashboard)
5. [Command Line Usage](#command-line-usage)
6. [Configuration](#configuration)
7. [Common Use Cases](#common-use-cases)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

## Introduction

The Dynamic Web Scraper is a powerful tool for extracting data from websites. It features:

- ✨ **Automatic site detection** - No manual configuration needed
- 🛡️ **Anti-bot evasion** - Bypass common protections
- 📊 **Data analysis** - Built-in analytics and visualization
- 🚀 **Easy to use** - Web dashboard or command line interface

## Installation

### Requirements

- Python 3.8 or higher
- Windows, Mac, or Linux
- Internet connection
- (Optional) Google Chrome for advanced features

### Step-by-Step Installation

1. **Download the project**
   ```bash
   git clone https://github.com/Yukselcsgn/dynamic_web_scraper.git
   cd dynamic_web_scraper
   ```

2. **Create a virtual environment**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Mac/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**
   ```bash
   python setup_and_test.py
   ```

## Quick Start

### Option 1: Web Dashboard (Recommended for Beginners)

1. **Start the dashboard**
   ```bash
   python run_dashboard.py
   ```

2. **Open your browser** - Navigate to `http://localhost:5000`

3. **Enter a URL** - Type the website you want to scrape

4. **Click "Start Scraping"** - Wait for results

5. **Download your data** - Export as CSV, JSON, or Excel

### Option 2: Python Script

```python
from scraper.Scraper import Scraper

# Create scraper
scraper = Scraper(
    url="https://example.com/products",
    config={"use_proxy": False}
)

# Fetch data
result = scraper.fetch_data()

# Save to CSV
scraper.save_data(
    data=result['raw_data'],
    file_name="products.csv",
    format="csv"
)
```

## Using the Web Dashboard

### Dashboard Overview

The web dashboard provides an easy-to-use interface for:
- Starting scraping jobs
- Monitoring progress
- Viewing results
- Managing configuration

### Starting a Scraping Job

1. **Navigate to "Start Scraping"** tab
2. **Enter the URL** you want to scrape
3. **Select output format** (CSV, JSON, or Excel)
4. **Configure options** (optional):
   - Enable proxy rotation
   - Set custom selectors
   - Adjust retry settings
5. **Click "Start Scraping"**

### Monitoring Jobs

- **Active Jobs**: Shows currently running scrapes
- **Job History**: View past scraping jobs
- **Results**: Download completed data

### Viewing Results

1. Go to **"Results"** tab
2. Click on a completed job
3. **Preview** the data
4. **Download** in your preferred format

## Command Line Usage

### Basic Scraping

```bash
python scraper/main.py
```

Follow the prompts to:
1. Enter target URL
2. Specify output file path
3. Choose format (CSV/JSON)

### Advanced Scraping

```python
from scraper.Scraper import Scraper

# Configure scraper
config = {
    "use_proxy": True,
    "max_retries": 3,
    "retry_delay": 2,
    "rate_limiting": {
        "requests_per_minute": 60
    }
}

# Initialize
scraper = Scraper(url="https://example.com", config=config)

# Scrape with options
result = scraper.fetch_data(
    enable_smart_detection=True,
    enable_enrichment=True,
    enable_analysis=True
)

# Access enriched data
enriched_data = result.get('enriched_data', [])
```

## Configuration

### Basic Configuration

Edit `config.json`:

```json
{
  "use_proxy": false,
  "max_retries": 3,
  "retry_delay": 2,
  "rate_limiting": {
    "requests_per_minute": 60
  }
}
```

### Common Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `use_proxy` | Enable proxy rotation | `false` |
| `max_retries` | Retry failed requests | `3` |
| `retry_delay` | Seconds between retries | `2` |
| `requests_per_minute` | Rate limit | `60` |

## Common Use Cases

### 1. E-commerce Price Monitoring

```python
from scraper.Scraper import Scraper

scraper = Scraper(
    url="https://example-shop.com/products",
    config={"use_proxy": False}
)

result = scraper.fetch_data()
scraper.save_data(result['raw_data'], "prices.csv", "csv")
```

### 2. News Article Scraping

```python
scraper = Scraper(
    url="https://news-site.com/articles",
    config={"max_retries": 5}
)

result = scraper.fetch_data()
```

### 3. Bulk Data Collection

```python
urls = [
    "https://site1.com",
    "https://site2.com",
    "https://site3.com"
]

for url in urls:
    scraper = Scraper(url=url, config={})
    result = scraper.fetch_data()
    scraper.save_data(result['raw_data'], f"{url}_data.csv", "csv")
```

## Troubleshooting

### Common Issues

#### No Data Extracted

**Problem**: Scraper runs but returns no data

**Solutions**:
1. Check if the site requires JavaScript (use Selenium mode)
2. Verify the URL is accessible
3. Enable debug logging:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

#### Connection Errors

**Problem**: Cannot connect to website

**Solutions**:
1. Check internet connection
2. Try using a proxy
3. Increase retry delay
4. Verify URL is correct

#### Blocked by Website

**Problem**: Getting 403 Forbidden errors

**Solutions**:
1. Enable anti-bot evasion
2. Use proxy rotation
3. Add delays between requests
4. Check robots.txt compliance

### Getting Help

-  Check the [FAQ](#faq)
- Review [documentation](../docs/README.md)
- Open an issue on [GitHub](https://github.com/Yukselcsgn/dynamic_web_scraper/issues)

## FAQ

### General Questions

**Q: Is web scraping legal?**
A: Web scraping legality varies by jurisdiction and use case. Always:
- Check the website's Terms of Service
- Respect robots.txt
- Don't overload servers
- Use scraped data ethically

**Q: What websites can I scrape?**
A: The scraper works with most websites, but success depends on:
- Website structure
- Anti-bot measures
- Rate limiting
- Terms of service

**Q: How fast can it scrape?**
A: Speed depends on:
- Website response time
- Rate limiting settings
- Network connection
- Anti-bot measures

### Technical Questions

**Q: Can I scrape JavaScript-heavy sites?**
A: Yes, the scraper supports Selenium for JavaScript rendering.

**Q: How do I handle CAPTCHAs?**
A: CAPTCHAs require manual intervention or third-party CAPTCHA solving services.

**Q: Can I schedule scraping jobs?**
A: Yes, use the distributed scraping features or external schedulers like cron.

**Q: What output formats are supported?**
A: CSV, JSON, Excel, and custom formats via the export manager.

## Next Steps

- Read [Advanced Features Guide](configuration.md)
- Explore [Tutorials](../tutorials/)
- Review [API Documentation](../api/index.md)

---

**Need more help?** Check our [GitHub repository](https://github.com/Yukselcsgn/dynamic_web_scraper) or open an issue.
