# Data Processing Package

The `data_processing` package provides advanced data enrichment and quality improvement.

## Modules

### Data Enricher (`data_enricher.py`)
Advanced data cleaning, normalization, and enrichment system.

**Key Classes:**
- **`EnrichmentResult`**: Result dataclass containing enriched data and statistics
- **`DataEnricher`**: Main enrichment engine
  - **Features:**
    - Price normalization with currency detection
    - Data deduplication
    - Category classification
    - Contact information extraction
    - URL validation
    - Quality scoring
    - Outlier detection
    - Metadata enrichment

## Usage

The enricher processes scraped data to improve quality, extract additional insights, and normalize formats for better analysis.
