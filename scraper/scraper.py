import time
import random
import logging
import pandas as pd
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.firefox import GeckoDriverManager
from scraper.utils.proxy_utils import rotate_proxy
from scraper.utils.user_agent_utils import get_random_user_agent
from scraper.site_detection.site_detector import SiteDetector
from scraper.data_parsers.data_parser import DataParser

class DynamicECommerceScraper:
    def __init__(self, url, headless=False, proxies=None):
        self.url = url
        self.data = []
        self.headless = headless
        self.proxies = proxies or []
        self.driver = None
        self.retry_count = 0
        self.proxy = None
        
        self.setup_driver()

    def setup_driver(self):
        # Firefox ayarları
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        if self.headless:
            options.add_argument("--headless")
            options.add_argument("--window-size=1920,1080")

        # Rastgele User-Agent ayarı
        ua = get_random_user_agent()
        options.add_argument(f"user-agent={ua}")

        # Proxy ayarlama (varsa)
        if self.proxies:
            self.proxy = rotate_proxy(self.proxies)
            options.add_argument(f'--proxy-server={self.proxy}')

        # WebDriver başlatma
        try:
            service = Service(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=options)
            logging.info(f"Firefox başlatıldı. Proxy: {self.proxy or 'None'}")
        except Exception as e:
            logging.error(f"Driver başlatılamadı: {e}")
            raise e

    def fetch_data(self):
        # Scrape işlemi başlatılıyor
        try:
            self.driver.get(self.url)
            logging.info(f"URL açıldı: {self.url}")

            # CAPTCHA kontrolü
            if "captcha" in self.driver.page_source.lower():
                logging.warning("CAPTCHA tespit edildi!")
                self.change_proxy_and_retry()
                return False

            # Site yapısını dinamik olarak algıla
            detector = SiteDetector(self.driver)
            site_structure = detector.detect()

            # Sayfa yüklendi, veriyi parse et
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, site_structure['listing']))
            )

            # Veriyi işle
            parser = DataParser(self.driver, site_structure)
            parser.parse_listings()
            self.data = parser.get_data()

            # Kaydet
            self.save_data()

            return True
        except TimeoutException as e:
            logging.error(f"Sayfa yükleme süresi doldu: {e}")
            self.change_proxy_and_retry()
            return False
        except Exception as e:
            logging.error(f"Veri çekme hatası: {e}")
            self.change_proxy_and_retry()
            return False

    def change_proxy_and_retry(self):
        if self.retry_count < 3:
            logging.info(f"Proxy değiştirilip tekrar deneniyor. {self.retry_count + 1}. deneme.")
            self.retry_count += 1
            if self.proxies:
                self.proxy = rotate_proxy(self.proxies)
                logging.info(f"Yeni proxy ayarlandı: {self.proxy}")
                self.stop()
                self.setup_driver()
                self.fetch_data()
            else:
                logging.error("Proxy listesi boş.")
        else:
            logging.error("Maksimum deneme sayısına ulaşıldı.")
            self.stop()

    def save_data(self):
        if self.data:
            df = pd.DataFrame(self.data)
            df.to_csv('data/all_listings.csv', index=False)
            logging.info("Veriler kaydedildi: data/all_listings.csv")
        else:
            logging.warning("Kaydedilecek veri bulunamadı.")

    def stop(self):
        if self.driver:
            self.driver.quit()
            logging.info("Driver kapatıldı.")

    def close_driver(self):
        if self.driver:
            self.driver.quit()
            logging.info("Driver kapatıldı.")
