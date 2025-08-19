from time import sleep
from random import uniform


def sleep_random(min_time, max_time):
    """
    Rastgele bir süre bekler.

    Args:
        min_time (float): Minimum bekleme süresi (saniye).
        max_time (float): Maksimum bekleme süresi (saniye).

    Usage:
        sleep_random(2, 5)  # 2 ile 5 saniye arasında rastgele bekler.
    """
    wait_time = uniform(min_time, max_time)
    print(f"{wait_time:.2f} saniye bekleniyor...")
    sleep(wait_time)
