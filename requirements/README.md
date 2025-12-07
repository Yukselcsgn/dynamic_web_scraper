# Dependency Management Guide

This directory contains organized dependency files for the Dynamic Web Scraper project.

## Directory Structure

```
requirements/
├── base.txt       → Core web scraping dependencies (always required)
├── web.txt        → Scheduling capabilities (depends on base)
├── data.txt       → Optional data analysis and visualization
├── advanced.txt   → Experimental features (Cloudflare bypass, Flask dashboard)
├── testing.txt    → Testing framework and coverage tools
├── dev.txt        → Development tools (linting, formatting, docs)
└── all.txt        → Convenience file installing everything
```

## Installation Guide

### Minimal Installation (Core Only)
For basic web scraping functionality:
```bash
pip install -r requirements/base.txt
```

### Standard Installation (Recommended)
Core + scheduling + testing:
```bash
pip install -r requirements/base.txt -r requirements/web.txt -r requirements/testing.txt
```

### Full Development Environment
Install everything:
```bash
pip install -r requirements/all.txt
```

### Custom Installation
Mix and match based on your needs:
```bash
# Core + data analysis
pip install -r requirements/base.txt -r requirements/data.txt

# Core + advanced features
pip install -r requirements/base.txt -r requirements/advanced.txt

# Development setup without experimental features
pip install -r requirements/base.txt -r requirements/web.txt -r requirements/testing.txt -r requirements/dev.txt
```

## Backward Compatibility

The root-level `requirements.txt` and `requirements-dev.txt` files are maintained as thin wrappers for backward compatibility. Existing installation commands continue to work:

```bash
# Still works - installs base + web + data + advanced + testing
pip install -r requirements.txt

# Still works - installs everything
pip install -r requirements-dev.txt
```

## File Responsibilities

### base.txt
Contains **only** core dependencies required for basic web scraping:
- Selenium, BeautifulSoup, requests
- Browser drivers (webdriver-manager, undetected-chromedriver)
- Essential utilities (filelock, colorama, click)

### web.txt
Extended web scraping capabilities:
- Scheduling (schedule library)
- Depends on: `base.txt`

### data.txt
**Optional** data handling dependencies:
- pandas, numpy, scipy
- Visualization (matplotlib, seaborn, plotly)
- Excel support (openpyxl)
- PDF generation (fpdf)

**Note**: Core scraper works without these. Install only if exporting data or generating reports.

### advanced.txt
**Experimental** and advanced features:
- Cloudflare bypass (cloudscraper, requests-html, playwright)
- Web dashboard (Flask + SQLAlchemy stack)
- Depends on: `base.txt`

**Warning**: These features may change. Not required for standard scraping workflows.

### testing.txt
Testing and coverage tools:
- pytest framework and plugins
- Test utilities (responses, httpretty, freezegun, factory-boy)
- Coverage reporting
- Depends on: `base.txt`

### dev.txt
Development and maintenance tools:
- Code quality (black, flake8, mypy, isort, pylint)
- Security scanning (bandit, safety, semgrep)
- Documentation (sphinx, mkdocs)
- Profiling and debugging tools
- Depends on: `base.txt`

## Version Pinning Strategy

- **Runtime dependencies** (base, web, data, advanced): Use exact pins (`==`) for reproducibility
- **Testing dependencies**: Flexible versions (`>=`) where safe, exact pins for pytest
- **Development tools**: Minimum versions (`>=`) for latest features

## Updating Dependencies

1. Update the specific file in `requirements/`
2. Test installation in a clean virtual environment
3. Run tests to verify compatibility
4. Update CHANGELOG.md with dependency changes

## Duplicate Resolution

The following duplicates from the original files have been consolidated:
- `pytest`: Kept in testing.txt (exact version 8.2.0)
- `click`: Kept in base.txt (exact version 8.2.1)
- `colorama`: Kept in base.txt (exact version 0.4.6)
- `safety`: Kept in dev.txt (minimum version >=2.3.0)

## Migration Notes

### From Old Structure
```
requirements.txt        → requirements/base.txt + web.txt + data.txt + advanced.txt + testing.txt
requirements-dev.txt    → requirements/all.txt
```

### Key Changes
1. Flask dashboard moved from implicit production → explicit experimental (advanced.txt)
2. Data analysis libraries (pandas, etc.) now clearly optional (data.txt)
3. Testing dependencies properly separated and duplicates removed (testing.txt)
4. Development tools organized by purpose (dev.txt)
