#!/usr/bin/env python3
"""
Advanced Anti-Bot Evasion Manager

This module implements sophisticated techniques to bypass anti-bot measures
including 403 Forbidden errors, CAPTCHAs, and other detection mechanisms.
"""

import base64
import hashlib
import json
import logging
import random
import threading
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Import log_message for consistent logging
try:
    from scraper.logging_manager.logging_manager import log_message
except ImportError:
    # Fallback to standard logging if import fails
    def log_message(level, message):
        logging.log(getattr(logging, level.upper(), logging.INFO), message)


# Selenium imports for advanced browser automation
try:
    from selenium import webdriver
    from selenium.common.exceptions import TimeoutException, WebDriverException
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logging.warning("Selenium not available. Advanced browser automation disabled.")

# Undetected ChromeDriver for better stealth
try:
    import undetected_chromedriver as uc

    UNDETECTED_AVAILABLE = True
    logging.info("Undetected ChromeDriver available - using for enhanced stealth")
except ImportError:
    UNDETECTED_AVAILABLE = False
    logging.warning("Undetected ChromeDriver not available. Using standard Selenium.")
    logging.info("To install: pip install undetected-chromedriver")


@dataclass
class StealthProfile:
    """Configuration profile for stealth behavior."""

    name: str
    user_agents: List[str]
    headers: Dict[str, str]
    cookies: Dict[str, str]
    wait_times: Tuple[float, float]  # (min, max) seconds
    mouse_movements: bool
    scroll_behavior: bool
    fingerprint_spoofing: bool
    proxy_rotation: bool
    session_persistence: bool
    captcha_solving: bool
    browser_automation: bool


