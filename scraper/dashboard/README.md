# Dashboard Package

The `dashboard` package provides web-based interfaces for monitoring and managing scraping operations.

## Modules

### 1. Flask App (`app.py`)
Web dashboard with job management and database backend.

**Key Features:**
- Job queue management
- SQLite database for job persistence
- Real-time job status monitoring
- Site analysis endpoint
- Background worker for async processing

### 2. Interactive Dashboard (`interactive_dashboard.py`)
Advanced data exploration and visualization dashboard.

**Key Class:** `InteractiveDashboard`
- **Features:**
  - Data loading and filtering
  - Interactive charts (price distribution, trends, comparisons)
  - Analysis recommendations
  - Export capabilities (HTML, PNG, PDF)
  - Standalone HTML generation

**Key Class:** `DashboardConfig`
- Configuration for dashboard server (port, host, theme, etc.)

## Usage

The dashboard can be launched as a web server to provide a visual interface for managing scraping jobs and analyzing collected data.
