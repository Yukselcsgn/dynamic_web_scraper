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
import random


class ProxyRotator:
    def __init__(self, proxies=None, retries=3):
        """
        Proxy rotator sınıfı, proxy'leri döndürür.
        :param proxies: Proxy listesi.
        :param retries: Proxy başarısız olursa kaç kez tekrar deneneceği.
        """
        self.proxies = proxies or []
        self.retries = retries
        self.current_proxy = None

    def rotate_proxy(self):
        """
        Rastgele bir proxy seçer ve döner. Başarısız olursa, alternatif proxy dener.
        :return: Yeni proxy (string).
        """
        attempt = 0
        while attempt < self.retries:
            try:
                if not self.proxies:
                    raise ValueError("Proxy listesi boş!")
                self.current_proxy = random.choice(self.proxies)
                logging.info(f"Yeni proxy seçildi: {self.current_proxy}")
                return self.current_proxy
            except Exception as e:
                logging.error(f"Proxy seçimi başarısız oldu: {e}")
                attempt += 1
        raise RuntimeError("Proxy rotasyonunda tüm denemeler başarısız oldu.")
