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

import logging
from random import randint
from time import sleep

import requests


def send_request(
    url,
    method="GET",
    headers=None,
    params=None,
    timeout=10,
    retries=3,
    proxies=None,
    min_wait=1,
    max_wait=5,
):
    """
    HTTP isteği gönderir ve yanıtı döner.
    """
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    if headers is None:
        headers = default_headers.copy()
    else:
        # Merge default headers with custom headers, custom overrides default
        merged = default_headers.copy()
        merged.update(headers)
        headers = merged

    # Use default timeout if invalid
    if not isinstance(timeout, (int, float)) or timeout <= 0:
        timeout = 10

    attempt = 0
    while attempt < retries:
        try:
            logging.info(f"İstek gönderiliyor: {url} (deneme {attempt + 1}/{retries})")
            response = requests.request(
                method,
                url,
                headers=headers,
                params=params,
                timeout=timeout,
                proxies=proxies,
            )
            response.raise_for_status()  # Hatalı statü kodları için hata fırlatır
            logging.info(f"Başarılı yanıt: {response.status_code} {url}")
            return response
        except requests.RequestException as e:
            logging.warning(
                f"İstek başarısız oldu (deneme {attempt + 1}/{retries}): {e}"
            )
            attempt += 1
            if attempt < retries:
                # İnsan benzeri bir bekleme süresi
                sleep(randint(min_wait, max_wait))
    raise requests.RequestException(
        f"{retries} deneme sonrasında istek başarısız oldu: {url}"
    )


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
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            logging.info("Yanıt JSON formatında işleniyor.")
            return response.json()
        elif "text/html" in content_type:
            logging.info("Yanıt HTML metni olarak işleniyor.")
            return response.text
        else:
            logging.warning(f"Bilinmeyen içerik tipi: {content_type}")
            return response.content  # Binary içerik döner
    except ValueError as e:
        raise ValueError(f"Yanıt işlenirken hata oluştu: {e}")
