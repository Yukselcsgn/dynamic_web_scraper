# Comparison Package

The `comparison` package provides comprehensive cross-site product comparison and price analysis capabilities.

## Modules

### Site Comparator (`site_comparator.py`)
Performs intelligent product matching and price comparison across multiple sites.

**Key Classes:**
- **`ProductMatch`**: Represents a product matched across multiple sites
- **`PriceComparison`**: Price comparison results for a product
- **`DealAnalysis`**: Deal analysis with savings metrics
- **`SiteComparator`**: Main comparison engine
  - **Features:**
    - Product matching using title/category/brand similarity
    - Price comparison with statistical analysis
    - Deal scoring and recommendations
    - Comprehensive comparison reports
    - Integration with analytics modules

## Usage

The comparator loads data from multiple sources, matches products based on similarity, performs price analysis, and generates recommendations for best deals.
