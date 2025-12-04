# Copyright 2024 Yüksel Coşgun
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import random

import requests


def load_proxies(source="data/proxies.txt"):
    """
    Proxy listesini belirli bir kaynaktan yükler (dosya veya API).

    Args:
        source (str): Proxy'lerin bulunduğu kaynak (dosya yolu veya API URL).

    Returns:
        list: Yüklenen proxy'lerin listesi.

    Raises:
        FileNotFoundError: Dosya bulunamazsa hata fırlatır.
        ValueError: Proxy listesi boşsa hata fırlatır.
    """
    proxies = []

    try:
        # Eğer kaynak bir dosya ise
        if source.startswith("http"):
            response = requests.get(source)
            proxies = response.text.splitlines()
        else:
            with open(source, "r") as file:
                proxies = [line.strip() for line in file.readlines() if line.strip()]

        if not proxies:
            raise ValueError("Proxy listesi boş.")
        return proxies
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Proxy dosyası bulunamadı: {e}")
    except requests.RequestException as e:
        raise requests.RequestException(f"Proxy API'den veri alınamadı: {e}")


def get_random_proxy(proxies):
    """
    Rastgele bir proxy döner.

    Args:
        proxies (list): Proxy'lerin bulunduğu liste.

    Returns:
        str: Rastgele bir proxy.

    Raises:
        ValueError: Proxy listesi boşsa hata fırlatır.
    """
    if not proxies:
        raise ValueError("Proxy listesi boş.")
    return random.choice(proxies)


def validate_proxy(proxy):
    """
    Proxy'nin geçerliliğini kontrol eder.

    Args:
        proxy (str): Test edilecek proxy.

    Returns:
        bool: Proxy geçerli ise True, aksi halde False.
    """
    test_url = "https://httpbin.org/ip"  # Proxy'yi test etmek için kullanılacak URL
    proxies = {"http": proxy, "https": proxy}

    try:
        response = requests.get(test_url, proxies=proxies, timeout=5)
        if response.status_code == 200:
            print(f"Proxy geçerli: {proxy}")
            return True
    except requests.RequestException:
        print(f"Proxy geçersiz: {proxy}")
    return False
