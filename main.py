import json
from scraper.scraper import DynamicECommerceScraper
from scraper.logging_config import setup_logging

def load_config():
    with open('config.json') as f:
        return json.load(f)

def main():
    setup_logging()
    config = load_config()
    urls = config.get("urls", [])
    proxies = config.get("proxies", [])
    
    for url in urls:
        scraper = DynamicECommerceScraper(url, headless=True, proxies=proxies)
        scraper.scrape()
        scraper.stop()

if __name__ == "__main__":
    main()
