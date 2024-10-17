import random

class ProxyManager:
    def __init__(self, proxies):
        self.proxies = proxies

    def get_random_proxy(self):
        if not self.proxies:
            return None
        return random.choice(self.proxies)

    def retry_proxy(self, failed_proxy):
        """ Retry logic for failed proxies (if needed). """
        if failed_proxy in self.proxies:
            self.proxies.remove(failed_proxy)
        return self.get_random_proxy()
