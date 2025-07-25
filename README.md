
# Dynamic Web Scraper

## Overview
Dynamic Web Scraper is a Python-based tool for extracting data from dynamic websites, especially e-commerce platforms. It features rotating user-agents and proxies, Selenium integration for JavaScript-heavy content, and robust logging with log rotation.

---

## Features
- User-Agent and Proxy Rotation (from config.json)
- Dynamic Content Handling (Selenium)
- Data Storage in CSV/JSON
- Log Rotation and Error Logging
- Modular, Testable Codebase

---

## Requirements
- Python 3.8 or later
- Google Chrome or Firefox
- All dependencies are version-pinned in `requirements.txt` for reproducibility and stability.

---

## Installation
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

---

## Configuration
All user agents and proxies are managed in `config.json`:
```json
{
  "user_agents": ["...", "..."],
  "proxies": ["http://...", "http://..."],
  ...
}
```
- Edit `config.json` to add/remove user agents or proxies.
- Do not use TXT files for user agents or proxies; only config.json is supported in the main workflow.

---

## Usage
To run the scraper:
```bash
python scraper/main.py
```
You will be prompted for:
- The URL to scrape
- The output file path (default: data/all_listings.csv)

---

## Example Output

After the scraper finishes running, you will have a CSV file with the extracted data. The file will contain details like product names, prices, descriptions, and other relevant information from the page.

---

## Project Structure

```
dynamic_web_scraper/
│
├── scraper/
│   ├── __init__.py                # Makes this directory a package
│   ├── main.py                     # Entry point for the scraper
│   ├── config.py                   # Configuration settings (URLs, proxies, etc.)
│   ├── scraper.py                  # Main scraper class and methods
│   ├── utils/
│   │   ├── __init__.py             # Makes this directory a package
│   │   ├── request_utils.py        # Utility functions for HTTP requests
│   │   ├── parse_utils.py          # Utility functions for parsing data
│   │   ├── wait_utils.py           # Utility functions for human-like waiting
│   │   ├── user_agent_utils.py     # Utility functions for managing user agents
│   │   └── proxy_utils.py          # Utility functions for proxy handling
│   ├── site_detection/              # Module for detecting site structures
│   │   ├── __init__.py
│   │   ├── site_detector.py         # Main logic for detecting site layouts
│   │   └── site_config.py           # Site-specific configurations (e.g., CSS selectors)
│   ├── data_parsers/               # Module for data extraction and parsing
│   │   ├── __init__.py
│   │   ├── data_parser.py           # Main data parsing logic
│   │   └── html_parser.py           # Fallback HTML parsing methods using BeautifulSoup
│   ├── proxy_manager/              # Module for managing proxy servers
│   │   ├── __init__.py
│   │   ├── proxy_manager.py         # Main logic for proxy management
│   │   ├── proxy_loader.py          # Logic for loading proxies from files or APIs
│   │   ├── proxy_rotator.py         # Logic for rotating proxies during scraping
│   │   └── proxy_validator.py       # Logic for validating proxy functionality
│   ├── user_agent_manager/         # Module for handling user agents
│   │   ├── __init__.py
│   │   ├── user_agent_manager.py    # Main logic for managing user agents
│   │   └── user_agent_loader.py     # Logic for loading user agents from files or APIs
│   ├── logging_manager/             # Module for handling logging
│   │   ├── __init__.py
│   │   └── logging_manager.py        # Centralized logging setup
│   └── exceptions/                  # Custom exceptions
│       ├── __init__.py
│       └── scraper_exceptions.py     # Custom exceptions for scraper-related errors
│
├── tests/
│   ├── __init__.py                 # Makes this directory a package
│   ├── test_scraper.py             # Unit tests for scraper functionality
│   ├── test_data_parser.py         # Unit tests for data parsing
│   ├── test_proxy_manager.py        # Unit tests for proxy manager functionality
│   ├── test_user_agent_manager.py   # Unit tests for user agent management
│   ├── test_logging_manager.py      # Unit tests for logging management
│   ├── test_utils.py               # Unit tests for utility functions
│   └── test_site_detector.py        # Unit tests for site detection functionality
│
├── logs/
│   ├── scraper.log                 # Log file for scraping activities
│
├── data/
│   ├── all_listings.csv            # Output data file for scraped listings
│   ├── processed_data/             # Directory for storing processed data
│   ├── user_agents.json            # User agents (JSON format, used in config.json)
│   ├── proxies.txt                 # (Legacy, not used in main workflow)
│   └── raw_data/                   # Directory for storing raw HTML responses
│
├── requirements.txt                # List of required packages for the project
├── README.md                       # Project documentation and usage instructions
├── CONTRIBUTING.md                 # Guidelines for contributing to the project
├── LICENSE                          # License for the project
└── .gitignore                      # Specifies files and directories to ignore in version control

---

## Logging & Troubleshooting
- Logs are written to `logs/scraper.log` with automatic rotation (max 5MB, 5 backups).
- Critical errors are also logged to daily files in `logs/`.
- If you see errors about missing config or dependencies, check your `config.json` and run `pip install -r requirements.txt`.

---

## Contributing
- Follow PEP8 and use `black` for formatting.
- Add or update tests for new features.
- See `DeveloperRead.md` for more details.

---

## License
MIT License
