# Getting Started with Dynamic Web Scraper

This guide will help you get your first scraper up and running.

## Prerequisites

- Python 3.8 or later
- pip (Python package manager)
- Google Chrome or Firefox (for Selenium)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd dynamic_web_scraper
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies (optional)
pip install -r requirements-dev.txt
```

### 4. Verify Installation

```bash
python setup_and_test.py
```

## Quick Start

### Option 1: Web Dashboard (Recommended)

```bash
python run_dashboard.py
```

The dashboard will open at `http://localhost:5000`

### Option 2: Command Line

```python
from scraper.Scraper import Scraper

# Initialize scraper
config = {
    "use_proxy": False,
    "max_retries": 3
}

scraper = Scraper(url="https://example.com", config=config)

# Fetch data
result = scraper.fetch_data()

# Access scraped data
print(result['raw_data'])
```

## Your First Scrape

1. **Choose a target website**
2. **Initialize the scraper** with the URL
3. **Run the scraper** - It will auto-detect the site structure
4. **Review the results** in your chosen format

## Next Steps

- Read the [Configuration Guide](configuration.md) to customize behavior
- Check [Basic Scraping Tutorial](../tutorials/basic-scraping.md) for detailed examples
- Explore [Anti-Bot Evasion](anti-bot-evasion.md) for challenging sites

## Troubleshooting

### Import Errors
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Selenium Issues
The scraper will auto-download webdrivers. If issues persist:
```bash
pip install webdriver-manager --upgrade
```

### Permission Errors
Run with appropriate permissions or adjust file paths in config.
