import logging
import random


class UserAgentManager:
    def __init__(self, user_agents=None):
        self.user_agents = user_agents or []
        logging.basicConfig(filename="logs/scraper.log", level=logging.INFO)
        logging.info(
            f"UserAgentManager başlatıldı. Toplam kullanıcı ajanı: {len(self.user_agents)}"
        )
        if self.user_agents:
            logging.info(f"User agents: {self.user_agents[:2]}")  # Show first 2
        else:
            logging.warning("No user agents provided to UserAgentManager")

    def get_user_agent(self):
        """Rastgele bir kullanıcı ajanı seçer ve döner."""
        try:
            if not self.user_agents:
                raise ValueError("Kullanıcı ajanı listesi boş!")
            user_agent = random.choice(self.user_agents)
            logging.info(f"Kullanıcı ajanı seçildi: {user_agent}")
            return user_agent
        except Exception as e:
            logging.error(f"Kullanıcı ajanı seçilirken hata: {e}")
            raise
