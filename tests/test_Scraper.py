import unittest
from unittest.mock import patch, MagicMock, mock_open
import requests
from bs4 import BeautifulSoup
import os
import sys

# Projenin kök dizinine giden yolu ekle
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from scraper.Scraper import Scraper
from scraper.exceptions.scraper_exceptions import ProxyError, UserAgentError
from scraper.logging_manager.logging_manager import setup_logging,log_message


class TestScraper(unittest.TestCase):
    def setUp(self):
        """Her test öncesi hazırlık"""
        self.config = {
            'user_agents': ['Mozilla/5.0 Test'],
            'user_agent': 'Mozilla/5.0 Test',
            'proxy': ['192.168.1.1:8080', '10.0.0.1:3128'],
            'use_proxy': True
        }
        self.test_url = 'https://example.com'

    def test_get_headers_success(self):
        """Kullanıcı ajanı başlığı alma testı"""
        scraper = Scraper(self.test_url, self.config)
        headers = scraper.get_headers()

        self.assertIn('User-Agent', headers)
        self.assertEqual(headers['User-Agent'], self.config['user_agent'])

    def test_get_headers_no_user_agent(self):
        """Kullanıcı ajanı olmadığında hata testi"""
        config_without_ua = {'user_agents': []}
        scraper = Scraper(self.test_url, config_without_ua)

        with self.assertRaises(UserAgentError):
            scraper.get_headers()

    def test_get_proxy_success(self):
        """Proxy seçme testı"""
        scraper = Scraper(self.test_url, self.config)
        proxy = scraper.get_proxy()

        self.assertIn('http', proxy)
        self.assertIn('https', proxy)
        self.assertIn(proxy['http'].split('//')[1], self.config['proxy'])

    def test_get_proxy_empty_list(self):
        """Proxy listesi boş olduğunda hata testi"""
        config_without_proxy = {'proxy': []}
        scraper = Scraper(self.test_url, config_without_proxy)

        with self.assertRaises(ProxyError):
            scraper.get_proxy()

    @patch('requests.get')
    @patch('scraper.Scraper.Scraper.get_headers')
    @patch('scraper.Scraper.Scraper.get_proxy')
    @patch('scraper.Scraper.Scraper.parse_response')
    def test_fetch_data_success(self, mock_parse, mock_get_proxy, mock_get_headers, mock_requests_get):
        """Veri çekme başarı senaryosu"""
        # Mock ayarları
        mock_get_headers.return_value = {'User-Agent': 'Test Agent'}
        mock_get_proxy.return_value = {'http': 'http://test-proxy:8080'}
        mock_response = MagicMock()
        mock_response.text = '<html><body>Test Data</body></html>'
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response
        mock_parse.return_value = [{'name': 'Test Product', 'price': '10.00'}]

        # Test
        scraper = Scraper(self.test_url, self.config)
        result = scraper.fetch_data()

        # Doğrulamalar
        mock_requests_get.assert_called_once_with(
            self.test_url,
            headers={'User-Agent': 'Test Agent'},
            proxies={'http': 'http://test-proxy:8080'},
            timeout=10
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'Test Product')

    @patch('requests.get')
    def test_fetch_data_max_retries(self, mock_requests_get):
        """Maksimum deneme sayısına ulaşma testi"""
        # Sürekli hata fırlatan mock
        mock_requests_get.side_effect = requests.exceptions.HTTPError("Test Error")

        scraper = Scraper(self.test_url, self.config, max_retries=3)

        with self.assertRaises(Exception):
            scraper.fetch_data()

    def test_parse_html(self):
        """HTML parsing testi"""
        html_content = '''
        <html>
            <body>
                <span class="product-name">Test Product</span>
                <span class="price">10.00</span>
            </body>
        </html>
        '''
        scraper = Scraper(self.test_url, self.config)
        parsed_html = scraper.parse_html(html_content)

        self.assertIsInstance(parsed_html, BeautifulSoup)
        product_name = parsed_html.find('span', {'class': 'product-name'})
        product_price = parsed_html.find('span', {'class': 'price'})

        self.assertEqual(product_name.text, 'Test Product')
        self.assertEqual(product_price.text, '10.00')

    def test_extract_product_info(self):
        """Ürün bilgisi çıkarma testi"""
        html_content = '''
        <html>
            <body>
                <span class="product-name">Product 1</span>
                <span class="price">15.00</span>
                <span class="product-name">Product 2</span>
                <span class="price">20.00</span>
            </body>
        </html>
        '''
        scraper = Scraper(self.test_url, self.config)
        parsed_html = scraper.parse_html(html_content)

        products = scraper.extract_product_info(parsed_html)

        # Doğrulamalar
        self.assertEqual(len(products), 2)
        self.assertEqual(products[0]['name'], 'Product 1')
        self.assertEqual(products[0]['price'], '15.00')
        self.assertEqual(products[1]['name'], 'Product 2')
        self.assertEqual(products[1]['price'], '20.00')

    @patch('scraper.Scraper.save_data')
    def test_save_data_calls_save_data_function(self, mock_save_data):
        """save_data fonksiyonunun çağrıldığını test et"""
        scraper = Scraper(self.test_url, self.config)
        data = [{'name': 'Product 1', 'price': '15.00'}]
        file_name = 'test_file'
        scraper.save_data(data, file_name)
        mock_save_data.assert_called_once_with(data, file_name, 'csv')


if __name__ == '__main__':
    unittest.main()