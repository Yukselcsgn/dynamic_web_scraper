import random
import logging

def rotate_proxy(proxies):
    """Proxy listesinden rastgele bir proxy seç."""
    if proxies:
        proxy = random.choice(proxies)
        logging.info(f"Proxy seçildi: {proxy}")
        return proxy
    else:
        logging.error("Proxy listesi boş.")
        return None

def validate_proxy(proxy):
    """Proxy'nin geçerli olup olmadığını kontrol et."""
    # Örnek olarak basit bir doğrulama (kendi proxy doğrulama servisinizi kullanabilirsiniz)
    try:
        response = requests.get("http://www.google.com", proxies={"http": proxy, "https": proxy}, timeout=5)
        if response.status_code == 200:
            logging.info(f"Proxy geçerli: {proxy}")
            return True
        else:
            logging.warning(f"Proxy geçersiz: {proxy}")
            return False
    except Exception as e:
        logging.error(f"Proxy doğrulama hatası: {e}")
        return False
