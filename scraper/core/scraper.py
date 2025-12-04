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
Main Scraper class that combines all core functionality.

This module provides the main Scraper class that orchestrates all the core
functionality including initialization, data fetching, site detection,
data extraction, processing, and utilities.
"""

import os
import sys
from typing import Any, Dict, List, Optional

# Add the project root to the path for absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.logging_manager.logging_manager import log_message

from .data_extraction import DataExtractor
from .data_fetching import DataFetcher
from .data_processing import DataProcessor

# Import core modules
from .initialization import ScraperInitializer
from .site_detection import SiteDetector
from .utilities import ScraperUtilities


class Scraper:
    """
    Enhanced Scraper class with modular architecture.

    This class combines all the core functionality into a single interface
    while maintaining separation of concerns through modular design.
    """

    def __init__(
        self, url: str, config: Dict, max_retries: int = 3, retry_delay: int = 2
    ):
        """
        Initialize the scraper with all its components.

        Args:
            url: Target URL for data fetching
            config: Configuration dictionary
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.url = url
        self.config = config
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        log_message("INFO", f"Initializing scraper for URL: {url}")

        # Initialize all components
        self._initialize_components()

        log_message("INFO", "Scraper initialization completed")

    def _initialize_components(self):
        """Initialize all scraper components."""
        # Initialize the main initializer
        self.initializer = ScraperInitializer(
            self.url, self.config, self.max_retries, self.retry_delay
        )

        # Initialize site detector
        self.site_detector = SiteDetector(self.initializer.smart_detector)

        # Initialize data extractor
        self.data_extractor = DataExtractor(self.initializer.universal_extractor)

        # Initialize data fetcher
        self.data_fetcher = DataFetcher(
            self.initializer.stealth_manager, self.initializer.stats
        )

        # Initialize data processor
        self.data_processor = DataProcessor(
            self.initializer.data_enricher,
            self.initializer.price_analyzer,
            self.initializer.data_visualizer,
            self.initializer.automated_reporter,
            self.initializer.site_comparator,
            self.initializer.plugin_manager,
        )

        # Initialize utilities
        self.utilities = ScraperUtilities(self.initializer.export_manager)

        # Expose commonly used attributes for backward compatibility
        self.user_agent_manager = self.initializer.user_agent_manager
        self.proxy_rotator = self.initializer.proxy_rotator
        self.session = self.initializer.session
        self.stats = self.initializer.stats
        self.site_profile = None

    def get_headers(self) -> Dict[str, str]:
        """
        Get headers for HTTP requests.

        Returns:
            Dictionary of HTTP headers
        """
        return self.initializer.get_headers()

    def get_proxy(self) -> Optional[Dict[str, str]]:
        """
        Get proxy configuration for requests.

        Returns:
            Proxy configuration dictionary or None
        """
        return self.initializer.get_proxy()

    def detect_site_profile(self, html_content: str = None) -> None:
        """
        Detect the site profile for smart scraping.

        Args:
            html_content: HTML content to analyze (optional)
        """
        self.site_profile = self.site_detector.detect_site_profile(
            self.url, html_content
        )

    def fetch_data(
        self,
        enable_smart_detection: bool = True,
        enable_enrichment: bool = True,
        enable_analysis: bool = True,
    ) -> Dict:
        """
        Enhanced data fetching with smart detection, enrichment, and analysis.

        Args:
            enable_smart_detection: Whether to use smart site detection
            enable_enrichment: Whether to enrich the data
            enable_analysis: Whether to perform price analysis

        Returns:
            dict: Comprehensive scraping results
        """
        log_message("INFO", f"Starting data fetching for: {self.url}")

        # Step 1: Detect site profile if enabled
        if enable_smart_detection:
            self.detect_site_profile()

        # Step 2: Fetch raw data
        raw_data = self._fetch_raw_data()

        if not raw_data:
            log_message("WARNING", "No data extracted from the page.")
            return self._create_empty_result()

        # Step 3: Process the data
        results = self._process_data(raw_data, enable_enrichment, enable_analysis)

        log_message(
            "INFO", f"Data fetching completed. Extracted {len(raw_data)} items."
        )
        return results

    def _fetch_raw_data(self) -> List[Dict]:
        """
        Fetch raw data from the URL.

        Returns:
            list: Raw extracted data
        """
        try:
            # Use the stealth manager to get the response
            response = self.initializer.stealth_manager.fetch_with_stealth(
                url=self.url,
                method="GET",
                use_browser=self.site_profile.use_selenium
                if self.site_profile
                else False,
            )

            if not response or not response.text:
                return []

            # Parse the response and extract data
            return self.data_extractor.extract_data(response.text, self.site_profile)

        except Exception as e:
            log_message("ERROR", f"Error fetching raw data: {e}")
            return []

    def _process_data(
        self, raw_data: List[Dict], enable_enrichment: bool, enable_analysis: bool
    ) -> Dict:
        """
        Process the raw data through various stages.

        Args:
            raw_data: Raw extracted data
            enable_enrichment: Whether to enrich the data
            enable_analysis: Whether to perform analysis

        Returns:
            dict: Processed results
        """
        results = {
            "raw_data": raw_data,
            "enriched_data": raw_data,
            "processing_time": self.stats.get("processing_time", 0),
            "data_items_extracted": len(raw_data),
        }

        # Step 1: Data enrichment
        if enable_enrichment and raw_data:
            enrichment_result = self.data_processor.enrich_data(raw_data)
            if enrichment_result:
                results["enrichment_result"] = enrichment_result
                results["enriched_data"] = getattr(
                    enrichment_result, "enriched_data", raw_data
                )

        # Step 2: Price analysis
        if enable_analysis and raw_data:
            price_analysis = self.data_processor.analyze_prices(raw_data)
            if price_analysis:
                results["price_analysis"] = price_analysis

        # Step 3: Comparative analysis
        if raw_data:
            comparison_analysis = self.data_processor.perform_comparative_analysis(
                raw_data
            )
            if comparison_analysis:
                results["comparison_analysis"] = comparison_analysis

        # Step 4: Data visualization
        if raw_data:
            visualization_results = self.data_processor.create_data_visualizations(
                raw_data
            )
            if visualization_results:
                results["visualization_results"] = visualization_results

        # Step 5: Distributed processing
        if raw_data:
            distributed_results = self.data_processor.process_distributed(raw_data)
            if distributed_results:
                results["distributed_results"] = distributed_results

        # Step 6: Plugin processing
        if raw_data:
            plugin_results = self.data_processor.process_with_plugins(raw_data)
            if plugin_results:
                results["plugin_results"] = plugin_results

        # Step 7: Automated reporting
        if raw_data:
            reporting_results = self.data_processor.generate_automated_report(raw_data)
            if reporting_results:
                results["reporting_results"] = reporting_results

        return results

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
        return self.utilities.save_data(data, file_name, format)

    def parse_html(self, response_text: str):
        """
        Parse HTML response text.

        Args:
            response_text: Raw HTML text

        Returns:
            BeautifulSoup: Parsed HTML object
        """
        return self.utilities.parse_html(response_text)

    def analyze_html_content(self, html_content: str, filename: str = None) -> Dict:
        """
        Analyze HTML content for debugging and optimization.

        Args:
            html_content: HTML content to analyze
            filename: Optional filename for saving analysis

        Returns:
            dict: Analysis results
        """
        return self.utilities.analyze_html_content(html_content, filename)

    def create_debug_summary(self, url: str, html_content: str = None) -> Dict:
        """
        Create a debug summary for troubleshooting.

        Args:
            url: Target URL
            html_content: HTML content (optional)

        Returns:
            dict: Debug summary
        """
        return self.utilities.create_debug_summary(url, html_content)

    def get_scraping_report(self) -> Dict:
        """
        Generate a comprehensive scraping report.

        Returns:
            dict: Scraping report
        """
        return self.utilities.get_scraping_report(self.stats)

    def _create_empty_result(self) -> Dict:
        """
        Create an empty result structure.

        Returns:
            dict: Empty result structure
        """
        return {
            "raw_data": [],
            "enriched_data": [],
            "processing_time": 0,
            "data_items_extracted": 0,
        }

    def cleanup(self):
        """Cleanup resources."""
        try:
            if hasattr(self.initializer, "stealth_manager"):
                self.initializer.stealth_manager.cleanup()

            if hasattr(self.initializer, "session"):
                self.initializer.session.close()

            log_message("INFO", "Scraper cleanup completed")

        except Exception as e:
            log_message("ERROR", f"Error during cleanup: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()

    # Backward compatibility methods
    def perform_comparative_analysis(self, data: List[Dict]) -> Dict:
        """Backward compatibility method."""
        return self.data_processor.perform_comparative_analysis(data)

    def create_data_visualizations(self, data: List[Dict]) -> List[str]:
        """Backward compatibility method."""
        return self.data_processor.create_data_visualizations(data)

    def process_distributed(self, data: List[Dict]) -> Dict:
        """Backward compatibility method."""
        return self.data_processor.process_distributed(data)

    def process_with_plugins(self, data: List[Dict]) -> Dict:
        """Backward compatibility method."""
        return self.data_processor.process_with_plugins(data)

    def generate_automated_report(self, data: List[Dict]) -> Dict:
        """Backward compatibility method."""
        return self.data_processor.generate_automated_report(data)
