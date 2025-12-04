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
Smart Site Detector - Automatically analyzes websites and generates optimal scraping strategies.
"""
import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


@dataclass
class SiteProfile:
    """Represents a detected site profile with optimal scraping strategies."""

    site_type: str
    confidence: float
    selectors: Dict[str, str]
    wait_time: int
    use_selenium: bool
    anti_bot_measures: List[str]
    recommended_settings: Dict[str, Any]


class SmartSiteDetector:
    """
    Intelligent site detection and configuration generator.
    Automatically analyzes websites and creates optimal scraping strategies.
    """

    def __init__(self):
        self.site_patterns = {
            "ecommerce": [
                r"shop|store|buy|cart|checkout|product|item",
                r"price|cost|sale|discount|offer",
                r"add to cart|buy now|purchase",
            ],
            "classifieds": [
                r"classified|listing|advertisement|advert",
                r"for sale|wanted|offer|contact seller",
                r"price|location|description",
            ],
            "news": [
                r"news|article|story|post|blog",
                r"publish|author|date|read more",
                r"headline|title|content",
            ],
            "social_media": [
                r"profile|user|follow|like|share",
                r"post|tweet|status|update",
                r"comment|reply|retweet",
            ],
        }

        self.common_selectors = {
            "ecommerce": {
                "product_container": '.product, .item, .listing, [class*="product"], [class*="item"]',
                "product_title": '.title, .name, h1, h2, h3, [class*="title"], [class*="name"]',
                "product_price": '.price, .cost, [class*="price"], [class*="cost"], [data-price]',
                "product_image": 'img[src*="product"], img[alt*="product"], .product img',
                "product_link": 'a[href*="product"], a[href*="item"], .product a',
                "add_to_cart": '.add-to-cart, .buy-now, [class*="cart"], [class*="buy"]',
            },
            "classifieds": {
                "listing_container": '.listing, .ad, .classified, [class*="listing"]',
                "listing_title": '.title, .name, h1, h2, h3, [class*="title"]',
                "listing_price": '.price, .cost, [class*="price"], [data-price]',
                "listing_image": 'img[src*="listing"], img[alt*="listing"], .listing img',
                "listing_link": 'a[href*="listing"], a[href*="ad"], .listing a',
                "contact_info": '.contact, .phone, .email, [class*="contact"]',
            },
        }

        self.anti_bot_indicators = [
            "captcha",
            "recaptcha",
            "cloudflare",
            "bot",
            "robot",
            "rate limit",
            "blocked",
            "suspicious",
            "security check",
            "javascript",
            "enable javascript",
            "turn on javascript",
        ]

    def detect_site(
        self, url: str, html_content: str = None, user_agent_manager=None
    ) -> SiteProfile:
        """
        Analyze a website and generate an optimal scraping profile.

        Args:
            url: The URL to analyze
            html_content: Optional HTML content (if not provided, will fetch)
            user_agent_manager: Optional UserAgentManager instance

        Returns:
            SiteProfile with optimal scraping configuration
        """
        try:
            # Fetch HTML if not provided
            if not html_content:
                html_content = self._fetch_html(url, user_agent_manager)

            # Parse HTML
            soup = BeautifulSoup(html_content, "html.parser")

            # Analyze site characteristics
            site_type = self._detect_site_type(url, soup)
            anti_bot_measures = self._detect_anti_bot_measures(soup)
            selectors = self._generate_optimal_selectors(site_type, soup)

            # Determine optimal settings
            use_selenium = self._should_use_selenium(anti_bot_measures, soup)
            wait_time = self._calculate_optimal_wait_time(anti_bot_measures, site_type)

            # Calculate confidence score
            confidence = self._calculate_confidence(
                site_type, selectors, anti_bot_measures
            )

            # Generate recommended settings
            recommended_settings = self._generate_recommended_settings(
                site_type, anti_bot_measures, use_selenium
            )

            return SiteProfile(
                site_type=site_type,
                confidence=confidence,
                selectors=selectors,
                wait_time=wait_time,
                use_selenium=use_selenium,
                anti_bot_measures=anti_bot_measures,
                recommended_settings=recommended_settings,
            )

        except Exception as e:
            logging.error(f"Error detecting site {url}: {e}")
            return self._get_default_profile()

    def _fetch_html(self, url: str, user_agent_manager=None) -> str:
        """Fetch HTML content from URL."""
        if user_agent_manager:
            try:
                user_agent = user_agent_manager.get_user_agent()
            except Exception as e:
                logging.warning(f"Failed to get user agent: {e}")
                user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        else:
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

        headers = {"User-Agent": user_agent}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text

    def _detect_site_type(self, url: str, soup: BeautifulSoup) -> str:
        """Detect the type of website based on content and URL patterns."""
        domain = urlparse(url).netloc.lower()
        text_content = soup.get_text().lower()

        scores = {"ecommerce": 0, "classifieds": 0, "news": 0, "social_media": 0}

        # Check domain patterns
        for site_type, patterns in self.site_patterns.items():
            if isinstance(patterns, list):
                for pattern in patterns:
                    if re.search(pattern, domain) or re.search(pattern, text_content):
                        scores[site_type] += 1
            else:
                # Handle case where patterns might not be a list
                if re.search(patterns, domain) or re.search(patterns, text_content):
                    scores[site_type] += 1

        # Check for specific indicators
        if any(word in text_content for word in ["price", "buy", "cart", "checkout"]):
            scores["ecommerce"] += 2
        if any(
            word in text_content for word in ["for sale", "wanted", "contact seller"]
        ):
            scores["classifieds"] += 2
        if any(word in text_content for word in ["article", "news", "published"]):
            scores["news"] += 2
        if any(word in text_content for word in ["profile", "follow", "like", "share"]):
            scores["social_media"] += 2

        # Return the type with highest score
        return max(scores, key=scores.get)

    def _detect_anti_bot_measures(self, soup: BeautifulSoup) -> List[str]:
        """Detect anti-bot measures on the page."""
        measures = []
        text_content = soup.get_text().lower()

        for indicator in self.anti_bot_indicators:
            if indicator in text_content:
                measures.append(indicator)

        # Check for JavaScript dependencies
        scripts = soup.find_all("script")
        if len(scripts) > 10:  # Many scripts might indicate dynamic content
            measures.append("javascript_heavy")

        # Check for forms that might be CAPTCHA
        forms = soup.find_all("form")
        for form in forms:
            if "captcha" in form.get_text().lower():
                measures.append("captcha")

        return measures

    def _generate_optimal_selectors(
        self, site_type: str, soup: BeautifulSoup
    ) -> Dict[str, str]:
        """Generate optimal CSS selectors for the detected site type."""
        selectors = self.common_selectors.get(
            site_type, self.common_selectors["ecommerce"]
        ).copy()

        # Try to find more specific selectors based on actual content
        if site_type == "ecommerce":
            selectors.update(self._find_ecommerce_selectors(soup))
        elif site_type == "classifieds":
            selectors.update(self._find_classified_selectors(soup))

        return selectors

    def _find_ecommerce_selectors(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Find specific ecommerce selectors from the page."""
        selectors = {}

        # Look for price elements
        price_elements = soup.find_all(text=re.compile(r"[\$€£¥]\d+"))
        if price_elements:
            # Find the most common parent class
            price_parents = [
                elem.parent.get("class", []) for elem in price_elements if elem.parent
            ]
            if price_parents:
                most_common_class = max(set(price_parents), key=price_parents.count)
                if most_common_class:
                    selectors["product_price"] = f".{most_common_class[0]}"

        # Look for product containers
        product_indicators = ["product", "item", "goods", "merchandise"]
        for indicator in product_indicators:
            containers = soup.find_all(class_=re.compile(indicator, re.I))
            if containers:
                selectors["product_container"] = f'[class*="{indicator}"]'
                break

        return selectors

    def _find_classified_selectors(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Find specific classified ad selectors from the page."""
        selectors = {}

        # Look for listing indicators
        listing_indicators = ["listing", "ad", "classified", "posting"]
        for indicator in listing_indicators:
            containers = soup.find_all(class_=re.compile(indicator, re.I))
            if containers:
                selectors["listing_container"] = f'[class*="{indicator}"]'
                break

        return selectors

    def _should_use_selenium(
        self, anti_bot_measures: List[str], soup: BeautifulSoup
    ) -> bool:
        """Determine if Selenium should be used based on anti-bot measures."""
        if any(
            measure in ["javascript_heavy", "captcha", "cloudflare"]
            for measure in anti_bot_measures
        ):
            return True

        # Check if page requires JavaScript
        scripts = soup.find_all("script")
        if len(scripts) > 15:  # Many scripts indicate dynamic content
            return True

        return False

    def _calculate_optimal_wait_time(
        self, anti_bot_measures: List[str], site_type: str
    ) -> int:
        """Calculate optimal wait time between requests."""
        base_wait = 2

        # Add time for anti-bot measures
        if "captcha" in anti_bot_measures:
            base_wait += 5
        if "rate_limit" in anti_bot_measures:
            base_wait += 3
        if "cloudflare" in anti_bot_measures:
            base_wait += 2

        # Add time based on site type
        if site_type == "ecommerce":
            base_wait += 1
        elif site_type == "classifieds":
            base_wait += 2

        return min(base_wait, 10)  # Cap at 10 seconds

    def _calculate_confidence(
        self, site_type: str, selectors: Dict[str, str], anti_bot_measures: List[str]
    ) -> float:
        """Calculate confidence score for the detection."""
        confidence = 0.5  # Base confidence

        # Higher confidence for more specific selectors
        if len(selectors) > 3:
            confidence += 0.2

        # Lower confidence for sites with anti-bot measures
        if anti_bot_measures:
            confidence -= 0.1 * len(anti_bot_measures)

        # Higher confidence for common site types
        if site_type in ["ecommerce", "classifieds"]:
            confidence += 0.1

        return max(0.1, min(1.0, confidence))

    def _generate_recommended_settings(
        self, site_type: str, anti_bot_measures: List[str], use_selenium: bool
    ) -> Dict[str, Any]:
        """Generate recommended scraping settings."""
        settings = {
            "user_agent_rotation": True,
            "proxy_rotation": len(anti_bot_measures) > 0,
            "respect_robots_txt": True,
            "follow_redirects": True,
            "verify_ssl": True,
            "session_persistence": True,
            "rate_limiting": {
                "requests_per_minute": 30 if anti_bot_measures else 60,
                "delay_between_requests": 2 if anti_bot_measures else 1,
            },
        }

        if use_selenium:
            settings.update(
                {"selenium_timeout": 30, "headless": True, "wait_for_elements": True}
            )

        return settings

    def _get_default_profile(self) -> SiteProfile:
        """Return a default profile when detection fails."""
        return SiteProfile(
            site_type="unknown",
            confidence=0.1,
            selectors=self.common_selectors["ecommerce"],
            wait_time=3,
            use_selenium=False,
            anti_bot_measures=[],
            recommended_settings={
                "user_agent_rotation": True,
                "proxy_rotation": False,
                "respect_robots_txt": True,
                "rate_limiting": {
                    "requests_per_minute": 30,
                    "delay_between_requests": 2,
                },
            },
        )

    def save_profile(self, profile: SiteProfile, filename: str):
        """Save a site profile to a JSON file."""
        profile_dict = {
            "site_type": profile.site_type,
            "confidence": profile.confidence,
            "selectors": profile.selectors,
            "wait_time": profile.wait_time,
            "use_selenium": profile.use_selenium,
            "anti_bot_measures": profile.anti_bot_measures,
            "recommended_settings": profile.recommended_settings,
        }

        with open(filename, "w") as f:
            json.dump(profile_dict, f, indent=2)

    def load_profile(self, filename: str) -> Optional[SiteProfile]:
        """Load a site profile from a JSON file."""
        try:
            with open(filename, "r") as f:
                profile_dict = json.load(f)

            return SiteProfile(**profile_dict)
        except Exception as e:
            logging.error(f"Error loading profile {filename}: {e}")
            return None
