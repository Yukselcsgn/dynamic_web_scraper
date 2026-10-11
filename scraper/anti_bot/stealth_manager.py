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
Advanced Anti-Bot Evasion Manager

This module implements sophisticated techniques to bypass anti-bot measures
including 403 Forbidden errors, CAPTCHAs, and other detection mechanisms.
"""

import base64
import hashlib
import json
import logging
import random
import shutil
import tempfile
import threading
import time
import uuid
from dataclasses import dataclass, replace
from typing import Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from scraper.anti_bot.strategy import (
    AntiBotStrategy,
    body_suggests_bot_challenge,
    raise_tier,
)
from scraper.proxy_manager.proxy_formatter import (
    mask_proxy,
    parse_proxy,
    redact_proxy_credentials,
)
from scraper.proxy_manager.proxy_rotator import ProxyRotator

# Import log_message for consistent logging
try:
    from scraper.logging_manager.logging_manager import log_message
except ImportError:
    # Fallback to standard logging if import fails
    def log_message(level, message):
        logging.log(getattr(logging, level.upper(), logging.INFO), message)


# Import Cloudflare bypass
try:
    from scraper.anti_bot.cloudflare_bypass import CloudflareBypass

    CLOUDFLARE_BYPASS_AVAILABLE = True
except ImportError:
    CLOUDFLARE_BYPASS_AVAILABLE = False
    log_message("WARNING", "Cloudflare bypass not available")

# Import human behavior simulator
try:
    from scraper.anti_bot.human_behavior import HumanBehaviorSimulator

    HUMAN_BEHAVIOR_AVAILABLE = True
except ImportError:
    HUMAN_BEHAVIOR_AVAILABLE = False
    log_message("WARNING", "Human behavior simulator not available")


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

    class WebDriverException(Exception):  # type: ignore[no-redef]
        """Placeholder so except-clauses stay valid without Selenium."""

    class TimeoutException(WebDriverException):  # type: ignore[no-redef]
        """Placeholder so except-clauses stay valid without Selenium."""

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
        self.strategy = AntiBotStrategy.from_config(self.config)
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

        # Initialize Cloudflare bypass
        if CLOUDFLARE_BYPASS_AVAILABLE:
            self.cloudflare_bypass = CloudflareBypass(config)
        else:
            self.cloudflare_bypass = None

        # Initialize human behavior simulator
        if HUMAN_BEHAVIOR_AVAILABLE:
            self.human_behavior = HumanBehaviorSimulator(config)
        else:
            self.human_behavior = None

        # Setup advanced session
        self._setup_advanced_session()

        # Proxy rotation (requests / Selenium / Playwright share the same proxy)
        self.current_proxy: Optional[str] = None
        self._requests_proxies: Optional[Dict[str, str]] = None
        proxies = self.config.get("proxies") or []
        self.proxy_rotator = ProxyRotator(proxies) if proxies else None
        self._apply_proxy(rotate=True)

    @classmethod
    def _get_browser_from_pool(cls, proxy: Optional[str] = None):
        """Get a live pooled browser bound to ``proxy``, or None."""
        with cls._pool_lock:
            for driver in list(cls._browser_pool):
                if getattr(driver, "_dws_proxy", None) != proxy:
                    continue
                cls._browser_pool.remove(driver)
                if cls._is_driver_alive(driver):
                    return driver
                cls._quit_driver(driver)  # dead browser: release it, keep looking
            return None

    @classmethod
    def _return_browser_to_pool(cls, driver):
        """Return a browser instance to the pool (or quit it if the pool is full)."""
        with cls._pool_lock:
            if len(cls._browser_pool) < cls._max_browsers:
                cls._browser_pool.append(driver)
                return
        # Pool is full: quit outside the lock (can be slow)
        cls._quit_driver(driver)

    def _apply_proxy(self, rotate: bool = True) -> None:
        """
        Select the active proxy and push it to requests and Cloudflare bypass.

        The browser picks it up on the next ``_setup_browser_automation`` call
        (a driver bound to a different proxy is never reused).
        """
        if self.proxy_rotator is None:
            return

        if rotate or self.current_proxy is None:
            try:
                self.current_proxy = self.proxy_rotator.rotate_proxy()
            except RuntimeError as e:
                logging.error(f"Proxy rotation failed, using direct connection: {e}")
                self.current_proxy = None

        try:
            self._requests_proxies = (
                parse_proxy(self.current_proxy).requests_proxies()
                if self.current_proxy
                else None
            )
        except ValueError as e:
            logging.error(f"Invalid proxy ignored: {e}")
            self.current_proxy = None
            self._requests_proxies = None

        self.session.proxies.clear()
        if self._requests_proxies:
            self.session.proxies.update(self._requests_proxies)

        if self.cloudflare_bypass:
            self.cloudflare_bypass.set_proxy(self.current_proxy)

        logging.info(f"Active proxy: {mask_proxy(self.current_proxy)}")

    def _should_reset_session(self):
        """Check if session should be reset due to request limit or timeout."""
        current_time = time.time()
        return (
            self._request_count >= self._max_requests_per_session
            or (current_time - self._session_start_time) > self._session_timeout
        )

    def _reset_session(self):
        """Reset the session to prevent unlimited requests."""
        if self.driver:
            self._return_browser_to_pool(self.driver)
            self.driver = None

        self.session.close()
        self.session = requests.Session()
        self._setup_advanced_session()
        self._request_count = 0
        self._session_start_time = time.time()
        self._apply_proxy(rotate=True)
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
            "minimal": StealthProfile(
                name="minimal",
                user_agents=[
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                ],
                headers=modern_headers,
                cookies={},
                wait_times=(0.5, 1.5),
                mouse_movements=False,
                scroll_behavior=False,
                fingerprint_spoofing=False,
                proxy_rotation=False,
                session_persistence=True,
                captcha_solving=False,
                browser_automation=False,
            ),
            "balanced": StealthProfile(
                name="balanced",
                user_agents=[
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                ],
                headers=modern_headers,
                cookies={},
                wait_times=(1.0, 3.0),
                mouse_movements=False,
                scroll_behavior=False,
                fingerprint_spoofing=True,
                proxy_rotation=True,
                session_persistence=True,
                captcha_solving=False,
                browser_automation=False,
            ),
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

    def select_profile(
        self, url: str, site_type: str = None, site_profile=None
    ) -> StealthProfile:
        """
        Select the stealth profile for ``url``.

        Resolution order: per-domain override, sahibinden.com special case,
        then the strategy tier (raised by ``site_profile`` when
        ``adapt_to_site`` is on). Known marketplaces / social networks only
        raise the tier, never lower it.

        Args:
            url: Target URL
            site_type: Type of website (e.g., 'ecommerce', 'news', 'social')
            site_profile: Optional detected site profile

        Returns:
            Selected stealth profile (also stored as ``current_profile``)
        """
        domain = urlparse(url).netloc.lower()
        name = self.strategy.profile_name_for_url(url, site_profile)

        if self.strategy.domain_override(url) is None:
            if "sahibinden.com" in domain:
                name = "aggressive"
            elif self.strategy.adapt_to_site:
                if any(site in domain for site in ["amazon", "ebay", "walmart"]):
                    name = raise_tier(name, "stealth")
                elif any(site in domain for site in ["facebook", "twitter", "instagram"]):
                    name = "mobile"

        profile = self.profiles[name]
        if "sahibinden.com" in domain:
            # Copy so Turkish-specific headers don't leak into the shared profile
            profile = replace(
                profile,
                headers={
                    **profile.headers,
                    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
                    "Referer": "https://www.sahibinden.com/",
                    "Origin": "https://www.sahibinden.com",
                    "Sec-Fetch-Site": "same-origin",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-User": "?1",
                    "Sec-Fetch-Dest": "document",
                },
            )

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

        if self.strategy.human_delay_style == "none":
            return

        if self.human_behavior:
            # Use human behavior simulator for more realistic timing
            self.human_behavior.simulate_realistic_delay("general")
            return

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

    @staticmethod
    def _quit_driver(driver, temp_dir: Optional[str] = None) -> None:
        """
        Quit a driver and remove its profile directory.

        Never raises: browser shutdown errors are logged at debug level so
        cleanup paths cannot mask the original exception.
        """
        if temp_dir is None and driver is not None:
            temp_dir = getattr(driver, "_dws_temp_dir", None)

        if driver is not None:
            try:
                driver.quit()
            except (WebDriverException, OSError, AttributeError, urllib3.exceptions.HTTPError) as e:
                logging.debug(f"driver.quit() failed: {e}")

        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)

    @staticmethod
    def _is_driver_alive(driver) -> bool:
        """Cheap liveness probe for pooled / cached drivers."""
        try:
            _ = driver.current_url
            return True
        except (WebDriverException, OSError, AttributeError, urllib3.exceptions.HTTPError):
            return False

    def _create_driver(self, user_data_dir: str, proxy: Optional[str], minimal: bool = False):
        """
        Build a Chrome driver (undetected if available, else standard Selenium).

        Args:
            user_data_dir: Unique profile directory owned by the returned driver.
            proxy: Proxy string or None. Passed to Chrome via ``--proxy-server``.
            minimal: Use the reduced option set (second-chance fallback).
        """
        endpoint = parse_proxy(proxy) if proxy else None
        if endpoint and endpoint.has_auth:
            # Chrome silently ignores credentials in --proxy-server.
            logging.warning(
                f"Selenium cannot authenticate to {endpoint.masked()}; "
                "use an IP-whitelisted proxy or the Playwright path for this proxy"
            )

        options = uc.ChromeOptions() if UNDETECTED_AVAILABLE else Options()
        options.add_argument(f"--user-data-dir={user_data_dir}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--remote-debugging-port=0")
        if endpoint:
            options.add_argument(endpoint.chrome_argument())

        if minimal:
            options.add_argument("--headless")
        elif UNDETECTED_AVAILABLE:
            for arg in (
                "--disable-extensions",
                "--disable-plugins",
                "--disable-blink-features=AutomationControlled",
                "--window-size=1920,1080",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-infobars",
                "--disable-notifications",
                "--disable-popup-blocking",
                "--disable-client-side-phishing-detection",
                "--disable-sync",
                "--disable-translate",
                "--hide-scrollbars",
                "--mute-audio",
                "--no-first-run",
                "--disable-default-apps",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-background-networking",
                "--disable-crash-reporter",
                "--disable-oopr-debug-crash-dump",
                "--no-crash-upload",
                "--disable-gpu-sandbox",
                "--disable-software-rasterizer",
                "--log-level=3",
                "--lang=tr-TR",
            ):
                options.add_argument(arg)
            options.add_experimental_option(
                "prefs",
                {
                    "profile.default_content_setting_values": {
                        "notifications": 2,
                        "geolocation": 2,
                        "media_stream": 2,
                    },
                    "profile.managed_default_content_settings": {"images": 1},
                },
            )
        else:
            for arg in (
                "--headless",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-images",
                "--disable-blink-features=AutomationControlled",
                "--window-size=1920,1080",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--log-level=3",
            ):
                options.add_argument(arg)

        if UNDETECTED_AVAILABLE:
            return uc.Chrome(options=options, version_main=None)
        return webdriver.Chrome(options=options)

    def _setup_browser_automation(self) -> bool:
        """Setup browser automation for sites that require JavaScript."""

        if not SELENIUM_AVAILABLE:
            logging.warning("Selenium not available for browser automation")
            return False

        # Reuse the current driver only if it is alive and bound to the active proxy
        if self.driver is not None:
            if (
                getattr(self.driver, "_dws_proxy", None) == self.current_proxy
                and self._is_driver_alive(self.driver)
            ):
                return True
            self._quit_driver(self.driver)
            self.driver = None

        # Try to get a matching browser from the pool first
        pooled = self._get_browser_from_pool(self.current_proxy)
        if pooled:
            logging.info("Reusing browser from pool")
            self.driver = pooled
            return True

        # First the full option set, then the minimal one as second chance
        for minimal in (False, True):
            if minimal:
                logging.info("Attempting fallback browser setup...")

            temp_dir = tempfile.mkdtemp(prefix=f"chrome_profile_{uuid.uuid4().hex[:8]}_")
            driver = None
            ready = False
            try:
                driver = self._create_driver(temp_dir, self.current_proxy, minimal)
                driver.execute_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )
                # The driver owns its profile dir and proxy binding
                driver._dws_temp_dir = temp_dir
                driver._dws_proxy = self.current_proxy
                self.driver = driver
                ready = True
                logging.info("Browser automation setup successful")
                return True
            except (WebDriverException, OSError, RuntimeError, ValueError) as e:
                logging.error(
                    f"Failed to setup browser automation (minimal={minimal}): "
                    f"{redact_proxy_credentials(e)}"
                )
            finally:
                if not ready:
                    self._quit_driver(driver, temp_dir)

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
        site_profile=None,
    ) -> requests.Response:
        """
        Fetch URL with the strategy configured under ``config["anti_bot"]``.

        Order (default ``minimal`` mode): plain HTTP -> Cloudflare bypass when
        the response is a block/challenge -> browser (only if the selected
        profile allows it). ``cloudflare_first`` (aggressive) swaps the first
        two steps.

        Args:
            url: Target URL
            method: HTTP method
            data: Request data
            use_browser: Force browser automation (skips plain HTTP and bypass)
            site_profile: Detected site profile; may raise the strategy tier

        Returns:
            Response object
        """

        # Check if session should be reset
        if self._should_reset_session():
            self._reset_session()

        # Increment request counter
        self._request_count += 1

        # Select appropriate profile (strategy + site profile + domain rules)
        profile = self.select_profile(url, site_profile=site_profile)

        # Browser explicitly requested: skip plain HTTP and Cloudflare bypass.
        # This lets the caller's fallback chain escalate when extraction was empty.
        if use_browser:
            log_message(
                "INFO",
                "Browser automation explicitly requested, skipping Cloudflare bypass",
            )
            return self._fetch_with_browser(url, method, data)

        # sahibinden.com always needs a real browser
        if "sahibinden.com" in url.lower():
            log_message("INFO", "Attempting browser automation for sahibinden.com")
            return self._fetch_with_browser(url, method, data)

        steps = (
            ("cloudflare", "plain")
            if self.strategy.cloudflare_first or not self.strategy.plain_http_first
            else ("plain", "cloudflare")
        )

        last_response = None
        last_error: Optional[requests.exceptions.RequestException] = None
        for step in steps:
            if step == "cloudflare":
                if not self.cloudflare_bypass:
                    continue
                log_message("INFO", "Attempting Cloudflare bypass...")
                response = self.cloudflare_bypass.bypass_cloudflare(url, method, data)
                if response is not None and response.status_code == 200:
                    log_message("INFO", "Successfully bypassed Cloudflare protection")
                    return response
                log_message(
                    "WARNING", "Cloudflare bypass failed, trying other methods..."
                )
                continue

            try:
                response = self._fetch_plain_http(url, method, data)
            except requests.exceptions.RequestException as e:
                last_error = e
                continue
            if not self._needs_escalation(response):
                return response
            last_response = response
            logging.info(
                f"Plain HTTP blocked ({response.status_code}); escalating for {url}"
            )

        # Use browser automation if the profile allows it
        if profile.browser_automation:
            return self._fetch_with_browser(url, method, data)

        if last_response is not None:
            return last_response
        if last_error is not None:
            raise last_error
        raise requests.exceptions.RequestException(
            f"All fetch strategies failed for {url}"
        )

    @staticmethod
    def _needs_escalation(response) -> bool:
        """True when a response looks like a block or a bot challenge."""
        if response.status_code in (403, 429, 503):
            return True
        return response.status_code == 200 and body_suggests_bot_challenge(
            getattr(response, "text", "")
        )

    def _fetch_plain_http(
        self, url: str, method: str, data: Dict
    ) -> requests.Response:
        """Plain HTTP request; never falls back to the browser by itself."""
        return self._fetch_with_requests(
            url, method, data, allow_browser_fallback=False
        )

    def _browser_fallback_enabled(self) -> bool:
        """Whether a final 403 may be retried in a real browser."""
        return self.strategy.browser_on_forbidden or bool(
            self.current_profile and self.current_profile.browser_automation
        )

    def _sleep_range(self, low: float, high: float) -> None:
        """Sleep a random time unless delays are disabled by config."""
        if self.strategy.human_delay_style == "none":
            return
        time.sleep(random.uniform(low, high))

    def _fetch_with_requests(
        self,
        url: str,
        method: str,
        data: Dict,
        allow_browser_fallback: bool = True,
    ) -> requests.Response:
        """Fetch using enhanced requests with stealth techniques.

        Fallback direction is strictly requests -> browser -> requests(terminal);
        the browser path passes ``allow_browser_fallback=False`` to prevent loops.
        """

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
                    method=method,
                    url=url,
                    headers=headers,
                    data=data,
                    timeout=30,
                    proxies=self._requests_proxies,
                )

                # Handle 403 Forbidden with retry strategy
                if response.status_code == 403:
                    if attempt < max_retries - 1:
                        logging.warning(
                            f"403 Forbidden on attempt {attempt + 1}, retrying with different strategy..."
                        )
                        # Try different approach: reset session, change user agent, add delay
                        self._reset_session()
                        self._sleep_range(5, 10)  # Longer delay for 403
                        continue
                    else:
                        logging.error(
                            f"403 Forbidden after {max_retries} attempts. Site may be blocking requests."
                        )
                        if allow_browser_fallback and self._browser_fallback_enabled():
                            # Try browser automation as last resort (one-way:
                            # the browser path calls us with allow_browser_fallback=False)
                            return self._fetch_with_browser(url, method, data)
                        return response

                # Store cookies for session persistence
                if response.cookies:
                    self.session_cookies[url] = response.cookies

                self.request_count += 1
                self.last_request_time = time.time()

                return response

            except requests.exceptions.RequestException as e:
                safe_error = redact_proxy_credentials(e)
                if isinstance(e, requests.exceptions.ProxyError):
                    self._apply_proxy(rotate=True)
                if attempt < max_retries - 1:
                    logging.warning(
                        f"Request failed on attempt {attempt + 1}: {safe_error}, retrying..."
                    )
                    self._sleep_range(2, 5)
                    continue
                else:
                    logging.error(
                        f"Request failed after {max_retries} attempts: {safe_error}"
                    )
                    raise

    def _fetch_with_browser(
        self, url: str, method: str, data: Dict
    ) -> requests.Response:
        """Fetch using browser automation for JavaScript-heavy sites."""

        if not self._setup_browser_automation():
            # One-way fallback: browser -> requests (never back to browser)
            return self._fetch_with_requests(
                url, method, data, allow_browser_fallback=False
            )

        succeeded = False
        try:
            # Navigate to URL with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.driver.get(url)
                    break
                except WebDriverException as nav_error:
                    if attempt == max_retries - 1:
                        raise nav_error
                    logging.warning(
                        f"Navigation attempt {attempt + 1} failed: {nav_error}"
                    )
                    time.sleep(2)

            # Humanize behavior
            self._humanize_browser_behavior()

            # Wait for page to load with timeout and JavaScript content
            try:
                # First wait for basic page structure
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                # Wait for JavaScript content to load - look for common content indicators
                content_selectors = [
                    "div",
                    "main",
                    "article",
                    "section",
                    "ul",
                    "ol",
                    "table",
                    "[class*='content']",
                    "[class*='main']",
                    "[class*='container']",
                    "[id*='content']",
                    "[id*='main']",
                    "[id*='container']",
                ]

                content_loaded = False
                for selector in content_selectors:
                    try:
                        WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        content_loaded = True
                        break
                    except TimeoutException:
                        continue

                if not content_loaded:
                    # Fallback: wait for any element with text content
                    WebDriverWait(self.driver, 5).until(
                        lambda driver: len(
                            driver.find_elements(By.XPATH, "//*[text()]")
                        )
                        > 0
                    )

                # Additional wait for dynamic content
                time.sleep(2)

                # Special handling for VFS Global website
                if "vfsglobal.com" in url.lower():
                    try:
                        # Wait for VFS-specific content to load
                        vfs_selectors = [
                            "[class*='appointment']",
                            "[class*='booking']",
                            "[class*='service']",
                            "[class*='visa']",
                            "[class*='application']",
                            "form",
                            "button",
                        ]
                        for selector in vfs_selectors:
                            try:
                                WebDriverWait(self.driver, 3).until(
                                    EC.presence_of_element_located(
                                        (By.CSS_SELECTOR, selector)
                                    )
                                )
                                break
                            except TimeoutException:
                                continue
                        time.sleep(1)  # Additional wait for VFS content
                    except WebDriverException as e:
                        logging.debug(f"VFS-specific wait failed: {e}")

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

            except OSError as e:
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

            succeeded = True
            return MockResponse(page_source)

        except (WebDriverException, TimeoutException, OSError) as e:
            logging.error(f"Browser automation failed: {redact_proxy_credentials(e)}")
        finally:
            if not succeeded:
                # Always release the browser and its profile directory on failure
                self._quit_driver(self.driver)
                self.driver = None

        # One-way fallback: browser -> requests (never back to browser)
        return self._fetch_with_requests(
            url, method, data, allow_browser_fallback=False
        )

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
            # Return browser to pool instead of quitting (pool quits it if full/dead)
            self._return_browser_to_pool(self.driver)
            self.driver = None

        # Cleanup Cloudflare bypass
        if self.cloudflare_bypass:
            try:
                self.cloudflare_bypass.cleanup()
            except (requests.exceptions.RequestException, OSError, AttributeError) as e:
                logging.warning(
                    f"Cloudflare bypass cleanup failed: {redact_proxy_credentials(e)}"
                )

        # Human behavior simulator doesn't need explicit cleanup

        if self.session:
            self.session.close()

    @classmethod
    def cleanup_all_browsers(cls):
        """Cleanup all browsers in the pool."""
        with cls._pool_lock:
            for driver in cls._browser_pool:
                cls._quit_driver(driver)
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
