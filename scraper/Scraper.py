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
        Scraper sınıfı, belirli bir URL'den veri çekmek ve işlemek için kullanılır.

        Args:
            url (str): Veri çekilecek URL.
            config (dict): Kullanıcı ajanları, proxyler ve seçiciler gibi yapılandırmalar.
            max_retries (int): Maksimum deneme sayısı. Varsayılan: 3.
            retry_delay (int): Her deneme arasındaki bekleme süresi (saniye). Varsayılan: 2.
        """
        self.url = url
        self.config = config
        self.proxies = config.get('proxy', [])
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def get_headers(self):
        """
        Kullanıcı ajanını config'ten alarak HTTP başlıklarını oluşturur.

        Returns:
            dict: HTTP başlıkları.
        """
        try:
            user_agent = choice(self.config.get('user_agents', []))
            if not user_agent:
                raise UserAgentError("Kullanıcı ajanı bulunamadı.")
            return {'User-Agent': user_agent}
        except UserAgentError as e:
            log_message('ERROR', f"Kullanıcı ajanı hatası: {str(e)}")
            raise

    def get_proxy(self):
        """
        Proxy listesinden rastgele bir proxy seçer.

        Returns:
            dict: HTTP ve HTTPS proxy adresleri.

        Raises:
            ProxyError: Eğer proxy listesi boşsa.
        """
        if not self.proxies:
            raise ProxyError("Proxy listesi boş!")
        proxy = choice(self.proxies)
        return {'http': f'http://{proxy}', 'https': f'https://{proxy}'}

    def fetch_data(self):
        """
        URL'den veri çeker ve yanıtı işler.

        Returns:
            list: Çıkarılan ürün bilgileri.

        Raises:
            Exception: Veri çekme işlemi başarısız olursa hata fırlatır.
        """
        for attempt in range(self.max_retries):
            try:
                headers = self.get_headers()
                proxies = self.get_proxy() if self.config.get('use_proxy', False) else None
                response = requests.get(self.url, headers=headers, proxies=proxies, timeout=10)
                response.raise_for_status()

                log_message('INFO', f"Veri başarıyla çekildi: {self.url}")
                return self.parse_response(response.text)
            except (HTTPError, Timeout) as e:
                log_message('WARNING', f"İstek başarısız oldu: {str(e)}. Deneme {attempt + 1}/{self.max_retries}")
                time.sleep(self.retry_delay * (attempt + 1))  # Exponential Backoff
            except ProxyError as pe:
                log_message('ERROR', f"Proxy hatası: {str(pe)}")
            except UserAgentError as uae:
                log_message('ERROR', f"Kullanıcı ajanı hatası: {str(uae)}")

        log_message('ERROR', f"Veri çekme başarısız oldu: {self.url} için maksimum deneme sayısına ulaşıldı.")
        raise Exception("Veri çekme işlemi başarısız oldu.")

    def parse_response(self, response):
        """
        HTTP yanıtını işler ve ürün bilgilerini çıkarır.

        Args:
            response (str): HTTP yanıtı (HTML metni).

        Returns:
            list: Çıkarılan ürün bilgileri.
        """
        html_structure = parse_html(response)
        return self.extract_product_info(html_structure)

    def extract_product_info(self, html):
        """
        HTML yapısından ürün bilgilerini çıkarır.

        Args:
            html (BeautifulSoup): İşlenmiş HTML yapısı.

        Returns:
            list: Ürün bilgileri.
        """
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
        log_message('INFO', f"Toplam {len(products)} ürün çıkarıldı ve kaydedildi.")
        return products
