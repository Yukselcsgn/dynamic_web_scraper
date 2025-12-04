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
Data fetching module for the scraper.

This module handles fetching data from URLs with retry logic and error handling.
"""

import time
from datetime import datetime
from typing import Dict, List, Optional

import requests
from requests.exceptions import HTTPError, Timeout

from scraper.logging_manager.logging_manager import log_message


class DataFetcher:
    """
    Handles data fetching from URLs with advanced retry logic and error handling.
    """

    def __init__(self, stealth_manager, stats: Dict):
        """
        Initialize the data fetcher.

        Args:
            stealth_manager: Stealth manager instance for advanced fetching
            stats: Statistics dictionary for tracking
        """
        self.stealth_manager = stealth_manager
        self.stats = stats

    def fetch_data(
        self,
        url: str,
        max_retries: int = 3,
        retry_delay: int = 2,
        enable_smart_detection: bool = True,
        enable_enrichment: bool = True,
        enable_analysis: bool = True,
    ) -> Dict:
        """
        Enhanced data fetching with smart detection, enrichment, and analysis.

        Args:
            url: Target URL
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries
            enable_smart_detection: Whether to use smart site detection
            enable_enrichment: Whether to enrich the data
            enable_analysis: Whether to perform price analysis

        Returns:
            dict: Comprehensive scraping results
        """
        start_time = datetime.now()

        # Step 1: Smart Site Detection
        # Note: Site detection is handled by the main scraper, not here

        # Step 2: Fetch Data
        raw_data = self._fetch_raw_data(url, max_retries, retry_delay)

        if not raw_data:
            log_message("WARNING", "No data extracted from the page.")
            return self._create_empty_result()

        # Step 3: Data Enrichment
        enriched_data = raw_data
        if enable_enrichment:
            log_message("INFO", "Enriching extracted data...")
            # Note: This would need to be passed from the main scraper
            # self.enrichment_result = self.data_enricher.enrich_data(raw_data)
            # enriched_data = self.enrichment_result.enriched_data

        # Update statistics
        self.stats["processing_time"] = (datetime.now() - start_time).total_seconds()
        self.stats["data_items_extracted"] = len(raw_data)

        return {
            "raw_data": raw_data,
            "enriched_data": enriched_data,
            "processing_time": self.stats["processing_time"],
            "data_items_extracted": len(raw_data),
        }

    def _fetch_raw_data(
        self, url: str, max_retries: int, retry_delay: int
    ) -> List[Dict]:
        """
        Fetch raw data from the URL with advanced stealth techniques.

        Args:
            url: Target URL
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries

        Returns:
            list: Extracted product information

        Raises:
            Exception: If data fetching fails after maximum retries
        """
        for attempt in range(max_retries):
            try:
                self.stats["requests_made"] += 1

                # Determine if we need browser automation
                use_browser = False
                if (
                    hasattr(self, "site_profile")
                    and self.site_profile
                    and self.site_profile.use_selenium
                ):
                    use_browser = True
                elif "sahibinden.com" in url.lower():
                    # Force browser automation for sahibinden.com
                    use_browser = True
                    log_message("INFO", "Forcing browser automation for sahibinden.com")

                # Use stealth manager for advanced anti-bot evasion
                response = self.stealth_manager.fetch_with_stealth(
                    url=url, method="GET", use_browser=use_browser
                )

                response.raise_for_status()

                self.stats["successful_requests"] += 1

                # Parse the response
                data = self.parse_response(response.text)

                if data:
                    log_message(
                        "INFO", f"Successfully extracted {len(data)} items from {url}"
                    )
                    return data
                else:
                    log_message("WARNING", f"No data extracted from {url}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    else:
                        return []

            except (HTTPError, Timeout, requests.exceptions.RequestException) as e:
                self.stats["failed_requests"] += 1
                log_message(
                    "ERROR",
                    f"Request failed (attempt {attempt + 1}/{max_retries}): {e}",
                )

                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    raise Exception(
                        f"Failed to fetch data after {max_retries} attempts: {e}"
                    )

            except Exception as e:
                self.stats["failed_requests"] += 1
                log_message(
                    "ERROR",
                    f"Unexpected error (attempt {attempt + 1}/{max_retries}): {e}",
                )

                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    raise Exception(
                        f"Failed to fetch data after {max_retries} attempts: {e}"
                    )

        return []

    def parse_response(self, response_text: str) -> List[Dict]:
        """
        Parse the response text and extract data.

        Args:
            response_text: Raw response text

        Returns:
            list: Extracted data items
        """
        try:
            # This is a placeholder - the actual parsing logic would be implemented
            # based on the specific site being scraped
            log_message("INFO", f"Parsing response of {len(response_text)} characters")

            # For now, return empty list - this would be implemented with actual parsing logic
            return []

        except Exception as e:
            log_message("ERROR", f"Error parsing response: {e}")
            return []

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
