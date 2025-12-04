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
