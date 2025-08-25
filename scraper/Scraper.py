import os
import sys
import time
from datetime import datetime
from typing import Optional

import requests
from bs4 import BeautifulSoup

# Add the project root to the path for absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from requests.exceptions import HTTPError, Timeout

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
        self.user_agent_manager = UserAgentManager(config.get("user_agents", []))
        self.proxy_rotator = ProxyRotator(config.get("proxies", []))
        self.session = requests.Session()

        # Initialize advanced features
        self.smart_detector = SmartSiteDetector()
        self.data_enricher = DataEnricher()
        self.price_analyzer = PriceAnalyzer()
        self.stealth_manager = StealthManager(config)

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
        self.automated_reporter = AutomatedReporter("data", report_config, alert_config)

        # Initialize data visualizer
        self.data_visualizer = DataVisualizer("data/visualizations")

        # Initialize plugin manager
        self.plugin_manager = PluginManager("plugins")

        # Initialize distributed scraping components
        self.job_queue = JobQueue()
        self.worker_pool = WorkerPool(max_workers=3)

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
                    # Force browser automation for problematic sites
                    use_browser = True

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
            deal_analyses = self.site_comparator.analyze_deals(price_comparisons)
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
                job_id = self.job_queue.add_job(
                    {"type": "data_processing", "data": item, "priority": "normal"}
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
