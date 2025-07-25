import unittest
from unittest.mock import patch, Mock, MagicMock
import requests
import json
import logging
import ssl
from http.client import HTTPException
import sys
import os

# Projenin kök dizinine giden yolu ekle
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Gerekli importlar
from scraper.utils.request_utils import send_request, handle_response
from scraper.logging_manager.logging_manager import setup_logging,log_message


class TestHTTPRequestUtilityAdvanced(unittest.TestCase):
    def setUp(self):
        # Detaylı log kayıtları için log seviyesini ayarla
        logging.basicConfig(level=logging.DEBUG)
        self.test_url = 'https://example.com'

    def tearDown(self):
        # Her test sonrası log seviyesini sıfırla
        logging.getLogger().setLevel(logging.CRITICAL)

    def test_send_request_different_methods(self):
        """HTTP metodlarının (GET, POST, PUT, DELETE vb.) test edilmesi"""
        test_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']

        for method in test_methods:
            with self.subTest(method=method), \
                    patch('requests.request') as mock_request:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.raise_for_status = Mock()
                mock_request.return_value = mock_response

                response = send_request(self.test_url, method=method)

                mock_request.assert_called_once_with(
                    method,
                    self.test_url,
                    headers=unittest.mock.ANY,
                    params=None,
                    timeout=10,
                    proxies=None
                )
                self.assertEqual(response, mock_response)

    def test_send_request_timeout_scenarios(self):
        """Farklı zaman aşımı senaryolarının test edilmesi"""
        timeout_tests = [
            {'timeout': 5, 'expected': 5},
            {'timeout': 0, 'expected': 10},  # Varsayılan
            {'timeout': -1, 'expected': 10},  # Geçersiz değer
            {'timeout': 30, 'expected': 30}
        ]

        for test_case in timeout_tests:
            with self.subTest(timeout=test_case['timeout']), \
                    patch('requests.request') as mock_request:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.raise_for_status = Mock()
                mock_request.return_value = mock_response

                send_request(
                    self.test_url,
                    timeout=test_case['timeout']
                )

                call_args = mock_request.call_args[1]
                expected_timeout = test_case['expected']
                self.assertEqual(call_args['timeout'], expected_timeout)

    def test_advanced_retry_scenarios(self):
        """Gelişmiş yeniden deneme senaryoları"""
        error_scenarios = [
            requests.ConnectionError,
            requests.Timeout,
            requests.HTTPError
        ]

        for error_type in error_scenarios:
            with self.subTest(error_type=error_type.__name__), \
                    patch('requests.request') as mock_request, \
                    patch('time.sleep', return_value=None):
                # Her hata türü için farklı senaryolar
                mock_request.side_effect = [
                    error_type("First attempt failed"),
                    error_type("Second attempt failed"),
                    error_type("Third attempt failed")
                ]

                with self.assertRaises(requests.RequestException):
                    send_request(self.test_url, retries=3)

    def test_proxy_support(self):
        """Proxy desteğinin test edilmesi"""
        proxy_configs = [
            {'http': 'http://proxy1.example.com:8080'},
            {'https': 'https://proxy2.example.com:443'},
            None
        ]

        for proxy in proxy_configs:
            with self.subTest(proxy=proxy), \
                    patch('requests.request') as mock_request:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.raise_for_status = Mock()
                mock_request.return_value = mock_response

                send_request(self.test_url, proxies=proxy)

                call_args = mock_request.call_args[1]
                self.assertEqual(call_args['proxies'], proxy)

    def test_handle_response_advanced_content_types(self):
        """Gelişmiş içerik tipi işleme testleri"""
        content_type_tests = [
            {
                'content_type': 'application/json; charset=utf-8',
                'content': '{"key": "value"}',
                'expected_type': dict
            },
            {
                'content_type': 'text/plain; charset=utf-8',
                'content': 'Plain text response',
                'expected_type': str
            },
            {
                'content_type': 'application/xml',
                'content': b'<xml>Test</xml>',
                'expected_type': bytes
            }
        ]

        for test_case in content_type_tests:
            with self.subTest(content_type=test_case['content_type']):
                mock_response = MagicMock()
                mock_response.headers = {'Content-Type': test_case['content_type']}

                if test_case['content_type'].startswith('application/json'):
                    mock_response.json.return_value = json.loads(test_case['content'])
                    mock_response.text = test_case['content']
                    result = handle_response(mock_response)
                    self.assertIsInstance(result, test_case['expected_type'])
                elif test_case['content_type'].startswith('text/'):
                    mock_response.text = test_case['content']
                    result = handle_response(mock_response)
                    self.assertIsInstance(result, test_case['expected_type'])
                else:
                    mock_response.content = test_case['content']
                    result = handle_response(mock_response)
                    self.assertIsInstance(result, test_case['expected_type'])

    def test_request_headers_comprehensive(self):
        """Başlık (header) konfigürasyonunun detaylı testi"""
        header_tests = [
            None,  # Varsayılan başlıklar
            {'X-Custom-Header': 'Test'},  # Tek özel başlık
            {
                'X-Custom-Header': 'Test',
                'Authorization': 'Bearer token123'  # Çoklu başlık
            }
        ]

        for headers in header_tests:
            with self.subTest(headers=headers), \
                    patch('requests.request') as mock_request:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.raise_for_status = Mock()
                mock_request.return_value = mock_response

                send_request(self.test_url, headers=headers)

                call_args = mock_request.call_args[1]['headers']

                # Varsayılan başlıkların varlığını kontrol et
                self.assertIn('User-Agent', call_args)
                self.assertIn('Accept-Language', call_args)
                if headers:
                    for k, v in headers.items():
                        self.assertIn(k, call_args)
                        self.assertEqual(call_args[k], v)

    def test_wait_time_randomness(self):
        """Bekleme sürelerinin rastgeleliğinin test edilmesi"""
        with patch('time.sleep') as mock_sleep, \
                patch('scraper.utils.request_utils.randint') as mock_randint, \
                patch('requests.request') as mock_request:
            # İsteklerin başarısız olması için hazırla
            mock_request.side_effect = requests.ConnectionError("Test error")
            mock_randint.return_value = 3  # Sabit bir değer

            with self.assertRaises(requests.RequestException):
                send_request(self.test_url, retries=3, min_wait=1, max_wait=5)

            # Rastgele bekleme süresinin çağrıldığını doğrula
            self.assertEqual(mock_randint.call_count, 2)  # retries-1 kez çağrılır


if __name__ == '__main__':
    unittest.main()