import os

# URL'ler
SCRAPING_URLS = [
    "https://example.com/category/product1",
    "https://example.com/category/product2",
]

# Dosya yolları
USER_AGENT_FILE = os.path.join(os.getcwd(), 'data', 'user_agents.txt')
PROXY_FILE = os.path.join(os.getcwd(), 'data', 'proxies.txt')

# Proxy ve User Agent Ayarları
USE_PROXIES = True
USE_USER_AGENTS = True
ROTATE_PROXIES = True        # Proxy rotasyonu aktif mi?
VALIDATE_PROXIES = True      # Proxy doğrulama aktif mi?

# İstek ayarları
MAX_RETRIES = 5              # Yeniden deneme sayısı
TIMEOUT = 10                 # İstek zaman aşımı

# Bekleme süreleri
MIN_WAIT = 1
MAX_WAIT = 5
WAIT_FACTOR = 1.5

# Veritabanı ayarları
USE_DATABASE = True          # Verilerin veritabanına kaydedilmesi aktif mi?
DB_PATH = os.path.join(os.getcwd(), 'data', 'scraped_data.db')

# Siteye özel CSS seçiciler
SELECTORS = {
    'product_name': '.product-title',
    'price': '.price-tag',
    'availability': '.stock-status'
}
