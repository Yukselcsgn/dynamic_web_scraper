import sys
import logging
from config import load_config
from scraper.Scraper import Scraper
from logging_manager.logging_manager import setup_logging
from proxy_manager.proxy_rotator import ProxyRotator
from user_agent_manager.user_agent_manager import UserAgentManager


def main():
    # Loglama ayarlarını yapılandır
    log_file = "logs/scraper.log"
    setup_logging(log_file)

    # Kullanıcıdan URL alma
    url, output_file = get_user_input()

    # Konfigürasyon ayarlarını yükleme
    config = load_config()

    # UserAgentManager örneği oluştur ve kullanıcı ajanı seç
    user_agent_manager = UserAgentManager(
        source='file',
        file_path='D:\\Users\\Lenovo\\PycharmProjects\\dynamic_web_scraper\\config.json'
    )
    user_agent = user_agent_manager.get_user_agent()  # Rastgele kullanıcı ajanı seç

    # Proxy rotatör oluştur ve proxy seç
    proxy_rotator = ProxyRotator(
        file_path='D:\\Users\\Lenovo\\PycharmProjects\\dynamic_web_scraper\\config.json'
    )
    proxy = proxy_rotator.rotate_proxy()  # Rastgele proxy seç

    # Kullanıcı ajanı ve proxy'yi konfigürasyona ekle
    config['user_agent'] = user_agent
    config['proxy'] = proxy

    # Kazıyıcıyı başlatma
    try:
        scraper = Scraper(url, config)
        product_data = scraper.fetch_data()

        # Eğer veri varsa kaydet
        if product_data:
            scraper.save_data(product_data, output_file)
            logging.info("Kazıma işlemi başarıyla tamamlandı. Toplam ürün sayısı: %d", len(product_data))
        else:
            logging.warning("Kazıma işlemi sonucu ürün bulunamadı.")

    except Exception as e:
        logging.error("Kazıma işlemi sırasında bir hata oluştu: %s", e)
        sys.exit(1)


def get_user_input():
    """Kullanıcıdan URL ve çıktı dosyası için girişleri almak."""
    url = input("Kazımak istediğiniz URL'yi girin: ")
    validate_url(url)

    output_file = input("Veriyi kaydetmek için çıktı dosyasının yolunu girin (varsayılan: data/all_listings.csv): ")
    if not output_file:
        output_file = 'data/all_listings.csv'

    return url, output_file


def validate_url(url):
    """Verilen URL'nin geçerli bir formatta olup olmadığını kontrol eder."""
    if not url.startswith(('http://', 'https://')):
        logging.error("Geçersiz URL: %s. URL 'http://' veya 'https://' ile başlamalı.", url)
        sys.exit(1)


if __name__ == '__main__':
    main()
