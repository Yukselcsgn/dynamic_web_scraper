
# Developer Documentation for Dynamic Web Scraper

## Overview
Dynamic Web Scraper is a modular, testable Python tool for scraping dynamic web pages. It uses config-driven user-agent and proxy rotation, robust logging, and a clear module structure.

---

## Project Structure
```
dynamic_web_scraper/
├── scraper/
│   ├── main.py
│   ├── Scraper.py
│   ├── config.py
│   ├── user_agent_manager/
│   ├── proxy_manager/
│   ├── utils/
│   ├── css_selectors/
│   ├── site_detection/
│   ├── data_parsers/
│   ├── logging_manager/
│   └── exceptions/
├── data/
├── logs/
├── tests/
├── requirements.txt
├── README.md
└── DeveloperRead.md
```

---

## Configuration
- All user agents and proxies are managed in `config.json` (JSON format only).
- Example:
```json
{
  "user_agents": ["..."],
  "proxies": ["http://..."]
}
```

---

## Logging
- Uses rotating log files (`logs/scraper.log`, max 5MB, 5 backups).
- Critical errors are logged to daily files in `logs/`.
- Use `log_message(level, message)` for consistent logging.

---

## Exception Handling
- All custom exceptions inherit from `ScraperException` and provide user-friendly messages and suggestions.
- You can raise exceptions with or without context (e.g., `ProxyError()`, `ProxyError(proxy="1.2.3.4")`).

---

## Testing
- All modules, including utilities, selectors, and site detection, have unit tests in `tests/`.
- Integration tests cover the main scraping workflow.
- Run all tests with:
```bash
pytest
# or
python -m unittest discover tests
```

---

## Contributing
- Follow PEP8 and use `black` for formatting.
- Add or update tests for new features.
- Document new modules and functions.
- Submit pull requests with clear descriptions.

---

## Troubleshooting
- If you see errors about missing config or dependencies, check `config.json` and run `pip install -r requirements.txt`.
- Check logs in `logs/` for detailed error messages.
