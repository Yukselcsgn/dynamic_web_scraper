import warnings
from unittest.mock import ANY, MagicMock, patch

import pytest

from scraper.core.scraper import Scraper


@pytest.fixture
def mock_initializer():
    with patch("scraper.core.scraper.ScraperInitializer") as MockInit:
        # returns the Mock Object that will be assigned to self.initializer
        mock_instance = MockInit.return_value

        # Setup common mock attributes
        mock_instance.stealth_manager = MagicMock()
        mock_instance.stats = {
            "requests_made": 0,
            "successful_requests": 0,
            "failed_requests": 0,
        }
        mock_instance.universal_extractor = MagicMock()
        mock_instance.data_enricher = MagicMock()
        mock_instance.price_analyzer = MagicMock()
        mock_instance.data_visualizer = MagicMock()
        mock_instance.automated_reporter = MagicMock()
        mock_instance.site_comparator = MagicMock()
        mock_instance.plugin_manager = MagicMock()
        mock_instance.export_manager = MagicMock()

        yield mock_instance


@pytest.fixture
def mock_components():
    # Patch the component classes so we don't instantiate real ones
    with patch("scraper.core.scraper.SiteDetector") as MD, patch(
        "scraper.core.scraper.DataExtractor"
    ) as DE, patch("scraper.core.scraper.DataFetcher") as DF, patch(
        "scraper.core.scraper.DataProcessor"
    ) as DP, patch(
        "scraper.core.scraper.ScraperUtilities"
    ) as SU:
        yield {
            "SiteDetector": MD,
            "DataExtractor": DE,
            "DataFetcher": DF,
            "DataProcessor": DP,
            "ScraperUtilities": SU,
        }


@pytest.fixture
def scraper_instance(mock_initializer, mock_components):
    # Initialize with basic config
    config = {"timeout": 30}
    return Scraper(url="http://example.com", config=config)


class TestScraperMethods:
    def test_init_legacy_kwargs(self, mock_initializer, mock_components):
        """Test backward compatibility for initialization kwargs."""
        config = {}
        with pytest.warns(DeprecationWarning, match="headless"):
            scraper = Scraper("http://test.com", config, headless=True)

        assert config["selenium"]["driver"]["headless"] is True

    def test_fetch_data_happy_path(self, scraper_instance):
        """Test full data fetching workflow (Happy Path)."""
        # Arrange
        scraper_instance.site_detector.detect_site_profile.return_value = MagicMock()

        # Mock fetch_raw_data_with_fallback to return data
        # We need to mock the method of the instance, or the underlying calls
        # Let's mock the underlying calls controlled by helper methods

        # Mock stealth fetch response
        mock_response = MagicMock()
        mock_response.text = "<html></html>"
        scraper_instance.initializer.stealth_manager.fetch_with_stealth.return_value = (
            mock_response
        )

        # Mock extraction
        scraper_instance.data_extractor.extract_data.return_value = [{"item": 1}]

        # Mock processing
        scraper_instance.data_processor.enrich_data.return_value = MagicMock(
            enriched_data=[{"item": 1, "enriched": True}]
        )

        # Act
        result = scraper_instance.fetch_data()

        # Assert
        assert len(result["raw_data"]) == 1
        assert "enriched_data" in result
        scraper_instance.site_detector.detect_site_profile.assert_called_once()
        scraper_instance.initializer.stealth_manager.fetch_with_stealth.assert_called()

    def test_fetch_raw_data_with_fallback_chain(self, scraper_instance):
        """Test the fallback chain: Initial -> Selenium."""
        # Arrange
        # 1. Initial fetch fails (returns empty list from extractor)
        # 2. Browser fallback succeeds

        # Mock site profile
        scraper_instance.site_profile = MagicMock()
        scraper_instance.site_profile.use_selenium = False

        # Setup fetch_with_stealth responses
        # First call (Standard): Success HTTP but empty extraction
        # Second call (Browser): Success HTTP and good extraction

        response_empty = MagicMock()
        response_empty.text = "empty html"

        response_data = MagicMock()
        response_data.text = "data html"

        scraper_instance.initializer.stealth_manager.fetch_with_stealth.side_effect = [
            response_empty,
            response_data,
        ]

        # Mock extractor behavior
        # First call: returns []
        # Second call: returns [{"data": 1}]
        scraper_instance.data_extractor.extract_data.side_effect = [[], [{"data": 1}]]

        # Act
        result = scraper_instance._fetch_raw_data_with_fallback()

        # Assert
        assert len(result) == 1
        assert result == [{"data": 1}]
        # Check that we called fetch twice: once normal, once use_browser=True
        assert (
            scraper_instance.initializer.stealth_manager.fetch_with_stealth.call_count
            == 2
        )

        calls = (
            scraper_instance.initializer.stealth_manager.fetch_with_stealth.call_args_list
        )
        assert calls[0].kwargs.get("use_browser") is False
        assert calls[0].kwargs.get("site_profile") is scraper_instance.site_profile
        assert calls[1].kwargs.get("use_browser") is True
        assert calls[1].kwargs.get("site_profile") is scraper_instance.site_profile

    def test_context_manager_cleanup(self, mock_initializer, mock_components):
        """Test context manager calls cleanup."""
        config = {}
        with Scraper("http://test.com", config) as scraper:
            pass

        # Verify cleanups called
        scraper.initializer.stealth_manager.cleanup.assert_called_once()

    def test_process_data_flags(self, scraper_instance):
        """Test that processing flags are respected."""
        raw_data = [{"id": 1}]

        # Disable enrichment via flag
        scraper_instance._process_data(
            raw_data, enable_enrichment=False, enable_analysis=True
        )

        # Assert
        scraper_instance.data_processor.enrich_data.assert_not_called()
        scraper_instance.data_processor.analyze_prices.assert_called_once()

    def test_fetch_data_all_fail(self, scraper_instance):
        """Test returning empty result when all fallbacks fail."""
        # Mock extract_data to always return []
        scraper_instance.data_extractor.extract_data.return_value = []

        # Mock stealth manager responses to exist but yield no data
        mock_resp = MagicMock()
        mock_resp.text = "html"
        scraper_instance.initializer.stealth_manager.fetch_with_stealth.return_value = (
            mock_resp
        )

        # Since I am not mocking Playwright/RequestsHTML imports here, those blocks might be skipped or fail
        # depending on environment.
        # But the method should return [] eventually.

        result = scraper_instance.fetch_data()

        assert result["raw_data"] == []
        assert result["data_items_extracted"] == 0
