from scraper.scraper import Scraper
from scraper.config import SCRAPER_SETTINGS

def main():
    # Scraper ayarlarını yükle
    scraper_settings = SCRAPER_SETTINGS

    # Scraper'ı başlat
    scraper = Scraper(scraper_settings)
    
    try:
        scraper.run()
    except Exception as e:
        print(f"Error occurred during scraping: {e}")

if __name__ == "__main__":
    main()
