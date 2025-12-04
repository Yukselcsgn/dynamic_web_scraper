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
Advanced Cloudflare Bypass Manager

This module implements multiple techniques to bypass Cloudflare protection
including cloudscraper, playwright, and custom browser automation.
"""

import asyncio
import json
import logging
import random
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Import log_message for consistent logging
try:
    from scraper.logging_manager.logging_manager import log_message
except ImportError:

    def log_message(level, message):
        logging.log(getattr(logging, level.upper(), logging.INFO), message)


# Try to import cloudscraper
try:
    import cloudscraper

    CLOUDSCRAPER_AVAILABLE = True
    log_message("INFO", "Cloudscraper available - using for Cloudflare bypass")
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False
    log_message(
        "WARNING", "Cloudscraper not available. Install with: pip install cloudscraper"
    )

# Try to import playwright
try:
    from playwright.async_api import async_playwright

    PLAYWRIGHT_AVAILABLE = True
    log_message("INFO", "Playwright available - using for advanced browser automation")
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    log_message(
        "WARNING", "Playwright not available. Install with: pip install playwright"
    )

# Try to import requests-html
try:
    from requests_html import HTMLSession

    REQUESTS_HTML_AVAILABLE = True
    log_message("INFO", "Requests-HTML available - using for JavaScript rendering")
except ImportError:
    REQUESTS_HTML_AVAILABLE = False
    log_message(
        "WARNING",
        "Requests-HTML not available. Install with: pip install requests-html",
    )


class CloudflareBypass:
    """
    Advanced Cloudflare bypass manager with multiple techniques.
    """

    def __init__(self, config: Dict = None):
        """
        Initialize the Cloudflare bypass manager.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.session = None
        self.playwright_browser = None
        self.playwright_context = None

        # Initialize different bypass methods
        self._init_cloudscraper()
        self._init_requests_session()

    def _init_cloudscraper(self):
        """Initialize cloudscraper session."""
        if CLOUDSCRAPER_AVAILABLE:
            try:
                self.cloudscraper_session = cloudscraper.create_scraper(
                    browser={
                        "browser": "chrome",
                        "platform": "windows",
                        "mobile": False,
                    }
                )

                # Configure retry strategy
                retry_strategy = Retry(
                    total=3,
                    status_forcelist=[429, 500, 502, 503, 504],
                    allowed_methods=["HEAD", "GET", "OPTIONS"],
                    backoff_factor=1,
                )

                adapter = HTTPAdapter(max_retries=retry_strategy)
                self.cloudscraper_session.mount("http://", adapter)
                self.cloudscraper_session.mount("https://", adapter)

                log_message("INFO", "Cloudscraper session initialized successfully")
            except Exception as e:
                log_message("ERROR", f"Failed to initialize cloudscraper: {e}")
                self.cloudscraper_session = None
        else:
            self.cloudscraper_session = None

    def _init_requests_session(self):
        """Initialize enhanced requests session."""
        self.session = requests.Session()

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

        # Set realistic headers
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
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
        )

    def _get_realistic_headers(self, url: str) -> Dict[str, str]:
        """Generate realistic headers for the request."""
        domain = urlparse(url).netloc.lower()

        # Base headers
        headers = {
            "User-Agent": random.choice(
                [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                ]
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": random.choice(
                [
                    "en-US,en;q=0.9",
                    "en-GB,en;q=0.9",
                    "tr-TR,tr;q=0.9,en;q=0.8",
                    "de-DE,de;q=0.9,en;q=0.8",
                ]
            ),
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": random.choice(["1", "0"]),
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
            "Sec-CH-UA": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-CH-UA-Mobile": "?0",
            "Sec-CH-UA-Platform": '"Windows"',
        }

        # Add referer for better authenticity
        if "vfsglobal.com" in domain:
            headers["Referer"] = "https://www.google.com/"
            headers["Accept-Language"] = "tr-TR,tr;q=0.9,en;q=0.8"
        elif "sahibinden.com" in domain:
            headers["Referer"] = "https://www.sahibinden.com/"
            headers["Accept-Language"] = "tr-TR,tr;q=0.9,en;q=0.8"
        else:
            headers["Referer"] = "https://www.google.com/"

        return headers

    def _humanize_timing(self):
        """Add human-like timing delays."""
        # Random delay between 1-3 seconds
        delay = random.uniform(1.0, 3.0)

        # Add micro-delays for more human-like behavior
        micro_delays = [random.uniform(0.1, 0.5) for _ in range(random.randint(1, 3))]

        for micro_delay in micro_delays:
            time.sleep(micro_delay)

        time.sleep(delay)

    def bypass_with_cloudscraper(
        self, url: str, max_retries: int = 3
    ) -> Optional[requests.Response]:
        """
        Attempt to bypass Cloudflare using cloudscraper.

        Args:
            url: Target URL
            max_retries: Maximum number of retry attempts

        Returns:
            Response object or None if failed
        """
        if not CLOUDSCRAPER_AVAILABLE or not self.cloudscraper_session:
            return None

        for attempt in range(max_retries):
            try:
                log_message(
                    "INFO",
                    f"Attempting Cloudflare bypass with cloudscraper (attempt {attempt + 1})",
                )

                # Humanize timing
                self._humanize_timing()

                # Get realistic headers
                headers = self._get_realistic_headers(url)

                # Make request with cloudscraper
                response = self.cloudscraper_session.get(
                    url, headers=headers, timeout=30, allow_redirects=True
                )

                # Check if we successfully bypassed Cloudflare
                if response.status_code == 200 and not self._is_cloudflare_challenge(
                    response.text
                ):
                    log_message(
                        "INFO", f"Successfully bypassed Cloudflare with cloudscraper"
                    )
                    return response
                elif response.status_code == 403:
                    log_message(
                        "WARNING",
                        f"Still getting 403 with cloudscraper (attempt {attempt + 1})",
                    )
                    if attempt < max_retries - 1:
                        time.sleep(random.uniform(5, 10))  # Longer delay for 403
                        continue
                else:
                    log_message(
                        "INFO", f"Cloudscraper response: {response.status_code}"
                    )
                    return response

            except Exception as e:
                log_message(
                    "ERROR", f"Cloudscraper bypass failed (attempt {attempt + 1}): {e}"
                )
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(3, 7))
                    continue

        log_message("WARNING", "Cloudscraper bypass failed after all attempts")
        return None

    async def bypass_with_playwright(
        self, url: str, max_retries: int = 3
    ) -> Optional[str]:
        """
        Attempt to bypass Cloudflare using Playwright.

        Args:
            url: Target URL
            max_retries: Maximum number of retry attempts

        Returns:
            Page HTML content or None if failed
        """
        if not PLAYWRIGHT_AVAILABLE:
            return None

        try:
            async with async_playwright() as p:
                # Launch browser with stealth settings
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                        "--disable-web-security",
                        "--disable-features=VizDisplayCompositor",
                        "--disable-blink-features=AutomationControlled",
                        "--disable-extensions",
                        "--disable-plugins",
                        "--disable-images",
                        "--disable-javascript",  # Disable JS for faster loading
                        "--window-size=1920,1080",
                        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    ],
                )

                # Create context with realistic settings
                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    locale="en-US",
                    timezone_id="America/New_York",
                )

                page = await context.new_page()

                for attempt in range(max_retries):
                    try:
                        log_message(
                            "INFO",
                            f"Attempting Cloudflare bypass with Playwright (attempt {attempt + 1})",
                        )

                        # Navigate to URL
                        await page.goto(
                            url, wait_until="domcontentloaded", timeout=30000
                        )

                        # Wait for page to load
                        await page.wait_for_timeout(random.randint(2000, 5000))

                        # Check if we're on a Cloudflare challenge page
                        content = await page.content()
                        if not self._is_cloudflare_challenge(content):
                            log_message(
                                "INFO",
                                "Successfully bypassed Cloudflare with Playwright",
                            )
                            await browser.close()
                            return content
                        else:
                            log_message(
                                "WARNING",
                                f"Still on Cloudflare challenge page (attempt {attempt + 1})",
                            )
                            if attempt < max_retries - 1:
                                await page.wait_for_timeout(random.randint(5000, 10000))
                                continue

                    except Exception as e:
                        log_message(
                            "ERROR",
                            f"Playwright bypass failed (attempt {attempt + 1}): {e}",
                        )
                        if attempt < max_retries - 1:
                            await page.wait_for_timeout(random.randint(3000, 7000))
                            continue

                await browser.close()
                log_message("WARNING", "Playwright bypass failed after all attempts")
                return None

        except Exception as e:
            log_message("ERROR", f"Playwright initialization failed: {e}")
            return None

    def bypass_with_requests_html(
        self, url: str, max_retries: int = 3
    ) -> Optional[requests.Response]:
        """
        Attempt to bypass Cloudflare using requests-html.

        Args:
            url: Target URL
            max_retries: Maximum number of retry attempts

        Returns:
            Response object or None if failed
        """
        if not REQUESTS_HTML_AVAILABLE:
            return None

        try:
            session = HTMLSession()

            for attempt in range(max_retries):
                try:
                    log_message(
                        "INFO",
                        f"Attempting Cloudflare bypass with requests-html (attempt {attempt + 1})",
                    )

                    # Humanize timing
                    self._humanize_timing()

                    # Get realistic headers
                    headers = self._get_realistic_headers(url)

                    # Make request with JavaScript rendering
                    response = session.get(url, headers=headers, timeout=30)

                    # Render JavaScript
                    response.html.render(timeout=20)

                    # Check if we successfully bypassed Cloudflare
                    if (
                        response.status_code == 200
                        and not self._is_cloudflare_challenge(response.text)
                    ):
                        log_message(
                            "INFO",
                            "Successfully bypassed Cloudflare with requests-html",
                        )
                        return response
                    elif response.status_code == 403:
                        log_message(
                            "WARNING",
                            f"Still getting 403 with requests-html (attempt {attempt + 1})",
                        )
                        if attempt < max_retries - 1:
                            time.sleep(random.uniform(5, 10))
                            continue
                    else:
                        log_message(
                            "INFO", f"Requests-HTML response: {response.status_code}"
                        )
                        return response

                except Exception as e:
                    log_message(
                        "ERROR",
                        f"Requests-HTML bypass failed (attempt {attempt + 1}): {e}",
                    )
                    if attempt < max_retries - 1:
                        time.sleep(random.uniform(3, 7))
                        continue

            log_message("WARNING", "Requests-HTML bypass failed after all attempts")
            return None

        except Exception as e:
            log_message("ERROR", f"Requests-HTML initialization failed: {e}")
            return None

    def bypass_with_enhanced_requests(
        self, url: str, max_retries: int = 3
    ) -> Optional[requests.Response]:
        """
        Attempt to bypass Cloudflare using enhanced requests with advanced techniques.

        Args:
            url: Target URL
            max_retries: Maximum number of retry attempts

        Returns:
            Response object or None if failed
        """
        for attempt in range(max_retries):
            try:
                log_message(
                    "INFO",
                    f"Attempting Cloudflare bypass with enhanced requests (attempt {attempt + 1})",
                )

                # Humanize timing
                self._humanize_timing()

                # Get realistic headers
                headers = self._get_realistic_headers(url)

                # Add session cookies if available
                if hasattr(self, "session_cookies") and self.session_cookies.get(url):
                    self.session.cookies.update(self.session_cookies[url])

                # Make request
                response = self.session.get(
                    url, headers=headers, timeout=30, allow_redirects=True
                )

                # Store cookies for session persistence
                if response.cookies:
                    if not hasattr(self, "session_cookies"):
                        self.session_cookies = {}
                    self.session_cookies[url] = response.cookies

                # Check if we successfully bypassed Cloudflare
                if response.status_code == 200 and not self._is_cloudflare_challenge(
                    response.text
                ):
                    log_message(
                        "INFO",
                        "Successfully bypassed Cloudflare with enhanced requests",
                    )
                    return response
                elif response.status_code == 403:
                    log_message(
                        "WARNING",
                        f"Still getting 403 with enhanced requests (attempt {attempt + 1})",
                    )
                    if attempt < max_retries - 1:
                        # Try different approach: reset session, change user agent, add delay
                        self.session.close()
                        self._init_requests_session()
                        time.sleep(random.uniform(5, 10))
                        continue
                else:
                    log_message(
                        "INFO", f"Enhanced requests response: {response.status_code}"
                    )
                    return response

            except Exception as e:
                log_message(
                    "ERROR",
                    f"Enhanced requests bypass failed (attempt {attempt + 1}): {e}",
                )
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(3, 7))
                    continue

        log_message("WARNING", "Enhanced requests bypass failed after all attempts")
        return None

    def bypass_cloudflare(
        self, url: str, method: str = "GET", data: Dict = None
    ) -> Optional[requests.Response]:
        """
        Main method to bypass Cloudflare using multiple techniques.

        Args:
            url: Target URL
            method: HTTP method
            data: Request data

        Returns:
            Response object or None if all methods failed
        """
        log_message("INFO", f"Attempting to bypass Cloudflare for URL: {url}")

        # Try different bypass methods in order of effectiveness
        bypass_methods = [
            ("cloudscraper", self.bypass_with_cloudscraper),
            ("enhanced_requests", self.bypass_with_enhanced_requests),
            ("requests_html", self.bypass_with_requests_html),
        ]

        # Try each method
        for method_name, method_func in bypass_methods:
            try:
                if method_name == "requests_html":
                    response = method_func(url)
                else:
                    response = method_func(url)

                if response and response.status_code == 200:
                    log_message(
                        "INFO", f"Successfully bypassed Cloudflare using {method_name}"
                    )
                    return response

            except Exception as e:
                log_message("ERROR", f"Bypass method {method_name} failed: {e}")
                continue

        # Try Playwright as last resort (async)
        if PLAYWRIGHT_AVAILABLE:
            try:
                log_message("INFO", "Trying Playwright as last resort...")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                content = loop.run_until_complete(self.bypass_with_playwright(url))
                loop.close()

                if content:
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

                    log_message(
                        "INFO", "Successfully bypassed Cloudflare using Playwright"
                    )
                    return MockResponse(content)

            except Exception as e:
                log_message("ERROR", f"Playwright bypass failed: {e}")

        log_message("ERROR", "All Cloudflare bypass methods failed")
        return None

    def _is_cloudflare_challenge(self, content: str) -> bool:
        """
        Check if the content is a Cloudflare challenge page.

        Args:
            content: HTML content to check

        Returns:
            True if it's a Cloudflare challenge page
        """
        if not content:
            return False

        content_lower = content.lower()
        cloudflare_indicators = [
            "cloudflare",
            "checking your browser",
            "ddos protection",
            "olağandışı bir durum tespit ettik",
            "unusual situation detected",
            "challenge-platform",
            "__cf$cv$params",
            "cf-browser-verification",
            "cf-challenge",
            "ray id",
            "cloudflare ray id",
            "please wait while we check your browser",
            "browser check",
            "security check",
            "verifying you are human",
        ]

        return any(indicator in content_lower for indicator in cloudflare_indicators)

    def cleanup(self):
        """Cleanup resources."""
        if self.session:
            self.session.close()

        if hasattr(self, "cloudscraper_session") and self.cloudscraper_session:
            self.cloudscraper_session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
