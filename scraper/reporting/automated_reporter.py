#!/usr/bin/env python3
"""
Automated Reporting and Alerts Module

This module provides comprehensive automated reporting and alerting capabilities
for the Dynamic Web Scraper, including scheduled reports and notifications.
"""

import json
import logging
import os
import smtplib
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go
import schedule
from plotly.subplots import make_subplots

# Add the project root to the path for imports
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from scraper.analytics import DataVisualizer, PriceAnalyzer, TimeSeriesAnalyzer
from scraper.logging_manager.logging_manager import log_message, setup_logging


@dataclass
class AlertConfig:
    """Configuration for alerting system."""

    email_enabled: bool = True
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_from: str = ""
    email_password: str = ""
    email_to: List[str] = None

    # Alert thresholds
    price_drop_threshold: float = 10.0  # percentage
    price_increase_threshold: float = 15.0  # percentage
    anomaly_threshold: float = 2.0  # standard deviations
    new_listing_threshold: int = 5  # minimum new listings to trigger alert

    # Notification settings
    daily_report: bool = True
    weekly_report: bool = True
    price_alerts: bool = True
    anomaly_alerts: bool = True
    new_listing_alerts: bool = True

    def __post_init__(self):
        if self.email_to is None:
            self.email_to = []


@dataclass
class ReportConfig:
    """Configuration for reporting system."""

    report_directory: str = "reports"
    report_format: str = "html"  # html, pdf, json
    include_charts: bool = True
    include_recommendations: bool = True
    include_summary: bool = True

    # Report scheduling
    daily_report_time: str = "09:00"
    weekly_report_day: str = "monday"
    weekly_report_time: str = "10:00"


