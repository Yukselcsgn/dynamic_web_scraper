import random
import logging
from .user_agent_loader import load_user_agents_from_file, load_user_agents_from_api
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class UserAgentManager:
    def __init__(self, source='file', file_path=None, api_url=None):
        self.user_agents = []
        self.source = source
        self.file_path = file_path
        self.api_url = api_url
        self.load_user_agents()

        logging.basicConfig(filename='logs/scraper.log', level=logging.INFO)
        logging.info(f"UserAgentManager başlatıldı: Kaynak - {self.source}")

    def load_user_agents(self):
        """Kullanıcı ajanlarını belirlenen kaynaktan yükler (dosya veya API)."""
        try:
            if self.source == 'file' and self.file_path:
                self.user_agents = load_user_agents_from_file(self.file_path)
            elif self.source == 'api' and self.api_url:
                self.user_agents = load_user_agents_from_api(self.api_url)
            else:
                raise ValueError("Geçersiz kullanıcı ajanı kaynağı.")

            if not self.user_agents:
                raise ValueError("Yüklenen kullanıcı ajanı listesi boş!")

            logging.info(f"{len(self.user_agents)} kullanıcı ajanı başarıyla yüklendi.")
        except Exception as e:
            logging.error(f"Kullanıcı ajanları yüklenirken hata: {e}")
            raise

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
