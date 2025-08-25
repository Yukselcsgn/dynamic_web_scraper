#!/usr/bin/env python3
"""
Data Visualizer Module

This module provides comprehensive data visualization capabilities for the Dynamic Web Scraper,
including charts, graphs, and interactive visualizations for scraped data analysis.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from plotly.subplots import make_subplots

# Set up matplotlib for non-interactive backend
plt.switch_backend("Agg")

# Configure seaborn style
sns.set_theme(style="whitegrid")
sns.set_palette("husl")


class DataVisualizer:
    """
    Comprehensive data visualization system for scraped data analysis.
    """

    def __init__(self, output_directory: str = "data/visualizations"):
        """
        Initialize the data visualizer.

        Args:
            output_directory: Directory to save visualization files
        """
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger("DataVisualizer")

        # Color schemes for different chart types
        self.color_schemes = {
            "primary": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
            "qualitative": ["#e377c2", "#7f7f7f", "#bcbd22", "#17becf"],
            "sequential": ["#f7fbff", "#deebf7", "#c6dbef", "#9ecae1", "#6baed6"],
            "diverging": ["#d73027", "#f46d43", "#fdae61", "#fee08b", "#e6f598"],
        }

    def create_price_distribution_chart(
        self, data: List[Dict[str, Any]], output_file: str = "price_distribution.html"
    ) -> str:
        """
        Create a comprehensive price distribution visualization.

        Args:
            data: List of scraped data items
            output_file: Output file name

        Returns:
            Path to the generated visualization file
        """
        try:
            # Convert to DataFrame
            df = pd.DataFrame(data)

            if df.empty or "price" not in df.columns:
                self.logger.warning("No price data available for visualization")
                return ""

            # Clean price data
            df["price_numeric"] = pd.to_numeric(
                df["price"].str.replace(r"[^\d.]", "", regex=True), errors="coerce"
            )
            df = df.dropna(subset=["price_numeric"])

            if df.empty:
                self.logger.warning("No valid price data after cleaning")
                return ""

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

            # 1. Price Distribution Histogram
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

            # 2. Price by Category (if available)
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

            # 3. Price Box Plot
            fig.add_trace(
                go.Box(
                    y=df["price_numeric"],
                    name="Price Distribution",
                    marker_color="#2ca02c",
                ),
                row=2,
                col=1,
            )

            # 4. Price Statistics Table
            stats = {
                "Metric": [
                    "Count",
                    "Mean",
                    "Median",
                    "Std Dev",
                    "Min",
                    "Max",
                    "Q1",
                    "Q3",
                ],
                "Value": [
                    len(df),
                    f"${df['price_numeric'].mean():.2f}",
                    f"${df['price_numeric'].median():.2f}",
                    f"${df['price_numeric'].std():.2f}",
                    f"${df['price_numeric'].min():.2f}",
                    f"${df['price_numeric'].max():.2f}",
                    f"${df['price_numeric'].quantile(0.25):.2f}",
                    f"${df['price_numeric'].quantile(0.75):.2f}",
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

            # Update layout
            fig.update_layout(
                title="Price Distribution Analysis",
                height=800,
                showlegend=False,
                template="plotly_white",
            )

            # Save the visualization
            output_path = self.output_directory / output_file
            fig.write_html(str(output_path))

            self.logger.info(f"Price distribution chart saved to {output_path}")
            return str(output_path)

        except Exception as e:
            self.logger.error(f"Error creating price distribution chart: {e}")
            return ""

    def create_trend_analysis_chart(
        self, data: List[Dict[str, Any]], output_file: str = "trend_analysis.html"
    ) -> str:
        """
        Create trend analysis visualizations for time-series data.

        Args:
            data: List of scraped data items with timestamps
            output_file: Output file name

        Returns:
            Path to the generated visualization file
        """
        try:
            df = pd.DataFrame(data)

            if df.empty:
                self.logger.warning("No data available for trend analysis")
                return ""

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

            # 1. Price Trends Over Time
            if not df.empty and "price_numeric" in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df["timestamp"],
                        y=df["price_numeric"],
                        mode="lines+markers",
                        name="Price Trend",
                        line=dict(color="#1f77b4", width=2),
                    ),
                    row=1,
                    col=1,
                )

                # Add moving average
                window_size = min(7, len(df) // 4)
                if window_size > 1:
                    moving_avg = df["price_numeric"].rolling(window=window_size).mean()
                    fig.add_trace(
                        go.Scatter(
                            x=df["timestamp"],
                            y=moving_avg,
                            mode="lines",
                            name=f"{window_size}-Day Moving Avg",
                            line=dict(color="#ff7f0e", width=2, dash="dash"),
                        ),
                        row=1,
                        col=1,
                    )

            # 2. Daily Price Changes
            if not df.empty and "price_numeric" in df.columns:
                df_sorted = df.sort_values("timestamp")
                price_changes = df_sorted["price_numeric"].diff().dropna()

                fig.add_trace(
                    go.Bar(
                        x=df_sorted["timestamp"][1:],
                        y=price_changes,
                        name="Daily Price Changes",
                        marker_color=[
                            "green" if x >= 0 else "red" for x in price_changes
                        ],
                    ),
                    row=1,
                    col=2,
                )

            # 3. Moving Averages Comparison
            if not df.empty and "price_numeric" in df.columns:
                df_sorted = df.sort_values("timestamp")

                # Short-term moving average
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

                # Long-term moving average
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

            # 4. Price Volatility
            if not df.empty and "price_numeric" in df.columns:
                # Calculate rolling standard deviation
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

            # Update layout
            fig.update_layout(
                title="Price Trend Analysis", height=800, template="plotly_white"
            )

            # Save the visualization
            output_path = self.output_directory / output_file
            fig.write_html(str(output_path))

            self.logger.info(f"Trend analysis chart saved to {output_path}")
            return str(output_path)

        except Exception as e:
            self.logger.error(f"Error creating trend analysis chart: {e}")
            return ""

    def create_comparative_analysis_chart(
        self, data: List[Dict[str, Any]], output_file: str = "comparative_analysis.html"
    ) -> str:
        """
        Create comparative analysis visualizations across different sources/categories.

        Args:
            data: List of scraped data items
            output_file: Output file name

        Returns:
            Path to the generated visualization file
        """
        try:
            df = pd.DataFrame(data)

            if df.empty:
                self.logger.warning("No data available for comparative analysis")
                return ""

            # Clean price data
            if "price" in df.columns:
                df["price_numeric"] = pd.to_numeric(
                    df["price"].str.replace(r"[^\d.]", "", regex=True), errors="coerce"
                )
                df = df.dropna(subset=["price_numeric"])

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

            # 1. Price Comparison by Source
            if (
                "source" in df.columns
                and not df.empty
                and "price_numeric" in df.columns
            ):
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

            # 2. Category Distribution
            if "category" in df.columns:
                category_counts = df["category"].value_counts()
                fig.add_trace(
                    go.Pie(
                        labels=category_counts.index,
                        values=category_counts.values,
                        name="Category Distribution",
                        marker_colors=self.color_schemes["primary"],
                    ),
                    row=1,
                    col=2,
                )

            # 3. Price Range Analysis
            if not df.empty and "price_numeric" in df.columns:
                # Create price ranges
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

            # 4. Source Statistics Table
            if (
                "source" in df.columns
                and not df.empty
                and "price_numeric" in df.columns
            ):
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

            # Update layout
            fig.update_layout(
                title="Comparative Analysis", height=800, template="plotly_white"
            )

            # Save the visualization
            output_path = self.output_directory / output_file
            fig.write_html(str(output_path))

            self.logger.info(f"Comparative analysis chart saved to {output_path}")
            return str(output_path)

        except Exception as e:
            self.logger.error(f"Error creating comparative analysis chart: {e}")
            return ""

    def create_heatmap_visualization(
        self, data: List[Dict[str, Any]], output_file: str = "price_heatmap.html"
    ) -> str:
        """
        Create a heatmap visualization for price patterns.

        Args:
            data: List of scraped data items
            output_file: Output file name

        Returns:
            Path to the generated visualization file
        """
        try:
            df = pd.DataFrame(data)

            if df.empty:
                self.logger.warning("No data available for heatmap visualization")
                return ""

            # Clean price data
            if "price" in df.columns:
                df["price_numeric"] = pd.to_numeric(
                    df["price"].str.replace(r"[^\d.]", "", regex=True), errors="coerce"
                )
                df = df.dropna(subset=["price_numeric"])

            # Create heatmap data
            if (
                "category" in df.columns
                and "source" in df.columns
                and not df.empty
                and "price_numeric" in df.columns
            ):
                # Pivot table for heatmap
                heatmap_data = df.pivot_table(
                    values="price_numeric",
                    index="category",
                    columns="source",
                    aggfunc="mean",
                ).fillna(0)

                # Create heatmap
                fig = go.Figure(
                    data=go.Heatmap(
                        z=heatmap_data.values,
                        x=heatmap_data.columns,
                        y=heatmap_data.index,
                        colorscale="Viridis",
                        text=heatmap_data.values.round(2),
                        texttemplate="%{text}",
                        textfont={"size": 10},
                        colorbar=dict(title="Average Price"),
                    )
                )

                fig.update_layout(
                    title="Price Heatmap by Category and Source",
                    xaxis_title="Source",
                    yaxis_title="Category",
                    height=600,
                    template="plotly_white",
                )

                # Save the visualization
                output_path = self.output_directory / output_file
                fig.write_html(str(output_path))

                self.logger.info(f"Price heatmap saved to {output_path}")
                return str(output_path)
            else:
                self.logger.warning(
                    "Insufficient data for heatmap (need category and source columns)"
                )
                return ""

        except Exception as e:
            self.logger.error(f"Error creating heatmap visualization: {e}")
            return ""

    def create_summary_dashboard(
        self, data: List[Dict[str, Any]], output_file: str = "summary_dashboard.html"
    ) -> str:
        """
        Create a comprehensive summary dashboard with multiple visualizations.

        Args:
            data: List of scraped data items
            output_file: Output file name

        Returns:
            Path to the generated visualization file
        """
        try:
            df = pd.DataFrame(data)

            if df.empty:
                self.logger.warning("No data available for summary dashboard")
                return ""

            # Clean price data
            if "price" in df.columns:
                df["price_numeric"] = pd.to_numeric(
                    df["price"].str.replace(r"[^\d.]", "", regex=True), errors="coerce"
                )
                df = df.dropna(subset=["price_numeric"])

            # Create comprehensive dashboard
            fig = make_subplots(
                rows=3,
                cols=3,
                subplot_titles=(
                    "Price Distribution",
                    "Category Distribution",
                    "Source Comparison",
                    "Price Trends",
                    "Price Ranges",
                    "Top Categories",
                    "Price Statistics",
                    "Data Quality",
                    "Summary Metrics",
                ),
                specs=[
                    [{"type": "histogram"}, {"type": "pie"}, {"type": "bar"}],
                    [{"type": "scatter"}, {"type": "bar"}, {"type": "bar"}],
                    [{"type": "table"}, {"type": "indicator"}, {"type": "table"}],
                ],
            )

            # 1. Price Distribution
            if not df.empty and "price_numeric" in df.columns:
                fig.add_trace(
                    go.Histogram(
                        x=df["price_numeric"], nbinsx=20, name="Price Distribution"
                    ),
                    row=1,
                    col=1,
                )

            # 2. Category Distribution
            if "category" in df.columns:
                category_counts = df["category"].value_counts().head(10)
                fig.add_trace(
                    go.Pie(labels=category_counts.index, values=category_counts.values),
                    row=1,
                    col=2,
                )

            # 3. Source Comparison
            if (
                "source" in df.columns
                and not df.empty
                and "price_numeric" in df.columns
            ):
                source_avg = (
                    df.groupby("source")["price_numeric"]
                    .mean()
                    .sort_values(ascending=False)
                )
                fig.add_trace(
                    go.Bar(x=source_avg.index, y=source_avg.values), row=1, col=3
                )

            # 4. Price Trends (if timestamp available)
            if (
                "timestamp" in df.columns
                and not df.empty
                and "price_numeric" in df.columns
            ):
                df_sorted = df.sort_values("timestamp")
                fig.add_trace(
                    go.Scatter(
                        x=df_sorted["timestamp"],
                        y=df_sorted["price_numeric"],
                        mode="lines+markers",
                    ),
                    row=2,
                    col=1,
                )

            # 5. Price Ranges
            if not df.empty and "price_numeric" in df.columns:
                df["price_range"] = pd.cut(df["price_numeric"], bins=5)
                range_counts = df["price_range"].value_counts()
                fig.add_trace(
                    go.Bar(x=range_counts.index.astype(str), y=range_counts.values),
                    row=2,
                    col=2,
                )

            # 6. Top Categories by Count
            if "category" in df.columns:
                top_categories = df["category"].value_counts().head(10)
                fig.add_trace(
                    go.Bar(
                        x=top_categories.values, y=top_categories.index, orientation="h"
                    ),
                    row=2,
                    col=3,
                )

            # 7. Price Statistics Table
            if not df.empty and "price_numeric" in df.columns:
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
                        header=dict(values=list(stats.keys())),
                        cells=dict(values=list(stats.values())),
                    ),
                    row=3,
                    col=1,
                )

            # 8. Data Quality Indicator
            total_items = len(df)
            complete_items = len(df.dropna())
            quality_percentage = (
                (complete_items / total_items * 100) if total_items > 0 else 0
            )

            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=quality_percentage,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": "Data Quality (%)"},
                    gauge={
                        "axis": {"range": [None, 100]},
                        "bar": {"color": "darkblue"},
                        "steps": [
                            {"range": [0, 50], "color": "lightgray"},
                            {"range": [50, 80], "color": "yellow"},
                            {"range": [80, 100], "color": "green"},
                        ],
                    },
                ),
                row=3,
                col=2,
            )

            # 9. Summary Metrics Table
            summary_metrics = {
                "Metric": [
                    "Total Items",
                    "Categories",
                    "Sources",
                    "Date Range",
                    "Avg Price",
                ],
                "Value": [
                    len(df),
                    df["category"].nunique() if "category" in df.columns else "N/A",
                    df["source"].nunique() if "source" in df.columns else "N/A",
                    f"{df['timestamp'].min().date() if 'timestamp' in df.columns else 'N/A'} to {df['timestamp'].max().date() if 'timestamp' in df.columns else 'N/A'}",
                    f"${df['price_numeric'].mean():.2f}"
                    if not df.empty and "price_numeric" in df.columns
                    else "N/A",
                ],
            }
            fig.add_trace(
                go.Table(
                    header=dict(values=list(summary_metrics.keys())),
                    cells=dict(values=list(summary_metrics.values())),
                ),
                row=3,
                col=3,
            )

            # Update layout
            fig.update_layout(
                title="Comprehensive Data Analysis Dashboard",
                height=1200,
                showlegend=False,
                template="plotly_white",
            )

            # Save the visualization
            output_path = self.output_directory / output_file
            fig.write_html(str(output_path))

            self.logger.info(f"Summary dashboard saved to {output_path}")
            return str(output_path)

        except Exception as e:
            self.logger.error(f"Error creating summary dashboard: {e}")
            return ""

    def export_visualization_report(
        self, data: List[Dict[str, Any]], output_file: str = "visualization_report.html"
    ) -> str:
        """
        Create a comprehensive visualization report with all charts.

        Args:
            data: List of scraped data items
            output_file: Output file name

        Returns:
            Path to the generated report file
        """
        try:
            # Create all visualizations
            visualizations = {}

            # Price distribution
            price_dist_path = self.create_price_distribution_chart(
                data, "temp_price_dist.html"
            )
            if price_dist_path:
                visualizations["Price Distribution"] = price_dist_path

            # Trend analysis
            trend_path = self.create_trend_analysis_chart(data, "temp_trend.html")
            if trend_path:
                visualizations["Trend Analysis"] = trend_path

            # Comparative analysis
            comp_path = self.create_comparative_analysis_chart(data, "temp_comp.html")
            if comp_path:
                visualizations["Comparative Analysis"] = comp_path

            # Heatmap
            heatmap_path = self.create_heatmap_visualization(data, "temp_heatmap.html")
            if heatmap_path:
                visualizations["Price Heatmap"] = heatmap_path

            # Summary dashboard
            dashboard_path = self.create_summary_dashboard(data, "temp_dashboard.html")
            if dashboard_path:
                visualizations["Summary Dashboard"] = dashboard_path

            # Create report HTML
            report_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Data Visualization Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                    .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                    .visualization {{ margin: 10px 0; }}
                    iframe {{ width: 100%; height: 600px; border: none; }}
                    .stats {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>📊 Data Visualization Report</h1>
                    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>Total data points: {len(data)}</p>
                </div>

                <div class="stats">
                    <h2>📈 Quick Statistics</h2>
                    <p>Number of visualizations created: {len(visualizations)}</p>
                    <p>Data sources: {len(set(item.get('source', 'Unknown') for item in data))}</p>
                    <p>Categories: {len(set(item.get('category', 'Unknown') for item in data))}</p>
                </div>
            """

            # Add each visualization
            for title, path in visualizations.items():
                report_html += f"""
                <div class="section">
                    <h2>{title}</h2>
                    <div class="visualization">
                        <iframe src="{path}"></iframe>
                    </div>
                </div>
                """

            report_html += """
            </body>
            </html>
            """

            # Save the report
            output_path = self.output_directory / output_file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report_html)

            self.logger.info(f"Visualization report saved to {output_path}")
            return str(output_path)

        except Exception as e:
            self.logger.error(f"Error creating visualization report: {e}")
            return ""

    def get_visualization_summary(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get a summary of available visualizations for the data.

        Args:
            data: List of scraped data items

        Returns:
            Dictionary with visualization summary
        """
        df = pd.DataFrame(data)

        summary = {
            "total_items": len(df),
            "available_visualizations": [],
            "data_quality": {},
            "recommendations": [],
        }

        # Check data quality
        if not df.empty:
            summary["data_quality"] = {
                "total_rows": len(df),
                "complete_rows": len(df.dropna()),
                "missing_values": df.isnull().sum().to_dict(),
            }

        # Check what visualizations can be created
        if "price" in df.columns:
            summary["available_visualizations"].append("Price Distribution")
            summary["available_visualizations"].append("Price Trends")
            summary["available_visualizations"].append("Price Heatmap")

        if "category" in df.columns:
            summary["available_visualizations"].append("Category Analysis")

        if "source" in df.columns:
            summary["available_visualizations"].append("Source Comparison")

        if "timestamp" in df.columns:
            summary["available_visualizations"].append("Time Series Analysis")

        # Add recommendations
        if len(df) < 10:
            summary["recommendations"].append(
                "Consider collecting more data for better visualizations"
            )

        if "price" not in df.columns:
            summary["recommendations"].append(
                "Price data would enable price analysis visualizations"
            )

        if "category" not in df.columns:
            summary["recommendations"].append(
                "Category data would enable categorical analysis"
            )

        return summary
