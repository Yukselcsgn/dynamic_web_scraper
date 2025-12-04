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
Export and Sharing Manager Module

This module provides comprehensive export and sharing capabilities for the Dynamic Web Scraper.
"""

import csv
import io
import json
import logging
import os
import sys
import zipfile
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import requests

# Add the project root to the path for imports
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from scraper.logging_manager.logging_manager import log_message, setup_logging


@dataclass
class ExportConfig:
    """Configuration for export operations."""

    export_directory: str = "exports"
    default_format: str = "json"  # json, csv, excel, zip
    include_metadata: bool = True

    # Email sharing settings
    email_sharing_enabled: bool = False
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_from: str = ""
    email_password: str = ""

    # Slack integration
    slack_enabled: bool = False
    slack_webhook_url: str = ""


@dataclass
class ExportResult:
    """Represents the result of an export operation."""

    success: bool
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    format: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ExportManager:
    """
    Comprehensive export and sharing management system.
    """

    def __init__(
        self, data_directory: str = "data", export_config: Optional[ExportConfig] = None
    ):
        """
        Initialize the export manager.

        Args:
            data_directory: Directory containing data to export
            export_config: Export configuration
        """
        self.data_directory = Path(data_directory)
        self.export_config = export_config or ExportConfig()
        self.logger = logging.getLogger("ExportManager")

        # Create necessary directories
        self.data_directory.mkdir(parents=True, exist_ok=True)
        self.export_dir = Path(self.export_config.export_directory)
        self.export_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("Export manager initialized")

    def export_data(
        self, data: List[Dict[str, Any]], format: str = None, filename: str = None
    ) -> ExportResult:
        """
        Export data in the specified format.

        Args:
            data: Data to export
            format: Export format (json, csv, excel, zip)
            filename: Custom filename (without extension)

        Returns:
            ExportResult with operation details
        """
        try:
            if not data:
                return ExportResult(
                    success=False, error_message="No data provided for export"
                )

            # Use default format if not specified
            format = format or self.export_config.default_format
            format = format.lower()

            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"export_{timestamp}"

            # Export based on format
            if format == "json":
                return self._export_json(data, filename)
            elif format == "csv":
                return self._export_csv(data, filename)
            elif format == "excel":
                return self._export_excel(data, filename)
            elif format == "zip":
                return self._export_zip(data, filename)
            else:
                return ExportResult(
                    success=False, error_message=f"Unsupported export format: {format}"
                )

        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            return ExportResult(success=False, error_message=str(e))

    def _export_json(self, data: List[Dict[str, Any]], filename: str) -> ExportResult:
        """Export data as JSON."""
        try:
            file_path = self.export_dir / f"{filename}.json"

            # Add metadata if enabled
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "total_items": len(data),
                "data": data,
            }

            if self.export_config.include_metadata:
                export_data["metadata"] = {
                    "source": "Dynamic Web Scraper",
                    "version": "2.9",
                    "export_format": "json",
                    "data_types": list(
                        set(item.get("category", "Unknown") for item in data)
                    ),
                    "sources": list(
                        set(item.get("source", "Unknown") for item in data)
                    ),
                }

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            file_size = file_path.stat().st_size

            return ExportResult(
                success=True,
                file_path=str(file_path),
                file_size=file_size,
                format="json",
                metadata=export_data.get("metadata"),
            )

        except Exception as e:
            self.logger.error(f"Error exporting JSON: {e}")
            return ExportResult(success=False, error_message=str(e))

    def _export_csv(self, data: List[Dict[str, Any]], filename: str) -> ExportResult:
        """Export data as CSV."""
        try:
            file_path = self.export_dir / f"{filename}.csv"

            if not data:
                return ExportResult(success=False, error_message="No data to export")

            # Convert to DataFrame for easier CSV export
            df = pd.DataFrame(data)

            # Export to CSV
            df.to_csv(file_path, index=False, encoding="utf-8")

            file_size = file_path.stat().st_size

            return ExportResult(
                success=True,
                file_path=str(file_path),
                file_size=file_size,
                format="csv",
                metadata={
                    "total_rows": len(df),
                    "total_columns": len(df.columns),
                    "columns": list(df.columns),
                },
            )

        except Exception as e:
            self.logger.error(f"Error exporting CSV: {e}")
            return ExportResult(success=False, error_message=str(e))

    def _export_excel(self, data: List[Dict[str, Any]], filename: str) -> ExportResult:
        """Export data as Excel file."""
        try:
            file_path = self.export_dir / f"{filename}.xlsx"

            if not data:
                return ExportResult(success=False, error_message="No data to export")

            # Convert to DataFrame
            df = pd.DataFrame(data)

            # Create Excel writer
            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                # Main data sheet
                df.to_excel(writer, sheet_name="Data", index=False)

                # Summary sheet
                summary_data = {
                    "Metric": ["Total Items", "Categories", "Sources"],
                    "Value": [
                        len(data),
                        len(set(item.get("category", "Unknown") for item in data)),
                        len(set(item.get("source", "Unknown") for item in data)),
                    ],
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name="Summary", index=False)

                # Categories breakdown
                category_counts = df["category"].value_counts().reset_index()
                category_counts.columns = ["Category", "Count"]
                category_counts.to_excel(writer, sheet_name="Categories", index=False)

                # Sources breakdown
                source_counts = df["source"].value_counts().reset_index()
                source_counts.columns = ["Source", "Count"]
                source_counts.to_excel(writer, sheet_name="Sources", index=False)

            file_size = file_path.stat().st_size

            return ExportResult(
                success=True,
                file_path=str(file_path),
                file_size=file_size,
                format="excel",
                metadata={
                    "total_rows": len(df),
                    "total_columns": len(df.columns),
                    "sheets": ["Data", "Summary", "Categories", "Sources"],
                },
            )

        except Exception as e:
            self.logger.error(f"Error exporting Excel: {e}")
            return ExportResult(success=False, error_message=str(e))

    def _export_zip(self, data: List[Dict[str, Any]], filename: str) -> ExportResult:
        """Export data as a comprehensive ZIP package."""
        try:
            zip_path = self.export_dir / f"{filename}_complete.zip"

            with zipfile.ZipFile(zip_path, "w") as zipf:
                # Add JSON data
                json_data = {
                    "exported_at": datetime.now().isoformat(),
                    "total_items": len(data),
                    "data": data,
                }
                zipf.writestr("data.json", json.dumps(json_data, indent=2))

                # Add CSV data
                df = pd.DataFrame(data)
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                zipf.writestr("data.csv", csv_buffer.getvalue())

                # Add summary report
                summary = {
                    "total_items": len(data),
                    "categories": list(
                        set(item.get("category", "Unknown") for item in data)
                    ),
                    "sources": list(
                        set(item.get("source", "Unknown") for item in data)
                    ),
                }
                zipf.writestr("summary.json", json.dumps(summary, indent=2))

                # Add README
                readme_content = f"""
