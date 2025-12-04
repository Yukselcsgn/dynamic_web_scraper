# Analytics Package

The `analytics` package provides comprehensive data analysis and visualization capabilities for the Dynamic Web Scraper. It includes modules for price analysis, time series forecasting, and interactive data visualization.

## Modules

### 1. Data Visualizer (`data_visualizer.py`)
Handles the creation of charts, graphs, and interactive dashboards.

**Key Class:** `DataVisualizer`
- **Features:**
  - Price distribution charts
  - Trend analysis visualizations
  - Comparative analysis
  - Heatmaps
  - Summary dashboards
- **Output:** Generates HTML files with interactive plots (using Plotly/Seaborn).

### 2. Price Analyzer (`price_analyzer.py`)
Performs statistical analysis on price data to identify patterns, outliers, and insights.

**Key Class:** `PriceAnalyzer`
- **Features:**
  - Basic statistics (mean, median, etc.)
  - Price distribution analysis
  - Outlier detection
  - Trend analysis
  - Actionable recommendations
- **Data Class:** `PriceAnalysis` (stores analysis results)

### 3. Time Series Analyzer (`time_series_analyzer.py`)
Advanced analysis for time-dependent data, including forecasting and anomaly detection.

**Key Class:** `TimeSeriesAnalyzer`
- **Features:**
  - Trend detection (direction, strength)
  - Seasonality analysis
  - Anomaly detection (Z-score, IQR, Isolation Forest)
  - Price prediction (Linear, Exponential, Moving Average)
- **Data Classes:** `TrendAnalysis`, `SeasonalityAnalysis`, `AnomalyDetection`, `PricePrediction`

## Usage

The analytics modules are typically used in conjunction with the scraper to process and visualize the collected data. They can be initialized and used to generate reports and insights based on the scraped datasets.
