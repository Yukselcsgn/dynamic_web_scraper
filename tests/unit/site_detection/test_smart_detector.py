"""Unit tests for SmartSiteDetector."""

from __future__ import annotations

import pytest
from bs4 import BeautifulSoup

from scraper.site_detection.smart_detector import SmartSiteDetector


@pytest.fixture
def detector():
    return SmartSiteDetector()


@pytest.mark.unit
class TestSmartSiteDetector:
    def test_detect_ecommerce_from_content(self, detector):
        html = """
        <html><body>
          <div class="product"><span class="price">$10</span>
          <button>add to cart</button></motion.div>
        </body></html>
        """.replace("motion.", "")
        soup = BeautifulSoup(html, "html.parser")
        site_type = detector._detect_site_type("https://shop.example.com", soup)
        assert site_type == "ecommerce"

    def test_detect_cloudflare_measure(self, detector):
        html = "<html><body>Checking your browser before accessing cloudflare</body></html>"
        soup = BeautifulSoup(html, "html.parser")
        measures = detector._detect_anti_bot_measures(soup)
        assert "cloudflare" in measures

    def test_recommended_settings_include_cloudflare_flag(self, detector):
        settings = detector._generate_recommended_settings(
            "ecommerce", ["cloudflare"], use_selenium=False
        )
        assert settings["cloudflare_protection"] is True
        assert settings["javascript_required"] is False

    def test_should_use_selenium_when_js_heavy(self, detector):
        scripts = "".join(f"<script src='{i}.js'></script>" for i in range(20))
        soup = BeautifulSoup(f"<html><body>{scripts}</body></html>", "html.parser")
        assert detector._should_use_selenium([], soup) is True

    def test_detect_site_returns_profile(self, detector):
        html = (
            "<html><body><div class='product'><span class='price'>1</span></div>"
            "</body></html>"
        )
        profile = detector.detect_site("https://shop.test/", html_content=html)
        assert profile.site_type == "ecommerce"
        assert 0.0 < profile.confidence <= 1.0
        assert isinstance(profile.selectors, dict)
