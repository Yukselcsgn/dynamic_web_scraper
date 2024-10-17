import logging
from scraper.config import Config
from scraper.scraper import DynamicECommerceScraper

def main():
    # Logging ayarları
    logging.basicConfig(filename='logs/scraper.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Konfigürasyonu yükle
    config = Config()

    # Scraper'ı başlat
    scraper = DynamicECommerceScraper(
        url=config.URL,
        headless=config.HEADLESS,
        proxies=config.PROXIES
    )

    # Site yapısını algıla ve verileri topla
    if scraper.fetch_data():
        scraper.parse_listings()
    else:
        logging.error("Veri çekme başarısız oldu.")

    # Scraper'ı kapat
    scraper.close_driver()

if __name__ == "__main__":
    main()
