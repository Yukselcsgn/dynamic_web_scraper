import logging
import os
from datetime import datetime


def setup_logging(log_file='logs/scraper.log', log_level=logging.INFO):
    """
    Loglama ayarlarını yapar. Dosya ve konsola loglama seçenekleri sunar.

    Args:
        log_file (str): Logların kaydedileceği dosyanın yolu. Varsayılan olarak 'logs/scraper.log'.
        log_level (int): Loglama düzeyi. Varsayılan olarak INFO düzeyinde loglanır.
    """
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        log_format = '[%(asctime)s] [%(levelname)s]: %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'

        logging.basicConfig(
            level=log_level,
            format=log_format,
            datefmt=date_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        logging.info("Loglama başarıyla ayarlandı.")
    except Exception as e:
        print(f"Loglama ayarları yapılandırılırken bir hata oluştu: {e}")


def log_message(level, message):
    """
    Mesajı belirtilen düzeyde loglar.

    Args:
        level (str): Loglama düzeyi (INFO, DEBUG, WARNING, ERROR, CRITICAL).
        message (str): Loglanacak mesaj.
    """
    level = level.upper()
    if level == 'DEBUG':
        logging.debug(message)
    elif level == 'INFO':
        logging.info(message)
    elif level == 'WARNING':
        logging.warning(message)
    elif level == 'ERROR':
        logging.error(message)
    elif level == 'CRITICAL':
        logging.critical(message)
    else:
        raise ValueError(f"Desteklenmeyen log seviyesi: {level}")

    if level in ['ERROR', 'CRITICAL']:
        with open(f'logs/critical_errors_{datetime.now().strftime("%Y%m%d")}.log', 'a') as critical_log_file:
            critical_log_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
