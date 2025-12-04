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
Adaptive Configuration Manager - Automatically learns and updates selectors based on successful extractions
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


@dataclass
class SelectorPerformance:
    """Tracks performance of a selector."""

    selector: str
    success_count: int = 0
    failure_count: int = 0
    last_used: Optional[str] = None
    confidence: float = 0.0
    data_count: int = 0


@dataclass
class SiteLearningData:
    """Learning data for a specific site."""

    domain: str
    successful_selectors: Dict[str, SelectorPerformance]
    failed_selectors: Dict[str, SelectorPerformance]
    last_updated: str
    total_attempts: int = 0
    success_rate: float = 0.0


class AdaptiveConfigManager:
    """
    Manages configuration learning and adaptation based on extraction results.
    Automatically updates selectors based on what works best for each site.
    """

    def __init__(self, learning_file: str = "data/selector_learning.json"):
        self.learning_file = learning_file
        self.logger = logging.getLogger(__name__)
        self.learning_data: Dict[str, SiteLearningData] = {}
        self.load_learning_data()

    def load_learning_data(self):
        """Load learning data from file."""
        try:
            with open(self.learning_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for domain, site_data in data.items():
                    # Convert dict back to dataclass
                    successful_selectors = {}
                    for selector, perf_data in site_data.get(
                        "successful_selectors", {}
                    ).items():
                        successful_selectors[selector] = SelectorPerformance(
                            **perf_data
                        )

                    failed_selectors = {}
                    for selector, perf_data in site_data.get(
                        "failed_selectors", {}
                    ).items():
                        failed_selectors[selector] = SelectorPerformance(**perf_data)

                    self.learning_data[domain] = SiteLearningData(
                        domain=domain,
                        successful_selectors=successful_selectors,
                        failed_selectors=failed_selectors,
                        last_updated=site_data.get("last_updated", ""),
                        total_attempts=site_data.get("total_attempts", 0),
                        success_rate=site_data.get("success_rate", 0.0),
                    )
        except FileNotFoundError:
            self.logger.info("No learning data file found, starting fresh")
        except Exception as e:
            self.logger.error(f"Error loading learning data: {e}")

    def save_learning_data(self):
        """Save learning data to file."""
        try:
            import os

            os.makedirs(os.path.dirname(self.learning_file), exist_ok=True)

            data = {}
            for domain, site_data in self.learning_data.items():
                data[domain] = {
                    "domain": site_data.domain,
                    "successful_selectors": {
                        k: asdict(v) for k, v in site_data.successful_selectors.items()
                    },
                    "failed_selectors": {
                        k: asdict(v) for k, v in site_data.failed_selectors.items()
                    },
                    "last_updated": site_data.last_updated,
                    "total_attempts": site_data.total_attempts,
                    "success_rate": site_data.success_rate,
                }

            with open(self.learning_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error saving learning data: {e}")

    def record_extraction_result(
        self,
        url: str,
        selectors_used: Dict[str, str],
        success: bool,
        data_count: int = 0,
        method: str = "",
    ):
        """Record the result of an extraction attempt."""
        domain = urlparse(url).netloc.lower()

        if domain not in self.learning_data:
            self.learning_data[domain] = SiteLearningData(
                domain=domain,
                successful_selectors={},
                failed_selectors={},
                last_updated=datetime.now().isoformat(),
            )

        site_data = self.learning_data[domain]
        site_data.total_attempts += 1
        site_data.last_updated = datetime.now().isoformat()

        # Update selector performance
        for selector_name, selector_value in selectors_used.items():
            if success:
                if selector_value in site_data.successful_selectors:
                    perf = site_data.successful_selectors[selector_value]
                    perf.success_count += 1
                    perf.data_count += data_count
                    perf.last_used = datetime.now().isoformat()
                    perf.confidence = perf.success_count / (
                        perf.success_count + perf.failure_count
                    )
                else:
                    site_data.successful_selectors[
                        selector_value
                    ] = SelectorPerformance(
                        selector=selector_value,
                        success_count=1,
                        data_count=data_count,
                        last_used=datetime.now().isoformat(),
                        confidence=1.0,
                    )
            else:
                if selector_value in site_data.failed_selectors:
                    perf = site_data.failed_selectors[selector_value]
                    perf.failure_count += 1
                    perf.last_used = datetime.now().isoformat()
                else:
                    site_data.failed_selectors[selector_value] = SelectorPerformance(
                        selector=selector_value,
                        failure_count=1,
                        last_used=datetime.now().isoformat(),
                        confidence=0.0,
                    )

        # Update success rate
        successful_attempts = sum(
            1
            for perf in site_data.successful_selectors.values()
            for _ in range(perf.success_count)
        )
        site_data.success_rate = (
            successful_attempts / site_data.total_attempts
            if site_data.total_attempts > 0
            else 0.0
        )

        # Save learning data
        self.save_learning_data()

    def get_best_selectors_for_site(self, url: str) -> Dict[str, str]:
        """Get the best known selectors for a site based on learning data."""
        domain = urlparse(url).netloc.lower()

        if domain not in self.learning_data:
            return {}

        site_data = self.learning_data[domain]

        # Get selectors sorted by confidence
        best_selectors = {}
        for selector_value, perf in site_data.successful_selectors.items():
            if perf.confidence > 0.5:  # Only use selectors with >50% success rate
                # Try to determine selector type from context
                selector_type = self._determine_selector_type(selector_value, perf)
                if selector_type:
                    best_selectors[selector_type] = selector_value

        return best_selectors

    def _determine_selector_type(
        self, selector: str, performance: SelectorPerformance
    ) -> Optional[str]:
        """Determine what type of selector this is based on its value and performance."""
        selector_lower = selector.lower()

        # Price selectors
        if any(keyword in selector_lower for keyword in ["price", "cost", "amount"]):
            return "product_price"

        # Title selectors
        if any(
            keyword in selector_lower
            for keyword in ["title", "name", "heading", "h1", "h2", "h3"]
        ):
            return "product_title"

        # Image selectors
        if "img" in selector_lower:
            return "product_image"

        # Link selectors
        if "a" in selector_lower and "href" in selector_lower:
            return "product_link"

        # Container selectors
        if any(
            keyword in selector_lower
            for keyword in ["container", "item", "product", "listing"]
        ):
            return "product_container"

        # Location selectors
        if any(
            keyword in selector_lower for keyword in ["location", "address", "city"]
        ):
            return "product_location"

        # Date selectors
        if any(keyword in selector_lower for keyword in ["date", "time", "created"]):
            return "product_date"

        return None

    def get_learning_summary(self) -> Dict[str, Any]:
        """Get a summary of learning data."""
        summary = {"total_sites": len(self.learning_data), "sites": {}}

        for domain, site_data in self.learning_data.items():
            summary["sites"][domain] = {
                "total_attempts": site_data.total_attempts,
                "success_rate": site_data.success_rate,
                "successful_selectors": len(site_data.successful_selectors),
                "failed_selectors": len(site_data.failed_selectors),
                "last_updated": site_data.last_updated,
            }

        return summary

    def generate_adaptive_config(self, url: str) -> Dict[str, Any]:
        """Generate an adaptive configuration for a site based on learning data."""
        domain = urlparse(url).netloc.lower()
        best_selectors = self.get_best_selectors_for_site(url)

        if not best_selectors:
            return {}

        # Generate configuration
        config = {
            "selectors": best_selectors,
            "wait_time": 3,
            "use_selenium": True,  # Default to True for better success
            "confidence": 0.0,
        }

        # Calculate overall confidence
        if domain in self.learning_data:
            site_data = self.learning_data[domain]
            config["confidence"] = site_data.success_rate

        return config

    def cleanup_old_data(self, days_old: int = 30):
        """Remove learning data older than specified days."""
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)

        for domain, site_data in list(self.learning_data.items()):
            try:
                last_updated = datetime.fromisoformat(
                    site_data.last_updated
                ).timestamp()
                if last_updated < cutoff_date:
                    del self.learning_data[domain]
                    self.logger.info(f"Removed old learning data for {domain}")
            except Exception as e:
                self.logger.warning(f"Error processing date for {domain}: {e}")

        self.save_learning_data()

    def export_learning_data(self, filename: str):
        """Export learning data to a file."""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.get_learning_summary(), f, indent=2, ensure_ascii=False)
            self.logger.info(f"Learning data exported to {filename}")
        except Exception as e:
            self.logger.error(f"Error exporting learning data: {e}")

    def import_learning_data(self, filename: str):
        """Import learning data from a file."""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                # This would need to be implemented based on the export format
                self.logger.info(f"Learning data imported from {filename}")
        except Exception as e:
            self.logger.error(f"Error importing learning data: {e}")
