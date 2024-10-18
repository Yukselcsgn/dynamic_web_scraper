import requests
from scraper.utils.request_utils import get_random_user_agent, get_proxies
from scraper.utils.parse_utils import parse_html

class Scraper:
    def __init__(self, settings):
        self.settings = settings
        self.proxies = get_proxies(self.settings.get("proxies"))
        self.user_agents = get_random_user_agent(self.settings.get("user_agents"))

    def run(self):
        for site in self.settings["target_sites"]:
            print(f"Scraping site: {site['name']}")
            html_content = self.fetch_page(site["url"])
            
            if html_content:
                parsed_data = parse_html(html_content, site["selectors"])
                self.save_data(parsed_data)
            else:
                print(f"Failed to fetch page for {site['name']}")

    def fetch_page(self, url):
        """Belirtilen URL'yi proxy ve user agent kullanarak getirir."""
        headers = {
            "User-Agent": self.user_agents
        }
        proxies = self.proxies

        try:
            response = requests.get(url, headers=headers, proxies=proxies, timeout=self.settings["request_timeout"])
            response.raise_for_status()  # HTTP hata varsa istisna fırlat
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the URL {url}: {e}")
            return None

    def save_data(self, data):
        """Elde edilen verileri CSV formatında kaydeder."""
        with open("data/all_listings.csv", "a") as f:
            for entry in data:
                f.write(f"{entry['product_name']},{entry['price']},{entry['availability']}\n")
        print("Data saved successfully.")
