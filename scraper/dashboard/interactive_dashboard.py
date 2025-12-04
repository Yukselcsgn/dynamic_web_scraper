#!/usr/bin/env python3
# Copyright 2024 Yüksel Coşgun
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Interactive Dashboard Module

This module provides a comprehensive web-based dashboard for the Dynamic Web Scraper,
allowing users to explore, filter, and visualize data without coding.
"""

import json
import logging
import os
import sys
import threading
import time
import webbrowser
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add the project root to the path for imports
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from scraper.analytics import DataVisualizer, PriceAnalyzer, TimeSeriesAnalyzer
from scraper.logging_manager.logging_manager import log_message, setup_logging


@dataclass
class DashboardConfig:
    """Configuration for the interactive dashboard."""

    port: int = 8050
    host: str = "localhost"
    debug: bool = False
    auto_open: bool = True
    theme: str = "plotly_white"
    update_interval: int = 30  # seconds


class InteractiveDashboard:
    """
    Comprehensive interactive dashboard for data exploration and visualization.
    """

    def __init__(
        self, data_directory: str = "data", config: Optional[DashboardConfig] = None
    ):
        """
        Initialize the interactive dashboard.

        Args:
            data_directory: Directory containing scraped data
            config: Dashboard configuration
        """
        self.data_directory = Path(data_directory)
        self.config = config or DashboardConfig()

        self.logger = logging.getLogger("InteractiveDashboard")

        # Initialize analytics components
        self.visualizer = DataVisualizer(f"{data_directory}/visualizations")
        self.time_analyzer = TimeSeriesAnalyzer(f"{data_directory}/time_series")
        self.price_analyzer = PriceAnalyzer()

        # Dashboard state
        self.current_data = []
        self.filters = {}
        self.selected_products = []
        self.date_range = None

        # Create necessary directories
        self.data_directory.mkdir(parents=True, exist_ok=True)
        (self.data_directory / "visualizations").mkdir(exist_ok=True)
        (self.data_directory / "time_series").mkdir(exist_ok=True)

        self.logger.info("Interactive dashboard initialized")

    def load_data(self, data_file: Optional[str] = None) -> bool:
        """
        Load data for the dashboard.

        Args:
            data_file: Optional specific data file to load

        Returns:
            True if data loaded successfully
        """
        try:
            if data_file:
                file_path = self.data_directory / data_file
                if file_path.exists():
                    with open(file_path, "r", encoding="utf-8") as f:
                        self.current_data = json.load(f)
                else:
                    self.logger.error(f"Data file not found: {file_path}")
                    return False
            else:
                # Load the most recent data file
                data_files = list(self.data_directory.glob("*.json"))
                if data_files:
                    latest_file = max(data_files, key=os.path.getctime)
                    with open(latest_file, "r", encoding="utf-8") as f:
                        self.current_data = json.load(f)
                    self.logger.info(f"Loaded data from: {latest_file}")
                else:
                    self.logger.warning("No data files found")
                    return False

            self.logger.info(f"Loaded {len(self.current_data)} data points")
            return True

        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            return False

    def get_data_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for the current data.

        Returns:
            Dictionary with data summary
        """
        try:
            if not self.current_data:
                return {"error": "No data loaded"}

            df = pd.DataFrame(self.current_data)

            # Basic statistics
            summary = {
                "total_items": len(df),
                "sources": df["source"].nunique() if "source" in df.columns else 0,
                "categories": df["category"].nunique()
                if "category" in df.columns
                else 0,
                "date_range": None,
                "price_stats": {},
            }

            # Date range
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                summary["date_range"] = {
                    "start": df["timestamp"].min().isoformat(),
                    "end": df["timestamp"].max().isoformat(),
                    "days": (df["timestamp"].max() - df["timestamp"].min()).days,
                }

            # Price statistics
            if "price" in df.columns:
                df["price_numeric"] = pd.to_numeric(
                    df["price"].str.replace(r"[^\d.]", "", regex=True), errors="coerce"
                )
                price_data = df["price_numeric"].dropna()

                if len(price_data) > 0:
                    summary["price_stats"] = {
                        "mean": float(price_data.mean()),
                        "median": float(price_data.median()),
                        "min": float(price_data.min()),
                        "max": float(price_data.max()),
                        "std": float(price_data.std()),
                        "count": len(price_data),
                    }

            return summary

        except Exception as e:
            self.logger.error(f"Error generating data summary: {e}")
            return {"error": str(e)}

    def get_filter_options(self) -> Dict[str, List[str]]:
        """
        Get available filter options for the dashboard.

        Returns:
            Dictionary with filter options
        """
        try:
            if not self.current_data:
                return {}

            df = pd.DataFrame(self.current_data)

            filters = {}

            # Source filter
            if "source" in df.columns:
                filters["sources"] = sorted(df["source"].unique().tolist())

            # Category filter
            if "category" in df.columns:
                filters["categories"] = sorted(df["category"].unique().tolist())

            # Date range filter
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                filters["date_range"] = {
                    "min": df["timestamp"].min().isoformat(),
                    "max": df["timestamp"].max().isoformat(),
                }

            return filters

        except Exception as e:
            self.logger.error(f"Error getting filter options: {e}")
            return {}

    def apply_filters(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply filters to the current data.

        Args:
            filters: Dictionary with filter criteria

        Returns:
            Filtered data
        """
        try:
            if not self.current_data:
                return []

            df = pd.DataFrame(self.current_data)
            filtered_df = df.copy()

            # Apply source filter
            if "sources" in filters and filters["sources"]:
                filtered_df = filtered_df[
                    filtered_df["source"].isin(filters["sources"])
                ]

            # Apply category filter
            if "categories" in filters and filters["categories"]:
                filtered_df = filtered_df[
                    filtered_df["category"].isin(filters["categories"])
                ]

            # Apply date range filter
            if "date_range" in filters and filters["date_range"]:
                start_date = pd.to_datetime(filters["date_range"]["start"])
                end_date = pd.to_datetime(filters["date_range"]["end"])
                filtered_df["timestamp"] = pd.to_datetime(filtered_df["timestamp"])
                filtered_df = filtered_df[
                    (filtered_df["timestamp"] >= start_date)
                    & (filtered_df["timestamp"] <= end_date)
                ]

            self.logger.info(f"Applied filters: {len(filtered_df)} items remaining")
            return filtered_df.to_dict("records")

        except Exception as e:
            self.logger.error(f"Error applying filters: {e}")
            return self.current_data

    def create_price_distribution_chart(self, data: List[Dict[str, Any]]) -> go.Figure:
        """
        Create an interactive price distribution chart.

        Args:
            data: Data to visualize

        Returns:
            Plotly figure object
        """
        try:
            df = pd.DataFrame(data)

            if df.empty or "price" not in df.columns:
                return go.Figure().add_annotation(
                    text="No price data available",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                )

            # Clean price data
            df["price_numeric"] = pd.to_numeric(
                df["price"].str.replace(r"[^\d.]", "", regex=True), errors="coerce"
            )
            df = df.dropna(subset=["price_numeric"])

            if df.empty:
                return go.Figure().add_annotation(
                    text="No valid price data",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                )

            # Create subplots
            fig = make_subplots(
                rows=2,
                cols=2,
                subplot_titles=(
                    "Price Distribution",
                    "Price by Category",
                    "Price Box Plot",
                    "Price Statistics",
                ),
                specs=[
                    [{"type": "histogram"}, {"type": "bar"}],
                    [{"type": "box"}, {"type": "table"}],
                ],
            )

            # Price distribution histogram
            fig.add_trace(
                go.Histogram(
                    x=df["price_numeric"],
                    nbinsx=30,
                    name="Price Distribution",
                    marker_color="#1f77b4",
                ),
                row=1,
                col=1,
            )

            # Price by category
            if "category" in df.columns:
                category_prices = (
                    df.groupby("category")["price_numeric"]
                    .mean()
                    .sort_values(ascending=False)
                )
                fig.add_trace(
                    go.Bar(
                        x=category_prices.index,
                        y=category_prices.values,
                        name="Avg Price by Category",
                        marker_color="#ff7f0e",
                    ),
                    row=1,
                    col=2,
                )

            # Price box plot
            fig.add_trace(
                go.Box(
                    y=df["price_numeric"],
                    name="Price Distribution",
                    marker_color="#2ca02c",
                ),
                row=2,
                col=1,
            )

            # Price statistics table
            stats = {
                "Metric": ["Count", "Mean", "Median", "Std Dev", "Min", "Max"],
                "Value": [
                    len(df),
                    f"${df['price_numeric'].mean():.2f}",
                    f"${df['price_numeric'].median():.2f}",
                    f"${df['price_numeric'].std():.2f}",
                    f"${df['price_numeric'].min():.2f}",
                    f"${df['price_numeric'].max():.2f}",
                ],
            }

            fig.add_trace(
                go.Table(
                    header=dict(
                        values=list(stats.keys()),
                        fill_color="#d62728",
                        font=dict(color="white"),
                    ),
                    cells=dict(values=list(stats.values()), fill_color="lavender"),
                ),
                row=2,
                col=2,
            )

            fig.update_layout(
                title="Price Distribution Analysis",
                height=600,
                showlegend=False,
                template=self.config.theme,
            )

            return fig

        except Exception as e:
            self.logger.error(f"Error creating price distribution chart: {e}")
            return go.Figure().add_annotation(
                text=f"Error creating chart: {e}",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )

    def create_trend_analysis_chart(self, data: List[Dict[str, Any]]) -> go.Figure:
        """
        Create an interactive trend analysis chart.

        Args:
            data: Data to visualize

        Returns:
            Plotly figure object
        """
        try:
            df = pd.DataFrame(data)

            if df.empty:
                return go.Figure().add_annotation(
                    text="No data available for trend analysis",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                )

            # Add timestamp if not present
            if "timestamp" not in df.columns:
                df["timestamp"] = datetime.now()
            else:
                df["timestamp"] = pd.to_datetime(df["timestamp"])

            # Clean price data
            if "price" in df.columns:
                df["price_numeric"] = pd.to_numeric(
                    df["price"].str.replace(r"[^\d.]", "", regex=True), errors="coerce"
                )
                df = df.dropna(subset=["price_numeric"])

            if df.empty:
                return go.Figure().add_annotation(
                    text="No valid price data for trend analysis",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                )

            # Create subplots
            fig = make_subplots(
                rows=2,
                cols=2,
                subplot_titles=(
                    "Price Trends Over Time",
                    "Daily Price Changes",
                    "Moving Averages",
                    "Price Volatility",
                ),
                specs=[
                    [{"type": "scatter"}, {"type": "bar"}],
                    [{"type": "scatter"}, {"type": "histogram"}],
                ],
            )

            # Price trends over time
            df_sorted = df.sort_values("timestamp")
            fig.add_trace(
                go.Scatter(
                    x=df_sorted["timestamp"],
                    y=df_sorted["price_numeric"],
                    mode="lines+markers",
                    name="Price Trend",
                    line=dict(color="#1f77b4", width=2),
                ),
                row=1,
                col=1,
            )

            # Add moving average
            window_size = min(7, len(df_sorted) // 4)
            if window_size > 1:
                moving_avg = (
                    df_sorted["price_numeric"].rolling(window=window_size).mean()
                )
                fig.add_trace(
                    go.Scatter(
                        x=df_sorted["timestamp"],
                        y=moving_avg,
                        mode="lines",
                        name=f"{window_size}-Day Moving Avg",
                        line=dict(color="#ff7f0e", width=2, dash="dash"),
                    ),
                    row=1,
                    col=1,
                )

            # Daily price changes
            price_changes = df_sorted["price_numeric"].diff().dropna()
            fig.add_trace(
                go.Bar(
                    x=df_sorted["timestamp"][1:],
                    y=price_changes,
                    name="Daily Price Changes",
                    marker_color=["green" if x >= 0 else "red" for x in price_changes],
                ),
                row=1,
                col=2,
            )

            # Moving averages comparison
            short_ma = df_sorted["price_numeric"].rolling(window=3).mean()
            fig.add_trace(
                go.Scatter(
                    x=df_sorted["timestamp"],
                    y=short_ma,
                    mode="lines",
                    name="3-Day MA",
                    line=dict(color="#2ca02c"),
                ),
                row=2,
                col=1,
            )

            long_ma = df_sorted["price_numeric"].rolling(window=7).mean()
            fig.add_trace(
                go.Scatter(
                    x=df_sorted["timestamp"],
                    y=long_ma,
                    mode="lines",
                    name="7-Day MA",
                    line=dict(color="#d62728"),
                ),
                row=2,
                col=1,
            )

            # Price volatility
            volatility = df_sorted["price_numeric"].rolling(window=5).std()
            fig.add_trace(
                go.Histogram(
                    x=volatility.dropna(),
                    nbinsx=20,
                    name="Price Volatility",
                    marker_color="#9467bd",
                ),
                row=2,
                col=2,
            )

            fig.update_layout(
                title="Price Trend Analysis", height=600, template=self.config.theme
            )

            return fig

        except Exception as e:
            self.logger.error(f"Error creating trend analysis chart: {e}")
            return go.Figure().add_annotation(
                text=f"Error creating chart: {e}",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )

    def create_comparative_analysis_chart(
        self, data: List[Dict[str, Any]]
    ) -> go.Figure:
        """
        Create an interactive comparative analysis chart.

        Args:
            data: Data to visualize

        Returns:
            Plotly figure object
        """
        try:
            df = pd.DataFrame(data)

            if df.empty:
                return go.Figure().add_annotation(
                    text="No data available for comparative analysis",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                )

            # Clean price data
            if "price" in df.columns:
                df["price_numeric"] = pd.to_numeric(
                    df["price"].str.replace(r"[^\d.]", "", regex=True), errors="coerce"
                )
                df = df.dropna(subset=["price_numeric"])

            if df.empty:
                return go.Figure().add_annotation(
                    text="No valid price data for comparative analysis",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                )

            # Create subplots
            fig = make_subplots(
                rows=2,
                cols=2,
                subplot_titles=(
                    "Price Comparison by Source",
                    "Category Distribution",
                    "Price Range Analysis",
                    "Source Statistics",
                ),
                specs=[
                    [{"type": "box"}, {"type": "pie"}],
                    [{"type": "bar"}, {"type": "table"}],
                ],
            )

            # Price comparison by source
            if "source" in df.columns:
                fig.add_trace(
                    go.Box(
                        x=df["source"],
                        y=df["price_numeric"],
                        name="Price by Source",
                        marker_color="#1f77b4",
                    ),
                    row=1,
                    col=1,
                )

            # Category distribution
            if "category" in df.columns:
                category_counts = df["category"].value_counts()
                fig.add_trace(
                    go.Pie(
                        labels=category_counts.index,
                        values=category_counts.values,
                        name="Category Distribution",
                    ),
                    row=1,
                    col=2,
                )

            # Price range analysis
            df["price_range"] = pd.cut(
                df["price_numeric"],
                bins=5,
                labels=["Very Low", "Low", "Medium", "High", "Very High"],
            )
            range_counts = df["price_range"].value_counts()

            fig.add_trace(
                go.Bar(
                    x=range_counts.index,
                    y=range_counts.values,
                    name="Price Range Distribution",
                    marker_color="#ff7f0e",
                ),
                row=2,
                col=1,
            )

            # Source statistics table
            if "source" in df.columns:
                source_stats = (
                    df.groupby("source")["price_numeric"]
                    .agg(["count", "mean", "median", "std", "min", "max"])
                    .round(2)
                )

                fig.add_trace(
                    go.Table(
                        header=dict(
                            values=["Source"] + list(source_stats.columns),
                            fill_color="#d62728",
                            font=dict(color="white"),
                        ),
                        cells=dict(
                            values=[source_stats.index]
                            + [source_stats[col] for col in source_stats.columns],
                            fill_color="lavender",
                        ),
                    ),
                    row=2,
                    col=2,
                )

            fig.update_layout(
                title="Comparative Analysis", height=600, template=self.config.theme
            )

            return fig

        except Exception as e:
            self.logger.error(f"Error creating comparative analysis chart: {e}")
            return go.Figure().add_annotation(
                text=f"Error creating chart: {e}",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )

    def export_chart(self, fig: go.Figure, filename: str, format: str = "html") -> str:
        """
        Export a chart to a file.

        Args:
            fig: Plotly figure object
            filename: Output filename
            format: Export format ('html', 'png', 'pdf')

        Returns:
            Path to the exported file
        """
        try:
            output_dir = self.data_directory / "visualizations"
            output_dir.mkdir(exist_ok=True)

            file_path = output_dir / f"{filename}.{format}"

            if format == "html":
                fig.write_html(str(file_path))
            elif format == "png":
                fig.write_image(str(file_path))
            elif format == "pdf":
                fig.write_image(str(file_path))
            else:
                raise ValueError(f"Unsupported format: {format}")

            self.logger.info(f"Chart exported to: {file_path}")
            return str(file_path)

        except Exception as e:
            self.logger.error(f"Error exporting chart: {e}")
            return ""

    def get_analysis_recommendations(self, data: List[Dict[str, Any]]) -> List[str]:
        """
        Get intelligent recommendations based on the data.

        Args:
            data: Data to analyze

        Returns:
            List of recommendations
        """
        try:
            if not data:
                return ["No data available for analysis"]

            recommendations = []
            df = pd.DataFrame(data)

            # Price analysis recommendations
            if "price" in df.columns:
                df["price_numeric"] = pd.to_numeric(
                    df["price"].str.replace(r"[^\d.]", "", regex=True), errors="coerce"
                )
                price_data = df["price_numeric"].dropna()

                if len(price_data) > 0:
                    # Price range recommendations
                    price_range = price_data.max() - price_data.min()
                    if price_range > price_data.mean() * 2:
                        recommendations.append(
                            "High price variability detected - consider segmenting by category"
                        )

                    # Outlier recommendations
                    outliers = price_data[
                        abs(price_data - price_data.mean()) > 2 * price_data.std()
                    ]
                    if len(outliers) > len(price_data) * 0.1:
                        recommendations.append(
                            f"Found {len(outliers)} price outliers - verify data quality"
                        )

            # Source analysis recommendations
            if "source" in df.columns:
                source_counts = df["source"].value_counts()
                if len(source_counts) < 2:
                    recommendations.append(
                        "Limited source diversity - consider adding more sources"
                    )
                elif source_counts.iloc[0] > source_counts.sum() * 0.8:
                    recommendations.append(
                        "Data heavily skewed toward one source - diversify sources"
                    )

            # Category analysis recommendations
            if "category" in df.columns:
                category_counts = df["category"].value_counts()
                if len(category_counts) < 3:
                    recommendations.append(
                        "Limited category diversity - expand product categories"
                    )

            # Time-based recommendations
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                date_range = (df["timestamp"].max() - df["timestamp"].min()).days
                if date_range < 7:
                    recommendations.append(
                        "Limited time range - collect data over longer periods"
                    )
                elif date_range > 90:
                    recommendations.append(
                        "Long time range - consider seasonal analysis"
                    )

            # Data quality recommendations
            missing_data = df.isnull().sum().sum()
            if missing_data > len(df) * 0.1:
                recommendations.append(
                    "Significant missing data - improve data collection"
                )

            if not recommendations:
                recommendations.append("Data looks good - continue monitoring")

            return recommendations

        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return ["Error generating recommendations"]

    def create_standalone_html(
        self, data: List[Dict[str, Any]], output_file: str = "dashboard.html"
    ) -> str:
        """
        Create a standalone HTML dashboard file.

        Args:
            data: Data to visualize
            output_file: Output filename

        Returns:
            Path to the created HTML file
        """
        try:
            # Create all charts
            price_chart = self.create_price_distribution_chart(data)
            trend_chart = self.create_trend_analysis_chart(data)
            comp_chart = self.create_comparative_analysis_chart(data)

            # Create HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Dynamic Web Scraper Dashboard</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                    .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; border-radius: 5px; }}
                    .chart-container {{ background-color: white; margin: 20px 0; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .summary {{ background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                    h2 {{ color: #2c3e50; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Dynamic Web Scraper - Interactive Dashboard</h1>
                    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>

                <div class="summary">
                    <h2>Data Summary</h2>
                    <p>Total Items: {len(data)}</p>
                    <p>Sources: {len(set(item.get('source', 'Unknown') for item in data))}</p>
                    <p>Categories: {len(set(item.get('category', 'Unknown') for item in data))}</p>
                </div>

                <div class="chart-container">
                    <h2>Price Distribution Analysis</h2>
                    <div id="price-chart"></div>
                </div>

                <div class="chart-container">
                    <h2>Trend Analysis</h2>
                    <div id="trend-chart"></div>
                </div>

                <div class="chart-container">
                    <h2>Comparative Analysis</h2>
                    <div id="comp-chart"></div>
                </div>

                <script>
                    {price_chart.to_json()}
                    {trend_chart.to_json()}
                    {comp_chart.to_json()}

                    Plotly.newPlot('price-chart', price_chart.data, price_chart.layout);
                    Plotly.newPlot('trend-chart', trend_chart.data, trend_chart.layout);
                    Plotly.newPlot('comp-chart', comp_chart.data, comp_chart.layout);
                </script>
            </body>
            </html>
            """

            # Save HTML file
            output_path = self.data_directory / output_file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            self.logger.info(f"Standalone HTML dashboard created: {output_path}")
            return str(output_path)

        except Exception as e:
            self.logger.error(f"Error creating standalone HTML: {e}")
            return ""
