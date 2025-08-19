import sys
import os

# Add the project root to the path for absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.config import load_config
from scraper.Scraper import Scraper
from scraper.logging_manager.logging_manager import setup_logging, log_message
from scraper.proxy_manager.proxy_rotator import ProxyRotator
from scraper.user_agent_manager.user_agent_manager import UserAgentManager


def main():
    # Loglama ayarlarını yapılandır
    log_file = "logs/scraper.log"
    setup_logging(log_file)
    log_message("INFO", f"Logging initialized. Log file: {log_file}")

    # Kullanıcıdan URL alma
    url, output_file = get_user_input()

    # Konfigürasyon ayarlarını yükleme
    config = load_config()

    # UserAgentManager örneği oluştur ve kullanıcı ajanı seç
    user_agent_manager = UserAgentManager(user_agents=config.get("user_agents", []))
    user_agent = user_agent_manager.get_user_agent()  # Rastgele kullanıcı ajanı seç

    # Proxy rotatör oluştur ve proxy seç
    proxy_rotator = ProxyRotator(proxies=config.get("proxies", []))
    proxy = proxy_rotator.rotate_proxy()  # Rastgele proxy seç

    # Kullanıcı ajanı ve proxy'yi konfigürasyona ekle
    config["user_agent"] = user_agent
    config["proxy"] = proxy

    # Kazıyıcıyı başlatma
    try:
        scraper = Scraper(url, config)
        product_data = scraper.fetch_data()
        print("MAIN Try ilk")
        # Eğer veri varsa kaydet
        if product_data:
            scraper.save_data(product_data, output_file)
            log_message(
                "INFO",
                f"Scraping completed successfully for URL: {url}. Total products: {len(product_data)}. Output file: {output_file}",
            )
        else:
            log_message("WARNING", f"No products found for URL: {url}.")

    except Exception as e:
        log_message(
            "ERROR", f"An error occurred during scraping for URL: {url}. Error: {e}"
        )
        sys.exit(1)


def get_user_input():
    """Kullanıcıdan URL ve çıktı dosyası için girişleri almak."""
    url = input("Kazımak istediğiniz URL'yi girin: ")
    validate_url(url)

    output_file = input(
        "Veriyi kaydetmek için çıktı dosyasının yolunu girin (varsayılan: data/all_listings.csv): "
    )
    if not output_file:
        output_file = "data/all_listings.csv"

    return url, output_file


def validate_url(url):
    """Verilen URL'nin geçerli bir formatta olup olmadığını kontrol eder."""
    if not url.startswith(("http://", "https://")):
        log_message(
            "ERROR",
            f"Invalid URL: {url}. URL must start with 'http://' or 'https://'.",
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
