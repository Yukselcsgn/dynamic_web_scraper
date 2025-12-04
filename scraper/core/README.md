# Core Package

The `core` package contains the main scraping functionality split into modular components.

## Modules

### 1. Scraper (`scraper.py`)
Main orchestration class that combines all core functionality.

**Key Class:** `Scraper`
- **Features:**
  - Component initialization and orchestration
  - Data fetching with smart detection
  - Data enrichment and analysis
  - Multiple export formats (CSV, JSON, Excel)
  - Context manager support

### 2. Initialization (`initialization.py`)
Handles scraper initialization and configuration.

### 3. Data Fetching (`data_fetching.py`)
Manages HTTP requests, retry logic, and response handling.

### 4. Site Detection (`site_detection.py`)
Detects site types and profiles for smart scraping.

### 5. Data Extraction (`data_extraction.py`)
Extracts structured data from HTML content.

### 6. Data Processing (`data_processing.py`)
Processes, normalizes, and enriches extracted data.

### 7. Utilities (`utilities.py`)
Common utility functions for the scraper.

## Architecture

The core package follows a modular design where each component handles specific responsibilities, making the codebase maintainable and extensible.
