import random
import logging

class ProxyRotator:
    def __init__(self, proxies, retries=3):
        """
        Proxy rotator sınıfı, proxy'leri döndürür.
        :param proxies: Proxy listesi.
        :param retries: Proxy başarısız olursa kaç kez tekrar deneneceği.
        """
        self.proxies = proxies
        self.retries = retries
        self.current_proxy = None

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
