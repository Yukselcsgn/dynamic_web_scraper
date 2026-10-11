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

import requests

from .proxy_formatter import mask_proxy

logger = logging.getLogger(__name__)


def validate_proxy(proxy, timeout=5):
    """
    Bir proxy'nin geçerli olup olmadığını kontrol eder.
    :param proxy: Kontrol edilecek proxy (string).
    :param timeout: Zaman aşımı süresi (saniye).
    :return: Geçerli (True) veya geçersiz (False).
    """
    try:
        proxies = {"http": proxy, "https": proxy}
        response = requests.get(
            "http://www.google.com", proxies=proxies, timeout=timeout
        )
        if response.status_code == 200:
            logger.info(f"Proxy geçerli: {mask_proxy(proxy)}")
            return True
        else:
            logger.info(f"Proxy geçersiz: {mask_proxy(proxy)}")
            return False
    except requests.RequestException:
        logger.info(f"Proxy geçersiz: {mask_proxy(proxy)}")
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

    logger.info(f"{len(valid_proxies)} geçerli proxy bulundu.")
    return valid_proxies
