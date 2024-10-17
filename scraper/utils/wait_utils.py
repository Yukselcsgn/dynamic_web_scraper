import random
import time
import logging

def human_like_wait(min_wait=1, max_wait=5):
    """İnsan benzeri rastgele bekleme süresi uygula."""
    wait_time = random.uniform(min_wait, max_wait)
    logging.info(f"{wait_time:.2f} saniye bekleniyor.")
    time.sleep(wait_time)
