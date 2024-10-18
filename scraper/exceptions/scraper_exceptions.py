import logging

# Scraper özel hata sınıfları için temel bir logger oluşturuyoruz
logger = logging.getLogger("ScraperExceptions")
logger.setLevel(logging.ERROR)

# Logları bir dosyaya kaydetme
file_handler = logging.FileHandler("logs/scraper_exceptions.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class ScraperException(Exception):
    """
    Genel bir scraper hatası. Proje kapsamında tüm scraper işlemleri sırasında oluşabilecek genel hataları temsil eder.
    Aynı zamanda loglama ve çözüm önerileri içerir.
    """
    def __init__(self, message="Scraper işleminde bir hata oluştu.", suggestion=None, *args):
        super().__init__(message, *args)
        self.message = message
        self.suggestion = suggestion or "Lütfen log dosyasına göz atarak detaylı bilgi edinin."
        logger.error(f"{self.__class__.__name__}: {self.message}")

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message} | Çözüm Önerisi: {self.suggestion}"

class ProxyError(ScraperException):
    """
    Proxy hatalarını temsil eden özel bir hata sınıfı. Proxy bağlantıları sırasında oluşabilecek sorunları ele alır.
    """
    def __init__(self, proxy, message="Proxy hatası oluştu.", suggestion=None, *args):
        self.proxy = proxy
        suggestion = suggestion or "Proxy ayarlarını kontrol edin veya yeni bir proxy deneyin."
        super().__init__(message, suggestion, *args)
        logger.error(f"ProxyError: {self.message} | Proxy: {self.proxy}")

    def __str__(self):
        return f"ProxyError: {self.message} | Proxy: {self.proxy} | Çözüm Önerisi: {self.suggestion}"

class UserAgentError(ScraperException):
    """
    Kullanıcı ajanı ile ilgili hataları temsil eden özel bir hata sınıfı. Yanlış ya da geçersiz kullanıcı ajanı kullanımı durumlarında bu hata tetiklenir.
    """
    def __init__(self, user_agent, message="Kullanıcı ajanı hatası oluştu.", suggestion=None, *args):
        self.user_agent = user_agent
        suggestion = suggestion or "Geçerli bir kullanıcı ajanı kullanın veya listeyi güncelleyin."
        super().__init__(message, suggestion, *args)
        logger.error(f"UserAgentError: {self.message} | Kullanıcı Ajanı: {self.user_agent}")

    def __str__(self):
        return f"UserAgentError: {self.message} | Kullanıcı Ajanı: {self.user_agent} | Çözüm Önerisi: {self.suggestion}"

class InvalidURLError(ScraperException):
    """
    Geçersiz URL hatasını temsil eder. İstenen web sitesine bağlanılamadığında veya URL yanlış olduğunda tetiklenir.
    """
    def __init__(self, url, message="Geçersiz URL veya bağlantı hatası.", suggestion=None, *args):
        self.url = url
        suggestion = suggestion or "URL'nin doğruluğunu kontrol edin veya doğru URL ile tekrar deneyin."
        super().__init__(message, suggestion, *args)
        logger.error(f"InvalidURLError: {self.message} | URL: {self.url}")

    def __str__(self):
        return f"InvalidURLError: {self.message} | URL: {self.url} | Çözüm Önerisi: {self.suggestion}"

class ParsingError(ScraperException):
    """
    Verinin çözümlenmesi veya ayrıştırılması sırasında oluşan hataları temsil eder. Bu hata, HTML veya JSON gibi formatlarda beklenen verinin alınamaması durumunda tetiklenir.
    """
    def __init__(self, element, message="Veri ayrıştırma hatası.", suggestion=None, *args):
        self.element = element
        suggestion = suggestion or "Veri yapısında bir sorun olabilir, doğru etiketleri ve formatları kontrol edin."
        super().__init__(message, suggestion, *args)
        logger.error(f"ParsingError: {self.message} | Hatalı Eleman: {self.element}")

    def __str__(self):
        return f"ParsingError: {self.message} | Hatalı Eleman: {self.element} | Çözüm Önerisi: {self.suggestion}"

class RateLimitExceededError(ScraperException):
    """
    İstek sınırının aşılması durumunda oluşan hata. API veya site tarafından belirlenen limitlerin ihlal edilmesi durumunda tetiklenir.
    """
    def __init__(self, limit, message="İstek sınırı aşıldı.", suggestion=None, *args):
        self.limit = limit
        suggestion = suggestion or "Bir süre bekleyip tekrar deneyin veya istek hızını düşürün."
        super().__init__(message, suggestion, *args)
        logger.error(f"RateLimitExceededError: {self.message} | Limit: {self.limit}")

    def __str__(self):
        return f"RateLimitExceededError: {self.message} | Limit: {self.limit} | Çözüm Önerisi: {self.suggestion}"

class AuthenticationError(ScraperException):
    """
    Kimlik doğrulama ile ilgili hataları temsil eder. Özel API anahtarları veya giriş bilgileri gibi doğrulama gerektiren işlemlerde hata oluştuğunda tetiklenir.
    """
    def __init__(self, credentials, message="Kimlik doğrulama hatası.", suggestion=None, *args):
        self.credentials = credentials
        suggestion = suggestion or "Kimlik bilgilerinizi veya API anahtarınızı kontrol edin."
        super().__init__(message, suggestion, *args)
        logger.error(f"AuthenticationError: {self.message} | Kimlik Bilgileri: {self.credentials}")

    def __str__(self):
        return f"AuthenticationError: {self.message} | Kimlik Bilgileri: {self.credentials} | Çözüm Önerisi: {self.suggestion}"

class InvalidResponseError(ScraperException):
    """
    Sunucudan alınan geçersiz veya beklenmeyen yanıtları temsil eder. HTTP kodu dışında da yanlış formatlarda gelen verilerde tetiklenir.
    """
    def __init__(self, status_code, response_body, message="Geçersiz yanıt alındı.", suggestion=None, *args):
        self.status_code = status_code
        self.response_body = response_body
        suggestion = suggestion or "Sunucunun yanıtını kontrol edin, veya formatı doğru bir şekilde ele aldığınızdan emin olun."
        super().__init__(message, suggestion, *args)
        logger.error(f"InvalidResponseError: {self.message} | Durum Kodu: {self.status_code} | Yanıt: {self.response_body}")

    def __str__(self):
        return f"InvalidResponseError: {self.message} | Durum Kodu: {self.status_code} | Yanıt: {self.response_body} | Çözüm Önerisi: {self.suggestion}"

class TimeoutError(ScraperException):
    """
    İsteklerin zaman aşımına uğraması durumunda oluşan hata. Web sitesiyle veya API ile bağlantı kurarken zaman aşımı meydana geldiğinde tetiklenir.
    """
    def __init__(self, timeout_value, message="İstek zaman aşımına uğradı.", suggestion=None, *args):
        self.timeout_value = timeout_value
        suggestion = suggestion or "Bağlantı süresini artırın veya ağ bağlantınızı kontrol edin."
        super().__init__(message, suggestion, *args)
        logger.error(f"TimeoutError: {self.message} | Zaman Aşımı Değeri: {self.timeout_value}")

    def __str__(self):
        return f"TimeoutError: {self.message} | Zaman Aşımı Değeri: {self.timeout_value} | Çözüm Önerisi: {self.suggestion}"
