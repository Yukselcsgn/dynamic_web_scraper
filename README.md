
# Dynamic E-Commerce Scraper

## Overview

Dynamic E-Commerce Scraper is a Python-based web scraping tool designed to efficiently extract product data from various e-commerce websites. Utilizing Selenium, BeautifulSoup, and concurrent threading, this scraper adapts to different site structures dynamically, making it versatile for various e-commerce platforms.

## Features

- **Dynamic Selector Detection**: Automatically identifies the structure of different e-commerce sites to locate product listings, prices, and titles.
- **Human-Like Interaction**: Simulates user behavior to avoid detection and CAPTCHA challenges.
- **Parallel Scraping**: Utilizes threading to scrape multiple URLs concurrently, increasing efficiency.
- **Proxy Support**: Supports the use of proxies for anonymity and to bypass potential restrictions.
- **Robust Error Handling**: Logs errors and warnings to a file for debugging and performance monitoring.
- **CSV Export**: Saves extracted data in a CSV format for easy analysis and sharing.

## Installation

### Prerequisites

- Python 3.1.2
- pip (Python package installer)

### Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Yukselcsgn/dynamic_web_scraper.git
   cd dynamic-ecommerce-scraper
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv env
   ```

3. **Activate the Virtual Environment**:
   - **Windows**:
     ```bash
     .\env\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source env/bin/activate
     ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To use the scraper, modify the `urls_to_scrape` list in the `main.py` file with the URLs of the e-commerce pages you want to scrape. You can also specify proxies if needed.

Run the scraper using the following command:
```bash
python main.py
```

### Example URLs
```python
urls_to_scrape = ['https://example.com/page1', 'https://example.com/page2']
proxies = ['http://proxy1', 'http://proxy2', 'http://proxy3']
```

## Logging

The scraper logs important actions and errors in `scraper.log`, allowing you to review the scraping process and troubleshoot any issues.

## Contributing

Contributions are welcome! If you have suggestions or improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Selenium](https://www.selenium.dev/) for web automation.
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for parsing HTML and XML documents.
- [Fake UserAgent](https://github.com/helixdragon/fake-useragent) for generating random user agents.
- [Webdriver Manager](https://github.com/SergeyPirogov/webdriver_manager) for managing browser drivers.
