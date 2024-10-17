import random
from fake_useragent import UserAgent
import time

class UserAgentHelper:
    def __init__(self):
        self.ua = UserAgent()

    def get_random_user_agent(self):
        return self.ua.random

def human_like_wait(min_time=3, max_time=7):
    """ Simulate human-like delay between actions. """
    wait_time = random.uniform(min_time, max_time)
    time.sleep(wait_time)

class PriceExtractor:
    @staticmethod
    def extract_price(price_text):
        """ Extract numerical value from price text. """
        try:
            cleaned_price = ''.join(filter(lambda x: x.isdigit() or x == '.', price_text))
            return float(cleaned_price) if cleaned_price else 0
        except ValueError:
            logging.error(f"Error extracting price from {price_text}")
            return 0
