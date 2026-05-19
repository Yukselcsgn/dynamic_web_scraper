"""Unit tests for StealthManager fetch pipeline."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from scraper.anti_bot.stealth_manager import StealthManager
from tests.helpers.factories.config_factory import make_config


def _http_response(text: str, status: int = 200) -> requests.Response:
    resp = requests.Response()
    resp.status_code = status
    resp._content = text.encode("utf-8")
    resp.url = "https://example.com/"
    return resp


@pytest.fixture
def stealth_minimal():
    return StealthManager(make_config(anti_bot_mode="minimal"))


@pytest.mark.unit
class TestStealthManagerProfiles:
    def test_select_profile_minimal_by_default(self, stealth_minimal):
        profile = stealth_minimal.select_profile("https://simple-blog.example/")
        assert profile.name == "minimal"
        assert profile.browser_automation is False

    def test_select_profile_adapts_with_site_profile(
        self, stealth_minimal, cloudflare_site_profile
    ):
        profile = stealth_minimal.select_profile(
            "https://shop.example/", site_profile=cloudflare_site_profile
        )
        assert profile.name == "balanced"

    def test_domain_override_wins(self, stealth_minimal):
        stealth_minimal.strategy.domain_profile_overrides = {
            "shop.example": "aggressive"
        }
        profile = stealth_minimal.select_profile("https://shop.example/list")
        assert profile.name == "aggressive"


@pytest.mark.unit
class TestStealthManagerFetch:
    def test_plain_http_first_skips_cloudflare_on_success(self, stealth_minimal):
        html = "<html><body><h1>Catalog</h1></body></html>"
        stealth_minimal.cloudflare_bypass = MagicMock()

        with patch.object(
            stealth_minimal, "_fetch_plain_http", return_value=_http_response(html)
        ) as plain:
            result = stealth_minimal.fetch_with_stealth("https://example.com/")

        plain.assert_called_once()
        stealth_minimal.cloudflare_bypass.bypass_cloudflare.assert_not_called()
        assert "Catalog" in result.text

    def test_escalates_to_cloudflare_when_plain_returns_challenge(self, stealth_minimal):
        challenge = _http_response("<html>checking your browser</html>")
        good = _http_response("<html><body>OK</body></html>")

        stealth_minimal.cloudflare_bypass = MagicMock()
        stealth_minimal.cloudflare_bypass.bypass_cloudflare.return_value = good

        with patch.object(
            stealth_minimal, "_fetch_plain_http", return_value=challenge
        ):
            result = stealth_minimal.fetch_with_stealth("https://example.com/")

        stealth_minimal.cloudflare_bypass.bypass_cloudflare.assert_called_once()
        assert "OK" in result.text

    def test_use_browser_skips_plain_and_cloudflare(self, stealth_minimal):
        stealth_minimal.cloudflare_bypass = MagicMock()
        mock_resp = MagicMock()
        mock_resp.text = "<html>browser</html>"

        with patch.object(
            stealth_minimal, "_fetch_with_browser", return_value=mock_resp
        ) as browser, patch.object(stealth_minimal, "_fetch_plain_http") as plain:
            stealth_minimal.fetch_with_stealth(
                "https://example.com/", use_browser=True
            )

        browser.assert_called_once()
        plain.assert_not_called()
        stealth_minimal.cloudflare_bypass.bypass_cloudflare.assert_not_called()

    def test_passes_site_profile_to_select_profile(self, stealth_minimal, mock_site_profile):
        mock_site_profile.use_selenium = True
        stealth_minimal.cloudflare_bypass = MagicMock()
        stealth_minimal.cloudflare_bypass.bypass_cloudflare.return_value = None

        with patch.object(
            stealth_minimal, "_fetch_plain_http", return_value=_http_response("x")
        ), patch.object(
            stealth_minimal, "_fetch_with_browser", return_value=_http_response("data")
        ) as browser:
            stealth_minimal.fetch_with_stealth(
                "https://example.com/",
                use_browser=True,
                site_profile=mock_site_profile,
            )

        assert stealth_minimal.current_profile.name == "stealth"
        browser.assert_called_once()

    def test_403_does_not_open_browser_in_minimal_mode(self, stealth_minimal):
        stealth_minimal.cloudflare_bypass = None
        forbidden = _http_response("blocked", status=403)

        with patch.object(
            stealth_minimal, "_humanize_timing"
        ), patch.object(
            stealth_minimal, "_reset_session"
        ), patch.object(
            requests.Session,
            "request",
            return_value=forbidden,
        ), patch.object(
            stealth_minimal, "_fetch_with_browser"
        ) as browser:
            result = stealth_minimal._fetch_with_requests(
                "https://example.com/", "GET", None
            )

        browser.assert_not_called()
        assert result.status_code == 403
