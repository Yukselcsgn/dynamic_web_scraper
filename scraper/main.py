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

import os
import sys

print(">>> Python executable:", sys.executable)
print(">>> sys.path:", sys.path[:3])

# Add the project root to the path for absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.config import load_config
from scraper.core.scraper import Scraper
from scraper.logging_manager.logging_manager import log_message, setup_logging
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
        print("🚀 Starting enhanced scraping with advanced features...")

        # Fetch data with all advanced features enabled
        result = scraper.fetch_data(
            enable_smart_detection=True, enable_enrichment=True, enable_analysis=True
        )

        print("✅ Scraping completed with advanced analysis!")

        # Extract the main data for saving
        product_data = result.get("enriched_data", result.get("raw_data", []))

        # Eğer veri varsa kaydet
        if product_data:
            scraper.save_data(product_data, output_file)

            # Display summary of advanced features
            print("\n📊 Advanced Analysis Summary:")
            print(f"   • Raw data items: {len(result.get('raw_data', []))}")
            print(f"   • Enriched data items: {len(result.get('enriched_data', []))}")

            if result.get("plugin_results"):
                print(
                    f"   • Active plugins: {len(result['plugin_results'].get('active_plugins', []))}"
                )
                print(
                    f"   • Data validation: {len(result['plugin_results'].get('validation_results', []))}"
                )

            if result.get("distributed_results"):
                print(
                    f"   • Jobs processed: {result['distributed_results'].get('jobs_processed', 0)}"
                )
                print(
                    f"   • Successful jobs: {result['distributed_results'].get('successful_jobs', 0)}"
                )

            if result.get("price_analysis"):
                print(
                    f"   • Price outliers detected: {len(result['price_analysis'].outliers)}"
                )
                print(
                    f"   • Price recommendations: {len(result['price_analysis'].recommendations)}"
                )

            if result.get("comparison_analysis"):
                print(
                    f"   • Product matches found: {len(result['comparison_analysis'].get('product_matches', []))}"
                )
                print(
                    f"   • Price comparisons: {len(result['comparison_analysis'].get('price_comparisons', []))}"
                )
                print(
                    f"   • Deal analyses: {len(result['comparison_analysis'].get('deal_analyses', []))}"
                )

            if result.get("visualization_results"):
                print(f"   • Charts created: {len(result['visualization_results'])}")
                print(f"   • Visualizations saved to: data/visualizations/")

            if result.get("reporting_results"):
                print(
                    f"   • Alerts generated: {len(result['reporting_results'].get('alerts', []))}"
                )
                print(
                    f"   • Recommendations: {len(result['reporting_results'].get('recommendations', []))}"
                )

            print(f"\n💾 Data saved to: {output_file}")
            print("📁 Additional exports available in 'exports/' directory")
            print("📋 Reports available in 'reports/' directory")
            print("📊 Visualizations available in 'data/visualizations/' directory")
            print("🔌 Plugin results available in 'plugins/' directory")

            log_message(
                "INFO",
                f"Enhanced scraping completed successfully for URL: {url}. Total products: {len(product_data)}. Output file: {output_file}",
            )
        else:
            log_message("WARNING", f"No products found for URL: {url}.")
            # Create a summary report for debugging
            scraper._create_debug_summary(url)
            print(f"\n🔍 DEBUGGING INFO:")
            print(f"   • Check 'debug_html/' directory for saved HTML content")
            print(f"   • Check 'response.html' for the latest response")
            print(f"   • Look for '*_analysis.txt' files for content analysis")
            print(f"   • This will help identify why no products were extracted")

    except KeyboardInterrupt:
        log_message("WARNING", "Scraping interrupted by user")
        print("\n⚠️  Scraping interrupted by user (Ctrl+C)")
        print("🔄 You can run the scraper again when ready.")
        sys.exit(0)
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
