import logging
from fake_useragent import UserAgent

def get_random_user_agent():
    """Rastgele bir User-Agent döndür."""
    try:
        ua = UserAgent()
        user_agent = ua.random
        logging.info(f"Rastgele User-Agent seçildi: {user_agent}")
        return user_agent
    except Exception as e:
        logging.error(f"User-Agent oluşturulamadı: {e}")
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"  # Varsayılan UA
