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
        """
        Scraper nesnesini başlatır.
        
        Args:
            url (str): Kazınacak sitenin URL'si.
            config (dict): Kazıma işlemi için gerekli konfigürasyon ayarları.
            max_retries (int): Yeniden deneme sayısı.
            retry_delay (int): Hatalardan sonra bekleme süresi (saniye).
        """
        self.url = url
        self.config = config
        self.logger = None
        self.proxies = config.get('proxies', [])
        self.user_agents = config.get('user_agents', [])
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def get_headers(self):
        """
        Dinamik kullanıcı ajanı döndürür.
        
        Returns:
            dict: Kullanıcı ajanı ile birlikte HTTP başlıkları.
        """
        if not self.user_agents:
            raise UserAgentError("Kullanıcı ajanı listesi boş!")
        
        headers = {
            'User-Agent': choice(self.user_agents)
        }
        return headers
    
    def get_proxy(self):
        """
        Rastgele bir proxy döndürür.
        
        Returns:
            dict: Proxy ayarları.
        """
        if not self.proxies:
            raise ProxyError("Proxy listesi boş!")
        
        proxy = choice(self.proxies)
        return {
            'http': proxy,
            'https': proxy
        }

    def fetch_data(self):
        """
        Veriyi çeker ve işlemek için gerekli fonksiyonları tetikler.
        Hatalarda belirli bir sayıda yeniden deneme yapar.
        """
        for attempt in range(self.max_retries):
            try:
                headers = self.get_headers()
                proxies = self.get_proxy() if self.config.get('use_proxy') else None
                response = requests.get(self.url, headers=headers, proxies=proxies, timeout=10)
                response.raise_for_status()  # HTTP hatalarını yakala
                
                log_message(self.logger, 'INFO', f"Veri başarıyla çekildi: {self.url}")
                self.parse_response(response.text)
                return
            except (HTTPError, Timeout) as e:
                log_message(self.logger, 'WARNING', f"İstek başarısız oldu: {str(e)}. Deneme {attempt + 1}/{self.max_retries}")
                time.sleep(self.retry_delay * (attempt + 1))  # Exponential Backoff
            except ProxyError as pe:
                log_message(self.logger, 'ERROR', f"Proxy hatası: {str(pe)}")
            except UserAgentError as uae:
                log_message(self.logger, 'ERROR', f"Kullanıcı ajanı hatası: {str(uae)}")

        log_message(self.logger, 'ERROR', f"Veri çekme başarısız oldu: {self.url} için maksimum deneme sayısına ulaşıldı.")

    def parse_response(self, response):
        """
        Yanıtı işler ve gerekli bilgileri çıkarır.
        
        Args:
            response (str): HTML içeriği.
        """
        html_structure = parse_html(response)
        self.extract_product_info(html_structure)

    def extract_product_info(self, html):
        """
        HTML içeriğinden ürün bilgilerini çıkarır ve kaydeder.
        
        Args:
            html (BeautifulSoup): Analiz edilmiş HTML içeriği.
        """
        products = []
        
        # Örnek: Ürün adlarını ve fiyatlarını çıkar
        product_names = html.select(self.config['selectors']['product_name'])
        product_prices = html.select(self.config['selectors']['product_price'])
        
        for name, price in zip(product_names, product_prices):
            product_data = {
                'name': name.get_text().strip(),
                'price': price.get_text().strip()
            }
            products.append(product_data)
        
        # Veriyi kaydet
        save_data(products)
        log_message(self.logger, 'INFO', f"Toplam {len(products)} ürün çıkarıldı ve kaydedildi.")
