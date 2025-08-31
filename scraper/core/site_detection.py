#!/usr/bin/env python3
"""
Site detection and analysis module.

This module handles site detection, profile creation, and site-specific configurations.
"""

from typing import Dict, Optional

from scraper.logging_manager.logging_manager import log_message
from scraper.site_detection.smart_detector import SiteProfile, SmartSiteDetector


class SiteDetector:
    """
    Handles site detection and profile creation for smart scraping.
    """

    def __init__(self, smart_detector: SmartSiteDetector):
        """
        Initialize the site detector.

        Args:
            smart_detector: Smart site detector instance
        """
        self.smart_detector = smart_detector
        self.site_profile = None

    def detect_site_profile(self, url: str, html_content: str = None) -> SiteProfile:
        """
        Detect the site profile for smart scraping.

        Args:
            url: Target URL
            html_content: HTML content to analyze (optional)

        Returns:
            SiteProfile: Detected site profile
        """
        try:
            log_message("INFO", f"Detecting site profile for: {url}")

            # Use smart detector to identify site type
            self.site_profile = self.smart_detector.detect_site(url, html_content)

            if self.site_profile:
                log_message(
                    "INFO", f"Detected site type: {self.site_profile.site_type}"
                )
                log_message("INFO", f"Use Selenium: {self.site_profile.use_selenium}")
                log_message("INFO", f"Confidence: {self.site_profile.confidence}")
            else:
                log_message(
                    "WARNING", "Could not detect site profile, using default settings"
                )
                self.site_profile = self._create_default_profile()

            return self.site_profile

        except Exception as e:
            log_message("ERROR", f"Error detecting site profile: {e}")
            self.site_profile = self._create_default_profile()
            return self.site_profile

    def _create_default_profile(self) -> SiteProfile:
        """
        Create a default site profile when detection fails.

        Returns:
            SiteProfile: Default site profile
        """
        return SiteProfile(
            site_type="generic",
            confidence=0.5,
            selectors={},
            wait_time=2,
            use_selenium=False,
            anti_bot_measures=[],
            recommended_settings={
                "user_agent_rotation": True,
                "proxy_rotation": False,
                "javascript_required": False,
                "captcha_present": False,
                "rate_limiting": False,
                "cloudflare_protection": False,
            },
        )

    def _create_sahibinden_profile(self) -> SiteProfile:
        """
        Create a specialized profile for sahibinden.com.

        Returns:
            SiteProfile: Sahibinden-specific profile
        """
        return SiteProfile(
            site_type="sahibinden",
            confidence=0.95,
            selectors={
                "product_container": ".classified-item",
                "title": ".classified-title",
                "price": ".classified-price",
                "location": ".classified-location",
                "description": ".classified-description",
                "image": ".classified-image img",
                "link": ".classified-title a",
            },
            wait_time=3,
            use_selenium=True,
            anti_bot_measures=["cloudflare", "rate_limiting", "user_agent_check"],
            recommended_settings={
                "user_agent_rotation": True,
                "proxy_rotation": True,
                "javascript_required": True,
                "captcha_present": True,
                "rate_limiting": True,
                "cloudflare_protection": True,
                "extraction_rules": {
                    "price_cleanup": True,
                    "remove_currency": True,
                    "extract_numbers": True,
                },
            },
        )

    def get_site_specific_config(self, url: str) -> Dict:
        """
        Get site-specific configuration based on detected profile.

        Args:
            url: Target URL

        Returns:
            dict: Site-specific configuration
        """
        if not self.site_profile:
            self.detect_site_profile(url)

        config = {
            "use_selenium": self.site_profile.use_selenium,
            "selectors": self.site_profile.selectors,
            "wait_time": self.site_profile.wait_time,
            "recommended_settings": self.site_profile.recommended_settings,
        }

        # Add site-specific configurations
        if "sahibinden.com" in url.lower():
            config.update(self._get_sahibinden_config())
        elif "vfsglobal.com" in url.lower():
            config.update(self._get_vfs_config())

        return config

    def _get_sahibinden_config(self) -> Dict:
        """
        Get sahibinden-specific configuration.

        Returns:
            dict: Sahibinden configuration
        """
        return {
            "wait_for_element": ".classified-item",
            "scroll_behavior": True,
            "human_behavior": True,
            "anti_detection": True,
            "retry_on_failure": True,
            "max_retries": 5,
        }

    def _get_vfs_config(self) -> Dict:
        """
        Get VFS Global-specific configuration.

        Returns:
            dict: VFS configuration
        """
        return {
            "wait_for_element": "form, .appointment, .booking",
            "scroll_behavior": True,
            "human_behavior": True,
            "anti_detection": True,
            "retry_on_failure": True,
            "max_retries": 3,
            "cloudflare_bypass": True,
        }

    def is_cloudflare_protected(self, html_content: str) -> bool:
        """
        Check if the page is protected by Cloudflare.

        Args:
            html_content: HTML content to check

        Returns:
            bool: True if Cloudflare protection is detected
        """
        if not html_content:
            return False

        cloudflare_indicators = [
            "cloudflare",
            "checking your browser",
            "ddos protection",
            "challenge-platform",
            "__cf$cv$params",
            "cf-browser-verification",
            "cf-challenge",
            "ray id",
            "please wait while we check your browser",
            "browser check",
            "security check",
            "verifying you are human",
        ]

        html_lower = html_content.lower()
        return any(indicator in html_lower for indicator in cloudflare_indicators)

    def get_recommended_strategy(self, url: str) -> str:
        """
        Get recommended scraping strategy for the site.

        Args:
            url: Target URL

        Returns:
            str: Recommended strategy
        """
        if not self.site_profile:
            self.detect_site_profile(url)

        if self.site_profile.recommended_settings.get("cloudflare_protection", False):
            return "cloudflare_bypass"
        elif self.site_profile.use_selenium:
            return "browser_automation"
        elif self.site_profile.recommended_settings.get("javascript_required", False):
            return "javascript_rendering"
        else:
            return "standard_requests"
