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
        self,
        url: str,
        config: Dict,
        max_retries: int = 3,
        retry_delay: int = 2,
        **kwargs,
    ):
        """
        Initialize the scraper with all its components.

        Args:
            url: Target URL for data fetching
            config: Configuration dictionary
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries in seconds
            **kwargs: Legacy keyword arguments (deprecated)
        """
        import warnings

        # Handle legacy keyword arguments for backward compatibility
        if kwargs:
            # Map known legacy kwargs to config
            if "headless" in kwargs:
                warnings.warn(
                    "The 'headless' parameter is deprecated and will be removed in v1.1.0. "
                    "Please use config['selenium']['headless'] instead.",
                    DeprecationWarning,
                    stacklevel=2,
                )
                # Ensure selenium config exists
                if "selenium" not in config:
                    config["selenium"] = {}
                if "driver" not in config["selenium"]:
                    config["selenium"]["driver"] = {}
                config["selenium"]["driver"]["headless"] = kwargs.pop("headless")

            if "js_render" in kwargs:
                warnings.warn(
                    "The 'js_render' parameter is deprecated and will be removed in v1.1.0. "
                    "Please use config settings instead.",
                    DeprecationWarning,
                    stacklevel=2,
                )
                # Log and ignore for now
                log_message(
                    "WARN",
                    f"Legacy parameter 'js_render' ignored: {kwargs.pop('js_render')}",
                )

            if "timeout" in kwargs:
                warnings.warn(
                    "The 'timeout' parameter is deprecated and will be removed in v1.1.0. "
                    "Please use config['timeout'] instead.",
                    DeprecationWarning,
                    stacklevel=2,
                )
                config["timeout"] = kwargs.pop("timeout")

            # Log any unknown kwargs but don't crash
            if kwargs:
                log_message(
                    "WARN", f"Unknown keyword arguments ignored: {list(kwargs.keys())}"
                )

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

        # Step 2: Fetch raw data with automatic fallback
        raw_data = self._fetch_raw_data_with_fallback()

        if not raw_data:
            log_message(
                "WARNING", "No data extracted from the page after all attempts."
            )
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

    def _fetch_raw_data_with_fallback(self) -> List[Dict]:
        """
        Fetch raw data with automatic fallback to advanced methods when empty.

        Fallback chain:
        1. Try initial fetch (respects site_profile.use_selenium)
        2. If empty, retry with forced browser automation
        3. If empty, try Playwright (if available)
        4. If empty, try requests-html (if available)

        Returns:
            list: Raw extracted data from the first successful method
        """
        # Step 1: Try initial fetch
        log_message("INFO", "Attempting initial data fetch...")
        raw_data = self._fetch_raw_data()

        if raw_data:
            log_message(
                "INFO", f"Initial fetch successful: {len(raw_data)} items extracted"
            )
            return raw_data

        log_message(
            "INFO", "Extracted 0 items from initial fetch → continuing fallback..."
        )

        # Step 2: Retry with forced browser automation (if not already used)
        if not (self.site_profile and self.site_profile.use_selenium):
            log_message("INFO", "Fallback 1: Trying browser automation (Selenium)...")
            try:
                response = self.initializer.stealth_manager.fetch_with_stealth(
                    url=self.url, method="GET", use_browser=True  # Force browser usage
                )

                if response and response.text:
                    raw_data = self.data_extractor.extract_data(
                        response.text, self.site_profile
                    )
                    if raw_data:
                        log_message(
                            "INFO",
                            f"Browser automation successful: {len(raw_data)} items extracted",
                        )
                        return raw_data
                    else:
                        log_message(
                            "INFO",
                            "Extracted 0 items from browser automation → continuing fallback...",
                        )
            except Exception as e:
                log_message("INFO", f"Browser automation fallback failed: {e}")
        else:
            log_message("INFO", "Skipping browser automation fallback (already tried)")

        # Step 3: Try Playwright if available
        if (
            hasattr(self.initializer.stealth_manager, "cloudflare_bypass")
            and self.initializer.stealth_manager.cloudflare_bypass
        ):
            # Check if Playwright is available
            try:
                from scraper.anti_bot.cloudflare_bypass import PLAYWRIGHT_AVAILABLE

                if PLAYWRIGHT_AVAILABLE:
                    log_message(
                        "INFO", "Fallback 2: Trying Playwright browser automation..."
                    )
                    try:
                        import asyncio

                        # Use existing async wrapper pattern
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        content = loop.run_until_complete(
                            self.initializer.stealth_manager.cloudflare_bypass.bypass_with_playwright(
                                self.url
                            )
                        )
                        loop.close()

                        if content:
                            raw_data = self.data_extractor.extract_data(
                                content, self.site_profile
                            )
                            if raw_data:
                                log_message(
                                    "INFO",
                                    f"Playwright successful: {len(raw_data)} items extracted",
                                )
                                return raw_data
                            else:
                                log_message(
                                    "INFO",
                                    "Extracted 0 items from Playwright → continuing fallback...",
                                )
                    except Exception as e:
                        log_message("INFO", f"Playwright fallback failed: {e}")
            except ImportError:
                pass  # Playwright not available

        # Step 4: Try requests-html if available
        if (
            hasattr(self.initializer.stealth_manager, "cloudflare_bypass")
            and self.initializer.stealth_manager.cloudflare_bypass
        ):
            try:
                from scraper.anti_bot.cloudflare_bypass import REQUESTS_HTML_AVAILABLE

                if REQUESTS_HTML_AVAILABLE:
                    log_message(
                        "INFO", "Fallback 3: Trying requests-html (JS rendering)..."
                    )
                    try:
                        response = self.initializer.stealth_manager.cloudflare_bypass.bypass_with_requests_html(
                            self.url
                        )

                        if response and response.text:
                            raw_data = self.data_extractor.extract_data(
                                response.text, self.site_profile
                            )
                            if raw_data:
                                log_message(
                                    "INFO",
                                    f"Requests-html successful: {len(raw_data)} items extracted",
                                )
                                return raw_data
                            else:
                                log_message(
                                    "INFO",
                                    "Extracted 0 items from requests-html → all fallbacks exhausted",
                                )
                    except Exception as e:
                        log_message("INFO", f"Requests-html fallback failed: {e}")
            except ImportError:
                pass  # Requests-html not available

        # All fallback methods exhausted
        log_message("INFO", "All fallback methods exhausted, no data found")
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
