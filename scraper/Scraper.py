import requests
from random import choice
import time
from data_parsers.html_parser import parse_html
from data_parsers.data_parser import save_data
from logging_manager.logging_manager import log_message
from exceptions.scraper_exceptions import ProxyError, UserAgentError
from requests.exceptions import HTTPError, Timeout


class Scraper:
    def __init__(self, url, config, max_retries=3, retry_delay=2):
        self.url = url
        self.config = config
        self.logger = None  # logger tanımlandı ama kullanılmadı
        self.proxies = config.get('proxy', [])
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def get_headers(self):
        try:
            user_agent = self.config.get('user_agent')  # Kullanıcı ajanı doğrudan config'ten al
            headers = {
                'User-Agent': user_agent
            }
            return headers
        except UserAgentError as e:
            log_message(self.logger, 'ERROR', f"Kullanıcı ajanı hatası: {str(e)}")
            raise

    def get_proxy(self):
        if not self.proxies:
            raise ProxyError("Proxy listesi boş!")

        proxy = choice(self.proxies)
        return {
            'http': f'http://{proxy}',
            'https': f'https://{proxy}'
        }

    def fetch_data(self):
        for attempt in range(self.max_retries):
            try:
                headers = self.get_headers()
                proxies = self.get_proxy() if self.config.get('use_proxy') else None
                response = requests.get(self.url, headers=headers, proxies=proxies, timeout=10)
                response.raise_for_status()  # HTTP hatalarını yakala

                log_message(self.logger, 'INFO', f"Veri başarıyla çekildi: {self.url}")
                return self.parse_response(response.text)  # Veriyi döndür
            except (HTTPError, Timeout) as e:
                log_message(self.logger, 'WARNING',
                            f"İstek başarısız oldu: {str(e)}. Deneme {attempt + 1}/{self.max_retries}")
                time.sleep(self.retry_delay * (attempt + 1))  # Exponential Backoff
            except ProxyError as pe:
                log_message(self.logger, 'ERROR', f"Proxy hatası: {str(pe)}")
            except UserAgentError as uae:
                log_message(self.logger, 'ERROR', f"Kullanıcı ajanı hatası: {str(uae)}")

        log_message(self.logger, 'ERROR',
                    f"Veri çekme başarısız oldu: {self.url} için maksimum deneme sayısına ulaşıldı.")

    def parse_response(self, response):
        html_structure = parse_html(response)
        return self.extract_product_info(html_structure)

    def extract_product_info(self, html):
        products = []
        product_names = html.select(self.config['selectors']['product_name'])
        product_prices = html.select(self.config['selectors']['product_price'])

        for name, price in zip(product_names, product_prices):
            product_data = {
                'name': name.get_text().strip(),
                'price': price.get_text().strip()
            }
            products.append(product_data)

        save_data(products)
        log_message(self.logger, 'INFO', f"Toplam {len(products)} ürün çıkarıldı ve kaydedildi.")
        return products  # Dönüş değeri eklendi
