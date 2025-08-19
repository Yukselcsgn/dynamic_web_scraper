import logging
from .proxy_loader import load_proxies_from_file, load_proxies_from_api
from .proxy_validator import test_proxies


class ProxyManager:
    def __init__(self, source="file", file_path=None, api_url=None):
        """
        ProxyManager sınıfı, proxy havuzunu yönetir.
        :param source: Proxy yükleme kaynağı ('file' veya 'api').
        :param file_path: Dosyadan proxy yüklemek için dosya yolu.
        :param api_url: API'den proxy yüklemek için URL.
        """
        self.proxies = []
        self.source = source
        self.file_path = file_path
        self.api_url = api_url
        self.load_proxies()

        logging.basicConfig(filename="logs/scraper.log", level=logging.INFO)
        logging.info(f"ProxyManager başlatıldı: Kaynak - {self.source}")

    def load_proxies(self):
        """
        Proxy'leri belirlenen kaynaktan yükler (dosya veya API).
        """
        try:
            if self.source == "file" and self.file_path:
                self.proxies = load_proxies_from_file(self.file_path)
            elif self.source == "api" and self.api_url:
                self.proxies = load_proxies_from_api(self.api_url)
            else:
                raise ValueError("Geçersiz proxy kaynağı.")

            if not self.proxies:
                raise ValueError("Yüklenen proxy listesi boş!")

            logging.info(f"{len(self.proxies)} proxy başarıyla yüklendi.")
            # Yüklenen proxy'lerin geçerliliğini kontrol edelim.
            self.proxies = test_proxies(self.proxies)

        except Exception as e:
            logging.error(f"Proxy'ler yüklenirken hata: {e}")
            raise

    def manage_proxies(self):
        """
        Proxy havuzunu yönetir ve geçersiz olanları çıkarır.
        """
        logging.info("Proxy havuzu yönetimi başlatıldı.")
        try:
            self.proxies = test_proxies(self.proxies)
            logging.info(f"{len(self.proxies)} geçerli proxy mevcut.")
        except Exception as e:
            logging.error(f"Proxy yönetimi sırasında hata: {e}")

    def remove_invalid_proxies(self):
        """
        Geçersiz proxy'leri havuzdan çıkarır.
        """
        logging.info("Geçersiz proxy'ler çıkarılıyor.")
        try:
            valid_proxies = test_proxies(self.proxies)
            invalid_count = len(self.proxies) - len(valid_proxies)
            self.proxies = valid_proxies
            logging.info(
                f"{invalid_count} geçersiz proxy çıkarıldı. Kalan geçerli proxy sayısı: {len(self.proxies)}"
            )
        except Exception as e:
            logging.error(f"Geçersiz proxy'ler çıkarılırken hata: {e}")
            raise