class AutomatedReporter:
    """
    Comprehensive automated reporting and alerting system.
    """

    def __init__(
        self,
        data_directory: str = "data",
        alert_config: Optional[AlertConfig] = None,
        report_config: Optional[ReportConfig] = None,
    ):
        """
        Initialize the automated reporter.

        Args:
            data_directory: Directory containing scraped data
            alert_config: Alert configuration
            report_config: Report configuration
        """
        self.data_directory = Path(data_directory)
        self.alert_config = alert_config or AlertConfig()
        self.report_config = report_config or ReportConfig()

        self.logger = logging.getLogger("AutomatedReporter")

        # Initialize analytics components
        self.visualizer = DataVisualizer(f"{data_directory}/visualizations")
        self.time_analyzer = TimeSeriesAnalyzer(f"{data_directory}/time_series")
        self.price_analyzer = PriceAnalyzer()

        # Create necessary directories
        self.data_directory.mkdir(parents=True, exist_ok=True)
        self.report_dir = Path(self.report_config.report_directory)
        self.report_dir.mkdir(parents=True, exist_ok=True)

        # Alert history
        self.alert_history = []
        self.last_report_date = None

        self.logger.info("Automated reporter initialized")

    def load_historical_data(self, days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Load historical data for analysis.

        Args:
            days_back: Number of days to look back

        Returns:
            List of historical data items
        """
        try:
            all_data = []
            cutoff_date = datetime.now() - timedelta(days=days_back)

            # Load all data files in the data directory
            data_files = list(self.data_directory.glob("*.json"))

            for file_path in data_files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        file_data = json.load(f)

                    # Filter by date if timestamp is available
                    if file_data and isinstance(file_data, list) and len(file_data) > 0:
                        if "timestamp" in file_data[0]:
                            # Filter data by date
                            filtered_data = []
                            for item in file_data:
                                try:
                                    item_date = datetime.fromisoformat(
                                        item["timestamp"].replace("Z", "+00:00")
                                    )
                                    if item_date >= cutoff_date:
                                        filtered_data.append(item)
                                except:
                                    filtered_data.append(
                                        item
                                    )  # Include if date parsing fails
                            all_data.extend(filtered_data)
                        else:
                            all_data.extend(file_data)

                except Exception as e:
                    self.logger.warning(f"Error loading {file_path}: {e}")
                    continue

            self.logger.info(f"Loaded {len(all_data)} historical data items")
            return all_data

        except Exception as e:
            self.logger.error(f"Error loading historical data: {e}")
            return []

    def detect_price_changes(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect significant price changes in the data.

        Args:
            data: Data to analyze

        Returns:
            List of price change alerts
        """
        try:
            if not data:
                return []

            df = pd.DataFrame(data)

            if df.empty or "price" not in df.columns:
                return []

            # Clean price data
            df["price_numeric"] = pd.to_numeric(
                df["price"].str.replace(r"[^\d.]", "", regex=True), errors="coerce"
            )
            df = df.dropna(subset=["price_numeric"])

            if df.empty:
                return []

            alerts = []

            # Group by product/category to detect price changes
            if "title" in df.columns:
                # Group by product title
                grouped = df.groupby("title")
            elif "category" in df.columns:
                # Group by category
                grouped = df.groupby("category")
            else:
                # No grouping possible
                return []

            for name, group in grouped:
                if len(group) < 2:
                    continue

                # Sort by timestamp
                if "timestamp" in group.columns:
                    group = group.sort_values("timestamp")

                # Calculate price changes
                prices = group["price_numeric"].values
                if len(prices) >= 2:
                    current_price = prices[-1]
                    previous_price = prices[-2]

                    if previous_price > 0:
                        price_change_pct = (
                            (current_price - previous_price) / previous_price
                        ) * 100

                        # Check for significant price drops
                        if price_change_pct <= -self.alert_config.price_drop_threshold:
                            alerts.append(
                                {
                                    "type": "price_drop",
                                    "product": name,
                                    "current_price": current_price,
                                    "previous_price": previous_price,
                                    "change_percentage": price_change_pct,
                                    "timestamp": datetime.now().isoformat(),
                                    "severity": "high"
                                    if abs(price_change_pct) > 20
                                    else "medium",
                                }
                            )

                        # Check for significant price increases
                        elif (
                            price_change_pct
                            >= self.alert_config.price_increase_threshold
                        ):
                            alerts.append(
                                {
                                    "type": "price_increase",
                                    "product": name,
                                    "current_price": current_price,
                                    "previous_price": previous_price,
                                    "change_percentage": price_change_pct,
                                    "timestamp": datetime.now().isoformat(),
                                    "severity": "high"
                                    if price_change_pct > 30
                                    else "medium",
                                }
                            )

            self.logger.info(f"Detected {len(alerts)} price change alerts")
            return alerts

        except Exception as e:
            self.logger.error(f"Error detecting price changes: {e}")
            return []

    def detect_anomalies(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect price anomalies in the data.

        Args:
            data: Data to analyze

        Returns:
            List of anomaly alerts
        """
        try:
            if not data:
                return []

            df = pd.DataFrame(data)

            if df.empty or "price" not in df.columns:
                return []

            # Clean price data
            df["price_numeric"] = pd.to_numeric(
                df["price"].str.replace(r"[^\d.]", "", regex=True), errors="coerce"
            )
            df = df.dropna(subset=["price_numeric"])

            if df.empty:
                return []

            alerts = []

            # Detect anomalies using z-score method
            mean_price = df["price_numeric"].mean()
            std_price = df["price_numeric"].std()

            if std_price > 0:
                # Calculate z-scores
                df["z_score"] = abs((df["price_numeric"] - mean_price) / std_price)

                # Find anomalies
                anomalies = df[df["z_score"] > self.alert_config.anomaly_threshold]

                for _, row in anomalies.iterrows():
                    alerts.append(
                        {
                            "type": "anomaly",
                            "product": row.get("title", "Unknown"),
                            "price": row["price_numeric"],
                            "z_score": row["z_score"],
                            "mean_price": mean_price,
                            "timestamp": datetime.now().isoformat(),
                            "severity": "high" if row["z_score"] > 3 else "medium",
                        }
                    )

            self.logger.info(f"Detected {len(alerts)} anomaly alerts")
            return alerts

        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {e}")
            return []

    def detect_new_listings(
        self, data: List[Dict[str, Any]], previous_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect new product listings.

        Args:
            data: Current data
            previous_data: Previous data for comparison

        Returns:
            List of new listing alerts
        """
        try:
            if not data or not previous_data:
                return []

            current_df = pd.DataFrame(data)
            previous_df = pd.DataFrame(previous_data)

            if current_df.empty or previous_df.empty:
                return []

            alerts = []

            # Identify new products
            if "title" in current_df.columns and "title" in previous_df.columns:
                current_products = set(current_df["title"].unique())
                previous_products = set(previous_df["title"].unique())
                new_products = current_products - previous_products

                if len(new_products) >= self.alert_config.new_listing_threshold:
                    # Get details for new products
                    new_product_data = current_df[
                        current_df["title"].isin(new_products)
                    ]

                    for _, row in new_product_data.iterrows():
                        alerts.append(
                            {
                                "type": "new_listing",
                                "product": row["title"],
                                "price": row.get("price", "Unknown"),
                                "category": row.get("category", "Unknown"),
                                "source": row.get("source", "Unknown"),
                                "timestamp": datetime.now().isoformat(),
                                "severity": "medium",
                            }
                        )

            self.logger.info(f"Detected {len(alerts)} new listing alerts")
            return alerts

        except Exception as e:
            self.logger.error(f"Error detecting new listings: {e}")
            return []

    def generate_daily_report(self) -> Dict[str, Any]:
        """
        Generate a daily report with key insights.

        Returns:
            Dictionary with report data
        """
        try:
            # Load recent data
            data = self.load_historical_data(days_back=7)

            if not data:
                return {"error": "No data available for daily report"}

            # Generate report content
            report = {
                "report_type": "daily",
                "generated_at": datetime.now().isoformat(),
                "data_summary": self._generate_data_summary(data),
                "price_analysis": self._generate_price_analysis(data),
                "trend_analysis": self._generate_trend_analysis(data),
                "alerts": self._generate_alert_summary(data),
                "recommendations": self._generate_recommendations(data),
            }

            # Save report
            self._save_report(report, "daily")

            self.logger.info("Daily report generated successfully")
            return report

        except Exception as e:
            self.logger.error(f"Error generating daily report: {e}")
            return {"error": str(e)}

    def generate_weekly_report(self) -> Dict[str, Any]:
        """
        Generate a weekly report with comprehensive insights.

        Returns:
            Dictionary with report data
        """
        try:
            # Load recent data
            data = self.load_historical_data(days_back=30)

            if not data:
                return {"error": "No data available for weekly report"}

            # Generate comprehensive report
            report = {
                "report_type": "weekly",
                "generated_at": datetime.now().isoformat(),
                "data_summary": self._generate_data_summary(data),
                "price_analysis": self._generate_price_analysis(data),
                "trend_analysis": self._generate_trend_analysis(data),
                "seasonality_analysis": self._generate_seasonality_analysis(data),
                "comparative_analysis": self._generate_comparative_analysis(data),
                "alerts": self._generate_alert_summary(data),
                "recommendations": self._generate_recommendations(data),
                "forecast": self._generate_forecast(data),
            }

            # Save report
            self._save_report(report, "weekly")

            self.logger.info("Weekly report generated successfully")
            return report

        except Exception as e:
            self.logger.error(f"Error generating weekly report: {e}")
            return {"error": str(e)}

    def _generate_data_summary(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate data summary for reports."""
        try:
            df = pd.DataFrame(data)

            summary = {
                "total_items": len(df),
                "date_range": None,
                "sources": df["source"].nunique() if "source" in df.columns else 0,
                "categories": df["category"].nunique()
                if "category" in df.columns
                else 0,
            }

            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                summary["date_range"] = {
                    "start": df["timestamp"].min().isoformat(),
                    "end": df["timestamp"].max().isoformat(),
                    "days": (df["timestamp"].max() - df["timestamp"].min()).days,
                }

            return summary
        except Exception as e:
            self.logger.error(f"Error generating data summary: {e}")
            return {}

    def _generate_price_analysis(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate price analysis for reports."""
        try:
            df = pd.DataFrame(data)

            if df.empty or "price" not in df.columns:
                return {}

            # Clean price data
            df["price_numeric"] = pd.to_numeric(
                df["price"].str.replace(r"[^\d.]", "", regex=True), errors="coerce"
            )
            df = df.dropna(subset=["price_numeric"])

            if df.empty:
                return {}

            analysis = {
                "price_stats": {
                    "mean": float(df["price_numeric"].mean()),
                    "median": float(df["price_numeric"].median()),
                    "min": float(df["price_numeric"].min()),
                    "max": float(df["price_numeric"].max()),
                    "std": float(df["price_numeric"].std()),
                },
                "price_changes": self.detect_price_changes(data),
                "anomalies": self.detect_anomalies(data),
            }

            return analysis
        except Exception as e:
            self.logger.error(f"Error generating price analysis: {e}")
            return {}

    def _generate_trend_analysis(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate trend analysis for reports."""
        try:
            if not data:
                return {}

            # Use time series analyzer for trend analysis
            analysis_results = self.time_analyzer.comprehensive_analysis(data)

            if "error" in analysis_results:
                return {}

            return {
                "trend_direction": analysis_results.get("trend_analysis", {}).get(
                    "trend_direction"
                ),
                "trend_strength": analysis_results.get("trend_analysis", {}).get(
                    "trend_strength"
                ),
                "anomaly_count": analysis_results.get("anomaly_detection", {}).get(
                    "anomaly_count", 0
                ),
                "prediction_accuracy": analysis_results.get("price_prediction", {}).get(
                    "model_accuracy", 0
                ),
            }
        except Exception as e:
            self.logger.error(f"Error generating trend analysis: {e}")
            return {}

    def _generate_seasonality_analysis(
        self, data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate seasonality analysis for reports."""
        try:
            if not data:
                return {}

            df = pd.DataFrame(data)

            if df.empty or "timestamp" not in df.columns:
                return {}

            # Prepare data for time series analysis
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("timestamp")

            # Use time series analyzer
            analysis_results = self.time_analyzer.analyze_seasonality(
                self.time_analyzer.prepare_time_series_data(data)
            )

            return {
                "has_seasonality": analysis_results.has_seasonality,
                "seasonal_period": analysis_results.seasonal_period,
                "seasonal_strength": analysis_results.seasonal_strength,
            }
        except Exception as e:
            self.logger.error(f"Error generating seasonality analysis: {e}")
            return {}

    def _generate_comparative_analysis(
        self, data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comparative analysis for reports."""
        try:
            df = pd.DataFrame(data)

            if df.empty:
                return {}

            analysis = {}

            # Source comparison
            if "source" in df.columns and "price" in df.columns:
                df["price_numeric"] = pd.to_numeric(
                    df["price"].str.replace(r"[^\d.]", "", regex=True), errors="coerce"
                )
                source_stats = (
                    df.groupby("source")["price_numeric"]
                    .agg(["mean", "count"])
                    .round(2)
                )
                analysis["source_comparison"] = source_stats.to_dict()

            # Category comparison
            if "category" in df.columns and "price" in df.columns:
                category_stats = (
                    df.groupby("category")["price_numeric"]
                    .agg(["mean", "count"])
                    .round(2)
                )
                analysis["category_comparison"] = category_stats.to_dict()

            return analysis
        except Exception as e:
            self.logger.error(f"Error generating comparative analysis: {e}")
            return {}

    def _generate_alert_summary(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate alert summary for reports."""
        try:
            alerts = {
                "price_changes": self.detect_price_changes(data),
                "anomalies": self.detect_anomalies(data),
                "total_alerts": 0,
            }

            alerts["total_alerts"] = len(alerts["price_changes"]) + len(
                alerts["anomalies"]
            )

            return alerts
        except Exception as e:
            self.logger.error(f"Error generating alert summary: {e}")
            return {}

    def _generate_recommendations(self, data: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations for reports."""
        try:
            if not data:
                return ["No data available for recommendations"]

            recommendations = []
            df = pd.DataFrame(data)

            # Price-based recommendations
            if "price" in df.columns:
                df["price_numeric"] = pd.to_numeric(
                    df["price"].str.replace(r"[^\d.]", "", regex=True), errors="coerce"
                )
                price_data = df["price_numeric"].dropna()

                if len(price_data) > 0:
                    price_range = price_data.max() - price_data.min()
                    if price_range > price_data.mean() * 2:
                        recommendations.append(
                            "High price variability detected - consider segmenting analysis by category"
                        )

            # Source-based recommendations
            if "source" in df.columns:
                source_counts = df["source"].value_counts()
                if len(source_counts) < 2:
                    recommendations.append(
                        "Limited source diversity - consider adding more sources for better comparison"
                    )

            # Time-based recommendations
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                date_range = (df["timestamp"].max() - df["timestamp"].min()).days
                if date_range < 7:
                    recommendations.append(
                        "Limited time range - collect data over longer periods for trend analysis"
                    )

            if not recommendations:
                recommendations.append(
                    "Data looks good - continue monitoring current trends"
                )

            return recommendations
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return ["Error generating recommendations"]

    def _generate_forecast(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate price forecast for reports."""
        try:
            if not data:
                return {}

            # Use time series analyzer for forecasting
            df = self.time_analyzer.prepare_time_series_data(data)

            if df.empty:
                return {}

            prediction = self.time_analyzer.predict_prices(
                df, horizon=7, method="linear"
            )

            return {
                "forecast_horizon": prediction.prediction_horizon,
                "model_accuracy": prediction.model_accuracy,
                "predicted_prices": prediction.predicted_prices[
                    :5
                ],  # First 5 predictions
                "confidence_intervals": prediction.confidence_intervals[:5],
            }
        except Exception as e:
            self.logger.error(f"Error generating forecast: {e}")
            return {}

    def _save_report(self, report: Dict[str, Any], report_type: str):
        """Save report to file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{report_type}_report_{timestamp}.json"
            filepath = self.report_dir / filename

            with open(filepath, "w") as f:
                json.dump(report, f, indent=2, default=str)

            self.logger.info(f"Report saved to {filepath}")

        except Exception as e:
            self.logger.error(f"Error saving report: {e}")

    def send_email_alert(
        self, subject: str, body: str, attachments: List[str] = None
    ) -> bool:
        """
        Send email alert.

        Args:
            subject: Email subject
            body: Email body
            attachments: List of file paths to attach

        Returns:
            True if email sent successfully
        """
        try:
            if not self.alert_config.email_enabled:
                self.logger.info("Email alerts disabled")
                return False

            if not self.alert_config.email_from or not self.alert_config.email_password:
                self.logger.warning("Email credentials not configured")
                return False

            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.alert_config.email_from
            msg["To"] = ", ".join(self.alert_config.email_to)
            msg["Subject"] = subject

            # Add body
            msg.attach(MIMEText(body, "html"))

            # Add attachments
            if attachments:
                for filepath in attachments:
                    if os.path.exists(filepath):
                        with open(filepath, "rb") as attachment:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(attachment.read())

                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename= {os.path.basename(filepath)}",
                        )
                        msg.attach(part)

            # Send email
            server = smtplib.SMTP(
                self.alert_config.smtp_server, self.alert_config.smtp_port
            )
            server.starttls()
            server.login(self.alert_config.email_from, self.alert_config.email_password)
            text = msg.as_string()
            server.sendmail(
                self.alert_config.email_from, self.alert_config.email_to, text
            )
            server.quit()

            self.logger.info(f"Email alert sent: {subject}")
            return True

        except Exception as e:
            self.logger.error(f"Error sending email alert: {e}")
            return False

    def send_price_alert(self, alerts: List[Dict[str, Any]]) -> bool:
        """
        Send price change alerts.

        Args:
            alerts: List of price change alerts

        Returns:
            True if alerts sent successfully
        """
        try:
            if not alerts:
                return True

            subject = f"Price Alert: {len(alerts)} significant price changes detected"

            # Create HTML body
            body = f"""
            <html>
            <body>
                <h2>Price Change Alerts</h2>
                <p>Detected {len(alerts)} significant price changes:</p>
                <table border="1" style="border-collapse: collapse; width: 100%;">
                    <tr style="background-color: #f2f2f2;">
                        <th>Product</th>
                        <th>Type</th>
                        <th>Previous Price</th>
                        <th>Current Price</th>
                        <th>Change %</th>
                        <th>Severity</th>
                    </tr>
            """

            for alert in alerts:
                if alert["type"] in ["price_drop", "price_increase"]:
                    body += f"""
                    <tr>
                        <td>{alert['product']}</td>
                        <td>{alert['type'].replace('_', ' ').title()}</td>
                        <td>${alert['previous_price']:.2f}</td>
                        <td>${alert['current_price']:.2f}</td>
                        <td>{alert['change_percentage']:.1f}%</td>
                        <td style="color: {'red' if alert['severity'] == 'high' else 'orange'}">{alert['severity'].title()}</td>
                    </tr>
                    """

            body += """
                </table>
                <p><small>Generated on: {}</small></p>
            </body>
            </html>
            """.format(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

            return self.send_email_alert(subject, body)

        except Exception as e:
            self.logger.error(f"Error sending price alert: {e}")
            return False

    def send_daily_report_email(self, report: Dict[str, Any]) -> bool:
        """
        Send daily report via email.

        Args:
            report: Daily report data

        Returns:
            True if email sent successfully
        """
        try:
            subject = f"Daily Report - {datetime.now().strftime('%Y-%m-%d')}"

            # Create HTML body
            body = f"""
            <html>
            <body>
                <h2>Daily Scraping Report</h2>
                <p><strong>Generated:</strong> {report.get('generated_at', 'Unknown')}</p>

                <h3>Data Summary</h3>
                <ul>
                    <li>Total Items: {report.get('data_summary', {}).get('total_items', 0)}</li>
                    <li>Sources: {report.get('data_summary', {}).get('sources', 0)}</li>
                    <li>Categories: {report.get('data_summary', {}).get('categories', 0)}</li>
                </ul>

                <h3>Price Analysis</h3>
                <p>Average Price: ${report.get('price_analysis', {}).get('price_stats', {}).get('mean', 0):.2f}</p>
                <p>Price Range: ${report.get('price_analysis', {}).get('price_stats', {}).get('min', 0):.2f} - ${report.get('price_analysis', {}).get('price_stats', {}).get('max', 0):.2f}</p>

                <h3>Alerts</h3>
                <p>Total Alerts: {report.get('alerts', {}).get('total_alerts', 0)}</p>

                <h3>Recommendations</h3>
                <ul>
            """

            for rec in report.get("recommendations", []):
                body += f"<li>{rec}</li>"

            body += """
                </ul>
                <p><small>This is an automated report from the Dynamic Web Scraper.</small></p>
            </body>
            </html>
            """

            return self.send_email_alert(subject, body)

        except Exception as e:
            self.logger.error(f"Error sending daily report email: {e}")
            return False

    def schedule_reports(self):
        """Schedule automated reports."""
        try:
            # Schedule daily report
            if self.alert_config.daily_report:
                schedule.every().day.at(self.report_config.daily_report_time).do(
                    self._run_daily_report
                )
                self.logger.info(
                    f"Scheduled daily report at {self.report_config.daily_report_time}"
                )

            # Schedule weekly report
            if self.alert_config.weekly_report:
                getattr(schedule.every(), self.report_config.weekly_report_day).at(
                    self.report_config.weekly_report_time
                ).do(self._run_weekly_report)
                self.logger.info(
                    f"Scheduled weekly report on {self.report_config.weekly_report_day} at {self.report_config.weekly_report_time}"
                )

            # Start scheduler in background thread
            def run_scheduler():
                while True:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute

            scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
            scheduler_thread.start()

            self.logger.info("Report scheduler started")

        except Exception as e:
            self.logger.error(f"Error scheduling reports: {e}")

    def _run_daily_report(self):
        """Run daily report and send email."""
        try:
            report = self.generate_daily_report()
            if "error" not in report:
                self.send_daily_report_email(report)
        except Exception as e:
            self.logger.error(f"Error running daily report: {e}")

    def _run_weekly_report(self):
        """Run weekly report and send email."""
        try:
            report = self.generate_weekly_report()
            if "error" not in report:
                self.send_daily_report_email(report)  # Reuse daily email function
        except Exception as e:
            self.logger.error(f"Error running weekly report: {e}")

    def run_alert_check(self) -> List[Dict[str, Any]]:
        """
        Run comprehensive alert check.

        Returns:
            List of all alerts
        """
        try:
            # Load recent data
            data = self.load_historical_data(days_back=7)

            if not data:
                return []

            all_alerts = []

            # Check for price changes
            if self.alert_config.price_alerts:
                price_alerts = self.detect_price_changes(data)
                all_alerts.extend(price_alerts)

            # Check for anomalies
            if self.alert_config.anomaly_alerts:
                anomaly_alerts = self.detect_anomalies(data)
                all_alerts.extend(anomaly_alerts)

            # Check for new listings (would need previous data for comparison)
            if self.alert_config.new_listing_alerts:
                # This would require storing previous data state
                pass

            # Send alerts if any found
            if all_alerts:
                self.send_price_alert(all_alerts)

            # Store in alert history
            self.alert_history.extend(all_alerts)

            self.logger.info(f"Alert check completed: {len(all_alerts)} alerts found")
            return all_alerts

        except Exception as e:
            self.logger.error(f"Error running alert check: {e}")
            return []