class StealthManager:
    """
    Advanced anti-bot evasion manager with multiple stealth techniques.
    """

    # Class-level browser pool to prevent multiple instances
    _browser_pool = []
    _max_browsers = 2  # Maximum number of browser instances
    _pool_lock = threading.Lock()

    def __init__(self, config: Dict = None):
        """
        Initialize the stealth manager.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.session = requests.Session()
        self.driver = None
        self.current_profile = None
        self._request_count = 0
        self._max_requests_per_session = 50  # Limit requests per session
        self._session_start_time = time.time()
        self._session_timeout = 300  # 5 minutes per session

        # Initialize stealth profiles
        self.profiles = self._initialize_profiles()

        # Session persistence
        self.session_cookies = {}
        self.session_headers = {}

        # Anti-detection counters
        self.request_count = 0
        self.last_request_time = 0

        # Setup advanced session
        self._setup_advanced_session()

    @classmethod
    def _get_browser_from_pool(cls):
        """Get a browser instance from the pool or create a new one."""
        with cls._pool_lock:
            if cls._browser_pool:
                return cls._browser_pool.pop()
            return None

    @classmethod
    def _return_browser_to_pool(cls, driver):
        """Return a browser instance to the pool."""
        with cls._pool_lock:
            if len(cls._browser_pool) < cls._max_browsers:
                cls._browser_pool.append(driver)
            else:
                # Pool is full, quit the browser
                try:
                    driver.quit()
                except:
                    pass

    def _should_reset_session(self):
        """Check if session should be reset due to request limit or timeout."""
        current_time = time.time()
        return (
            self._request_count >= self._max_requests_per_session
            or (current_time - self._session_start_time) > self._session_timeout
        )

    def _reset_session(self):
        """Reset the session to prevent unlimited requests."""
        try:
            if self.driver:
                self._return_browser_to_pool(self.driver)
                self.driver = None
        except:
            pass

        self.session.close()
        self.session = requests.Session()
        self._request_count = 0
        self._session_start_time = time.time()
        logging.info("Session reset to prevent unlimited requests")

    def _initialize_profiles(self) -> Dict[str, StealthProfile]:
        """Initialize different stealth profiles for different scenarios."""

        # Modern browser headers
        modern_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }

        # Mobile headers
        mobile_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
            "Viewport-Width": "375",
            "DPR": "2",
        }

        return {
            "stealth": StealthProfile(
                name="stealth",
                user_agents=[
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                ],
                headers=modern_headers,
                cookies={},
                wait_times=(2.0, 5.0),
                mouse_movements=True,
                scroll_behavior=True,
                fingerprint_spoofing=True,
                proxy_rotation=True,
                session_persistence=True,
                captcha_solving=True,
                browser_automation=True,
            ),
            "mobile": StealthProfile(
                name="mobile",
                user_agents=[
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Mobile/15E148 Safari/604.1",
                    "Mozilla/5.0 (Linux; Android 14; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
                    "Mozilla/5.0 (iPad; CPU OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Mobile/15E148 Safari/604.1",
                ],
                headers=mobile_headers,
                cookies={},
                wait_times=(3.0, 7.0),
                mouse_movements=False,
                scroll_behavior=True,
                fingerprint_spoofing=True,
                proxy_rotation=True,
                session_persistence=True,
                captcha_solving=True,
                browser_automation=True,
            ),
            "aggressive": StealthProfile(
                name="aggressive",
                user_agents=[
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
                ],
                headers=modern_headers,
                cookies={},
                wait_times=(5.0, 10.0),
                mouse_movements=True,
                scroll_behavior=True,
                fingerprint_spoofing=True,
                proxy_rotation=True,
                session_persistence=True,
                captcha_solving=True,
                browser_automation=True,
            ),
        }

    def _setup_advanced_session(self):
        """Setup advanced session with retry logic and custom adapters."""

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set default timeout
        self.session.timeout = 30

    def select_profile(self, url: str, site_type: str = None) -> StealthProfile:
        """
        Select the most appropriate stealth profile based on URL and site type.

        Args:
            url: Target URL
            site_type: Type of website (e.g., 'ecommerce', 'news', 'social')

        Returns:
            Selected stealth profile
        """
        domain = urlparse(url).netloc.lower()

        # Site-specific profile selection
        if "sahibinden.com" in domain:
            # Turkish e-commerce site - use aggressive profile with enhanced anti-detection
            profile = self.profiles["aggressive"]
            # Add Turkish-specific headers
            profile.headers.update(
                {
                    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
                    "Referer": "https://www.sahibinden.com/",
                    "Origin": "https://www.sahibinden.com",
                    "Sec-Fetch-Site": "same-origin",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-User": "?1",
                    "Sec-Fetch-Dest": "document",
                }
            )
        elif any(site in domain for site in ["amazon", "ebay", "walmart"]):
            # Major e-commerce - use stealth profile
            profile = self.profiles["stealth"]
        elif any(site in domain for site in ["facebook", "twitter", "instagram"]):
            # Social media - use mobile profile
            profile = self.profiles["mobile"]
        else:
            # Default to stealth profile
            profile = self.profiles["stealth"]

        self.current_profile = profile
        logging.info(f"Selected stealth profile: {profile.name} for {domain}")
        return profile

    def _generate_fingerprint(self) -> Dict[str, str]:
        """Generate browser fingerprint to appear more human-like."""

        # Screen resolution
        resolutions = [
            "1920x1080",
            "1366x768",
            "1440x900",
            "1536x864",
            "1280x720",
            "1600x900",
            "1024x768",
            "2560x1440",
        ]

        # Color depth
        color_depths = ["24", "32"]

        # Timezone
        timezones = [
            "America/New_York",
            "Europe/London",
            "Asia/Tokyo",
            "Australia/Sydney",
            "Europe/Istanbul",
        ]

        # Language
        languages = [
            "en-US,en;q=0.9",
            "en-GB,en;q=0.9",
            "tr-TR,tr;q=0.9,en;q=0.8",
            "de-DE,de;q=0.9,en;q=0.8",
            "fr-FR,fr;q=0.9,en;q=0.8",
        ]

        return {
            "screen_resolution": random.choice(resolutions),
            "color_depth": random.choice(color_depths),
            "timezone": random.choice(timezones),
            "language": random.choice(languages),
            "platform": random.choice(["Win32", "MacIntel", "Linux x86_64"]),
            "cookie_enabled": "true",
            "do_not_track": random.choice(["1", "0"]),
            "webdriver": "false",
        }

    def _add_stealth_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Add stealth headers to appear more human-like."""

        if not self.current_profile:
            return headers

        # Add fingerprint-based headers
        fingerprint = self._generate_fingerprint()

        enhanced_headers = headers.copy()
        enhanced_headers.update(self.current_profile.headers)

        # Add dynamic headers
        enhanced_headers.update(
            {
                "Accept-Language": fingerprint["language"],
                "DNT": fingerprint["do_not_track"],
                "Sec-CH-UA": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "Sec-CH-UA-Mobile": "?0",
                "Sec-CH-UA-Platform": f'"{fingerprint["platform"]}"',
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Dest": "document",
                "Upgrade-Insecure-Requests": "1",
            }
        )

        return enhanced_headers

    def _humanize_timing(self):
        """Add human-like timing delays."""

        if not self.current_profile:
            time.sleep(random.uniform(1, 3))
            return

        min_wait, max_wait = self.current_profile.wait_times

        # Add random delay
        delay = random.uniform(min_wait, max_wait)

        # Add micro-delays for more human-like behavior
        micro_delays = [random.uniform(0.1, 0.5) for _ in range(random.randint(1, 3))]

        for micro_delay in micro_delays:
            time.sleep(micro_delay)

        time.sleep(delay)

    def _rotate_user_agent(self) -> str:
        """Rotate user agent string."""

        if not self.current_profile:
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

        return random.choice(self.current_profile.user_agents)

    def _setup_browser_automation(self) -> bool:
        """Setup browser automation for sites that require JavaScript."""

        if not SELENIUM_AVAILABLE:
            logging.warning("Selenium not available for browser automation")
            return False

        # Try to get browser from pool first
        self.driver = self._get_browser_from_pool()
        if self.driver:
            logging.info("Reusing browser from pool")
            return True

        try:
            # Create unique user data directory for each browser instance
            import tempfile
            import uuid

            user_data_dir = tempfile.mkdtemp(
                prefix=f"chrome_profile_{uuid.uuid4().hex[:8]}_"
            )

            if UNDETECTED_AVAILABLE:
                # Use undetected ChromeDriver for better stealth
                options = uc.ChromeOptions()

                # Critical fixes for DevToolsActivePort error
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--disable-extensions")
                options.add_argument("--disable-plugins")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--disable-web-security")
                options.add_argument("--disable-features=VizDisplayCompositor")
                options.add_argument("--disable-infobars")
                options.add_argument("--disable-notifications")
                options.add_argument("--disable-popup-blocking")

                # Additional anti-detection arguments
                options.add_argument("--disable-client-side-phishing-detection")
                options.add_argument("--disable-sync")
                options.add_argument("--disable-translate")
                options.add_argument("--hide-scrollbars")
                options.add_argument("--mute-audio")
                options.add_argument("--no-first-run")
                options.add_argument("--disable-default-apps")
                options.add_argument("--disable-background-timer-throttling")
                options.add_argument("--disable-backgrounding-occluded-windows")
                options.add_argument("--disable-renderer-backgrounding")

                # Fix for DevToolsActivePort error
                options.add_argument("--remote-debugging-port=0")
                options.add_argument("--disable-background-networking")
                options.add_argument("--disable-background-timer-throttling")
                options.add_argument("--disable-renderer-backgrounding")
                options.add_argument("--disable-backgrounding-occluded-windows")
                options.add_argument("--disable-client-side-phishing-detection")
                options.add_argument("--disable-crash-reporter")
                options.add_argument("--disable-oopr-debug-crash-dump")
                options.add_argument("--no-crash-upload")
                options.add_argument("--disable-gpu-sandbox")
                options.add_argument("--disable-software-rasterizer")

                # Use a more stable user data directory approach
                import os
                import shutil

                temp_dir = tempfile.mkdtemp()
                options.add_argument(f"--user-data-dir={temp_dir}")

                options.add_experimental_option(
                    "excludeSwitches", ["enable-automation", "enable-logging"]
                )
                options.add_experimental_option("useAutomationExtension", False)
                options.add_argument("--log-level=3")  # Suppress Chrome logs

                # Add Turkish locale for sahibinden.com
                options.add_argument("--lang=tr-TR")

                # Add prefs to make browser look more natural
                prefs = {
                    "profile.default_content_setting_values": {
                        "notifications": 2,
                        "geolocation": 2,
                        "media_stream": 2,
                    },
                    "profile.managed_default_content_settings": {"images": 1},
                }
                options.add_experimental_option("prefs", prefs)

                # Add timeout and retry logic
                try:
                    self.driver = uc.Chrome(options=options, version_main=None)
                    # Store temp directory for cleanup
                    self.temp_dir = temp_dir
                except Exception as e:
                    logging.error(f"Failed to create undetected Chrome: {e}")
                    # Cleanup temp directory
                    if os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir, ignore_errors=True)
                    raise
            else:
                # Use standard ChromeDriver
                options = Options()
                options.add_argument("--headless")  # Run in headless mode
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")  # Disable GPU for headless
                options.add_argument("--disable-extensions")
                options.add_argument("--disable-plugins")
                options.add_argument(
                    "--disable-images"
                )  # Don't load images for faster performance
                options.add_argument("--disable-javascript")  # Disable JS if not needed
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument(
                    "--window-size=1920,1080"
                )  # Set window size for headless
                options.add_argument(f"--user-data-dir={user_data_dir}")
                options.add_argument("--disable-web-security")
                options.add_argument("--disable-features=VizDisplayCompositor")
                options.add_experimental_option(
                    "excludeSwitches", ["enable-automation"]
                )
                options.add_experimental_option("useAutomationExtension", False)
                # Disable logging to reduce noise
                options.add_experimental_option("excludeSwitches", ["enable-logging"])
                options.add_experimental_option("useAutomationExtension", False)
                options.add_argument("--log-level=3")  # Suppress Chrome logs

                self.driver = webdriver.Chrome(options=options)

            # Execute stealth script
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            logging.info("Browser automation setup successful")
            return True

        except Exception as e:
            logging.error(f"Failed to setup browser automation: {e}")
            # Clean up the temporary directory if it was created
            try:
                if "user_data_dir" in locals():
                    import shutil

                    shutil.rmtree(user_data_dir, ignore_errors=True)
            except:
                pass

            # Try fallback with minimal options
            try:
                logging.info("Attempting fallback browser setup...")
                options = uc.ChromeOptions() if UNDETECTED_AVAILABLE else Options()
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--remote-debugging-port=0")

                if UNDETECTED_AVAILABLE:
                    self.driver = uc.Chrome(options=options, version_main=None)
                else:
                    self.driver = webdriver.Chrome(options=options)

                logging.info("Fallback browser setup successful")
                return True
            except Exception as fallback_error:
                logging.error(f"Fallback browser setup also failed: {fallback_error}")
                return False

    def _humanize_browser_behavior(self):
        """Add human-like behavior to browser automation."""

        if not self.driver or not self.current_profile:
            return

        try:
            # Get viewport size to ensure mouse movements stay within bounds
            viewport_size = self.driver.get_window_size()
            viewport_width = viewport_size["width"]
            viewport_height = viewport_size["height"]

            # Random mouse movements within viewport bounds
            if self.current_profile.mouse_movements:
                actions = ActionChains(self.driver)
                for _ in range(random.randint(2, 5)):
                    # Ensure mouse movements stay within viewport
                    x = random.randint(50, min(viewport_width - 50, 800))
                    y = random.randint(50, min(viewport_height - 50, 600))
                    try:
                        actions.move_by_offset(x, y)
                        actions.pause(random.uniform(0.1, 0.3))
                    except Exception as move_error:
                        logging.debug(f"Mouse movement failed: {move_error}")
                        break
                try:
                    actions.perform()
                except Exception as perform_error:
                    logging.debug(f"Action chain perform failed: {perform_error}")

            # Random scrolling
            if self.current_profile.scroll_behavior:
                scroll_amount = random.randint(100, 500)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(random.uniform(0.5, 2.0))

                # Scroll back up sometimes
                if random.random() < 0.3:
                    self.driver.execute_script(
                        f"window.scrollBy(0, -{scroll_amount//2});"
                    )
                    time.sleep(random.uniform(0.3, 1.0))

        except Exception as e:
            logging.warning(f"Failed to humanize browser behavior: {e}")

    def fetch_with_stealth(
        self,
        url: str,
        method: str = "GET",
        data: Dict = None,
        use_browser: bool = False,
    ) -> requests.Response:
        """
        Fetch URL with advanced stealth techniques.

        Args:
            url: Target URL
            method: HTTP method
            data: Request data
            use_browser: Whether to use browser automation

        Returns:
            Response object
        """

        # Check if session should be reset
        if self._should_reset_session():
            self._reset_session()

        # Increment request counter
        self._request_count += 1

        # Select appropriate profile
        self.select_profile(url)

        # Use browser automation if required or requested
        if use_browser or (
            self.current_profile and self.current_profile.browser_automation
        ):
            return self._fetch_with_browser(url, method, data)

        # For sahibinden.com, try browser automation if requests fail
        if "sahibinden.com" in url.lower():
            log_message("INFO", "Attempting browser automation for sahibinden.com")
            return self._fetch_with_browser(url, method, data)

        # Use enhanced requests
        return self._fetch_with_requests(url, method, data)

    def _fetch_with_requests(
        self, url: str, method: str, data: Dict
    ) -> requests.Response:
        """Fetch using enhanced requests with stealth techniques."""

        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Humanize timing
                self._humanize_timing()

                # Prepare headers
                headers = {"User-Agent": self._rotate_user_agent()}
                headers = self._add_stealth_headers(headers)

                # Add session cookies if available
                if self.session_cookies.get(url):
                    self.session.cookies.update(self.session_cookies[url])

                # Make request
                response = self.session.request(
                    method=method, url=url, headers=headers, data=data, timeout=30
                )

                # Handle 403 Forbidden with retry strategy
                if response.status_code == 403:
                    if attempt < max_retries - 1:
                        logging.warning(
                            f"403 Forbidden on attempt {attempt + 1}, retrying with different strategy..."
                        )
                        # Try different approach: reset session, change user agent, add delay
                        self._reset_session()
                        time.sleep(random.uniform(5, 10))  # Longer delay for 403
                        continue
                    else:
                        logging.error(
                            f"403 Forbidden after {max_retries} attempts. Site may be blocking requests."
                        )
                        # Try browser automation as last resort
                        return self._fetch_with_browser(url, method, data)

                # Store cookies for session persistence
                if response.cookies:
                    self.session_cookies[url] = response.cookies

                self.request_count += 1
                self.last_request_time = time.time()

                return response

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    logging.warning(
                        f"Request failed on attempt {attempt + 1}: {e}, retrying..."
                    )
                    time.sleep(random.uniform(2, 5))
                    continue
                else:
                    logging.error(f"Request failed after {max_retries} attempts: {e}")
                    raise

    def _fetch_with_browser(
        self, url: str, method: str, data: Dict
    ) -> requests.Response:
        """Fetch using browser automation for JavaScript-heavy sites."""

        if not self._setup_browser_automation():
            # Fallback to requests
            return self._fetch_with_requests(url, method, data)

        try:
            # Navigate to URL with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.driver.get(url)
                    break
                except Exception as nav_error:
                    if attempt == max_retries - 1:
                        raise nav_error
                    logging.warning(
                        f"Navigation attempt {attempt + 1} failed: {nav_error}"
                    )
                    time.sleep(2)

            # Humanize behavior
            self._humanize_browser_behavior()

            # Wait for page to load with timeout
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except TimeoutException:
                logging.warning("Page load timeout, proceeding with available content")

            # Check for Cloudflare challenge and wait for it to resolve
            if self._is_cloudflare_challenge():
                log_message(
                    "INFO", "Cloudflare challenge detected, waiting for resolution..."
                )
                self._wait_for_cloudflare_challenge()

            # Get page source
            page_source = self.driver.page_source

            # Save browser content for debugging
            try:
                import os
                from datetime import datetime

                # Create debug directory if it doesn't exist
                debug_dir = "debug_html"
                if not os.path.exists(debug_dir):
                    os.makedirs(debug_dir)

                # Generate filename with timestamp and domain
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                domain = url.split("/")[2].replace(".", "_")
                filename = f"{debug_dir}/browser_{domain}_{timestamp}.html"

                with open(filename, "w", encoding="utf-8") as file:
                    file.write(f"<!-- URL: {url} -->\n")
                    file.write(f"<!-- Timestamp: {datetime.now().isoformat()} -->\n")
                    file.write(
                        f"<!-- Content Length: {len(page_source)} characters -->\n"
                    )
                    file.write(f"<!-- Browser: Chrome with stealth settings -->\n")
                    file.write(page_source)

                log_message(
                    "INFO",
                    f"Browser content saved to '{filename}' ({len(page_source)} characters)",
                )

            except Exception as e:
                log_message("WARNING", f"Could not save browser content: {e}")

            # Create mock response object
            class MockResponse:
                def __init__(self, content, status_code=200, headers=None):
                    self.content = content.encode("utf-8")
                    self.text = content
                    self.status_code = status_code
                    self.headers = headers or {}
                    self.cookies = {}

                def raise_for_status(self):
                    if self.status_code >= 400:
                        raise requests.HTTPError(f"HTTP {self.status_code}")

            return MockResponse(page_source)

        except Exception as e:
            logging.error(f"Browser automation failed: {e}")
            # Clean up browser resources
            try:
                if self.driver:
                    self.driver.quit()
                    self.driver = None
            except:
                pass
            # Fallback to requests
            return self._fetch_with_requests(url, method, data)

    def solve_captcha(self, response_text: str) -> Optional[str]:
        """
        Attempt to solve CAPTCHA if present.

        Args:
            response_text: Response HTML content

        Returns:
            CAPTCHA solution or None
        """
        # This is a placeholder for CAPTCHA solving logic
        # In a real implementation, you would integrate with services like:
        # - 2captcha
        # - Anti-Captcha
        # - reCAPTCHA solver

        if "captcha" in response_text.lower() or "recaptcha" in response_text.lower():
            logging.warning("CAPTCHA detected - manual intervention may be required")
            # Here you would implement CAPTCHA solving logic
            return None

        return None

    def _is_cloudflare_challenge(self):
        """Check if the current page is a Cloudflare challenge page."""
        try:
            # Check for common Cloudflare challenge indicators
            page_source = self.driver.page_source.lower()
            cloudflare_indicators = [
                "cloudflare",
                "checking your browser",
                "ddos protection",
                "olağandışı bir durum tespit ettik",
                "unusual situation detected",
                "challenge-platform",
                "__cf$cv$params",
            ]

            return any(indicator in page_source for indicator in cloudflare_indicators)
        except Exception as e:
            log_message("WARNING", f"Error checking for Cloudflare challenge: {e}")
            return False

    def _wait_for_cloudflare_challenge(self):
        """Wait for Cloudflare challenge to be resolved with improved handling."""
        try:
            max_wait_time = 30  # Reduced wait time to prevent long hangs
            check_interval = 2  # Check every 2 seconds
            waited_time = 0

            log_message(
                "INFO",
                f"Waiting for Cloudflare challenge resolution (max {max_wait_time}s)...",
            )

            while waited_time < max_wait_time:
                try:
                    if not self._is_cloudflare_challenge():
                        log_message(
                            "INFO",
                            f"Cloudflare challenge resolved after {waited_time} seconds",
                        )
                        return True

                    time.sleep(check_interval)
                    waited_time += check_interval

                    # Show progress every 10 seconds
                    if waited_time % 10 == 0:
                        log_message(
                            "INFO",
                            f"Still waiting for Cloudflare challenge... ({waited_time}s/{max_wait_time}s)",
                        )

                    # Try to interact with the page to help resolve the challenge
                    try:
                        # More varied scrolling patterns
                        import random

                        scroll_patterns = [
                            "window.scrollTo(0, document.body.scrollHeight/3);",
                            "window.scrollTo(0, document.body.scrollHeight/2);",
                            "window.scrollTo(0, document.body.scrollHeight*2/3);",
                            "window.scrollTo(0, document.body.scrollHeight);",
                            "window.scrollTo(0, 0);",
                        ]

                        pattern = random.choice(scroll_patterns)
                        self.driver.execute_script(pattern)
                        time.sleep(random.uniform(1, 2))

                        # Sometimes try mouse movement
                        if random.random() < 0.3:
                            self._humanize_browser_behavior()

                    except Exception as e:
                        log_message(
                            "DEBUG", f"Error during Cloudflare interaction: {e}"
                        )

                except KeyboardInterrupt:
                    log_message("WARNING", "Cloudflare wait interrupted by user")
                    return False
                except Exception as e:
                    log_message("WARNING", f"Error during Cloudflare wait: {e}")
                    break

            log_message(
                "WARNING",
                f"Cloudflare challenge not resolved after {max_wait_time} seconds",
            )
            return False

        except KeyboardInterrupt:
            log_message("WARNING", "Cloudflare wait interrupted by user")
            return False
        except Exception as e:
            log_message("ERROR", f"Error waiting for Cloudflare challenge: {e}")
            return False

    def cleanup(self):
        """Cleanup resources."""
        if self.driver:
            try:
                # Return browser to pool instead of quitting
                self._return_browser_to_pool(self.driver)
            except:
                pass
            self.driver = None

        # Cleanup temp directory
        if hasattr(self, "temp_dir") and self.temp_dir:
            try:
                import os
                import shutil

                if os.path.exists(self.temp_dir):
                    shutil.rmtree(self.temp_dir, ignore_errors=True)
            except:
                pass

        if self.session:
            self.session.close()

    @classmethod
    def cleanup_all_browsers(cls):
        """Cleanup all browsers in the pool."""
        with cls._pool_lock:
            for driver in cls._browser_pool:
                try:
                    driver.quit()
                except:
                    pass
            cls._browser_pool.clear()
            logging.info("All browser instances cleaned up")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


# Global cleanup function for application shutdown
import atexit


def cleanup_all_stealth_managers():
    """Cleanup all browser instances on application exit."""
    StealthManager.cleanup_all_browsers()


# Register cleanup function to run on exit
atexit.register(cleanup_all_stealth_managers)
