import requests
import logging

def validate_proxy(proxy, timeout=5):
    """
    Bir proxy'nin geçerli olup olmadığını kontrol eder.
    :param proxy: Kontrol edilecek proxy (string).
    :param timeout: Zaman aşımı süresi (saniye).
    :return: Geçerli (True) veya geçersiz (False).
    """
    try:
        proxies = {"http": proxy, "https": proxy}
        response = requests.get('http://www.google.com', proxies=proxies, timeout=timeout)
        if response.status_code == 200:
            logging.info(f"Proxy geçerli: {proxy}")
            return True
        else:
            logging.info(f"Proxy geçersiz: {proxy}")
            return False
    except requests.RequestException:
        logging.info(f"Proxy geçersiz: {proxy}")
        return False

def test_proxies(proxies, max_threads=10):
    """
    Bir dizi proxy'yi test eder ve geçerli olanları döner.
    :param proxies: Test edilecek proxy listesi.
    :param max_threads: Aynı anda kaç proxy'nin test edileceği (varsayılan 10).
    :return: Geçerli proxy listesi.
    """
    valid_proxies = []
    for proxy in proxies:
        if validate_proxy(proxy):
            valid_proxies.append(proxy)

    logging.info(f"{len(valid_proxies)} geçerli proxy bulundu.")
    return valid_proxies
