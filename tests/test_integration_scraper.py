import unittest
from unittest.mock import patch, MagicMock
from scraper.Scraper import Scraper


class TestScraperIntegration(unittest.TestCase):
    @patch("scraper.Scraper.requests.get")
    def test_fetch_data_success(self, mock_get):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<html><span class="product-name">Test Product</span><span class="price">$10</span></html>'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        config = {"user_agent": "test-agent", "proxy": None, "use_proxy": False}
        scraper = Scraper("http://example.com", config)
        data = scraper.fetch_data()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Test Product")
        self.assertEqual(data[0]["price"], "$10")


if __name__ == "__main__":
    unittest.main()
