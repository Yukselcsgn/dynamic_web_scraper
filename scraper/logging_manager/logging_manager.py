import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logging(log_file='logs/scraper.log', log_level=logging.INFO, max_bytes=5*1024*1024, backup_count=5):
    """
    Loglama ayarlarını yapar. Dosya ve konsola loglama seçenekleri sunar.
    Log dosyası için otomatik rotasyon uygular.

    Args:
        log_file (str): Logların kaydedileceği dosyanın yolu. Varsayılan olarak 'logs/scraper.log'.
        log_level (int): Loglama düzeyi. Varsayılan olarak INFO düzeyinde loglanır.
        max_bytes (int): Bir log dosyasının maksimum boyutu (bayt cinsinden). Varsayılan: 5MB.
        backup_count (int): Saklanacak eski log dosyası sayısı. Varsayılan: 5.
    """
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        log_format = '[%(asctime)s] [%(levelname)s]: %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'

        rotating_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8'
        )
        stream_handler = logging.StreamHandler()

        logging.basicConfig(
            level=log_level,
            format=log_format,
            datefmt=date_format,
            handlers=[rotating_handler, stream_handler]
        )
        logging.info("Loglama başarıyla ayarlandı (rotasyonlu).")
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
        with open(f'logs/critical_errors_{datetime.now().strftime("%Y%m%d")}.log', 'a', encoding='utf-8') as critical_log_file:
            critical_log_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
