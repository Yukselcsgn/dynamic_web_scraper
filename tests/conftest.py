"""
Shared pytest configuration and fixtures.

Optional heavy dependencies are stubbed so unit tests can run without
matplotlib / plotly / selenium when only core logic is tested.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Project root on path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _ensure_optional_dependency_stubs() -> None:
    """Stub optional imports before ``scraper`` package loads."""
    import types

    def _pkg(name: str) -> types.ModuleType:
        if name in sys.modules:
            return sys.modules[name]
        mod = types.ModuleType(name)
        mod.__path__ = []  # treat as package for nested imports
        sys.modules[name] = mod
        return mod

    # Matplotlib
    _pkg("matplotlib")
    pyplot = _pkg("matplotlib.pyplot")
    pyplot.switch_backend = MagicMock()

    # Seaborn
    seaborn = _pkg("seaborn")
    seaborn.set_theme = MagicMock()
    seaborn.set_palette = MagicMock()

    # Plotly submodules
    _pkg("plotly")
    _pkg("plotly.express")
    _pkg("plotly.graph_objects")
    subplots = _pkg("plotly.subplots")
    subplots.make_subplots = MagicMock()

    # SciPy
    scipy = _pkg("scipy")
    scipy.stats = MagicMock()
    signal = _pkg("scipy.signal")
    signal.detrend = MagicMock()

    _pkg("schedule")

    # Browser / bypass stacks
    for name in (
        "selenium",
        "selenium.webdriver",
        "selenium.webdriver.chrome",
        "selenium.webdriver.chrome.options",
        "selenium.webdriver.common.by",
        "selenium.webdriver.common.action_chains",
        "selenium.webdriver.support",
        "selenium.webdriver.support.ui",
        "selenium.webdriver.support.expected_conditions",
        "selenium.common",
        "selenium.common.exceptions",
        "undetected_chromedriver",
        "cloudscraper",
        "playwright",
        "playwright.async_api",
        "requests_html",
    ):
        if name not in sys.modules:
            sys.modules[name] = MagicMock()


_ensure_optional_dependency_stubs()

import pytest  # noqa: E402


@pytest.fixture
def project_root() -> Path:
    return ROOT


@pytest.fixture
def minimal_config() -> dict:
    """Default anti-bot-friendly config for unit tests."""
    return {
        "user_agents": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ],
        "proxies": [],
        "use_proxy": False,
        "anti_bot": {
            "mode": "minimal",
            "adapt_to_site": True,
            "plain_http_first": True,
            "cloudflare_first": False,
            "human_delay_style": "none",
            "browser_on_forbidden": False,
        },
    }


@pytest.fixture
def sample_product_html() -> str:
    return """
    <html><body>
      <motion.div class="product">
        <h2 class="title"><a href="/p/1">Widget</a></h2>
        <span class="price">$12.00</span>
      </div>
    </body></html>
    """.replace("motion.", "")


@pytest.fixture
def mock_site_profile():
    profile = MagicMock()
    profile.site_type = "ecommerce"
    profile.confidence = 0.9
    profile.use_selenium = False
    profile.anti_bot_measures = []
    profile.recommended_settings = {
        "cloudflare_protection": False,
        "javascript_required": False,
    }
    profile.selectors = {
        "product_container": ".product",
        "title": ".title",
        "price": ".price",
    }
    return profile


@pytest.fixture
def cloudflare_site_profile(mock_site_profile):
    mock_site_profile.anti_bot_measures = ["cloudflare"]
    mock_site_profile.recommended_settings["cloudflare_protection"] = True
    return mock_site_profile
