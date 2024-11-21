import requests
import logging
import json

def load_user_agents_from_file(file_path):
    """
    Dosyadan kullanıcı ajanlarını yükler.
    :param file_path: Kullanıcı ajanı listesini içeren dosya yolu.
    :return: Kullanıcı ajanı listesi (liste şeklinde).
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.loads(file.read())
        user_agents = data['user_agents']
        logging.info(f"{len(user_agents)} kullanıcı ajanı dosyadan yüklendi.")
        return user_agents
    except FileNotFoundError:
        logging.error(f"{file_path} bulunamadı.")
        return []
    except Exception as e:
        logging.error(f"Kullanıcı ajanları dosyasından yüklenirken hata: {e}")
        return []

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
