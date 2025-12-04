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
import os

# Scraper özel hata sınıfları için temel bir logger oluşturuyoruz
logger = logging.getLogger("ScraperExceptions")
logger.setLevel(logging.ERROR)

# Ensure the logs directory exists
os.makedirs("logs", exist_ok=True)
# Logları bir dosyaya kaydetme
file_handler = logging.FileHandler("logs/scraper_exceptions.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class ScraperException(Exception):
    """
    Genel bir scraper hatası. Proje kapsamında tüm scraper işlemleri sırasında oluşabilecek genel hataları temsil eder.
    Aynı zamanda loglama ve çözüm önerileri içerir.
    """

    def __init__(self, message=None, suggestion=None, *args):
        message = message or "Scraper işleminde bir hata oluştu."
        suggestion = (
            suggestion or "Lütfen log dosyasına göz atarak detaylı bilgi edinin."
        )
        super().__init__(message, *args)
        self.message = message
        self.suggestion = suggestion
        logger.error(f"{self.__class__.__name__}: {self.message}")

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message} | Çözüm Önerisi: {self.suggestion}"


class ProxyError(ScraperException):
    """
    Proxy hatalarını temsil eden özel bir hata sınıfı. Proxy bağlantıları sırasında oluşabilecek sorunları ele alır.
    """

    def __init__(self, proxy=None, message=None, suggestion=None, *args):
        message = message or "Proxy hatası oluştu."
        suggestion = (
            suggestion or "Proxy ayarlarını kontrol edin veya yeni bir proxy deneyin."
        )
        self.proxy = proxy
        super().__init__(message, suggestion, *args)
        logger.error(f"ProxyError: {self.message} | Proxy: {self.proxy}")

    def __str__(self):
        return f"ProxyError: {self.message} | Proxy: {self.proxy} | Çözüm Önerisi: {self.suggestion}"


class UserAgentError(ScraperException):
    """
    Kullanıcı ajanı ile ilgili hataları temsil eden özel bir hata sınıfı. Yanlış ya da geçersiz kullanıcı ajanı kullanımı durumlarında bu hata tetiklenir.
    """

    def __init__(self, user_agent=None, message=None, suggestion=None, *args):
        message = message or "Kullanıcı ajanı hatası oluştu."
        suggestion = (
            suggestion
            or "Geçerli bir kullanıcı ajanı kullanın veya listeyi güncelleyin."
        )
        self.user_agent = user_agent
        super().__init__(message, suggestion, *args)
        logger.error(
            f"UserAgentError: {self.message} | Kullanıcı Ajanı: {self.user_agent}"
        )

    def __str__(self):
        return f"UserAgentError: {self.message} | Kullanıcı Ajanı: {self.user_agent} | Çözüm Önerisi: {self.suggestion}"


class InvalidURLError(ScraperException):
    """
    Geçersiz URL hatasını temsil eder. İstenen web sitesine bağlanılamadığında veya URL yanlış olduğunda tetiklenir.
    """

    def __init__(self, url=None, message=None, suggestion=None, *args):
        message = message or "Geçersiz URL veya bağlantı hatası."
        suggestion = (
            suggestion
            or "URL'nin doğruluğunu kontrol edin veya doğru URL ile tekrar deneyin."
        )
        self.url = url
        super().__init__(message, suggestion, *args)
        logger.error(f"InvalidURLError: {self.message} | URL: {self.url}")

    def __str__(self):
        return f"InvalidURLError: {self.message} | URL: {self.url} | Çözüm Önerisi: {self.suggestion}"


