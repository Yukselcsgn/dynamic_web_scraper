import requests
from random import choice
import time
from bs4 import BeautifulSoup
from .logging_manager.logging_manager import log_message
from .exceptions.scraper_exceptions import ProxyError, UserAgentError
from requests.exceptions import HTTPError, Timeout

from .data_parsers import save_data

class Scraper:
    def __init__(self, url, config, max_retries=3, retry_delay=2):
        """
        Scraper class for fetching and processing data from a URL.

        Args:
            url (str): Target URL for data fetching.
            config (dict): Configuration for user agents, proxies, and selectors.
            max_retries (int): Maximum retry attempts. Default: 3.
            retry_delay (int): Delay between retries in seconds. Default: 2.
        """
        self.url = url
        self.config = config
        self.proxies = config.get('proxy', [])
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def get_headers(self):
        """
        Generate HTTP headers using a random user agent from the configuration.

        Returns:
            dict: HTTP headers.

        Raises:
            UserAgentError: If no user agents are available.
        """
        try:
            user_agent = self.config.get('user_agent')
            if not user_agent:
                raise UserAgentError(user_agent=None, message="No user agent available.", suggestion="Please check your config.json and ensure at least one user agent is provided.")
            return {'User-Agent': user_agent}
        except UserAgentError as e:
            log_message('ERROR', f"User agent error: {str(e)}")
            raise

    def get_proxy(self):
        """
        Select a random proxy from the configuration.

        Returns:
            dict: Proxy settings for HTTP and HTTPS.

        Raises:
            ProxyError: If no proxies are available.
        """
        if not self.proxies:
            raise ProxyError(proxy=None, message="Proxy list is empty!", suggestion="Please check your config.json and ensure at least one proxy is provided, or disable proxy usage.")
        proxy = choice(self.proxies)
        return {'http': f'http://{proxy}', 'https': f'https://{proxy}'}

    def fetch_data(self):
        """
        Fetch data from the URL and process the response.

        Returns:
            list: Extracted product information.

        Raises:
            Exception: If data fetching fails after maximum retries.
        """
        for attempt in range(self.max_retries):
            try:
                headers = self.get_headers()
                proxies = self.get_proxy() if self.config.get('use_proxy', False) else None
                response = requests.get(self.url, headers=headers, proxies=proxies, timeout=10)
                response.raise_for_status()

                log_message('INFO', f"Data successfully fetched from: {self.url}")
                return self.parse_response(response.text)
            except (HTTPError, Timeout) as e:
                log_message('WARNING', f"Request failed: {str(e)}. Attempt {attempt + 1}/{self.max_retries}")
                time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
            except ProxyError as pe:
                log_message('ERROR', f"Proxy error: {str(pe)}")
            except UserAgentError as uae:
                log_message('ERROR', f"User agent error: {str(uae)}")

        log_message('ERROR', f"Failed to fetch data: Maximum retries reached for {self.url}.")
        raise Exception("Data fetching failed.")

    def parse_response(self, response_text):
        """
        Process the HTTP response and extract product information.

        Args:
            response_text (str): HTML content of the response.

        Returns:
            list: Extracted product information.

        Raises:
            ValueError: If HTML parsing or data extraction fails.
        """
        html_structure = self.parse_html(response_text)
        if not html_structure:
            log_message('ERROR', "Invalid result during HTML parsing.")
            raise ValueError("HTML parsing returned invalid result.")

        try:
            with open("response.html", "w", encoding="utf-8") as file:
                file.write(response_text)
            log_message('INFO', "HTML response successfully saved to 'response.html'.")
        except Exception as e:
            log_message('ERROR', f"Error saving HTML file: {str(e)}")
            raise

        return self.extract_product_info(html_structure)

    def parse_html(self, response_text):
        """
        Parse the HTML response using BeautifulSoup.

        Args:
            response_text (str): HTML content.

        Returns:
            BeautifulSoup: Parsed HTML structure.
        """
        return BeautifulSoup(response_text, 'html.parser')

    def extract_product_info(self, html):
        """
        Extract product information from the parsed HTML.

        Args:
            html (BeautifulSoup): Parsed HTML structure.

        Returns:
            list: Product information as a list of dictionaries.
        """
        products = []
        product_names = html.find_all('span', {'class': 'product-name'})
        product_prices = html.find_all('span', {'class': 'price'})

        if not product_names or not product_prices:
            log_message('ERROR', "Product names or prices not found.")
            raise ValueError("Product names or prices are missing.")

        log_message('DEBUG', f"Found product names: {len(product_names)}")
        log_message('DEBUG', f"Found product prices: {len(product_prices)}")

        for name, price in zip(product_names, product_prices):
            try:
                product_data = {
                    'name': name.get_text(strip=True) if name else "Name not found",
                    'price': price.get_text(strip=True) if price else "Price not found"
                }
                products.append(product_data)
            except AttributeError as e:
                log_message('ERROR', f"Error extracting product info: {str(e)}")

        return products

    def save_data(self, data, file_name, format='csv'):
        """
        Save the extracted data using the data parser's save_data function.
        """
        save_data(data, file_name, format)