Dynamic Web Scraper Export Package
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Contents:
- data.json: Complete data in JSON format
- data.csv: Complete data in CSV format
- summary.json: Data summary and metadata

Total Items: {len(data)}
Categories: {len(summary['categories'])}
Sources: {len(summary['sources'])}

For more information, visit: https://github.com/your-repo/dynamic-web-scraper
                """
                zipf.writestr("README.txt", readme_content.strip())

            file_size = zip_path.stat().st_size

            return ExportResult(
                success=True,
                file_path=str(zip_path),
                file_size=file_size,
                format="zip",
                metadata={
                    "total_items": len(data),
                    "files_included": [
                        "data.json",
                        "data.csv",
                        "summary.json",
                        "README.txt",
                    ],
                },
            )

        except Exception as e:
            self.logger.error(f"Error exporting ZIP: {e}")
            return ExportResult(success=False, error_message=str(e))

    def share_via_slack(self, file_path: str, message: str = None) -> ExportResult:
        """
        Share exported file via Slack.

        Args:
            file_path: Path to the file to share
            message: Slack message

        Returns:
            ExportResult with sharing details
        """
        try:
            if not self.export_config.slack_enabled:
                return ExportResult(
                    success=False, error_message="Slack integration is not enabled"
                )

            if not self.export_config.slack_webhook_url:
                return ExportResult(
                    success=False, error_message="Slack webhook URL not configured"
                )

            # Prepare message
            slack_message = (
                message or f"Dynamic Web Scraper export: {Path(file_path).name}"
            )

            # For Slack, we'll send a message with file info
            payload = {
                "text": slack_message,
                "attachments": [
                    {
                        "title": "Export File",
                        "text": f"File: {Path(file_path).name}\nSize: {Path(file_path).stat().st_size} bytes\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        "color": "good",
                    }
                ],
            }

            # Send to Slack
            response = requests.post(
                self.export_config.slack_webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                return ExportResult(
                    success=True,
                    file_path=file_path,
                    format=Path(file_path).suffix[1:],
                    metadata={"method": "slack", "response": "success"},
                )
            else:
                return ExportResult(
                    success=False,
                    error_message=f"Slack API error: {response.status_code}",
                )

        except Exception as e:
            self.logger.error(f"Error sharing via Slack: {e}")
            return ExportResult(success=False, error_message=str(e))

    def export_and_share(
        self, data: List[Dict[str, Any]], format: str = None, share_method: str = None
    ) -> ExportResult:
        """
        Export data and share it automatically.

        Args:
            data: Data to export
            format: Export format
            share_method: Sharing method ('slack')

        Returns:
            ExportResult with export and sharing details
        """
        try:
            # Export the data
            export_result = self.export_data(data, format)

            if not export_result.success:
                return export_result

            # Share if requested
            if share_method == "slack":
                share_result = self.share_via_slack(export_result.file_path)
                if share_result.success:
                    export_result.metadata = export_result.metadata or {}
                    export_result.metadata["slack_shared"] = True

            return export_result

        except Exception as e:
            self.logger.error(f"Error in export and share: {e}")
            return ExportResult(success=False, error_message=str(e))

    def get_export_history(self, days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Get history of exported files.

        Args:
            days_back: Number of days to look back

        Returns:
            List of export history entries
        """
        try:
            history = []
            cutoff_date = datetime.now() - timedelta(days=days_back)

            for file_path in self.export_dir.glob("*"):
                if file_path.is_file():
                    file_stat = file_path.stat()
                    file_date = datetime.fromtimestamp(file_stat.st_mtime)

                    if file_date >= cutoff_date:
                        history.append(
                            {
                                "filename": file_path.name,
                                "file_path": str(file_path),
                                "file_size": file_stat.st_size,
                                "created_at": file_date.isoformat(),
                                "format": file_path.suffix[1:]
                                if file_path.suffix
                                else "unknown",
                            }
                        )

            # Sort by creation date (newest first)
            history.sort(key=lambda x: x["created_at"], reverse=True)

            return history

        except Exception as e:
            self.logger.error(f"Error getting export history: {e}")
            return []

    def cleanup_old_exports(self, days_to_keep: int = 7) -> int:
        """
        Clean up old export files.

        Args:
            days_to_keep: Number of days to keep files

        Returns:
            Number of files deleted
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            deleted_count = 0

            for file_path in self.export_dir.glob("*"):
                if file_path.is_file():
                    file_date = datetime.fromtimestamp(file_path.stat().st_mtime)

                    if file_date < cutoff_date:
                        file_path.unlink()
                        deleted_count += 1
                        self.logger.info(f"Deleted old export file: {file_path.name}")

            return deleted_count

        except Exception as e:
            self.logger.error(f"Error cleaning up old exports: {e}")
            return 0
