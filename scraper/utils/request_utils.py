import requests
from time import sleep
from random import randint
import logging

def send_request(
    url,
    method='GET',
    headers=None,
    params=None,
    timeout=10,
    retries=3,
    proxies=None,
    min_wait=1,
    max_wait=5
):
    """
    HTTP isteği gönderir ve yanıtı döner.

    Args:
        url (str): İstek yapılacak URL.
        method (str): HTTP metodu (GET, POST vs.). Varsayılan: 'GET'.
        headers (dict): İstek başlıkları. Varsayılan: None.
        params (dict): GET veya POST parametreleri. Varsayılan: None.
        timeout (int): İstek için zaman aşımı süresi (saniye). Varsayılan: 10.
        retries (int): Başarısız istekler için tekrar deneme sayısı. Varsayılan: 3.
        proxies (dict): Proxy bilgileri. Varsayılan: None.
        min_wait (int): Bekleme süresinin minimum değeri (saniye). Varsayılan: 1.
        max_wait (int): Bekleme süresinin maksimum değeri (saniye). Varsayılan: 5.

    Returns:
        requests.Response: HTTP yanıtı.

    Raises:
        requests.RequestException: İstek başarısız olursa hata fırlatır.
    """
    if headers is None:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

    attempt = 0
    while attempt < retries:
        try:
            logging.info(f"İstek gönderiliyor: {url} (deneme {attempt + 1}/{retries})")
            response = requests.request(
                method, url, headers=headers, params=params, timeout=timeout, proxies=proxies
            )
            response.raise_for_status()  # Hatalı statü kodları için hata fırlatır
            logging.info(f"Başarılı yanıt: {response.status_code} {url}")
            return response
        except requests.RequestException as e:
            logging.warning(f"İstek başarısız oldu (deneme {attempt + 1}/{retries}): {e}")
            attempt += 1
            sleep(randint(min_wait, max_wait))  # İnsan benzeri bir bekleme süresi
    raise requests.RequestException(f"{retries} deneme sonrasında istek başarısız oldu: {url}")


def handle_response(response):
    """
    HTTP yanıtını işler ve hata durumlarını yönetir.

    Args:
        response (requests.Response): HTTP yanıtı.

    Returns:
        dict or str: Yanıt JSON veya metin olarak döner.

    Raises:
        ValueError: Beklenen formatta olmayan yanıt için hata fırlatır.
    """
    try:
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            logging.info("Yanıt JSON formatında işleniyor.")
            return response.json()
        elif 'text/html' in content_type:
            logging.info("Yanıt HTML metni olarak işleniyor.")
            return response.text
        else:
            logging.warning(f"Bilinmeyen içerik tipi: {content_type}")
            return response.content  # Binary içerik döner
    except ValueError as e:
        raise ValueError(f"Yanıt işlenirken hata oluştu: {e}")