class ParsingError(ScraperException):
    """
    Verinin çözümlenmesi veya ayrıştırılması sırasında oluşan hataları temsil eder. Bu hata, HTML veya JSON gibi formatlarda beklenen verinin alınamaması durumunda tetiklenir.
    """

    def __init__(self, element=None, message=None, suggestion=None, *args):
        message = message or "Veri ayrıştırma hatası."
        suggestion = (
            suggestion
            or "Veri yapısında bir sorun olabilir, doğru etiketleri ve formatları kontrol edin."
        )
        self.element = element
        super().__init__(message, suggestion, *args)
        logger.error(f"ParsingError: {self.message} | Hatalı Eleman: {self.element}")

    def __str__(self):
        return f"ParsingError: {self.message} | Hatalı Eleman: {self.element} | Çözüm Önerisi: {self.suggestion}"


class RateLimitExceededError(ScraperException):
    """
    İstek sınırının aşılması durumunda oluşan hata. API veya site tarafından belirlenen limitlerin ihlal edilmesi durumunda tetiklenir.
    """

    def __init__(self, limit=None, message=None, suggestion=None, *args):
        message = message or "İstek sınırı aşıldı."
        suggestion = (
            suggestion or "Bir süre bekleyip tekrar deneyin veya istek hızını düşürün."
        )
        self.limit = limit
        super().__init__(message, suggestion, *args)
        logger.error(f"RateLimitExceededError: {self.message} | Limit: {self.limit}")

    def __str__(self):
        return f"RateLimitExceededError: {self.message} | Limit: {self.limit} | Çözüm Önerisi: {self.suggestion}"


class AuthenticationError(ScraperException):
    """
    Kimlik doğrulama ile ilgili hataları temsil eder. Özel API anahtarları veya giriş bilgileri gibi doğrulama gerektiren işlemlerde hata oluştuğunda tetiklenir.
    """

    def __init__(self, credentials=None, message=None, suggestion=None, *args):
        message = message or "Kimlik doğrulama hatası."
        suggestion = (
            suggestion or "Kimlik bilgilerinizi veya API anahtarınızı kontrol edin."
        )
        self.credentials = credentials
        super().__init__(message, suggestion, *args)
        logger.error(
            f"AuthenticationError: {self.message} | Kimlik Bilgileri: {self.credentials}"
        )

    def __str__(self):
        return f"AuthenticationError: {self.message} | Kimlik Bilgileri: {self.credentials} | Çözüm Önerisi: {self.suggestion}"


class InvalidResponseError(ScraperException):
    """
    Sunucudan alınan geçersiz veya beklenmeyen yanıtları temsil eder. HTTP kodu dışında da yanlış formatlarda gelen verilerde tetiklenir.
    """

    def __init__(
        self, status_code=None, response_body=None, message=None, suggestion=None, *args
    ):
        message = message or "Geçersiz yanıt alındı."
        suggestion = (
            suggestion
            or "Sunucunun yanıtını kontrol edin, veya formatı doğru bir şekilde ele aldığınızdan emin olun."
        )
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message, suggestion, *args)
        logger.error(
            f"InvalidResponseError: {self.message} | Durum Kodu: {self.status_code} | Yanıt: {self.response_body}"
        )

    def __str__(self):
        return f"InvalidResponseError: {self.message} | Durum Kodu: {self.status_code} | Yanıt: {self.response_body} | Çözüm Önerisi: {self.suggestion}"


class TimeoutError(ScraperException):
    """
    İsteklerin zaman aşımına uğraması durumunda oluşan hata. Web sitesiyle veya API ile bağlantı kurarken zaman aşımı meydana geldiğinde tetiklenir.
    """

    def __init__(self, timeout_value=None, message=None, suggestion=None, *args):
        message = message or "İstek zaman aşımına uğradı."
        suggestion = (
            suggestion or "Bağlantı süresini artırın veya ağ bağlantınızı kontrol edin."
        )
        self.timeout_value = timeout_value
        super().__init__(message, suggestion, *args)
        logger.error(
            f"TimeoutError: {self.message} | Zaman Aşımı Değeri: {self.timeout_value}"
        )

    def __str__(self):
        return f"TimeoutError: {self.message} | Zaman Aşımı Değeri: {self.timeout_value} | Çözüm Önerisi: {self.suggestion}"
