
# Dynamic Web Scraper

## Overview
**Dynamic Web Scraper** is a Python-based tool designed to extract data from dynamic websites, especially e-commerce platforms. It utilizes features such as rotating user-agents and proxies, and integrates with **Selenium** for handling JavaScript-heavy content. This tool can be customized for scraping different types of web pages and is capable of saving scraped data in multiple formats.

---

## Features
- **User-Agent Rotation**: Mimic real user behavior by cycling through different user-agents to avoid detection.
- **Proxy Support**: Avoid IP blocks by using rotating proxies.
- **Dynamic Content Handling**: Uses Selenium to render JavaScript-heavy pages before scraping.
- **Data Storage**: Save the scraped data in CSV format for easy access and further processing.
- **Logging**: Comprehensive logging of every step to track progress and troubleshoot.

---

## Requirements

- **Python 3.8 or later**: Ensure you have a compatible Python version installed.
- **Google Chrome** or **Firefox**: You need one of these browsers installed.
- **Required Python Libraries**: The libraries required to run the scraper are listed in the `requirements.txt` file.

---

## Installation

### Clone the Repository
To get started, clone the repository to your local machine:

```bash
git clone https://github.com/Yukselcsgn/dynamic_web_scraper.git
cd dynamic_web_scraper
```

### Set up Virtual Environment
1. **Create a virtual environment** to isolate project dependencies:
   ```bash
   python -m venv .venv
   ```
2. **Activate the environment**:
   - **Windows**: `.venv\Scriptsctivate`
   - **Mac/Linux**: `source .venv/bin/activate`

### Install Dependencies
Install the required libraries by running the following command:

```bash
pip install -r requirements.txt
```

---

## Usage

### Running the Scraper

To run the scraper, use the following command:

```bash
python scraper/main.py
```

### Input Prompts
When the script runs, you will be prompted to enter the following:
1. **URL to scrape**: Provide the URL of the product or page you want to extract data from.
2. **Output file path**: Specify the location where the scraped data will be saved. By default, the scraper saves to `data/all_listings.csv`. Press `Enter` to accept the default.

### Example Workflow

1. **Run the Script**:
   ```bash
   python scraper/main.py
   ```

2. **Enter the URL** of the page you want to scrape:
   ```bash
   https://www.teknosa.com/akilli-saat-c-100004001
   ```

3. **Specify the Output File**:
   Press `Enter` to save the data in `data/all_listings.csv` or provide a custom file path.

4. The scraper will extract data and save it to the specified file.

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
│   ├── raw_data/                   # Directory for storing raw HTML responses
│   ├── processed_data/             # Directory for storing processed data (if needed)
│   ├── proxies.txt                 # List of proxies (one proxy per line)
│   └── user_agents.txt             # List of user agents (one user agent per line)
│
├── requirements.txt                # List of required packages for the project
├── README.md                       # Project documentation and usage instructions
├── CONTRIBUTING.md                 # Guidelines for contributing to the project
├── LICENSE                          # License for the project
└── .gitignore                      # Specifies files and directories to ignore in version control

```

---

## Customization

You can customize the scraper by modifying several configuration files:

- **User-Agent Rotation**:
  - Open `data/user_agents.txt` and add more user-agent strings (one per line) to improve scraping mimicry.

- **Proxy Rotation**:
  - Add proxy URLs to `data/proxies.txt`. The scraper will use these proxies to avoid detection and prevent IP bans.

- **Scraping Logic**:
  - If you want to scrape different types of data, modify the `scraper/utils/html_parser.py` file to suit your needs. This file contains the logic for selecting and extracting data from web pages.

---

## Logging

The scraper includes a detailed logging mechanism to track every important action, including:

- **User-Agent and Proxy Selections**: Logs each time a new user-agent or proxy is selected.
- **Scraping Progress**: Logs the scraping process, including the number of elements found on the page.
- **Errors**: Logs any issues or errors during scraping.

Logs are displayed in the terminal and can also be saved to a file for future reference.

---

## Troubleshooting

### Common Issues

#### `ResultSet object has no attribute 'select'`
- **Cause**: This error occurs if you try to use the `select()` method on a list of elements (a `ResultSet` object) instead of a single element.
- **Solution**: Use `find()` for single elements and `find_all()` for multiple elements.

#### WebDriver Issues
- **Cause**: Missing or incompatible browser driver.
- **Solution**: Make sure `webdriver-manager` is installed and that the browser driver matches your installed browser version.

---

## Contributing

Contributions to the project are welcome! If you have any improvements or bug fixes, feel free to fork the repository and submit a pull request.

### Steps for Contributing:
1. Fork the repository.
2. Create a new branch.
3. Implement your changes.
4. Submit a pull request with a detailed description of the changes.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

For more information, visit the [GitHub repository](https://github.com/Yukselcsgn/dynamic_web_scraper).
