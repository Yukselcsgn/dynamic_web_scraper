import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

# Add the project root to the path for absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from requests.exceptions import HTTPError, Timeout

from scraper.adaptive_config_manager import AdaptiveConfigManager
from scraper.analytics import DataVisualizer
from scraper.analytics.price_analyzer import PriceAnalyzer
from scraper.anti_bot.stealth_manager import StealthManager
from scraper.comparison import SiteComparator
from scraper.data_parsers.data_parser import save_data
from scraper.data_processing.data_enricher import DataEnricher
from scraper.distributed import JobQueue, WorkerPool
from scraper.exceptions.scraper_exceptions import ProxyError, UserAgentError
from scraper.export import ExportConfig, ExportManager
from scraper.logging_manager.logging_manager import log_message
from scraper.plugins import PluginManager
from scraper.proxy_manager.proxy_rotator import ProxyRotator
from scraper.reporting import AlertConfig, AutomatedReporter, ReportConfig
from scraper.site_detection.smart_detector import SiteProfile, SmartSiteDetector
from scraper.universal_extractor import UniversalExtractor
from scraper.user_agent_manager.user_agent_manager import UserAgentManager


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
        user_agents = config.get("user_agents", [])
        log_message(
            "INFO", f"Initializing UserAgentManager with {len(user_agents)} user agents"
        )
        log_message(
            "INFO", f"User agents: {user_agents[:2] if user_agents else 'None'}"
        )  # Show first 2 user agents
        self.user_agent_manager = UserAgentManager(user_agents)
        self.proxy_rotator = ProxyRotator(config.get("proxies", []))
        self.session = requests.Session()

        # Initialize advanced features
        self.smart_detector = SmartSiteDetector()
        self.data_enricher = DataEnricher()
        self.price_analyzer = PriceAnalyzer()
        self.stealth_manager = StealthManager(config)
        self.universal_extractor = UniversalExtractor()
        self.adaptive_config_manager = AdaptiveConfigManager()

        # Initialize export manager
        export_config = ExportConfig(
            export_directory="exports", default_format="json", include_metadata=True
        )
        self.export_manager = ExportManager("data", export_config)

        # Initialize site comparator for cross-site analysis
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

        # Initialize distributed scraping components
        self.job_queue = JobQueue()
        self.worker_pool = WorkerPool(self.job_queue, num_workers=3)

        # Site profile (will be detected automatically)
        self.site_profile: Optional[SiteProfile] = None

        # Analysis results
        self.enrichment_result = None
        self.price_analysis = None
        self.comparison_analysis = None
        self.reporting_results = None
        self.visualization_results = None
        self.plugin_results = None
        self.distributed_results = None

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
                # Fetch a small sample for detection using stealth manager
                log_message(
                    "INFO",
                    "Fetching sample for site detection using stealth manager...",
                )
                response = self.stealth_manager.fetch_with_stealth(
                    url=self.url, method="GET", use_browser=False
                )
                response.raise_for_status()
                html_content = response.text

            self.site_profile = self.smart_detector.detect_site(
                self.url, html_content, self.user_agent_manager
            )

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
            # For sahibinden.com, create a specific profile even if detection fails
            if "sahibinden.com" in self.url.lower():
                log_message(
                    "INFO",
                    "Creating sahibinden-specific profile due to detection failure",
                )
                self.site_profile = self._create_sahibinden_profile()
            else:
                self.site_profile = self.smart_detector._get_default_profile()
            return self.site_profile

    def _create_sahibinden_profile(self):
        """
        Create a specific profile for sahibinden.com when detection fails.
        """
        from scraper.site_detection.smart_detector import SiteProfile

        # Create a profile specifically for sahibinden.com
        profile = SiteProfile(
            site_type="ecommerce",
            confidence=0.8,
            anti_bot_measures=["cloudflare", "rate_limiting"],
            wait_time=3.0,
            use_selenium=True,
            selectors={
                "product_container": "tr.searchResultsItem",
                "product_title": "td.searchResultsTitleValue a",
                "product_price": "td.searchResultsPriceValue",
                "product_location": "td.searchResultsLocationValue",
                "product_date": "td.searchResultsDateValue",
            },
            javascript_required=True,
            dynamic_content=True,
            pagination_type="next_page",
            captcha_present=False,
        )

        log_message(
            "INFO", "Created sahibinden-specific profile with enhanced settings"
        )
        return profile

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

        # Step 3.5: Plugin Processing
        plugin_results = None
        if enriched_data and len(enriched_data) > 0:
            log_message("INFO", "Processing data through plugins...")
            plugin_results = self.process_with_plugins(enriched_data)
            if plugin_results and plugin_results.get("enhanced_data"):
                enriched_data = plugin_results["enhanced_data"]

        # Step 3.6: Distributed Processing
        distributed_results = None
        if enriched_data and len(enriched_data) > 0:
            log_message("INFO", "Processing data with distributed workers...")
            distributed_results = self.process_distributed(enriched_data)

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

        # Step 5: Comparative Analysis (if we have data)
        comparison_analysis = None
        if enriched_data and len(enriched_data) > 0:
            log_message("INFO", "Performing comparative analysis...")
            comparison_analysis = self.perform_comparative_analysis(enriched_data)

        # Step 6: Data Visualization
        visualization_results = None
        if enriched_data and len(enriched_data) > 0:
            log_message("INFO", "Creating data visualizations...")
            visualization_results = self.create_data_visualizations(enriched_data)

        # Step 7: Automated Reporting
        reporting_results = None
        if enriched_data and len(enriched_data) > 0:
            log_message("INFO", "Generating automated report...")
            reporting_results = self.generate_automated_report(enriched_data)

        return {
            "raw_data": raw_data,
            "enriched_data": enriched_data,
            "enrichment_result": self.enrichment_result,
            "plugin_results": plugin_results,
            "distributed_results": distributed_results,
            "price_analysis": price_analysis,
            "comparison_analysis": comparison_analysis,
            "visualization_results": visualization_results,
            "reporting_results": reporting_results,
            "site_profile": self.site_profile,
            "stats": self.stats,
            "timestamp": datetime.now().isoformat(),
        }

    def cleanup(self):
        """Cleanup resources and close connections."""
        if hasattr(self, "stealth_manager"):
            self.stealth_manager.cleanup()
        if hasattr(self, "session"):
            self.session.close()
        log_message("INFO", "Scraper cleanup completed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def _fetch_raw_data(self):
        """
        Fetch raw data from the URL with advanced stealth techniques.

        Returns:
            list: Extracted product information.

        Raises:
            Exception: If data fetching fails after maximum retries.
        """
        for attempt in range(self.max_retries):
            try:
                self.stats["requests_made"] += 1

                # Determine if we need browser automation
                use_browser = False
                if self.site_profile and self.site_profile.use_selenium:
                    use_browser = True
                elif "sahibinden.com" in self.url.lower():
                    # Force browser automation for sahibinden.com
                    use_browser = True
                    log_message("INFO", "Forcing browser automation for sahibinden.com")

                # Use stealth manager for advanced anti-bot evasion
                response = self.stealth_manager.fetch_with_stealth(
                    url=self.url, method="GET", use_browser=use_browser
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

                # Try different stealth strategies on failure
                if attempt == 0:
                    log_message("INFO", "Trying with browser automation...")
                    try:
                        response = self.stealth_manager.fetch_with_stealth(
                            url=self.url, method="GET", use_browser=True
                        )
                        response.raise_for_status()

                        self.stats["successful_requests"] += 1
                        log_message(
                            "INFO", f"Success with browser automation: {self.url}"
                        )

                        raw_data = self.parse_response(response.text)

                        # Check if we got actual data or still on Cloudflare page
                        if not raw_data and "sahibinden.com" in self.url.lower():
                            log_message(
                                "WARNING",
                                "Still no data after browser automation, may be Cloudflare challenge",
                            )

                        return raw_data

                    except Exception as browser_error:
                        log_message(
                            "WARNING",
                            f"Browser automation also failed: {browser_error}",
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

        # Save HTML for debugging with timestamp and URL info
        try:
            import os
            from datetime import datetime

            # Create debug directory if it doesn't exist
            debug_dir = "debug_html"
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)

            # Generate filename with timestamp and domain
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            domain = self.url.split("/")[2].replace(".", "_")
            filename = f"{debug_dir}/response_{domain}_{timestamp}.html"

            with open(filename, "w", encoding="utf-8") as file:
                file.write(f"<!-- URL: {self.url} -->\n")
                file.write(f"<!-- Timestamp: {datetime.now().isoformat()} -->\n")
                file.write(
                    f"<!-- Content Length: {len(response_text)} characters -->\n"
                )
                file.write(response_text)

            log_message(
                "INFO",
                f"HTML response saved to '{filename}' ({len(response_text)} characters)",
            )

            # Also save a copy as the latest response for easy access
            with open("response.html", "w", encoding="utf-8") as file:
                file.write(f"<!-- URL: {self.url} -->\n")
                file.write(f"<!-- Timestamp: {datetime.now().isoformat()} -->\n")
                file.write(
                    f"<!-- Content Length: {len(response_text)} characters -->\n"
                )
                file.write(response_text)

            # Analyze the content to help with debugging
            self._analyze_html_content(response_text, filename)

        except Exception as e:
            log_message("ERROR", f"Error saving HTML file: {str(e)}")

        # Try universal extractor first (works for any site)
        log_message("INFO", "Attempting universal extraction...")
        universal_result = self.universal_extractor.extract_data(
            response_text, self.url
        )

        if universal_result.success and universal_result.data:
            log_message(
                "INFO",
                f"Universal extraction successful: {len(universal_result.data)} items using {universal_result.method}",
            )

            # Record successful extraction for learning
            self.adaptive_config_manager.record_extraction_result(
                url=self.url,
                selectors_used=universal_result.selectors_used,
                success=True,
                data_count=len(universal_result.data),
                method=universal_result.method,
            )

            return universal_result.data

        # Fallback to site-specific methods
        log_message(
            "INFO", "Universal extraction failed, trying site-specific methods..."
        )

        # Record failed universal extraction for learning
        self.adaptive_config_manager.record_extraction_result(
            url=self.url,
            selectors_used=universal_result.selectors_used,
            success=False,
            data_count=0,
            method=universal_result.method,
        )

        # Generate comprehensive extraction report for debugging
        self._generate_comprehensive_extraction_report(response_text)

        # Try adaptive configuration if available
        adaptive_config = self.adaptive_config_manager.generate_adaptive_config(
            self.url
        )
        if adaptive_config and adaptive_config.get("selectors"):
            log_message(
                "INFO",
                f"Trying adaptive configuration with confidence {adaptive_config.get('confidence', 0):.2f}",
            )
            adaptive_result = self._extract_with_adaptive_config(
                html_structure, adaptive_config
            )
            if adaptive_result:
                return adaptive_result

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

        # Special handling for sahibinden.com
        if "sahibinden.com" in self.url.lower():
            return self._extract_sahibinden_data(html)

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

    def _extract_sahibinden_data(self, html):
        """
        Extract data specifically for sahibinden.com structure using configuration.
        """
        products = []

        try:
            # Check if we're on a Cloudflare challenge page
            if self._is_cloudflare_challenge_page(html):
                log_message(
                    "WARNING", "Still on Cloudflare challenge page, cannot extract data"
                )
                return products

            # Get sahibinden configuration from config
            sahibinden_config = self.config.get("site_specific_configs", {}).get(
                "sahibinden.com", {}
            )
            selectors = sahibinden_config.get("selectors", {})

            # Fallback to hardcoded selectors if config not found
            if not selectors:
                log_message(
                    "WARNING",
                    "No sahibinden configuration found, using fallback selectors",
                )
                selectors = {
                    "product_container": "tr.searchResultsItem",
                    "product_title": "td.searchResultsTitleValue a",
                    "product_price": "td.searchResultsPriceValue",
                    "product_location": "td.searchResultsLocationValue",
                    "product_date": "td.searchResultsDateValue",
                }

            # Try multiple approaches to find the results
            containers = []

            # Method 1: Look for the main results table first
            results_table = html.find("table", {"id": "searchResultsTable"})
            if results_table:
                containers = results_table.find_all("tr", class_="searchResultsItem")
                log_message(
                    "INFO", f"Found {len(containers)} items in searchResultsTable"
                )

            # Method 2: Try direct container search
            if not containers:
                containers = html.select(
                    selectors.get("product_container", "tr.searchResultsItem")
                )
                log_message(
                    "INFO",
                    f"Found {len(containers)} items using direct container search",
                )

            # Method 3: Try alternative table structures
            if not containers:
                # Look for any table with search results
                tables = html.find_all("table")
                for table in tables:
                    rows = table.find_all("tr")
                    if len(rows) > 1:  # Has header and data rows
                        containers = rows[1:]  # Skip header row
                        log_message(
                            "INFO",
                            f"Found {len(containers)} items in alternative table structure",
                        )
                        break

            if not containers:
                log_message(
                    "WARNING", "Could not find any sahibinden product containers"
                )
                # Test selectors to help debug
                self._test_sahibinden_selectors(html)
                return products

            for container in containers:
                try:
                    product_data = {}

                    # Extract title and link using configuration
                    title_selector = selectors.get(
                        "product_title", "td.searchResultsTitleValue a"
                    )
                    title_elem = container.select_one(title_selector)
                    if title_elem:
                        product_data["title"] = title_elem.get_text(strip=True)
                        product_data["url"] = title_elem.get("href", "")

                    # Extract price using configuration
                    price_selector = selectors.get(
                        "product_price", "td.searchResultsPriceValue"
                    )
                    price_elem = container.select_one(price_selector)
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        if price_text and price_text != "Fiyatı Sor":
                            product_data["price"] = price_text

                    # Extract location using configuration
                    location_selector = selectors.get(
                        "product_location", "td.searchResultsLocationValue"
                    )
                    location_elem = container.select_one(location_selector)
                    if location_elem:
                        product_data["location"] = location_elem.get_text(strip=True)

                    # Extract date using configuration
                    date_selector = selectors.get(
                        "product_date", "td.searchResultsDateValue"
                    )
                    date_elem = container.select_one(date_selector)
                    if date_elem:
                        product_data["date"] = date_elem.get_text(strip=True)

                    # Extract image using configuration
                    image_selector = selectors.get(
                        "product_image", "td.searchResultsImageValue img"
                    )
                    image_elem = container.select_one(image_selector)
                    if image_elem:
                        product_data["image_url"] = image_elem.get("src", "")

                    # Add metadata
                    product_data["source_url"] = self.url
                    product_data["extraction_timestamp"] = datetime.now().isoformat()
                    product_data["site"] = "sahibinden.com"

                    # Only add if we have at least a title
                    if product_data.get("title"):
                        products.append(product_data)

                except Exception as e:
                    log_message(
                        "ERROR", f"Error extracting sahibinden product: {str(e)}"
                    )
                    continue

            log_message(
                "INFO",
                f"Successfully extracted {len(products)} products from sahibinden.com",
            )

        except Exception as e:
            log_message("ERROR", f"Error in sahibinden extraction: {str(e)}")

        return products

    def _is_cloudflare_challenge_page(self, html):
        """Check if the HTML content is a Cloudflare challenge page."""
        try:
            html_text = str(html).lower()
            cloudflare_indicators = [
                "cloudflare",
                "checking your browser",
                "ddos protection",
                "olağandışı bir durum tespit ettik",
                "unusual situation detected",
                "challenge-platform",
                "__cf$cv$params",
                "security-icon",
                "error-page-container",
            ]

            return any(indicator in html_text for indicator in cloudflare_indicators)
        except Exception as e:
            log_message("ERROR", f"Error checking for Cloudflare challenge page: {e}")
            return False

    def _analyze_html_content(self, html_content, filename):
        """Analyze HTML content to help with debugging extraction issues."""
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html_content, "html.parser")

            # Basic content analysis
            title = soup.find("title")
            title_text = title.get_text(strip=True) if title else "No title found"

            # Check for common indicators
            is_cloudflare = self._is_cloudflare_challenge_page(soup)
            has_search_results = bool(soup.find("table", {"id": "searchResultsTable"}))
            has_product_containers = bool(
                soup.find_all("tr", class_="searchResultsItem")
            )

            # Count various elements
            tables = len(soup.find_all("table"))
            divs = len(soup.find_all("div"))
            links = len(soup.find_all("a"))
            images = len(soup.find_all("img"))

            # Look for specific sahibinden elements
            sahibinden_elements = {
                "searchResultsTable": len(
                    soup.find_all("table", {"id": "searchResultsTable"})
                ),
                "searchResultsItem": len(
                    soup.find_all("tr", class_="searchResultsItem")
                ),
                "searchResultsTitleValue": len(
                    soup.find_all("td", class_="searchResultsTitleValue")
                ),
                "searchResultsPriceValue": len(
                    soup.find_all("td", class_="searchResultsPriceValue")
                ),
                "searchResultsLocationValue": len(
                    soup.find_all("td", class_="searchResultsLocationValue")
                ),
            }

            # Create analysis report
            analysis = f"""
=== HTML CONTENT ANALYSIS ===
File: {filename}
URL: {self.url}
Content Length: {len(html_content)} characters

=== PAGE INFO ===
Title: {title_text}
Is Cloudflare Challenge: {is_cloudflare}
Has Search Results Table: {has_search_results}
Has Product Containers: {has_product_containers}

=== ELEMENT COUNTS ===
Tables: {tables}
Divs: {divs}
Links: {links}
Images: {images}

=== SAHIBINDEN SPECIFIC ELEMENTS ===
searchResultsTable: {sahibinden_elements['searchResultsTable']}
searchResultsItem: {sahibinden_elements['searchResultsItem']}
searchResultsTitleValue: {sahibinden_elements['searchResultsTitleValue']}
searchResultsPriceValue: {sahibinden_elements['searchResultsPriceValue']}
searchResultsLocationValue: {sahibinden_elements['searchResultsLocationValue']}

=== EXTRACTION DIAGNOSIS ===
"""

            # Add diagnosis
            if is_cloudflare:
                analysis += "❌ ISSUE: Cloudflare challenge page detected - need to wait for resolution\n"
            elif not has_search_results:
                analysis += "❌ ISSUE: No search results table found - may be wrong page or blocked\n"
            elif sahibinden_elements["searchResultsItem"] == 0:
                analysis += "❌ ISSUE: No product items found in search results\n"
            else:
                analysis += f"✅ SUCCESS: Found {sahibinden_elements['searchResultsItem']} product items\n"

            # Save analysis to file
            analysis_filename = filename.replace(".html", "_analysis.txt")
            with open(analysis_filename, "w", encoding="utf-8") as f:
                f.write(analysis)

            log_message("INFO", f"Content analysis saved to '{analysis_filename}'")
            log_message(
                "INFO",
                f"Analysis: {title_text[:50]}... | Cloudflare: {is_cloudflare} | Products: {sahibinden_elements['searchResultsItem']}",
            )

        except Exception as e:
            log_message("ERROR", f"Error analyzing HTML content: {e}")

    def _create_debug_summary(self, url):
        """Create a debug summary when no products are found."""
        try:
            import os
            from datetime import datetime

            # Create debug directory if it doesn't exist
            debug_dir = "debug_html"
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)

            # Create summary report
            summary_filename = f"{debug_dir}/debug_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

            with open(summary_filename, "w", encoding="utf-8") as f:
                f.write(f"=== SCRAPING DEBUG SUMMARY ===\n")
                f.write(f"URL: {url}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Status: No products extracted\n\n")

                f.write(f"=== FILES TO CHECK ===\n")
                f.write(f"1. response.html - Latest HTML response\n")
                f.write(f"2. debug_html/response_*_*.html - Timestamped responses\n")
                f.write(
                    f"3. debug_html/browser_*_*.html - Browser automation responses\n"
                )
                f.write(f"4. debug_html/*_analysis.txt - Content analysis reports\n\n")

                f.write(f"=== COMMON ISSUES ===\n")
                f.write(
                    f"1. Cloudflare Challenge: Look for 'Olağandışı bir durum tespit ettik' in HTML\n"
                )
                f.write(f"2. Wrong Page: Check if title contains expected content\n")
                f.write(
                    f"3. No Results: Search might return no results for the query\n"
                )
                f.write(f"4. Blocked: Site might be blocking automated requests\n\n")

                f.write(f"=== NEXT STEPS ===\n")
                f.write(f"1. Open response.html in browser to see what was received\n")
                f.write(f"2. Check analysis files for detailed element counts\n")
                f.write(f"3. Try different URL or wait and retry\n")
                f.write(f"4. Consider using different user agents or proxies\n")

            log_message("INFO", f"Debug summary saved to '{summary_filename}'")

        except Exception as e:
            log_message("ERROR", f"Error creating debug summary: {e}")

    def _test_sahibinden_selectors(self, html):
        """Test current selectors against the HTML to help debug extraction issues."""
        try:
            import os
            from datetime import datetime

            # Create debug directory if it doesn't exist
            debug_dir = "debug_html"
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)

            # Get current selectors
            sahibinden_config = self.config.get("site_specific_configs", {}).get(
                "sahibinden.com", {}
            )
            selectors = sahibinden_config.get("selectors", {})

            # Test each selector
            selector_test_results = {}

            for selector_name, selector_value in selectors.items():
                try:
                    elements = html.select(selector_value)
                    selector_test_results[selector_name] = {
                        "selector": selector_value,
                        "count": len(elements),
                        "found": len(elements) > 0,
                        "sample_text": elements[0].get_text(strip=True)[:100]
                        if elements
                        else "None",
                    }
                except Exception as e:
                    selector_test_results[selector_name] = {
                        "selector": selector_value,
                        "count": 0,
                        "found": False,
                        "error": str(e),
                    }

            # Create test report
            test_filename = f"{debug_dir}/selector_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

            with open(test_filename, "w", encoding="utf-8") as f:
                f.write(f"=== SAHIBINDEN SELECTOR TEST RESULTS ===\n")
                f.write(f"URL: {self.url}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n\n")

                for selector_name, result in selector_test_results.items():
                    f.write(f"=== {selector_name.upper()} ===\n")
                    f.write(f"Selector: {result['selector']}\n")
                    f.write(f"Found: {result['found']}\n")
                    f.write(f"Count: {result['count']}\n")
                    if "sample_text" in result:
                        f.write(f"Sample: {result['sample_text']}\n")
                    if "error" in result:
                        f.write(f"Error: {result['error']}\n")
                    f.write("\n")

                # Overall assessment
                f.write("=== OVERALL ASSESSMENT ===\n")
                total_selectors = len(selector_test_results)
                working_selectors = sum(
                    1 for r in selector_test_results.values() if r["found"]
                )

                f.write(f"Working selectors: {working_selectors}/{total_selectors}\n")

                if working_selectors == 0:
                    f.write(
                        "❌ CRITICAL: No selectors are working - site structure may have changed\n"
                    )
                elif working_selectors < total_selectors:
                    f.write(
                        "⚠️  WARNING: Some selectors are not working - partial extraction expected\n"
                    )
                else:
                    f.write("✅ SUCCESS: All selectors are working\n")

            log_message("INFO", f"Selector test results saved to '{test_filename}'")
            log_message(
                "INFO",
                f"Selector test: {working_selectors}/{total_selectors} selectors working",
            )

        except Exception as e:
            log_message("ERROR", f"Error testing selectors: {e}")

    def _generate_comprehensive_extraction_report(self, html_content: str):
        """Generate a comprehensive report of all extraction methods and their results."""
        try:
            import os
            from datetime import datetime

            # Create debug directory if it doesn't exist
            debug_dir = "debug_html"
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)

            # Generate universal extractor report
            report = self.universal_extractor.generate_selector_report(
                html_content, self.url
            )

            # Save report
            report_filename = f"{debug_dir}/extraction_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_filename, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            log_message(
                "INFO", f"Comprehensive extraction report saved to '{report_filename}'"
            )

            # Log summary
            successful_strategies = [
                s for s in report["strategies_tested"] if s["success"]
            ]
            log_message(
                "INFO",
                f"Extraction report: {len(successful_strategies)}/{len(report['strategies_tested'])} strategies successful",
            )

            if successful_strategies:
                best_strategy = max(
                    successful_strategies, key=lambda x: x["confidence"]
                )
                log_message(
                    "INFO",
                    f"Best strategy: {best_strategy['method']} (confidence: {best_strategy['confidence']:.2f})",
                )

        except Exception as e:
            log_message("ERROR", f"Error generating extraction report: {e}")

    def _extract_with_adaptive_config(
        self, html, adaptive_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract data using adaptive configuration based on learning."""
        try:
            selectors = adaptive_config.get("selectors", {})
            if not selectors:
                return []

            products = []

            # Get container selector
            container_selector = selectors.get("product_container", "div")
            containers = html.select(container_selector)

            if not containers:
                log_message(
                    "WARNING",
                    f"No containers found with adaptive selector: {container_selector}",
                )
                return []

            log_message(
                "INFO",
                f"Found {len(containers)} containers with adaptive configuration",
            )

            for container in containers:
                try:
                    product_data = {}

                    # Extract title
                    if "product_title" in selectors:
                        title_elem = container.select_one(selectors["product_title"])
                        if title_elem:
                            product_data["title"] = title_elem.get_text(strip=True)
                            if title_elem.name == "a":
                                product_data["url"] = title_elem.get("href", "")

                    # Extract price
                    if "product_price" in selectors:
                        price_elem = container.select_one(selectors["product_price"])
                        if price_elem:
                            price_text = price_elem.get_text(strip=True)
                            if price_text and price_text != "Fiyatı Sor":
                                product_data["price"] = price_text

                    # Extract location
                    if "product_location" in selectors:
                        location_elem = container.select_one(
                            selectors["product_location"]
                        )
                        if location_elem:
                            product_data["location"] = location_elem.get_text(
                                strip=True
                            )

                    # Extract date
                    if "product_date" in selectors:
                        date_elem = container.select_one(selectors["product_date"])
                        if date_elem:
                            product_data["date"] = date_elem.get_text(strip=True)

                    # Extract image
                    if "product_image" in selectors:
                        img_elem = container.select_one(selectors["product_image"])
                        if img_elem:
                            product_data["image_url"] = img_elem.get("src", "")

                    # Extract link
                    if "product_link" in selectors and "url" not in product_data:
                        link_elem = container.select_one(selectors["product_link"])
                        if link_elem:
                            product_data["url"] = link_elem.get("href", "")

                    # Add metadata
                    product_data["source_url"] = self.url
                    product_data["extraction_timestamp"] = datetime.now().isoformat()
                    product_data["extraction_method"] = "adaptive_config"
                    product_data["confidence"] = adaptive_config.get("confidence", 0.0)

                    # Only add if we have at least a title
                    if product_data.get("title"):
                        products.append(product_data)

                except Exception as e:
                    log_message("ERROR", f"Error extracting adaptive product: {str(e)}")
                    continue

            log_message(
                "INFO",
                f"Adaptive extraction successful: {len(products)} products extracted",
            )

            # Record successful adaptive extraction
            self.adaptive_config_manager.record_extraction_result(
                url=self.url,
                selectors_used=selectors,
                success=True,
                data_count=len(products),
                method="adaptive_config",
            )

            return products

        except Exception as e:
            log_message("ERROR", f"Error in adaptive extraction: {str(e)}")

            # Record failed adaptive extraction
            self.adaptive_config_manager.record_extraction_result(
                url=self.url,
                selectors_used=adaptive_config.get("selectors", {}),
                success=False,
                data_count=0,
                method="adaptive_config",
            )

            return []

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
        Enhanced data saving with multiple format support and automatic export.
        """
        # Save in original format
        save_data(data, file_name, format)
        log_message("INFO", f"Data saved in {format} format: {file_name}")

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

        # Auto-export in multiple formats using ExportManager
        try:
            # Export in JSON format
            json_result = self.export_manager.export_data(
                data, "json", f"{file_name.replace('.csv', '')}_export.json"
            )
            if json_result.success:
                log_message("INFO", f"Auto-exported JSON: {json_result.file_path}")

            # Export in Excel format
            excel_result = self.export_manager.export_data(
                data, "excel", f"{file_name.replace('.csv', '')}_export.xlsx"
            )
            if excel_result.success:
                log_message("INFO", f"Auto-exported Excel: {excel_result.file_path}")

            # Export comprehensive ZIP package
            zip_result = self.export_manager.export_data(
                data, "zip", f"{file_name.replace('.csv', '')}_complete_package.zip"
            )
            if zip_result.success:
                log_message(
                    "INFO", f"Auto-exported ZIP package: {zip_result.file_path}"
                )

        except Exception as e:
            log_message("WARNING", f"Auto-export failed: {str(e)}")

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

    def perform_comparative_analysis(self, data):
        """
        Perform comparative analysis on scraped data.

        Args:
            data: List of scraped product data

        Returns:
            dict: Comparative analysis results
        """
        try:
            log_message("INFO", "Starting comparative analysis...")

            # Load historical data for comparison
            historical_data = self.site_comparator.load_data(days_back=30)

            # Add current data to historical data for analysis
            all_data = historical_data + data

            # Perform product matching
            product_matches = self.site_comparator.match_products(all_data)
            log_message("INFO", f"Found {len(product_matches)} product matches")

            # Compare prices
            price_comparisons = self.site_comparator.compare_prices(product_matches)
            log_message("INFO", f"Generated {len(price_comparisons)} price comparisons")

            # Analyze deals
            deal_analyses = []
            for price_comparison in price_comparisons:
                deal_analysis = self.site_comparator.analyze_deals([price_comparison])
                deal_analyses.extend(deal_analysis)
            log_message("INFO", f"Analyzed {len(deal_analyses)} deals")

            # Generate comparison report
            comparison_report = self.site_comparator.generate_comparison_report(
                deal_analyses
            )

            # Get intelligent recommendations
            recommendations = self.site_comparator.get_intelligent_recommendations(
                deal_analyses
            )

            self.comparison_analysis = {
                "product_matches": product_matches,
                "price_comparisons": price_comparisons,
                "deal_analyses": deal_analyses,
                "comparison_report": comparison_report,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat(),
            }

            log_message("INFO", "Comparative analysis completed successfully")
            return self.comparison_analysis

        except Exception as e:
            log_message("ERROR", f"Comparative analysis failed: {str(e)}")
            return None

    def create_data_visualizations(self, data):
        """
        Create comprehensive data visualizations for scraped data.

        Args:
            data: List of scraped product data

        Returns:
            dict: Visualization results
        """
        try:
            log_message("INFO", "Creating data visualizations...")

            # Create price distribution histogram
            price_chart = self.data_visualizer.create_price_distribution(data)

            # Create price trend analysis
            trend_chart = self.data_visualizer.create_price_trends(data)

            # Create source comparison chart
            source_chart = self.data_visualizer.create_source_comparison(data)

            # Create comprehensive dashboard
            dashboard = self.data_visualizer.create_comprehensive_dashboard(data)

            # Create summary statistics table
            summary_table = self.data_visualizer.create_summary_table(data)

            self.visualization_results = {
                "price_distribution": price_chart,
                "price_trends": trend_chart,
                "source_comparison": source_chart,
                "comprehensive_dashboard": dashboard,
                "summary_table": summary_table,
                "timestamp": datetime.now().isoformat(),
            }

            log_message("INFO", "Data visualizations created successfully")
            return self.visualization_results

        except Exception as e:
            log_message("ERROR", f"Data visualization failed: {str(e)}")
            return None

    def process_distributed(self, data):
        """
        Process data using distributed scraping capabilities.

        Args:
            data: List of scraped product data

        Returns:
            dict: Distributed processing results
        """
        try:
            log_message("INFO", "Starting distributed processing...")

            # Add jobs to queue for distributed processing
            job_ids = []
            for item in data:
                # Use the original URL for each job
                job_id = self.job_queue.add_job(
                    url=self.url,
                    config={
                        "type": "data_processing",
                        "data": item,
                        "priority": "normal",
                    },
                )
                job_ids.append(job_id)

            # Start worker pool
            self.worker_pool.start()

            # Process jobs
            processed_results = []
            for job_id in job_ids:
                result = self.job_queue.get_result(job_id, timeout=30)
                if result:
                    processed_results.append(result)

            # Stop worker pool
            self.worker_pool.stop()

            self.distributed_results = {
                "original_data": data,
                "processed_results": processed_results,
                "jobs_processed": len(job_ids),
                "successful_jobs": len(processed_results),
                "worker_stats": self.worker_pool.get_stats(),
                "timestamp": datetime.now().isoformat(),
            }

            log_message(
                "INFO",
                f"Distributed processing completed: {len(processed_results)}/{len(job_ids)} jobs successful",
            )
            return self.distributed_results

        except Exception as e:
            log_message("ERROR", f"Distributed processing failed: {str(e)}")
            return None

    def process_with_plugins(self, data):
        """
        Process scraped data through available plugins.

        Args:
            data: List of scraped product data

        Returns:
            dict: Plugin processing results
        """
        try:
            log_message("INFO", "Processing data through plugins...")

            # Load available plugins
            self.plugin_manager.load_plugins()

            # Process data through data processor plugins
            processed_data = self.plugin_manager.process_data(data)

            # Validate data through validator plugins
            validation_results = self.plugin_manager.validate_data(processed_data)

            # Apply custom scraper plugins if available
            enhanced_data = self.plugin_manager.apply_custom_scrapers(processed_data)

            self.plugin_results = {
                "original_data": data,
                "processed_data": processed_data,
                "validation_results": validation_results,
                "enhanced_data": enhanced_data,
                "active_plugins": self.plugin_manager.get_active_plugins(),
                "timestamp": datetime.now().isoformat(),
            }

            log_message(
                "INFO",
                f"Plugin processing completed with {len(self.plugin_manager.get_active_plugins())} active plugins",
            )
            return self.plugin_results

        except Exception as e:
            log_message("ERROR", f"Plugin processing failed: {str(e)}")
            return None

    def generate_automated_report(self, data):
        """
        Generate automated reports and alerts for scraped data.

        Args:
            data: List of scraped product data

        Returns:
            dict: Reporting results
        """
        try:
            log_message("INFO", "Generating automated report...")

            # Generate comprehensive report
            report_result = self.automated_reporter.generate_report(data)

            # Check for alerts
            alerts = self.automated_reporter.detect_alerts(data)

            # Generate recommendations
            recommendations = self.automated_reporter.generate_recommendations(data)

            self.reporting_results = {
                "report": report_result,
                "alerts": alerts,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat(),
            }

            log_message("INFO", f"Automated report generated with {len(alerts)} alerts")
            return self.reporting_results

        except Exception as e:
            log_message("ERROR", f"Automated reporting failed: {str(e)}")
            return None
