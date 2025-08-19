import requests
import logging


def load_user_agents_from_api(api_url, timeout=10):
    """
    Bir API'den kullanıcı ajanlarını yükler.
    :param api_url: Kullanıcı ajanı listesini sağlayan API URL'si.
    :param timeout: API isteği için zaman aşımı süresi (saniye).
    :return: Kullanıcı ajanı listesi (liste şeklinde).
    """
    try:
        response = requests.get(api_url, timeout=timeout)
        response.raise_for_status()  # Hata kodu varsa raise eder
        user_agents = response.text.splitlines()
        logging.info(f"{len(user_agents)} kullanıcı ajanı API'den yüklendi.")
        return user_agents
    except requests.Timeout:
        logging.error("API isteği zaman aşımına uğradı.")
        return []
    except requests.RequestException as e:
        logging.error(f"API isteği sırasında hata: {e}")
        return []
