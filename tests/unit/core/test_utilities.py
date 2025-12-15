from unittest.mock import MagicMock, mock_open, patch

import pytest
from bs4 import BeautifulSoup

from scraper.core.utilities import ScraperUtilities


@pytest.fixture
def mock_export_manager():
    return MagicMock()


@pytest.fixture
def scraper_utilities(mock_export_manager):
    return ScraperUtilities(mock_export_manager)


class TestScraperUtilities:
    def test_save_data_success(self, scraper_utilities):
        """Test data saving workflow."""
        data = [{"id": 1}]
        filename = "output/test.csv"

        with patch("scraper.core.utilities.save_data") as mock_save, patch(
            "os.makedirs"
        ) as mock_makedirs, patch("os.path.exists", return_value=False):
            result = scraper_utilities.save_data(data, filename)

            assert result is True
            mock_makedirs.assert_called_once()
            mock_save.assert_called_once_with(data, filename, "csv")

    def test_save_data_failure(self, scraper_utilities):
        """Test handling of save failure."""
        with patch(
            "scraper.core.utilities.save_data", side_effect=Exception("Disk full")
        ):
            result = scraper_utilities.save_data([], "file.csv")
            assert result is False

    def test_parse_html(self, scraper_utilities):
        """Test HTML parsing wrapper."""
        html = "<p>Test</p>"
        soup = scraper_utilities.parse_html(html)
        assert isinstance(soup, BeautifulSoup)
        assert soup.p.text == "Test"

    def test_analyze_html_content(self, scraper_utilities):
        """Test HTML content analysis."""
        html = """
        <html>
            <head><title>Page Title</title></head>
            <body>
                <h1>Header</h1>
                <a href="/link">Link</a>
                <img src="/img.jpg">
            </body>
        </html>
        """
        analysis = scraper_utilities.analyze_html_content(html)

        assert analysis["title"] == "Page Title"
        assert "Header" in analysis["headings"]
        assert "/link" in analysis["links"]
        assert "/img.jpg" in analysis["images"]

    def test_create_debug_summary(self, scraper_utilities):
        """Test debug summary creation and file writing."""
        html = "<html>debug</html>"
        url = "http://debug.com"

        with patch("builtins.open", mock_open()) as mock_file, patch("os.makedirs"):
            summary = scraper_utilities.create_debug_summary(url, html)

            assert summary["url"] == url
            assert summary["html_length"] > 0
            mock_file.assert_called()

    def test_get_scraping_report(self, scraper_utilities):
        """Test scraping report statistics calculation."""
        stats = {
            "requests_made": 10,
            "successful_requests": 8,
            "failed_requests": 2,
            "data_items_extracted": 100,
            "processing_time": 5,
        }

        report = scraper_utilities.get_scraping_report(stats)

        # Success rate = 8/10 = 80%
        assert report["summary"]["success_rate"] == 80.0
        # Requests per second = 10/5 = 2.0
        assert report["performance"]["requests_per_second"] == 2.0
        # Items per second = 100/5 = 20.0
        assert report["performance"]["items_per_second"] == 20.0

    def test_get_scraping_report_empty(self, scraper_utilities):
        """Test report with zero stats."""
        stats = {}
        report = scraper_utilities.get_scraping_report(stats)

        assert report["summary"]["success_rate"] == 0
