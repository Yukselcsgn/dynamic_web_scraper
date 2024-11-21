import random
import logging


class ProxyRotator:
    def __init__(self, proxies=None, retries=3, file_path=None):
        """
        Proxy rotator sınıfı, proxy'leri döndürür.
        :param proxies: Proxy listesi.
        :param retries: Proxy başarısız olursa kaç kez tekrar deneneceği.
        :param file_path: Proxy listesinin yükleneceği dosya yolu.
        """
        if proxies:
            self.proxies = proxies
        elif file_path:
            self.proxies = self.load_proxies_from_file(file_path)
        else:
            self.proxies = []

        self.retries = retries
        self.current_proxy = None

    def load_proxies_from_file(self, file_path):
        """
        Dosyadan proxy listesini yükler.
        :param file_path: Proxy listesinin yükleneceği dosya yolu.
        :return: Proxy listesi.
        """
        try:
            with open(file_path, 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
            logging.info(f"{len(proxies)} proxy dosyadan yüklendi.")
            return proxies
        except FileNotFoundError:
            logging.error(f"Proxy dosyası bulunamadı: {file_path}")
            return []
        except Exception as e:
            logging.error(f"Proxy dosyası yüklenirken hata oluştu: {e}")
            return []

    def rotate_proxy(self):
        """
        Rastgele bir proxy seçer ve döner. Başarısız olursa, alternatif proxy dener.
        :return: Yeni proxy (string).
        """
        attempt = 0
        while attempt < self.retries:
            try:
                if not self.proxies:
                    raise ValueError("Proxy listesi boş!")

                self.current_proxy = random.choice(self.proxies)
                logging.info(f"Yeni proxy seçildi: {self.current_proxy}")
                return self.current_proxy
            except Exception as e:
                logging.error(f"Proxy seçimi başarısız oldu: {e}")
                attempt += 1

        raise RuntimeError("Proxy rotasyonunda tüm denemeler başarısız oldu.")
