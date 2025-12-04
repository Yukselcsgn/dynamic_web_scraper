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
Time Series Analyzer Module

This module provides comprehensive time series analysis capabilities for the Dynamic Web Scraper,
including trend detection, seasonality analysis, price prediction, and anomaly detection.
"""

import json
import logging
import warnings
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import detrend

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")


@dataclass
class TrendAnalysis:
    """Results of trend analysis."""

    trend_direction: str  # 'increasing', 'decreasing', 'stable'
    trend_strength: float  # 0-1, how strong the trend is
    slope: float  # Linear regression slope
    r_squared: float  # R-squared value
    p_value: float  # Statistical significance
    confidence_interval: Tuple[float, float]  # 95% confidence interval
    trend_period: str  # Time period analyzed


@dataclass
class SeasonalityAnalysis:
    """Results of seasonality analysis."""

    has_seasonality: bool
    seasonal_period: Optional[int]  # Days, weeks, months
    seasonal_strength: float  # 0-1, how strong seasonality is
    seasonal_pattern: Dict[str, float]  # Pattern by time unit
    decomposition: Dict[str, List[float]]  # Trend, seasonal, residual


@dataclass
class AnomalyDetection:
    """Results of anomaly detection."""

    anomalies: List[Dict[str, Any]]  # List of detected anomalies
    anomaly_count: int
    anomaly_percentage: float
    detection_method: str
    thresholds: Dict[str, float]


@dataclass
class PricePrediction:
    """Results of price prediction."""

    predicted_prices: List[float]
    confidence_intervals: List[Tuple[float, float]]
    prediction_horizon: int  # Days ahead
    model_accuracy: float
    model_type: str


class TimeSeriesAnalyzer:
    """
    Comprehensive time series analysis system for price data.
    """

    def __init__(self, data_directory: str = "data/time_series"):
        """
        Initialize the time series analyzer.

        Args:
            data_directory: Directory to store time series data
        """
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger("TimeSeriesAnalyzer")

        # Analysis parameters
        self.min_data_points = 10
        self.default_prediction_horizon = 30  # days
        self.anomaly_threshold = 2.0  # standard deviations

    def prepare_time_series_data(
        self, data: List[Dict[str, Any]], product_id: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Prepare time series data from scraped data.

        Args:
            data: List of scraped data items
            product_id: Optional product identifier for filtering

        Returns:
            Prepared DataFrame with time series data
        """
        try:
            df = pd.DataFrame(data)

            if df.empty:
                self.logger.warning("No data provided for time series analysis")
                return pd.DataFrame()

            # Clean and prepare data
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
            else:
                # Add current timestamp if not present
                df["timestamp"] = datetime.now()

            # Clean price data
            if "price" in df.columns:
                df["price_numeric"] = pd.to_numeric(
                    df["price"].str.replace(r"[^\d.]", "", regex=True), errors="coerce"
                )
                df = df.dropna(subset=["price_numeric"])

            # Filter by product if specified
            if product_id and "product_id" in df.columns:
                df = df[df["product_id"] == product_id]

            # Sort by timestamp
            df = df.sort_values("timestamp")

            # Remove duplicates based on timestamp
            df = df.drop_duplicates(subset=["timestamp"])

            # Set timestamp as index
            df.set_index("timestamp", inplace=True)

            # Resample to daily frequency and forward fill missing values
            if len(df) > 1:
                df = df.resample("D").ffill()

            self.logger.info(f"Prepared time series data: {len(df)} data points")
            return df

        except Exception as e:
            self.logger.error(f"Error preparing time series data: {e}")
            return pd.DataFrame()

    def detect_trends(self, df: pd.DataFrame, window: int = 7) -> TrendAnalysis:
        """
        Detect trends in time series data.

        Args:
            df: DataFrame with time series data
            window: Rolling window size for trend analysis

        Returns:
            TrendAnalysis object with trend information
        """
        try:
            if df.empty or "price_numeric" not in df.columns:
                return TrendAnalysis(
                    trend_direction="unknown",
                    trend_strength=0.0,
                    slope=0.0,
                    r_squared=0.0,
                    p_value=1.0,
                    confidence_interval=(0.0, 0.0),
                    trend_period=f"{len(df)} days",
                )

            prices = df["price_numeric"].dropna()

            if len(prices) < self.min_data_points:
                self.logger.warning(
                    f"Insufficient data points for trend analysis: {len(prices)}"
                )
                return TrendAnalysis(
                    trend_direction="insufficient_data",
                    trend_strength=0.0,
                    slope=0.0,
                    r_squared=0.0,
                    p_value=1.0,
                    confidence_interval=(0.0, 0.0),
                    trend_period=f"{len(prices)} days",
                )

            # Calculate rolling mean for trend smoothing
            rolling_mean = prices.rolling(window=window, min_periods=1).mean()

            # Linear regression for trend analysis
            x = np.arange(len(prices))
            y = prices.values

            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            r_squared = r_value**2

            # Determine trend direction and strength
            if abs(slope) < 0.01:  # Very small slope
                trend_direction = "stable"
                trend_strength = 0.0
            elif slope > 0:
                trend_direction = "increasing"
                trend_strength = min(abs(slope) / prices.std() * 10, 1.0)
            else:
                trend_direction = "decreasing"
                trend_strength = min(abs(slope) / prices.std() * 10, 1.0)

            # Calculate confidence interval
            confidence_interval = (slope - 1.96 * std_err, slope + 1.96 * std_err)

            trend_analysis = TrendAnalysis(
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                slope=slope,
                r_squared=r_squared,
                p_value=p_value,
                confidence_interval=confidence_interval,
                trend_period=f"{len(prices)} days",
            )

            self.logger.info(
                f"Trend analysis completed: {trend_direction} trend (strength: {trend_strength:.2f})"
            )
            return trend_analysis

        except Exception as e:
            self.logger.error(f"Error in trend detection: {e}")
            return TrendAnalysis(
                trend_direction="error",
                trend_strength=0.0,
                slope=0.0,
                r_squared=0.0,
                p_value=1.0,
                confidence_interval=(0.0, 0.0),
                trend_period="error",
            )

    def analyze_seasonality(
        self, df: pd.DataFrame, period: Optional[int] = None
    ) -> SeasonalityAnalysis:
        """
        Analyze seasonality in time series data.

        Args:
            df: DataFrame with time series data
            period: Expected seasonal period (days)

        Returns:
            SeasonalityAnalysis object with seasonality information
        """
        try:
            if df.empty or "price_numeric" not in df.columns:
                return SeasonalityAnalysis(
                    has_seasonality=False,
                    seasonal_period=None,
                    seasonal_strength=0.0,
                    seasonal_pattern={},
                    decomposition={"trend": [], "seasonal": [], "residual": []},
                )

            prices = df["price_numeric"].dropna()

            if len(prices) < 30:  # Need sufficient data for seasonality analysis
                return SeasonalityAnalysis(
                    has_seasonality=False,
                    seasonal_period=None,
                    seasonal_strength=0.0,
                    seasonal_pattern={},
                    decomposition={"trend": [], "seasonal": [], "residual": []},
                )

            # Simple seasonality detection using autocorrelation
            autocorr = np.correlate(prices.values, prices.values, mode="full")
            autocorr = autocorr[len(autocorr) // 2 :]

            # Find peaks in autocorrelation (potential seasonal periods)
            peaks = []
            for i in range(1, len(autocorr) - 1):
                if autocorr[i] > autocorr[i - 1] and autocorr[i] > autocorr[i + 1]:
                    peaks.append(i)

            # Determine seasonal period
            if period:
                seasonal_period = period
            elif peaks:
                seasonal_period = peaks[0]  # First significant peak
            else:
                seasonal_period = None

            # Calculate seasonal strength
            if seasonal_period and seasonal_period < len(prices):
                seasonal_values = []
                for i in range(seasonal_period):
                    seasonal_values.append(prices.iloc[i::seasonal_period].mean())

                seasonal_strength = np.std(seasonal_values) / prices.std()
                has_seasonality = seasonal_strength > 0.1

                # Create seasonal pattern
                seasonal_pattern = {
                    f"period_{i}": val for i, val in enumerate(seasonal_values)
                }
            else:
                seasonal_strength = 0.0
                has_seasonality = False
                seasonal_pattern = {}

            # Simple decomposition (trend, seasonal, residual)
            if has_seasonality and seasonal_period:
                # Trend component (rolling mean)
                trend = prices.rolling(window=seasonal_period, center=True).mean()

                # Seasonal component
                seasonal = np.tile(
                    seasonal_values, len(prices) // len(seasonal_values) + 1
                )[: len(prices)]
                seasonal = pd.Series(seasonal, index=prices.index)

                # Residual component
                residual = prices - trend - seasonal
            else:
                trend = prices.rolling(window=7, center=True).mean()
                seasonal = pd.Series(0, index=prices.index)
                residual = prices - trend

            decomposition = {
                "trend": trend.dropna().tolist(),
                "seasonal": seasonal.dropna().tolist(),
                "residual": residual.dropna().tolist(),
            }

            seasonality_analysis = SeasonalityAnalysis(
                has_seasonality=has_seasonality,
                seasonal_period=seasonal_period,
                seasonal_strength=seasonal_strength,
                seasonal_pattern=seasonal_pattern,
                decomposition=decomposition,
            )

            self.logger.info(
                f"Seasonality analysis completed: {'Has' if has_seasonality else 'No'} seasonality"
            )
            return seasonality_analysis

        except Exception as e:
            self.logger.error(f"Error in seasonality analysis: {e}")
            return SeasonalityAnalysis(
                has_seasonality=False,
                seasonal_period=None,
                seasonal_strength=0.0,
                seasonal_pattern={},
                decomposition={"trend": [], "seasonal": [], "residual": []},
            )

    def detect_anomalies(
        self,
        df: pd.DataFrame,
        method: str = "zscore",
        threshold: Optional[float] = None,
    ) -> AnomalyDetection:
        """
        Detect anomalies in time series data.

        Args:
            df: DataFrame with time series data
            method: Detection method ('zscore', 'iqr', 'isolation_forest')
            threshold: Custom threshold for anomaly detection

        Returns:
            AnomalyDetection object with anomaly information
        """
        try:
            if df.empty or "price_numeric" not in df.columns:
                return AnomalyDetection(
                    anomalies=[],
                    anomaly_count=0,
                    anomaly_percentage=0.0,
                    detection_method=method,
                    thresholds={},
                )

            prices = df["price_numeric"].dropna()

            if len(prices) < 5:
                return AnomalyDetection(
                    anomalies=[],
                    anomaly_count=0,
                    anomaly_percentage=0.0,
                    detection_method=method,
                    thresholds={},
                )

            anomalies = []
            thresholds = {}

            if method == "zscore":
                # Z-score method
                z_scores = np.abs(stats.zscore(prices))
                threshold_val = threshold or self.anomaly_threshold
                thresholds["zscore_threshold"] = threshold_val

                anomaly_indices = np.where(z_scores > threshold_val)[0]

                for idx in anomaly_indices:
                    anomalies.append(
                        {
                            "timestamp": prices.index[idx],
                            "price": prices.iloc[idx],
                            "z_score": z_scores[idx],
                            "method": "zscore",
                            "severity": "high"
                            if z_scores[idx] > threshold_val * 1.5
                            else "medium",
                        }
                    )

            elif method == "iqr":
                # Interquartile Range method
                Q1 = prices.quantile(0.25)
                Q3 = prices.quantile(0.75)
                IQR = Q3 - Q1

                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                thresholds["lower_bound"] = lower_bound
                thresholds["upper_bound"] = upper_bound

                anomaly_indices = np.where(
                    (prices < lower_bound) | (prices > upper_bound)
                )[0]

                for idx in anomaly_indices:
                    price_val = prices.iloc[idx]
                    severity = (
                        "high"
                        if abs(price_val - prices.median()) > 2 * IQR
                        else "medium"
                    )

                    anomalies.append(
                        {
                            "timestamp": prices.index[idx],
                            "price": price_val,
                            "method": "iqr",
                            "severity": severity,
                            "deviation": abs(price_val - prices.median()),
                        }
                    )

            elif method == "rolling_stats":
                # Rolling statistics method
                window = min(30, len(prices) // 3)
                rolling_mean = prices.rolling(window=window, center=True).mean()
                rolling_std = prices.rolling(window=window, center=True).std()

                threshold_val = threshold or 2.0
                thresholds["rolling_threshold"] = threshold_val

                upper_bound = rolling_mean + threshold_val * rolling_std
                lower_bound = rolling_mean - threshold_val * rolling_std

                anomaly_indices = np.where(
                    (prices > upper_bound) | (prices < lower_bound)
                )[0]

                for idx in anomaly_indices:
                    price_val = prices.iloc[idx]
                    mean_val = rolling_mean.iloc[idx]
                    std_val = rolling_std.iloc[idx]

                    z_score = abs(price_val - mean_val) / std_val if std_val > 0 else 0
                    severity = "high" if z_score > threshold_val * 1.5 else "medium"

                    anomalies.append(
                        {
                            "timestamp": prices.index[idx],
                            "price": price_val,
                            "method": "rolling_stats",
                            "severity": severity,
                            "z_score": z_score,
                            "rolling_mean": mean_val,
                        }
                    )

            anomaly_count = len(anomalies)
            anomaly_percentage = (anomaly_count / len(prices)) * 100

            anomaly_detection = AnomalyDetection(
                anomalies=anomalies,
                anomaly_count=anomaly_count,
                anomaly_percentage=anomaly_percentage,
                detection_method=method,
                thresholds=thresholds,
            )

            self.logger.info(
                f"Anomaly detection completed: {anomaly_count} anomalies found ({anomaly_percentage:.1f}%)"
            )
            return anomaly_detection

        except Exception as e:
            self.logger.error(f"Error in anomaly detection: {e}")
            return AnomalyDetection(
                anomalies=[],
                anomaly_count=0,
                anomaly_percentage=0.0,
                detection_method=method,
                thresholds={},
            )

    def predict_prices(
        self, df: pd.DataFrame, horizon: int = None, method: str = "linear"
    ) -> PricePrediction:
        """
        Predict future prices using time series forecasting.

        Args:
            df: DataFrame with time series data
            horizon: Prediction horizon in days
            method: Prediction method ('linear', 'exponential', 'moving_average')

        Returns:
            PricePrediction object with prediction results
        """
        try:
            if df.empty or "price_numeric" not in df.columns:
                return PricePrediction(
                    predicted_prices=[],
                    confidence_intervals=[],
                    prediction_horizon=horizon or self.default_prediction_horizon,
                    model_accuracy=0.0,
                    model_type=method,
                )

            prices = df["price_numeric"].dropna()
            horizon = horizon or self.default_prediction_horizon

            if len(prices) < self.min_data_points:
                return PricePrediction(
                    predicted_prices=[],
                    confidence_intervals=[],
                    prediction_horizon=horizon,
                    model_accuracy=0.0,
                    model_type=method,
                )

            predicted_prices = []
            confidence_intervals = []

            if method == "linear":
                # Linear regression prediction
                x = np.arange(len(prices))
                y = prices.values

                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

                # Predict future values
                future_x = np.arange(len(prices), len(prices) + horizon)
                future_prices = slope * future_x + intercept

                predicted_prices = future_prices.tolist()

                # Calculate confidence intervals
                for i, pred in enumerate(predicted_prices):
                    # Simple confidence interval based on standard error
                    ci_width = (
                        1.96
                        * std_err
                        * np.sqrt(
                            1
                            + 1 / len(prices)
                            + (future_x[i] - np.mean(x)) ** 2
                            / np.sum((x - np.mean(x)) ** 2)
                        )
                    )
                    confidence_intervals.append((pred - ci_width, pred + ci_width))

                model_accuracy = r_value**2

            elif method == "exponential":
                # Exponential smoothing
                alpha = 0.3  # Smoothing parameter
                last_price = prices.iloc[-1]

                for i in range(horizon):
                    if i == 0:
                        pred = last_price
                    else:
                        pred = alpha * last_price + (1 - alpha) * predicted_prices[-1]

                    predicted_prices.append(pred)

                    # Simple confidence interval
                    std_dev = prices.std()
                    confidence_intervals.append(
                        (pred - 1.96 * std_dev, pred + 1.96 * std_dev)
                    )

                model_accuracy = 0.7  # Placeholder accuracy

            elif method == "moving_average":
                # Moving average prediction
                window = min(7, len(prices) // 2)
                ma = prices.rolling(window=window).mean()
                last_ma = ma.iloc[-1]

                # Simple moving average prediction
                for i in range(horizon):
                    predicted_prices.append(last_ma)

                    # Confidence interval based on historical volatility
                    std_dev = prices.std()
                    confidence_intervals.append(
                        (last_ma - 1.96 * std_dev, last_ma + 1.96 * std_dev)
                    )

                model_accuracy = 0.6  # Placeholder accuracy

            else:
                # Default to linear method
                return self.predict_prices(df, horizon, "linear")

            price_prediction = PricePrediction(
                predicted_prices=predicted_prices,
                confidence_intervals=confidence_intervals,
                prediction_horizon=horizon,
                model_accuracy=model_accuracy,
                model_type=method,
            )

            self.logger.info(
                f"Price prediction completed: {horizon} days ahead using {method} method"
            )
            return price_prediction

        except Exception as e:
            self.logger.error(f"Error in price prediction: {e}")
            return PricePrediction(
                predicted_prices=[],
                confidence_intervals=[],
                prediction_horizon=horizon or self.default_prediction_horizon,
                model_accuracy=0.0,
                model_type=method,
            )

    def comprehensive_analysis(
        self, data: List[Dict[str, Any]], product_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive time series analysis.

        Args:
            data: List of scraped data items
            product_id: Optional product identifier

        Returns:
            Dictionary with all analysis results
        """
        try:
            # Prepare data
            df = self.prepare_time_series_data(data, product_id)

            if df.empty:
                return {
                    "error": "No valid data for analysis",
                    "timestamp": datetime.now().isoformat(),
                }

            # Perform all analyses
            trend_analysis = self.detect_trends(df)
            seasonality_analysis = self.analyze_seasonality(df)
            anomaly_detection = self.detect_anomalies(df)
            price_prediction = self.predict_prices(df)

            # Compile results
            analysis_results = {
                "timestamp": datetime.now().isoformat(),
                "data_summary": {
                    "total_points": len(df),
                    "date_range": {
                        "start": df.index.min().isoformat(),
                        "end": df.index.max().isoformat(),
                    },
                    "price_stats": {
                        "mean": float(df["price_numeric"].mean()),
                        "median": float(df["price_numeric"].median()),
                        "std": float(df["price_numeric"].std()),
                        "min": float(df["price_numeric"].min()),
                        "max": float(df["price_numeric"].max()),
                    },
                },
                "trend_analysis": {
                    "trend_direction": trend_analysis.trend_direction,
                    "trend_strength": trend_analysis.trend_strength,
                    "slope": trend_analysis.slope,
                    "r_squared": trend_analysis.r_squared,
                    "p_value": trend_analysis.p_value,
                    "confidence_interval": trend_analysis.confidence_interval,
                    "trend_period": trend_analysis.trend_period,
                },
                "seasonality_analysis": {
                    "has_seasonality": seasonality_analysis.has_seasonality,
                    "seasonal_period": seasonality_analysis.seasonal_period,
                    "seasonal_strength": seasonality_analysis.seasonal_strength,
                    "seasonal_pattern": seasonality_analysis.seasonal_pattern,
                },
                "anomaly_detection": {
                    "anomaly_count": anomaly_detection.anomaly_count,
                    "anomaly_percentage": anomaly_detection.anomaly_percentage,
                    "detection_method": anomaly_detection.detection_method,
                    "anomalies": anomaly_detection.anomalies[:10],  # Limit to first 10
                },
                "price_prediction": {
                    "predicted_prices": price_prediction.predicted_prices,
                    "confidence_intervals": price_prediction.confidence_intervals,
                    "prediction_horizon": price_prediction.prediction_horizon,
                    "model_accuracy": price_prediction.model_accuracy,
                    "model_type": price_prediction.model_type,
                },
                "recommendations": self._generate_recommendations(
                    trend_analysis, seasonality_analysis, anomaly_detection
                ),
            }

            # Save analysis results
            self._save_analysis_results(analysis_results, product_id)

            self.logger.info("Comprehensive time series analysis completed")
            return analysis_results

        except Exception as e:
            self.logger.error(f"Error in comprehensive analysis: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def _generate_recommendations(
        self,
        trend_analysis: TrendAnalysis,
        seasonality_analysis: SeasonalityAnalysis,
        anomaly_detection: AnomalyDetection,
    ) -> List[str]:
        """Generate recommendations based on analysis results."""
        recommendations = []

        # Trend-based recommendations
        if trend_analysis.trend_direction == "increasing":
            if trend_analysis.trend_strength > 0.7:
                recommendations.append(
                    "Strong upward trend detected - consider buying soon"
                )
            else:
                recommendations.append(
                    "Moderate upward trend - monitor for better opportunities"
                )
        elif trend_analysis.trend_direction == "decreasing":
            if trend_analysis.trend_strength > 0.7:
                recommendations.append(
                    "Strong downward trend - wait for price stabilization"
                )
            else:
                recommendations.append("Moderate downward trend - good time to buy")

        # Seasonality-based recommendations
        if seasonality_analysis.has_seasonality:
            recommendations.append(
                f"Seasonal pattern detected (period: {seasonality_analysis.seasonal_period} days)"
            )
            if seasonality_analysis.seasonal_strength > 0.5:
                recommendations.append(
                    "Strong seasonality - plan purchases around seasonal lows"
                )

        # Anomaly-based recommendations
        if anomaly_detection.anomaly_count > 0:
            recommendations.append(
                f"Found {anomaly_detection.anomaly_count} price anomalies"
            )
            if anomaly_detection.anomaly_percentage > 10:
                recommendations.append("High anomaly rate - verify data quality")

        # General recommendations
        if trend_analysis.r_squared < 0.3:
            recommendations.append(
                "Low trend reliability - consider multiple data sources"
            )

        if not recommendations:
            recommendations.append("No specific recommendations - continue monitoring")

        return recommendations

    def _save_analysis_results(
        self, results: Dict[str, Any], product_id: Optional[str] = None
    ):
        """Save analysis results to file."""
        try:
            filename = f"analysis_{product_id or 'general'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.data_directory / filename

            with open(filepath, "w") as f:
                json.dump(results, f, indent=2, default=str)

            self.logger.info(f"Analysis results saved to {filepath}")

        except Exception as e:
            self.logger.error(f"Error saving analysis results: {e}")

    def get_analysis_summary(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get a quick summary of time series analysis capabilities.

        Args:
            data: List of scraped data items

        Returns:
            Dictionary with analysis summary
        """
        df = self.prepare_time_series_data(data)

        summary = {
            "total_data_points": len(df),
            "date_range_days": (df.index.max() - df.index.min()).days
            if len(df) > 1
            else 0,
            "can_analyze_trends": len(df) >= self.min_data_points,
            "can_analyze_seasonality": len(df) >= 30,
            "can_detect_anomalies": len(df) >= 5,
            "can_predict_prices": len(df) >= self.min_data_points,
            "data_quality": "good"
            if len(df) >= 20
            else "limited"
            if len(df) >= 10
            else "poor",
        }

        return summary
