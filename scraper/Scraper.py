import requests
import time
from bs4 import BeautifulSoup
import sys
import os
from typing import Optional
from datetime import datetime

# Add the project root to the path for absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.logging_manager.logging_manager import log_message
from scraper.exceptions.scraper_exceptions import ProxyError, UserAgentError
from requests.exceptions import HTTPError, Timeout
from scraper.user_agent_manager.user_agent_manager import UserAgentManager
from scraper.proxy_manager.proxy_rotator import ProxyRotator

from scraper.data_parsers.data_parser import save_data
from scraper.site_detection.smart_detector import SmartSiteDetector, SiteProfile
from scraper.data_processing.data_enricher import DataEnricher
from scraper.analytics.price_analyzer import PriceAnalyzer


class Scraper:
    def __init__(self, url, config, max_retries=3, retry_delay=2):
        """
        Enhanced Scraper class with smart detection, data enrichment, and analytics.

        Args:
            url (str): Target URL for data fetching.
            config (dict): Configuration for user agents, proxies, and selectors.
            max_retries (int): Maximum retry attempts. Default: 3.
            retry_delay (int): Delay between retries in seconds. Default: 2.
        """
        self.url = url
        self.config = config
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Initialize managers
        self.user_agent_manager = UserAgentManager(config.get("user_agents", []))
        self.proxy_rotator = ProxyRotator(config.get("proxies", []))
        self.session = requests.Session()

        # Initialize advanced features
        self.smart_detector = SmartSiteDetector()
        self.data_enricher = DataEnricher()
        self.price_analyzer = PriceAnalyzer()

        # Site profile (will be detected automatically)
        self.site_profile: Optional[SiteProfile] = None

        # Analysis results
        self.enrichment_result = None
        self.price_analysis = None

        # Scraping statistics
        self.stats = {
            "start_time": datetime.now(),
            "requests_made": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "data_items_extracted": 0,
            "processing_time": 0,
        }

    def get_headers(self):
        """
        Generate HTTP headers using a random user agent.

        Returns:
            dict: HTTP headers.

        Raises:
            UserAgentError: If no user agents are available.
        """
        try:
            user_agent = self.user_agent_manager.get_user_agent()
            if not user_agent:
                raise UserAgentError(
                    user_agent=None,
                    message="No user agent available.",
                    suggestion="Please check your config.json and ensure at least one user agent is provided.",
                )
            return {"User-Agent": user_agent}
        except UserAgentError as e:
            log_message("ERROR", f"User agent error: {str(e)}")
            raise

    def get_proxy(self):
        """
        Select a random proxy from the configuration.

        Returns:
            dict: Proxy settings for HTTP and HTTPS.

        Raises:
            ProxyError: If no proxies are available.
        """
        if not self.config.get("use_proxy", False):
            return None

        try:
            proxy = self.proxy_rotator.rotate_proxy()
            if not proxy:
                raise ProxyError(
                    proxy=None,
                    message="Proxy list is empty!",
                    suggestion="Please check your config.json and ensure at least one proxy is provided, or disable proxy usage.",
                )
            return {"http": f"http://{proxy}", "https": f"https://{proxy}"}
        except ProxyError as e:
            log_message("ERROR", f"Proxy error: {str(e)}")
            raise

    def detect_site_profile(self, html_content: str = None) -> SiteProfile:
        """
        Automatically detect site characteristics and generate optimal scraping profile.

        Args:
            html_content: Optional HTML content (if not provided, will fetch)

        Returns:
            SiteProfile with optimal scraping configuration
        """
        log_message("INFO", f"Detecting site profile for: {self.url}")

        try:
            if not html_content:
                # Fetch a small sample for detection
                headers = self.get_headers()
                proxies = self.get_proxy()
                response = requests.get(
                    self.url, headers=headers, proxies=proxies, timeout=10
                )
                response.raise_for_status()
                html_content = response.text

            self.site_profile = self.smart_detector.detect_site(self.url, html_content)

            log_message(
                "INFO",
                f"Site detected as: {self.site_profile.site_type} (confidence: {self.site_profile.confidence:.2f})",
            )
            log_message(
                "INFO",
                f"Anti-bot measures detected: {self.site_profile.anti_bot_measures}",
            )
            log_message(
                "INFO", f"Recommended wait time: {self.site_profile.wait_time}s"
            )
            log_message("INFO", f"Use Selenium: {self.site_profile.use_selenium}")

            return self.site_profile

        except Exception as e:
            log_message(
                "WARNING", f"Site detection failed: {e}. Using default profile."
            )
            self.site_profile = self.smart_detector._get_default_profile()
            return self.site_profile

    def fetch_data(
        self,
        enable_smart_detection: bool = True,
        enable_enrichment: bool = True,
        enable_analysis: bool = True,
    ):
        """
        Enhanced data fetching with smart detection, enrichment, and analysis.

        Args:
            enable_smart_detection: Whether to use smart site detection
            enable_enrichment: Whether to enrich the data
            enable_analysis: Whether to perform price analysis

        Returns:
            dict: Comprehensive scraping results including raw data, enriched data, and analysis
        """
        start_time = datetime.now()

        # Step 1: Smart Site Detection
        if enable_smart_detection:
            self.detect_site_profile()

        # Step 2: Fetch Data
        raw_data = self._fetch_raw_data()

        if not raw_data:
            log_message("WARNING", "No data extracted from the page.")
            return self._create_empty_result()

        # Step 3: Data Enrichment
        enriched_data = raw_data
        if enable_enrichment:
            log_message("INFO", "Enriching extracted data...")
            self.enrichment_result = self.data_enricher.enrich_data(raw_data)
            enriched_data = self.enrichment_result.enriched_data

            log_message(
                "INFO",
                f"Data enrichment completed. Quality score: {self.enrichment_result.quality_score:.2f}",
            )

        # Step 4: Price Analysis
        price_analysis = None
        if enable_analysis and enriched_data:
            log_message("INFO", "Performing price analysis...")
            self.price_analysis = self.price_analyzer.analyze_prices(enriched_data)
            price_analysis = self.price_analysis

            log_message(
                "INFO",
                f"Price analysis completed. Found {len(price_analysis.outliers)} outliers.",
            )

        # Update statistics
        self.stats["processing_time"] = (datetime.now() - start_time).total_seconds()
        self.stats["data_items_extracted"] = len(raw_data)

        return {
            "raw_data": raw_data,
            "enriched_data": enriched_data,
            "enrichment_result": self.enrichment_result,
            "price_analysis": price_analysis,
            "site_profile": self.site_profile,
            "stats": self.stats,
            "timestamp": datetime.now().isoformat(),
        }

    def _fetch_raw_data(self):
        """
        Fetch raw data from the URL with retry logic.

        Returns:
            list: Extracted product information.

        Raises:
            Exception: If data fetching fails after maximum retries.
        """
        for attempt in range(self.max_retries):
            try:
                self.stats["requests_made"] += 1

                headers = self.get_headers()
                proxies = self.get_proxy()

                # Use site-specific settings if available
                timeout = self.site_profile.wait_time if self.site_profile else 10

                response = self.session.get(
                    self.url, headers=headers, proxies=proxies, timeout=timeout
                )
                response.raise_for_status()

                self.stats["successful_requests"] += 1

                log_message("INFO", f"Data successfully fetched from: {self.url}")

                # Parse and extract data
                raw_data = self.parse_response(response.text)

                # Apply site-specific wait time
                if self.site_profile:
                    time.sleep(self.site_profile.wait_time)

                return raw_data

            except (HTTPError, Timeout) as e:
                self.stats["failed_requests"] += 1
                log_message(
                    "WARNING",
                    f"Request failed: {str(e)}. Attempt {attempt + 1}/{self.max_retries}",
                )
                # Exponential backoff
                time.sleep(self.retry_delay * (2**attempt))
            except ProxyError as pe:
                log_message("ERROR", f"Proxy error: {str(pe)}")
            except UserAgentError as uae:
                log_message("ERROR", f"User agent error: {str(uae)}")

        log_message(
            "ERROR", f"Failed to fetch data: Maximum retries reached for {self.url}."
        )
        raise Exception("Data fetching failed.")

    def parse_response(self, response_text):
        """
        Enhanced response parsing with smart selector detection.

        Args:
            response_text (str): HTML content of the response.

        Returns:
            list: Extracted product information.
        """
        html_structure = self.parse_html(response_text)
        if not html_structure:
            log_message("ERROR", "Invalid result during HTML parsing.")
            raise ValueError("HTML parsing returned invalid result.")

        # Save HTML for debugging
        try:
            with open("response.html", "w", encoding="utf-8") as file:
                file.write(response_text)
            log_message("INFO", "HTML response successfully saved to 'response.html'.")
        except Exception as e:
            log_message("ERROR", f"Error saving HTML file: {str(e)}")

        # Use smart selectors if available
        if self.site_profile and self.site_profile.selectors:
            return self._extract_with_smart_selectors(html_structure)
        else:
            return self._extract_with_default_selectors(html_structure)

    def _extract_with_smart_selectors(self, html):
        """
        Extract data using smart-detected selectors.
        """
        products = []
        selectors = self.site_profile.selectors

        # Get container selector
        container_selector = selectors.get(
            "product_container", ".product, .item, .listing"
        )
        containers = html.select(container_selector)

        log_message(
            "INFO",
            f"Found {len(containers)} product containers using selector: {container_selector}",
        )

        for container in containers:
            try:
                product_data = {}

                # Extract title
                title_selector = selectors.get(
                    "product_title", ".title, .name, h1, h2, h3"
                )
                title_elem = container.select_one(title_selector)
                if title_elem:
                    product_data["title"] = title_elem.get_text(strip=True)

                # Extract price
                price_selector = selectors.get(
                    "product_price", '.price, .cost, [class*="price"]'
                )
                price_elem = container.select_one(price_selector)
                if price_elem:
                    product_data["price"] = price_elem.get_text(strip=True)

                # Extract image
                image_selector = selectors.get("product_image", "img")
                image_elem = container.select_one(image_selector)
                if image_elem:
                    product_data["image_url"] = image_elem.get("src", "")

                # Extract link
                link_selector = selectors.get("product_link", "a")
                link_elem = container.select_one(link_selector)
                if link_elem:
                    product_data["url"] = link_elem.get("href", "")

                # Add source URL
                product_data["source_url"] = self.url
                product_data["extraction_timestamp"] = datetime.now().isoformat()

                if product_data.get("title") or product_data.get("price"):
                    products.append(product_data)

            except Exception as e:
                log_message("ERROR", f"Error extracting product info: {str(e)}")

        return products

    def _extract_with_default_selectors(self, html):
        """
        Extract data using default selectors.
        """
        products = []

        # Try multiple common selectors
        selectors_to_try = [
            ("span", {"class": "product-name"}),
            ("div", {"class": "product-title"}),
            ("h1", {}),
            ("h2", {}),
            ("h3", {}),
        ]

        product_names = []
        for tag, attrs in selectors_to_try:
            found = html.find_all(tag, attrs)
            if found:
                product_names = found
                break

        # Try price selectors
        price_selectors = [
            ("span", {"class": "price"}),
            ("div", {"class": "price"}),
            ("span", {"class": "cost"}),
        ]

        product_prices = []
        for tag, attrs in price_selectors:
            found = html.find_all(tag, attrs)
            if found:
                product_prices = found
                break

        if not product_names:
            log_message("WARNING", "No product names found with default selectors.")
            return []

        log_message("DEBUG", f"Found product names: {len(product_names)}")
        log_message("DEBUG", f"Found product prices: {len(product_prices)}")

        for i, name in enumerate(product_names):
            try:
                product_data = {
                    "title": name.get_text(strip=True) if name else "Title not found",
                    "price": (
                        product_prices[i].get_text(strip=True)
                        if i < len(product_prices)
                        else "Price not found"
                    ),
                    "source_url": self.url,
                    "extraction_timestamp": datetime.now().isoformat(),
                }
                products.append(product_data)
            except AttributeError as e:
                log_message("ERROR", f"Error extracting product info: {str(e)}")

        return products

    def parse_html(self, response_text):
        """
        Parse the HTML response using BeautifulSoup.

        Args:
            response_text (str): HTML content.

        Returns:
            BeautifulSoup: Parsed HTML structure.
        """
        return BeautifulSoup(response_text, "html.parser")

    def save_data(self, data, file_name, format="csv"):
        """
        Enhanced data saving with multiple format support.
        """
        save_data(data, file_name, format)

        # Also save analysis results if available
        if self.enrichment_result:
            enriched_filename = file_name.replace(".csv", "_enriched.json")
            self.data_enricher.export_enriched_data(
                self.enrichment_result, "json", enriched_filename
            )
            log_message("INFO", f"Enriched data saved to: {enriched_filename}")

        if self.price_analysis:
            analysis_filename = file_name.replace(".csv", "_analysis.json")
            self.price_analyzer.export_analysis(
                self.price_analysis, "json", analysis_filename
            )
            log_message("INFO", f"Price analysis saved to: {analysis_filename}")

    def _create_empty_result(self):
        """Create empty result structure."""
        return {
            "raw_data": [],
            "enriched_data": [],
            "enrichment_result": None,
            "price_analysis": None,
            "site_profile": self.site_profile,
            "stats": self.stats,
            "timestamp": datetime.now().isoformat(),
        }

    def get_scraping_report(self):
        """
        Generate a comprehensive scraping report.

        Returns:
            dict: Detailed scraping statistics and results
        """
        report = {
            "url": self.url,
            "site_profile": {
                "site_type": (
                    self.site_profile.site_type if self.site_profile else "unknown"
                ),
                "confidence": (
                    self.site_profile.confidence if self.site_profile else 0.0
                ),
                "anti_bot_measures": (
                    self.site_profile.anti_bot_measures if self.site_profile else []
                ),
                "use_selenium": (
                    self.site_profile.use_selenium if self.site_profile else False
                ),
            },
            "statistics": self.stats,
            "data_summary": {
                "raw_items": (
                    len(self.enrichment_result.original_data)
                    if self.enrichment_result
                    else 0
                ),
                "enriched_items": (
                    len(self.enrichment_result.enriched_data)
                    if self.enrichment_result
                    else 0
                ),
                "quality_score": (
                    self.enrichment_result.quality_score
                    if self.enrichment_result
                    else 0.0
                ),
            },
            "price_analysis": {
                "outliers_found": (
                    len(self.price_analysis.outliers) if self.price_analysis else 0
                ),
                "recommendations": (
                    self.price_analysis.recommendations if self.price_analysis else []
                ),
            },
            "timestamp": datetime.now().isoformat(),
        }

        return report
