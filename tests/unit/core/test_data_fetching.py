import time
from unittest.mock import MagicMock, Mock, patch

import pytest
from requests.exceptions import HTTPError, RequestException, Timeout

from scraper.core.data_fetching import DataFetcher


@pytest.fixture
def mock_stealth_manager():
    return MagicMock()


@pytest.fixture
def mock_stats():
    return {
        "requests_made": 0,
        "successful_requests": 0,
        "failed_requests": 0,
        "processing_time": 0,
        "data_items_extracted": 0,
    }


@pytest.fixture
def data_fetcher(mock_stealth_manager, mock_stats):
    return DataFetcher(mock_stealth_manager, mock_stats)


class TestDataFetcher:
    def test_fetch_data_success(self, data_fetcher, mock_stealth_manager):
        """Test successful data fetching with mocked response."""
        # Arrange
        url = "http://example.com"
        mock_response = MagicMock()
        mock_response.text = "<html>content</html>"
        mock_response.status_code = 200
        mock_stealth_manager.fetch_with_stealth.return_value = mock_response

        # Mock parse_response to return some dummy data
        data_fetcher.parse_response = MagicMock(return_value=[{"title": "Test Item"}])

        # Act
        result = data_fetcher.fetch_data(url)

        # Assert
        assert result["data_items_extracted"] == 1
        assert result["raw_data"] == [{"title": "Test Item"}]
        assert data_fetcher.stats["successful_requests"] == 1
        mock_stealth_manager.fetch_with_stealth.assert_called_once()

    def test_fetch_data_retry_success(self, data_fetcher, mock_stealth_manager):
        """Test that data fetching succeeds after a failure (retry mechanism)."""
        # Arrange
        url = "http://example.com"
        success_response = MagicMock()
        success_response.text = "<html>content</html>"
        success_response.status_code = 200

        # First call raises Timeout, second succeeds
        mock_stealth_manager.fetch_with_stealth.side_effect = [
            Timeout("Connection timed out"),
            success_response,
        ]

        data_fetcher.parse_response = MagicMock(return_value=[{"title": "Test Item"}])

        # Act
        with patch("time.sleep") as mock_sleep:  # Mock sleep to speed up test
            result = data_fetcher.fetch_data(url, max_retries=3, retry_delay=1)

        # Assert
        assert result["data_items_extracted"] == 1
        assert data_fetcher.stats["failed_requests"] == 1
        assert data_fetcher.stats["successful_requests"] == 1
        assert mock_stealth_manager.fetch_with_stealth.call_count == 2
        mock_sleep.assert_called_once()

    def test_fetch_data_all_retries_fail(self, data_fetcher, mock_stealth_manager):
        """Test that data fetching raises Exception after all retries fail."""
        # Arrange
        url = "http://example.com"
        mock_stealth_manager.fetch_with_stealth.side_effect = RequestException(
            "Network error"
        )

        # Act & Assert
        max_retries = 2
        with patch("time.sleep"):
            with pytest.raises(Exception) as excinfo:
                data_fetcher.fetch_data(url, max_retries=max_retries)

        assert f"Failed to fetch data after {max_retries} attempts" in str(
            excinfo.value
        )
        assert data_fetcher.stats["failed_requests"] == max_retries
        assert mock_stealth_manager.fetch_with_stealth.call_count == max_retries

    def test_fetch_data_empty_response(self, data_fetcher, mock_stealth_manager):
        """Test handling of empty response/extraction."""
        # Arrange
        url = "http://example.com"
        mock_response = MagicMock()
        mock_response.text = ""
        mock_response.status_code = 200
        mock_stealth_manager.fetch_with_stealth.return_value = mock_response

        # parse_response returns empty list
        data_fetcher.parse_response = MagicMock(return_value=[])

        # Act
        with patch("time.sleep"):
            result = data_fetcher.fetch_data(url, max_retries=2, retry_delay=0)

        # Assert
        assert result["data_items_extracted"] == 0
        assert result["raw_data"] == []
        # A successful request with an empty parse result is final: no re-request
        assert mock_stealth_manager.fetch_with_stealth.call_count == 1
        assert data_fetcher.stats["successful_requests"] == 1

    def test_fetch_with_site_profile_selenium(self, data_fetcher, mock_stealth_manager):
        """Test that use_browser is True when site_profile.use_selenium is True."""
        # Arrange
        url = "http://example.com"

        # Inject site_profile mock
        mock_profile = MagicMock()
        mock_profile.use_selenium = True
        data_fetcher.site_profile = mock_profile

        mock_response = MagicMock()
        mock_response.text = "<html>content</html>"
        mock_stealth_manager.fetch_with_stealth.return_value = mock_response
        data_fetcher.parse_response = MagicMock(return_value=[{"a": 1}])

        # Act
        data_fetcher.fetch_data(url)

        # Assert
        mock_stealth_manager.fetch_with_stealth.assert_called_with(
            url=url,
            method="GET",
            use_browser=True,
            site_profile=mock_profile,
        )

    def test_fetch_without_site_profile_uses_plain_http_path(
        self, data_fetcher, mock_stealth_manager
    ):
        """Without site_profile, browser automation is not forced."""
        url = "https://www.example.com/list"
        mock_response = MagicMock()
        mock_response.text = "<html>content</html>"
        mock_stealth_manager.fetch_with_stealth.return_value = mock_response
        data_fetcher.parse_response = MagicMock(return_value=[{"a": 1}])

        data_fetcher.fetch_data(url)

        mock_stealth_manager.fetch_with_stealth.assert_called_with(
            url=url,
            method="GET",
            use_browser=False,
            site_profile=None,
        )

    def test_parse_response_without_extractor_returns_empty(self, data_fetcher):
        """Without an extractor nothing can be parsed; result is []."""
        assert data_fetcher.parse_response("some html") == []

    def test_parse_response_delegates_to_extractor(
        self, mock_stealth_manager, mock_stats
    ):
        extractor = MagicMock()
        extractor.extract_data.return_value = [{"title": "x"}]
        profile = MagicMock()
        fetcher = DataFetcher(
            mock_stealth_manager, mock_stats, extractor=extractor, site_profile=profile
        )

        assert fetcher.parse_response("<html/>") == [{"title": "x"}]
        extractor.extract_data.assert_called_once_with("<html/>", profile)

    def test_parse_error_is_not_retried(self, mock_stealth_manager, mock_stats):
        extractor = MagicMock()
        extractor.extract_data.side_effect = ValueError("bad markup")
        fetcher = DataFetcher(mock_stealth_manager, mock_stats, extractor=extractor)
        response = MagicMock()
        response.text = "<html>x</html>"
        mock_stealth_manager.fetch_with_stealth.return_value = response

        result = fetcher.fetch_data("http://example.com", max_retries=3)

        assert result["raw_data"] == []
        assert mock_stealth_manager.fetch_with_stealth.call_count == 1
