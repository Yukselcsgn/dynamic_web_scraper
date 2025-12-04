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
Utility functions for the scraper.

This module contains utility functions for data saving, HTML parsing, and other common operations.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from scraper.data_parsers.data_parser import save_data
from scraper.logging_manager.logging_manager import log_message


class ScraperUtilities:
    """
    Utility functions for the scraper.
    """

    def __init__(self, export_manager):
        """
        Initialize the utilities.

        Args:
            export_manager: Export manager instance
        """
        self.export_manager = export_manager

    def save_data(self, data: List[Dict], file_name: str, format: str = "csv") -> bool:
        """
        Save data to file in specified format.

        Args:
            data: Data to save
            file_name: Output file name
            format: Output format (csv, json, excel)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            log_message(
                "INFO", f"Saving {len(data)} items to {file_name} in {format} format"
            )

            # Ensure output directory exists
            output_dir = os.path.dirname(file_name)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Use the data parser to save data
            save_data(data, file_name, format)

            log_message("INFO", f"Data saved successfully to {file_name}")
            return True

        except Exception as e:
            log_message("ERROR", f"Error saving data: {e}")
            return False

    def parse_html(self, response_text: str) -> BeautifulSoup:
        """
        Parse HTML response text.

        Args:
            response_text: Raw HTML text

        Returns:
            BeautifulSoup: Parsed HTML object
        """
        try:
            return BeautifulSoup(response_text, "html.parser")
        except Exception as e:
            log_message("ERROR", f"Error parsing HTML: {e}")
            return None

    def analyze_html_content(self, html_content: str, filename: str = None) -> Dict:
        """
        Analyze HTML content for debugging and optimization.

        Args:
            html_content: HTML content to analyze
            filename: Optional filename for saving analysis

        Returns:
            dict: Analysis results
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            analysis = {
                "total_length": len(html_content),
                "title": soup.title.string if soup.title else "No title",
                "meta_description": "",
                "headings": [],
                "links": [],
                "images": [],
                "forms": [],
                "scripts": [],
                "stylesheets": [],
                "potential_selectors": [],
            }

            # Extract meta description
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc:
                analysis["meta_description"] = meta_desc.get("content", "")

            # Extract headings
            for i in range(1, 7):
                headings = soup.find_all(f"h{i}")
                analysis["headings"].extend([h.get_text(strip=True) for h in headings])

            # Extract links
            links = soup.find_all("a", href=True)
            analysis["links"] = [
                link.get("href") for link in links[:10]
            ]  # First 10 links

            # Extract images
            images = soup.find_all("img", src=True)
            analysis["images"] = [
                img.get("src") for img in images[:10]
            ]  # First 10 images

            # Extract forms
            forms = soup.find_all("form")
            analysis["forms"] = [form.get("action", "") for form in forms]

            # Extract scripts
            scripts = soup.find_all("script", src=True)
            analysis["scripts"] = [
                script.get("src") for script in scripts[:5]
            ]  # First 5 scripts

            # Extract stylesheets
            stylesheets = soup.find_all("link", rel="stylesheet")
            analysis["stylesheets"] = [link.get("href") for link in stylesheets]

            # Find potential selectors
            analysis["potential_selectors"] = self._find_potential_selectors(soup)

            # Save analysis if filename provided
            if filename:
                self._save_analysis(analysis, filename)

            return analysis

        except Exception as e:
            log_message("ERROR", f"Error analyzing HTML content: {e}")
            return {}

    def _find_potential_selectors(self, soup: BeautifulSoup) -> List[str]:
        """
        Find potential CSS selectors for data extraction.

        Args:
            soup: BeautifulSoup object

        Returns:
            list: List of potential selectors
        """
        selectors = []

        try:
            # Look for common patterns
            common_classes = [
                "product",
                "item",
                "listing",
                "card",
                "post",
                "article",
                "title",
                "price",
                "description",
                "image",
                "link",
            ]

            for class_name in common_classes:
                elements = soup.find_all(class_=lambda x: x and class_name in x.lower())
                if elements:
                    selectors.append(f".{class_name}")

            # Look for data attributes
            data_elements = soup.find_all(attrs={"data-testid": True})
            for elem in data_elements:
                testid = elem.get("data-testid")
                if testid:
                    selectors.append(f"[data-testid='{testid}']")

            # Look for ID patterns
            id_elements = soup.find_all(id=True)
            for elem in id_elements[:10]:  # First 10 IDs
                elem_id = elem.get("id")
                if elem_id:
                    selectors.append(f"#{elem_id}")

        except Exception as e:
            log_message("ERROR", f"Error finding potential selectors: {e}")

        return selectors[:20]  # Return first 20 selectors

    def _save_analysis(self, analysis: Dict, filename: str):
        """
        Save analysis results to file.

        Args:
            analysis: Analysis results
            filename: Output filename
        """
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            log_message("INFO", f"Analysis saved to {filename}")
        except Exception as e:
            log_message("ERROR", f"Error saving analysis: {e}")

    def create_debug_summary(self, url: str, html_content: str = None) -> Dict:
        """
        Create a debug summary for troubleshooting.

        Args:
            url: Target URL
            html_content: HTML content (optional)

        Returns:
            dict: Debug summary
        """
        try:
            summary = {
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "html_length": len(html_content) if html_content else 0,
                "has_content": bool(html_content),
                "content_type": "text/html" if html_content else "unknown",
            }

            if html_content:
                # Analyze the content
                analysis = self.analyze_html_content(html_content)
                summary.update(
                    {
                        "title": analysis.get("title", "No title"),
                        "headings_count": len(analysis.get("headings", [])),
                        "links_count": len(analysis.get("links", [])),
                        "images_count": len(analysis.get("images", [])),
                        "forms_count": len(analysis.get("forms", [])),
                        "potential_selectors": analysis.get("potential_selectors", []),
                    }
                )

            # Save debug summary
            debug_filename = f"debug_html/debug_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs(os.path.dirname(debug_filename), exist_ok=True)

            with open(debug_filename, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)

            log_message("INFO", f"Debug summary created: {debug_filename}")
            return summary

        except Exception as e:
            log_message("ERROR", f"Error creating debug summary: {e}")
            return {}

    def generate_comprehensive_extraction_report(self, html_content: str) -> Dict:
        """
        Generate a comprehensive report on extraction possibilities.

        Args:
            html_content: HTML content to analyze

        Returns:
            dict: Comprehensive extraction report
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            report = {
                "content_analysis": self.analyze_html_content(html_content),
                "extraction_recommendations": [],
                "potential_issues": [],
                "optimization_suggestions": [],
            }

            # Analyze content structure
            if not soup.find_all(["div", "section", "article"]):
                report["potential_issues"].append(
                    "No structured content containers found"
                )

            if not soup.find_all(["h1", "h2", "h3"]):
                report["potential_issues"].append(
                    "No headings found - may indicate dynamic content"
                )

            if len(soup.find_all("script")) > 10:
                report["potential_issues"].append(
                    "High number of scripts - may require JavaScript rendering"
                )

            # Generate recommendations
            if soup.find_all(class_=lambda x: x and "product" in x.lower()):
                report["extraction_recommendations"].append(
                    "Use .product class selector"
                )

            if soup.find_all(attrs={"data-testid": True}):
                report["extraction_recommendations"].append(
                    "Use data-testid attributes for reliable selection"
                )

            if soup.find_all("script", type="application/ld+json"):
                report["extraction_recommendations"].append(
                    "Extract structured data from JSON-LD scripts"
                )

            return report

        except Exception as e:
            log_message("ERROR", f"Error generating extraction report: {e}")
            return {}

    def get_scraping_report(self, stats: Dict) -> Dict:
        """
        Generate a comprehensive scraping report.

        Args:
            stats: Statistics dictionary

        Returns:
            dict: Scraping report
        """
        try:
            report = {
                "summary": {
                    "total_requests": stats.get("requests_made", 0),
                    "successful_requests": stats.get("successful_requests", 0),
                    "failed_requests": stats.get("failed_requests", 0),
                    "success_rate": 0,
                    "data_items_extracted": stats.get("data_items_extracted", 0),
                    "processing_time": stats.get("processing_time", 0),
                },
                "performance": {
                    "requests_per_second": 0,
                    "items_per_second": 0,
                    "average_response_time": 0,
                },
                "recommendations": [],
            }

            # Calculate success rate
            total_requests = stats.get("requests_made", 0)
            successful_requests = stats.get("successful_requests", 0)
            if total_requests > 0:
                report["summary"]["success_rate"] = (
                    successful_requests / total_requests
                ) * 100

            # Calculate performance metrics
            processing_time = stats.get("processing_time", 0)
            if processing_time > 0:
                report["performance"]["requests_per_second"] = (
                    total_requests / processing_time
                )
                report["performance"]["items_per_second"] = (
                    stats.get("data_items_extracted", 0) / processing_time
                )

            # Generate recommendations
            if report["summary"]["success_rate"] < 50:
                report["recommendations"].append(
                    "Low success rate - consider using browser automation"
                )

            if stats.get("data_items_extracted", 0) == 0:
                report["recommendations"].append(
                    "No data extracted - check selectors and site structure"
                )

            if processing_time > 60:
                report["recommendations"].append(
                    "Long processing time - consider optimizing selectors"
                )

            return report

        except Exception as e:
            log_message("ERROR", f"Error generating scraping report: {e}")
            return {}
