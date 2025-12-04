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
Scraper initialization and configuration module.

This module handles the initialization of the scraper and its various components.
"""

from typing import Dict, List, Optional

import requests

from scraper.adaptive_config_manager import AdaptiveConfigManager
from scraper.analytics import DataVisualizer
from scraper.analytics.price_analyzer import PriceAnalyzer
from scraper.anti_bot.stealth_manager import StealthManager
from scraper.comparison import SiteComparator
from scraper.data_processing.data_enricher import DataEnricher
from scraper.distributed import JobQueue, WorkerPool
from scraper.export import ExportConfig, ExportManager
from scraper.logging_manager.logging_manager import log_message
from scraper.plugins import PluginManager
from scraper.proxy_manager.proxy_rotator import ProxyRotator
from scraper.reporting import AlertConfig, AutomatedReporter, ReportConfig
from scraper.site_detection.smart_detector import SmartSiteDetector
from scraper.universal_extractor import UniversalExtractor
from scraper.user_agent_manager.user_agent_manager import UserAgentManager


class ScraperInitializer:
    """
    Handles initialization of the scraper and all its components.
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

        # Initialize basic components
        self._init_basic_components()

        # Initialize advanced features
        self._init_advanced_features()

        # Initialize managers
        self._init_managers()

        # Initialize distributed components
        self._init_distributed_components()

        # Initialize statistics
        self._init_statistics()

    def _init_basic_components(self):
        """Initialize basic scraper components."""
        # Initialize user agent and proxy managers
        user_agents = self.config.get("user_agents", [])
        log_message(
            "INFO", f"Initializing UserAgentManager with {len(user_agents)} user agents"
        )
        log_message(
            "INFO", f"User agents: {user_agents[:2] if user_agents else 'None'}"
        )

        self.user_agent_manager = UserAgentManager(user_agents)
        self.proxy_rotator = ProxyRotator(self.config.get("proxies", []))
        self.session = requests.Session()

    def _init_advanced_features(self):
        """Initialize advanced scraper features."""
        self.smart_detector = SmartSiteDetector()
        self.data_enricher = DataEnricher()
        self.price_analyzer = PriceAnalyzer()
        self.stealth_manager = StealthManager(self.config)
        self.universal_extractor = UniversalExtractor()
        self.adaptive_config_manager = AdaptiveConfigManager()

    def _init_managers(self):
        """Initialize various managers."""
        # Initialize export manager
        export_config = ExportConfig(
            export_directory="exports", default_format="json", include_metadata=True
        )
        self.export_manager = ExportManager("data", export_config)

        # Initialize site comparator
        self.site_comparator = SiteComparator("data")

        # Initialize automated reporter
        report_config = ReportConfig(
            report_directory="reports",
            include_charts=True,
            include_recommendations=True,
        )
        alert_config = AlertConfig(
            price_drop_threshold=10.0,
            price_increase_threshold=15.0,
            anomaly_threshold=2.0,
        )
        self.automated_reporter = AutomatedReporter("data", alert_config, report_config)

        # Initialize data visualizer
        self.data_visualizer = DataVisualizer("data/visualizations")

        # Initialize plugin manager
        self.plugin_manager = PluginManager("plugins")

    def _init_distributed_components(self):
        """Initialize distributed scraping components."""
        self.job_queue = JobQueue()
        self.worker_pool = WorkerPool(self.job_queue, num_workers=3)

        # Initialize distributed scraping for large-scale operations
        self.distributed_enabled = self.config.get("distributed_scraping", False)
        if self.distributed_enabled:
            log_message("INFO", "Distributed scraping enabled")

    def _init_statistics(self):
        """Initialize statistics tracking."""
        self.stats = {
            "requests_made": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "data_items_extracted": 0,
            "processing_time": 0,
            "start_time": None,
            "end_time": None,
        }

        # Initialize enrichment result
        self.enrichment_result = None
        self.price_analysis = None

    def get_headers(self) -> Dict[str, str]:
        """
        Get headers for HTTP requests.

        Returns:
            Dictionary of HTTP headers
        """
        headers = {
            "User-Agent": self.user_agent_manager.get_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        # Add custom headers from config
        custom_headers = self.config.get("headers", {})
        headers.update(custom_headers)

        return headers

    def get_proxy(self) -> Optional[Dict[str, str]]:
        """
        Get proxy configuration for requests.

        Returns:
            Proxy configuration dictionary or None
        """
        proxy = self.proxy_rotator.rotate_proxy()
        if proxy:
            return {
                "http": proxy,
                "https": proxy,
            }
        return None
