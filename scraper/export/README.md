# Export Package

The `export` package provides comprehensive data export and sharing capabilities.

## Modules

### Export Manager (`export_manager.py`)
Multi-format export with sharing integrations.

**Key Classes:**
- **`ExportConfig`**: Configuration for export operations
- **`ExportResult`**: Result dataclass for export operations
- **`ExportManager`**: Main export engine
  - **Features:**
    - Multiple formats (JSON, CSV, Excel, ZIP)
    - Metadata inclusion
    - Slack integration for sharing
    - Export history tracking
    - Automatic cleanup of old exports
    - Comprehensive ZIP packages with summary reports

## Supported Formats

- **JSON**: Structured data with metadata
- **CSV**: Tabular format for spreadsheets
- **Excel**: Multi-sheet workbooks with formatting
- **ZIP**: Complete package with all formats and metadata

## Usage

The export manager provides a unified interface for exporting scraped data in various formats and sharing results through different channels.
