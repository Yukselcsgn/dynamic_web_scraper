#!/usr/bin/env python3
"""
Price Analyzer - Advanced price analysis, trend detection, and statistical insights.
"""
import json
import logging
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt


@dataclass
class PriceAnalysis:
    """Result of price analysis with comprehensive statistics."""

    basic_stats: Dict[str, float]
    price_distribution: Dict[str, Any]
    outliers: List[Dict[str, Any]]
    trends: Dict[str, Any]
    recommendations: List[str]
    analysis_timestamp: str


class PriceAnalyzer:
    """
    Advanced price analysis and trend detection system.
    Provides statistical insights, outlier detection, and trend analysis.
    """

    def __init__(self):
        self.outlier_threshold = 2.0  # Standard deviations for outlier detection
        self.trend_confidence = 0.95  # Confidence level for trend analysis

    def analyze_prices(
        self,
        data: List[Dict[str, Any]],
        category_field: str = "category",
        price_field: str = "normalized_price",
        date_field: str = None,
    ) -> PriceAnalysis:
        """
        Perform comprehensive price analysis on scraped data.

        Args:
            data: List of data dictionaries
            category_field: Field name for category grouping
            price_field: Field name for price values
            date_field: Optional field name for date/time analysis

        Returns:
            PriceAnalysis with comprehensive statistics and insights
        """
        if not data:
            return self._empty_analysis()

        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(data)

        # Filter data with valid prices
        price_df = df[df[price_field].notna() & (df[price_field] > 0)].copy()

        if price_df.empty:
            return self._empty_analysis()

        # Basic statistics
        basic_stats = self._calculate_basic_stats(price_df[price_field])

        # Price distribution analysis
        price_distribution = self._analyze_price_distribution(price_df[price_field])

        # Outlier detection
        outliers = self._detect_outliers(price_df, price_field)

        # Trend analysis (if date field is available)
        trends = {}
        if date_field and date_field in price_df.columns:
            trends = self._analyze_trends(price_df, price_field, date_field)

        # Category-based analysis
        category_analysis = self._analyze_by_category(
            price_df, category_field, price_field
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            basic_stats, price_distribution, outliers, trends, category_analysis
        )

        return PriceAnalysis(
            basic_stats=basic_stats,
            price_distribution=price_distribution,
            outliers=outliers,
            trends=trends,
            recommendations=recommendations,
            analysis_timestamp=datetime.now().isoformat(),
        )

    def _calculate_basic_stats(self, prices: pd.Series) -> Dict[str, float]:
        """Calculate basic statistical measures."""
        stats_dict = {
            "count": len(prices),
            "mean": float(prices.mean()),
            "median": float(prices.median()),
            "std": float(prices.std()),
            "min": float(prices.min()),
            "max": float(prices.max()),
            "q25": float(prices.quantile(0.25)),
            "q75": float(prices.quantile(0.75)),
            "iqr": float(prices.quantile(0.75) - prices.quantile(0.25)),
            "skewness": float(stats.skew(prices)),
            "kurtosis": float(stats.kurtosis(prices)),
        }

        # Calculate coefficient of variation
        if stats_dict["mean"] > 0:
            stats_dict["cv"] = stats_dict["std"] / stats_dict["mean"]
        else:
            stats_dict["cv"] = 0.0

        return stats_dict

    def _analyze_price_distribution(self, prices: pd.Series) -> Dict[str, Any]:
        """Analyze price distribution characteristics."""
        distribution = {
            "histogram": self._create_histogram_data(prices),
            "percentiles": self._calculate_percentiles(prices),
            "price_ranges": self._analyze_price_ranges(prices),
            "distribution_type": self._classify_distribution(prices),
        }

        return distribution

    def _create_histogram_data(self, prices: pd.Series) -> Dict[str, Any]:
        """Create histogram data for visualization."""
        hist, bins = np.histogram(prices, bins=20)

        return {
            "counts": hist.tolist(),
            "bin_edges": bins.tolist(),
            "bin_centers": [(bins[i] + bins[i + 1]) / 2 for i in range(len(bins) - 1)],
        }

    def _calculate_percentiles(self, prices: pd.Series) -> Dict[str, float]:
        """Calculate various percentiles."""
        percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
        return {f"p{p}": float(prices.quantile(p / 100)) for p in percentiles}

    def _analyze_price_ranges(self, prices: pd.Series) -> Dict[str, Any]:
        """Analyze price ranges and segments."""
        q25, q75 = prices.quantile([0.25, 0.75])
        iqr = q75 - q25

        ranges = {
            "low": float(prices.min()),
            "q25": float(q25),
            "median": float(prices.median()),
            "q75": float(q75),
            "high": float(prices.max()),
            "iqr": float(iqr),
        }

        # Price segments
        segments = {
            "budget": f"${ranges['low']:.2f} - ${ranges['q25']:.2f}",
            "mid_range": f"${ranges['q25']:.2f} - ${ranges['q75']:.2f}",
            "premium": f"${ranges['q75']:.2f} - ${ranges['high']:.2f}",
        }

        ranges["segments"] = segments
        return ranges

    def _classify_distribution(self, prices: pd.Series) -> str:
        """Classify the type of price distribution."""
        skewness = stats.skew(prices)
        kurtosis = stats.kurtosis(prices)

        if abs(skewness) < 0.5:
            if abs(kurtosis) < 1:
                return "normal"
            else:
                return "normal_with_outliers"
        elif skewness > 0.5:
            return "right_skewed"
        else:
            return "left_skewed"

    def _detect_outliers(
        self, df: pd.DataFrame, price_field: str
    ) -> List[Dict[str, Any]]:
        """Detect price outliers using multiple methods."""
        outliers = []
        prices = df[price_field]

        # Method 1: Z-score method
        z_scores = np.abs(stats.zscore(prices))
        z_outliers = df[z_scores > self.outlier_threshold]

        # Method 2: IQR method
        q1, q3 = prices.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        iqr_outliers = df[(prices < lower_bound) | (prices > upper_bound)]

        # Combine outliers
        all_outliers = pd.concat([z_outliers, iqr_outliers]).drop_duplicates()

        for _, row in all_outliers.iterrows():
            outlier_info = {
                "index": int(row.name),
                "price": float(row[price_field]),
                "title": str(row.get("title", row.get("name", "Unknown"))),
                "category": str(row.get("category", "Unknown")),
                "z_score": (
                    float(z_scores[row.name]) if row.name in z_scores.index else 0
                ),
                "is_iqr_outlier": row.name in iqr_outliers.index,
                "outlier_type": self._classify_outlier(row[price_field], prices),
            }
            outliers.append(outlier_info)

        return outliers

    def _classify_outlier(self, price: float, all_prices: pd.Series) -> str:
        """Classify the type of outlier."""
        median = all_prices.median()

        if price > median * 3:
            return "extreme_high"
        elif price > median * 2:
            return "high"
        elif price < median * 0.3:
            return "extreme_low"
        elif price < median * 0.5:
            return "low"
        else:
            return "moderate"

    def _analyze_trends(
        self, df: pd.DataFrame, price_field: str, date_field: str
    ) -> Dict[str, Any]:
        """Analyze price trends over time."""
        trends = {}

        try:
            # Convert date field to datetime
            df[date_field] = pd.to_datetime(df[date_field], errors="coerce")
            df = df.dropna(subset=[date_field])

            if len(df) < 3:
                return trends

            # Sort by date
            df_sorted = df.sort_values(date_field)

            # Calculate moving averages
            window_sizes = [3, 7, 14]
            for window in window_sizes:
                if len(df_sorted) >= window:
                    df_sorted[f"ma_{window}"] = (
                        df_sorted[price_field].rolling(window=window).mean()
                    )

            # Linear trend analysis
            x = np.arange(len(df_sorted))
            y = df_sorted[price_field].values

            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

            trends["linear_trend"] = {
                "slope": float(slope),
                "intercept": float(intercept),
                "r_squared": float(r_value**2),
                "p_value": float(p_value),
                "trend_direction": "increasing" if slope > 0 else "decreasing",
                "trend_significance": p_value < (1 - self.trend_confidence),
            }

            # Price volatility
            price_changes = df_sorted[price_field].pct_change().dropna()
            trends["volatility"] = {
                "std_dev": float(price_changes.std()),
                "max_change": float(price_changes.max()),
                "min_change": float(price_changes.min()),
                "volatility_score": float(price_changes.std() * 100),
            }

        except Exception as e:
            logging.warning(f"Error analyzing trends: {e}")

        return trends

    def _analyze_by_category(
        self, df: pd.DataFrame, category_field: str, price_field: str
    ) -> Dict[str, Any]:
        """Analyze prices by category."""
        if category_field not in df.columns:
            return {}

        category_analysis = {}

        for category in df[category_field].unique():
            if pd.isna(category):
                continue

            category_data = df[df[category_field] == category]
            if len(category_data) < 2:
                continue

            category_analysis[category] = {
                "count": len(category_data),
                "mean_price": float(category_data[price_field].mean()),
                "median_price": float(category_data[price_field].median()),
                "std_price": float(category_data[price_field].std()),
                "min_price": float(category_data[price_field].min()),
                "max_price": float(category_data[price_field].max()),
                "price_range": float(
                    category_data[price_field].max() - category_data[price_field].min()
                ),
            }

        return category_analysis

    def _generate_recommendations(
        self,
        basic_stats: Dict[str, float],
        price_distribution: Dict[str, Any],
        outliers: List[Dict[str, Any]],
        trends: Dict[str, Any],
        category_analysis: Dict[str, Any],
    ) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []

        # Price range recommendations
        if basic_stats["cv"] > 0.5:
            recommendations.append(
                "High price variability detected. Consider segmenting products by price range."
            )

        if basic_stats["skewness"] > 1:
            recommendations.append(
                "Prices are right-skewed. Focus on premium market segments."
            )
        elif basic_stats["skewness"] < -1:
            recommendations.append(
                "Prices are left-skewed. Consider budget-friendly options."
            )

        # Outlier recommendations
        if outliers:
            outlier_count = len(outliers)
            if outlier_count > len(outliers) * 0.1:
                recommendations.append(
                    f"High number of outliers ({outlier_count}). Review pricing strategy."
                )

            extreme_outliers = [
                o
                for o in outliers
                if o["outlier_type"] in ["extreme_high", "extreme_low"]
            ]
            if extreme_outliers:
                recommendations.append(
                    f"Found {len(extreme_outliers)} extreme outliers. Investigate for errors or special cases."
                )

        # Trend recommendations
        if trends.get("linear_trend"):
            trend = trends["linear_trend"]
            if trend["trend_significance"]:
                if trend["trend_direction"] == "increasing":
                    recommendations.append(
                        "Significant upward price trend detected. Consider early purchasing."
                    )
                else:
                    recommendations.append(
                        "Significant downward price trend detected. Consider waiting for better prices."
                    )

        # Category recommendations
        if category_analysis:
            categories = list(category_analysis.keys())
            if len(categories) > 1:
                price_means = [
                    (cat, data["mean_price"]) for cat, data in category_analysis.items()
                ]
                price_means.sort(key=lambda x: x[1])

                recommendations.append(
                    f"Price comparison across categories: {price_means[0][0]} (${price_means[0][1]:.2f}) to {price_means[-1][0]} (${price_means[-1][1]:.2f})"
                )

        # Data quality recommendations
        if basic_stats["count"] < 10:
            recommendations.append(
                "Limited data available. Consider collecting more samples for reliable analysis."
            )

        return recommendations

    def _empty_analysis(self) -> PriceAnalysis:
        """Return empty analysis when no data is available."""
        return PriceAnalysis(
            basic_stats={},
            price_distribution={},
            outliers=[],
            trends={},
            recommendations=["No price data available for analysis."],
            analysis_timestamp=datetime.now().isoformat(),
        )

    def create_visualizations(
        self, analysis: PriceAnalysis, save_path: str = None
    ) -> Dict[str, str]:
        """Create and save price analysis visualizations."""
        if not analysis.basic_stats:
            return {}

        plots = {}

        try:
            # Set style
            plt.style.use("seaborn-v0_8")

            # 1. Price Distribution Histogram
            if analysis.price_distribution.get("histogram"):
                fig, ax = plt.subplots(figsize=(10, 6))
                hist_data = analysis.price_distribution["histogram"]
                ax.hist(
                    hist_data["bin_centers"],
                    bins=hist_data["bin_edges"],
                    weights=hist_data["counts"],
                    alpha=0.7,
                    edgecolor="black",
                )
                ax.set_title("Price Distribution")
                ax.set_xlabel("Price")
                ax.set_ylabel("Frequency")

                if save_path:
                    plot_path = f"{save_path}_distribution.png"
                    plt.savefig(plot_path, dpi=300, bbox_inches="tight")
                    plots["distribution"] = plot_path
                plt.close()

            # 2. Box Plot (if outliers exist)
            if analysis.outliers:
                fig, ax = plt.subplots(figsize=(10, 6))
                prices = [outlier["price"] for outlier in analysis.outliers]
                ax.boxplot(prices)
                ax.set_title("Price Outliers")
                ax.set_ylabel("Price")

                if save_path:
                    plot_path = f"{save_path}_outliers.png"
                    plt.savefig(plot_path, dpi=300, bbox_inches="tight")
                    plots["outliers"] = plot_path
                plt.close()

            # 3. Category Comparison (if available)
            if hasattr(analysis, "category_analysis") and analysis.category_analysis:
                fig, ax = plt.subplots(figsize=(12, 6))
                categories = list(analysis.category_analysis.keys())
                means = [
                    analysis.category_analysis[cat]["mean_price"] for cat in categories
                ]

                ax.bar(categories, means)
                ax.set_title("Average Price by Category")
                ax.set_xlabel("Category")
                ax.set_ylabel("Average Price")
                plt.xticks(rotation=45)

                if save_path:
                    plot_path = f"{save_path}_categories.png"
                    plt.savefig(plot_path, dpi=300, bbox_inches="tight")
                    plots["categories"] = plot_path
                plt.close()

        except Exception as e:
            logging.error(f"Error creating visualizations: {e}")

        return plots

    def export_analysis(
        self, analysis: PriceAnalysis, format: str = "json", filename: str = None
    ) -> str:
        """Export analysis results to various formats."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"price_analysis_{timestamp}.{format}"

        if format.lower() == "json":
            with open(filename, "w") as f:
                json.dump(
                    {
                        "basic_stats": analysis.basic_stats,
                        "price_distribution": analysis.price_distribution,
                        "outliers": analysis.outliers,
                        "trends": analysis.trends,
                        "recommendations": analysis.recommendations,
                        "analysis_timestamp": analysis.analysis_timestamp,
                    },
                    f,
                    indent=2,
                    default=str,
                )

        elif format.lower() == "csv":
            # Export basic stats
            stats_df = pd.DataFrame([analysis.basic_stats])
            stats_df.to_csv(filename.replace(".csv", "_stats.csv"), index=False)

            # Export outliers
            if analysis.outliers:
                outliers_df = pd.DataFrame(analysis.outliers)
                outliers_df.to_csv(
                    filename.replace(".csv", "_outliers.csv"), index=False
                )

        return filename
