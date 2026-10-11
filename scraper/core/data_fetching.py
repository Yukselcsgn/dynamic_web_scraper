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

import logging
import time
from datetime import datetime
from typing import Dict, List

from requests.exceptions import RequestException

from scraper.logging_manager.logging_manager import log_message
from scraper.proxy_manager.proxy_formatter import redact_proxy_credentials

logger = logging.getLogger(__name__)


class DataFetcher:
    """
    Handles data fetching from URLs with advanced retry logic and error handling.
    """

    def __init__(
        self,
        stealth_manager,
        stats: Dict,
        extractor=None,
        site_profile=None,
    ):
        """
        Initialize the data fetcher.

        Args:
            stealth_manager: Stealth manager instance for advanced fetching
            stats: Statistics dictionary for tracking
            extractor: Object exposing ``extract_data(html, site_profile)``
                (e.g. ``DataExtractor``); required for parsing
            site_profile: Optional detected site profile
        """
        self.stealth_manager = stealth_manager
        self.stats = stats
        self.extractor = extractor
        self.site_profile = site_profile

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
        Fetch the page (with transport retries) and parse it exactly once.

        Args:
            url: Target URL
            max_retries: Maximum transport-level attempts
            retry_delay: Delay between attempts in seconds

        Returns:
            list: Extracted items (empty if the page contained none)

        Raises:
            Exception: If the request fails on every attempt
        """
        html = self._fetch_html(url, max_retries, retry_delay)

        data = self.parse_response(html)
        if data:
            logger.info("Successfully extracted %d items from %s", len(data), url)
        else:
            # The request succeeded, so re-requesting the same URL cannot
            # change the parse result: do not burn retries/proxy traffic here.
            logger.warning("No data extracted from %s", url)
        return data

    def _fetch_html(self, url: str, max_retries: int, retry_delay: int) -> str:
        """
        Download ``url`` through the stealth manager.

        Retries only on request-level failures (timeouts, connection errors,
        HTTP error statuses). Returns the response body on the first success.
        """
        use_browser = bool(self.site_profile and self.site_profile.use_selenium)
        if not use_browser and "sahibinden.com" in url.lower():
            use_browser = True
            logger.info("Forcing browser automation for sahibinden.com")

        for attempt in range(max_retries):
            self.stats["requests_made"] += 1
            try:
                response = self.stealth_manager.fetch_with_stealth(
                    url=url,
                    method="GET",
                    use_browser=use_browser,
                    site_profile=self.site_profile,
                )
                response.raise_for_status()
            except RequestException as e:
                self.stats["failed_requests"] += 1
                logger.error(
                    "Request failed (attempt %d/%d): %s",
                    attempt + 1,
                    max_retries,
                    redact_proxy_credentials(e),
                )
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                raise Exception(
                    f"Failed to fetch data after {max_retries} attempts: "
                    f"{redact_proxy_credentials(e)}"
                ) from e

            self.stats["successful_requests"] += 1
            return response.text or ""

        return ""

    def parse_response(self, response_text: str) -> List[Dict]:
        """
        Parse the response text and extract data.

        Delegates to the injected extractor (``DataExtractor.extract_data``)
        using the current ``site_profile``.

        Args:
            response_text: Raw response text

        Returns:
            list: Extracted data items (empty when nothing matched or when no
            extractor is configured)
        """
        if self.extractor is None:
            logger.error(
                "DataFetcher has no extractor configured; cannot parse response. "
                "Pass extractor=DataExtractor(...) when constructing DataFetcher."
            )
            return []

        if not response_text:
            return []

        logger.info("Parsing response of %d characters", len(response_text))
        try:
            return self.extractor.extract_data(response_text, self.site_profile) or []
        except (ValueError, TypeError, AttributeError, KeyError) as e:
            # Parsing bugs are deterministic: report them, never retry the request.
            logger.error("Error parsing response: %s", e, exc_info=True)
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
