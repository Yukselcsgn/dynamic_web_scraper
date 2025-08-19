import requests
import logging
import os


def load_proxies_from_file(file_path):
    """
    Bir dosyadan proxy bilgilerini yükler.
    :param file_path: Proxy listesini içeren dosya yolu.
    :return: Proxy listesi (liste şeklinde).
    """
    try:
        if not os.path.exists(file_path):
            logging.warning(f"Proxy dosyası bulunamadı: {file_path}")
            return []

        with open(file_path, "r", encoding="utf-8") as file:
            proxies = [line.strip() for line in file if line.strip()]

        logging.info(f"{len(proxies)} proxy dosyadan yüklendi: {file_path}")
        return proxies
    except Exception as e:
        logging.error(f"Proxy dosyası yüklenirken hata: {e}")
        return []


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
