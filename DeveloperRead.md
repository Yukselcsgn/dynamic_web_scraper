
# Developer Documentation for Dynamic Web Scraper

## Overview
The **Dynamic Web Scraper** is a Python-based scraping tool designed to efficiently extract data from dynamic web pages, particularly e-commerce sites. It uses a modular architecture to ensure scalability, maintainability, and reliability, employing techniques like user-agent rotation, proxy handling, and Selenium for rendering JavaScript-heavy content.

This document provides detailed information about the project structure, the purpose of each file, setup instructions, and customization options.

---

## Prerequisites
1. **Python**: Version 3.8 or later.
2. **Browser**: Chrome or Firefox installed locally.
3. **Required Libraries**: Listed in `requirements.txt`.

---

## Installation and Setup

### Clone the Repository
```bash
git clone https://github.com/Yukselcsgn/dynamic_web_scraper.git
cd dynamic_web_scraper
```

### Virtual Environment Setup
1. **Create a Virtual Environment**:
   ```bash
   python -m venv .venv
   ```
2. **Activate the Environment**:
   - **Windows**: `.venv\Scripts\activate`
   - **Mac/Linux**: `source .venv/bin/activate`

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Verify Setup
Run the main script:
```bash
python scraper/main.py
```

---

## Project Structure

```
dynamic_web_scraper/
│
├── scraper/                      # Core functionality of the scraper
│   ├── main.py                   # Entry point for running the scraper
│   ├── user_agent_manager.py     # Manages random user-agent selection
│   ├── proxy_manager.py          # Handles proxy loading and rotation
│   ├── utils/                    # Utility functions
│   │   ├── html_parser.py        # Parsing and data extraction logic
│   │   ├── logger.py             # Logging configuration and utilities
│   │   └── file_manager.py       # Functions for saving extracted data
│
├── data/                         # Storage for resources and outputs
│   ├── user_agents.txt           # List of user-agent strings
│   ├── proxies.txt               # List of proxy URLs
│   └── all_listings.csv          # Default output file for scraped data
│
├── tests/                        # Unit and integration tests
│   ├── test_user_agent_manager.py
│   ├── test_proxy_manager.py
│   └── test_main.py
│
├── requirements.txt              # List of required Python libraries
├── README.md                     # General project overview
└── LICENSE                       # License for the project
```

---

## File Descriptions

### **Main Script (`scraper/main.py`)**
- **Purpose**: Orchestrates the entire scraping process.
- **Responsibilities**:
  - Configure logging.
  - Load user-agent and proxy managers.
  - Prompt user for the target URL and output file path.
  - Use Selenium to fetch web pages and Beautiful Soup to parse content.
  - Save extracted data into a CSV file.
- **Key Sections**:
  - **Initialization**: Sets up proxies and user agents.
  - **Scraping Logic**: Navigates to the URL and parses specified elements.
  - **Data Output**: Saves data in the specified format.

---

### **User Agent Manager (`scraper/user_agent_manager.py`)**
- **Purpose**: Mimics real user behavior by cycling through user-agent strings.
- **Key Features**:
  - Loads user-agent strings from `data/user_agents.txt`.
  - Randomly selects a user-agent for each request.
- **Core Functions**:
  - `load_user_agents()`: Reads user-agent strings into memory.
  - `select_user_agent()`: Returns a random user-agent.
- **Extensibility**:
  - Add more user agents to `data/user_agents.txt` to diversify scraping patterns.

---

### **Proxy Manager (`scraper/proxy_manager.py`)**
- **Purpose**: Routes requests through multiple proxies to avoid detection and prevent IP bans.
- **Key Features**:
  - Loads proxies from `data/proxies.txt`.
  - Randomly selects and validates a proxy.
- **Core Functions**:
  - `load_proxies()`: Reads proxy URLs into memory.
  - `select_proxy()`: Selects a random proxy for the session.
- **Extensibility**:
  - Implement proxy validation logic to filter non-working proxies.

---

### **Utilities (`scraper/utils/`)**
1. **`html_parser.py`**:
   - Extracts data from the page using Beautiful Soup.
   - Handles dynamic element parsing.
2. **`logger.py`**:
   - Configures logging to track the script’s execution and errors.
   - Logs information to the console and optionally to a file.
3. **`file_manager.py`**:
   - Saves extracted data in CSV or other formats.
   - Handles file operations securely.

---

### **Data Folder (`data/`)**
- **Purpose**: Stores resources for scraping and output files.
- **Files**:
  - `user_agents.txt`: List of user-agent strings.
  - `proxies.txt`: List of proxy URLs.
  - `all_listings.csv`: Default file for saving scraped data.

---

### **Tests (`tests/`)**
- **Purpose**: Validates functionality of core modules.
- **Files**:
  - `test_user_agent_manager.py`: Ensures user-agent manager works correctly.
  - `test_proxy_manager.py`: Verifies proxy selection and loading.
  - `test_main.py`: Tests integration of the entire scraping process.
- **Run Tests**:
  ```bash
  pytest tests/
  ```

---

## Execution Instructions

1. **Run the Scraper**:
   ```bash
   python scraper/main.py
   ```

2. **Input Prompt**:
   - Enter the **URL** to scrape.
   - Specify the output file path (default: `data/all_listings.csv`).

3. **Check Logs**:
   - The script logs each step, including:
     - Selected proxies and user agents.
     - Scraping progress.
     - Errors or issues.

4. **Verify Output**:
   - Extracted data will be saved in the specified CSV file.

---

## Troubleshooting

### Common Errors

#### **`ResultSet object has no attribute 'select'`**
- **Cause**: Misuse of Beautiful Soup methods (`find()` vs. `find_all()`).
- **Solution**: Ensure the correct method is used for single vs. multiple elements.

#### **WebDriver Issues**
- **Cause**: Missing or mismatched browser driver.
- **Solution**: Ensure `webdriver-manager` is installed and the driver matches your browser version.

---

## Customization

### Add New User Agents
1. Open `data/user_agents.txt`.
2. Add new user-agent strings (one per line).

### Update Proxy List
1. Open `data/proxies.txt`.
2. Replace or append new proxy URLs.

### Extend Scraping Logic
Modify `scraper/utils/html_parser.py` to:
- Extract additional data fields.
- Handle new website structures.

---

## Future Enhancements

1. **Proxy Validation**:
   - Validate proxies before use to ensure reliability.

2. **Dynamic Configurations**:
   - Implement a `config.json` file for customizable settings like target elements and timeouts.

3. **Parallel Scraping**:
   - Add multithreading or multiprocessing for scraping multiple URLs concurrently.

4. **Detailed Logging**:
   - Save logs to a file for post-execution analysis.

---

## Contributing

1. Fork the repository:
   ```bash
   git fork https://github.com/Yukselcsgn/dynamic_web_scraper.git
   ```

2. Create a new feature branch:
   ```bash
   git checkout -b feature-name
   ```

3. Submit a pull request with a detailed description.

---

For more information, refer to the [GitHub repository](https://github.com/Yukselcsgn/dynamic_web_scraper).
