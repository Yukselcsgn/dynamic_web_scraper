import requests
import logging

def load_proxies_from_api(api_url, timeout=10):
    """
    Bir API'den proxy bilgilerini yükler.
    :param api_url: Proxy listesini sağlayan API URL'si.
    :param timeout: API isteği için zaman aşımı süresi (saniye).
    :return: Proxy listesi (liste şeklinde).
    """
    try:
        response = requests.get(api_url, timeout=timeout)
        response.raise_for_status()  # Hata kodu varsa raise eder
        proxies = response.text.splitlines()
        logging.info(f"{len(proxies)} proxy API'den yüklendi.")
        return proxies
    except requests.Timeout:
        logging.error("API isteği zaman aşımına uğradı.")
        return []
    except requests.RequestException as e:
        logging.error(f"API isteği sırasında hata: {e}")
        return []
