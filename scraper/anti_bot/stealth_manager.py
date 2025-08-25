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
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
except ImportError:
    UNDETECTED_AVAILABLE = False
    logging.warning("Undetected ChromeDriver not available. Using standard Selenium.")


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
            method_whitelist=["HEAD", "GET", "OPTIONS"],
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
            # Turkish e-commerce site - use aggressive profile
            profile = self.profiles["aggressive"]
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

        try:
            if UNDETECTED_AVAILABLE:
                # Use undetected ChromeDriver for better stealth
                options = uc.ChromeOptions()
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option(
                    "excludeSwitches", ["enable-automation"]
                )
                options.add_experimental_option("useAutomationExtension", False)

                self.driver = uc.Chrome(options=options)
            else:
                # Use standard ChromeDriver
                options = Options()
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option(
                    "excludeSwitches", ["enable-automation"]
                )
                options.add_experimental_option("useAutomationExtension", False)

                self.driver = webdriver.Chrome(options=options)

            # Execute stealth script
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            logging.info("Browser automation setup successful")
            return True

        except Exception as e:
            logging.error(f"Failed to setup browser automation: {e}")
            return False

    def _humanize_browser_behavior(self):
        """Add human-like behavior to browser automation."""

        if not self.driver or not self.current_profile:
            return

        try:
            # Random mouse movements
            if self.current_profile.mouse_movements:
                actions = ActionChains(self.driver)
                for _ in range(random.randint(2, 5)):
                    x = random.randint(100, 800)
                    y = random.randint(100, 600)
                    actions.move_by_offset(x, y)
                    actions.pause(random.uniform(0.1, 0.3))
                actions.perform()

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

        # Select appropriate profile
        self.select_profile(url)

        # Use browser automation if required or requested
        if use_browser or (
            self.current_profile and self.current_profile.browser_automation
        ):
            return self._fetch_with_browser(url, method, data)

        # Use enhanced requests
        return self._fetch_with_requests(url, method, data)

    def _fetch_with_requests(
        self, url: str, method: str, data: Dict
    ) -> requests.Response:
        """Fetch using enhanced requests with stealth techniques."""

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

        # Store cookies for session persistence
        if response.cookies:
            self.session_cookies[url] = response.cookies

        self.request_count += 1
        self.last_request_time = time.time()

        return response

    def _fetch_with_browser(
        self, url: str, method: str, data: Dict
    ) -> requests.Response:
        """Fetch using browser automation for JavaScript-heavy sites."""

        if not self._setup_browser_automation():
            # Fallback to requests
            return self._fetch_with_requests(url, method, data)

        try:
            # Navigate to URL
            self.driver.get(url)

            # Humanize behavior
            self._humanize_browser_behavior()

            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Get page source
            page_source = self.driver.page_source

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

    def cleanup(self):
        """Cleanup resources."""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

        if self.session:
            self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
