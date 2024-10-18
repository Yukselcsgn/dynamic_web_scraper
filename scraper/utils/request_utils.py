import requests
from time import sleep
from random import randint

def send_request(url, method='GET', headers=None, params=None, timeout=10, retries=3):
    """
    HTTP isteği gönderir ve yanıtı döner.
    
    Args:
        url (str): İstek yapılacak URL.
        method (str): HTTP metodu (GET, POST vs.). Varsayılan: 'GET'.
        headers (dict): İstek başlıkları. Varsayılan: None.
        params (dict): GET veya POST parametreleri. Varsayılan: None.
        timeout (int): İstek için zaman aşımı süresi (saniye). Varsayılan: 10.
        retries (int): Başarısız istekler için tekrar deneme sayısı. Varsayılan: 3.
    
    Returns:
        requests.Response: HTTP yanıtı.
    
    Raises:
        requests.RequestException: İstek başarısız olursa hata fırlatır.
    """
    attempt = 0
    while attempt < retries:
        try:
            response = requests.request(method, url, headers=headers, params=params, timeout=timeout)
            response.raise_for_status()  # Hatalı statü kodları için hata fırlatır
            return response
        except requests.RequestException as e:
            print(f"İstek başarısız oldu (deneme {attempt + 1}/{retries}): {e}")
            attempt += 1
            sleep(randint(1, 5))  # İnsan benzeri bir bekleme süresi
    raise requests.RequestException(f"{retries} deneme sonrasında istek başarısız oldu.")

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
        if response.headers.get('Content-Type') == 'application/json':
            return response.json()
        return response.text
    except ValueError as e:
        raise ValueError(f"Yanıt işlenirken hata oluştu: {e}")
