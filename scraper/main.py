import argparse
import logging
import sys
import os
from config import load_config
from scraper import Scraper
from logging_manager.logging_manager import setup_logging

def main():
    # Loglama ayarlarını yapılandır
    log_file = "logs/scraper.log"
    setup_logging(log_file)
    
    # Kullanıcıdan URL ve diğer girişleri alma
    url, output_file = get_user_input()
    
    # Konfigürasyon ayarlarını yükleme
    config = load_config()
    
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
    """Kullanıcıdan URL ve diğer girişleri almak için."""
    parser = argparse.ArgumentParser(description='E-ticaret sitesi kazıyıcı')
    parser.add_argument('url', type=str, help='Kazımak için hedef URL')
    
    # Opsiyonel argümanlar ekleyin
    parser.add_argument('--output', type=str, default='data/all_listings.csv', 
                        help='Çıktı dosyasının yolu (varsayılan: data/all_listings.csv)')
    
    # Kullanıcı ajanı ve proxy ayarları için opsiyonel argümanlar ekleme
    parser.add_argument('--user-agent', type=str, help='Kullanıcı ajanı belirleme')
    parser.add_argument('--proxy', type=str, help='Proxy adresini belirleme')
    
    args = parser.parse_args()
    
    # URL ve çıktı dosyasını döndür
    return args.url, args.output

def validate_url(url):
    """Verilen URL'nin geçerli bir formatta olup olmadığını kontrol eder."""
    if not url.startswith(('http://', 'https://')):
        logging.error("Geçersiz URL: %s. URL 'http://' veya 'https://' ile başlamalı.", url)
        sys.exit(1)

if __name__ == '__main__':
    main()
