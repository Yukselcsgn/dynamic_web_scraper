import logging
import os
from datetime import datetime

def setup_logging(log_file='logs/scraper.log', log_level=logging.INFO):
    """
    Loglama ayarlarını yapar. Dosya ve konsola loglama seçenekleri sunar.
    
    Args:
        log_file (str): Logların kaydedileceği dosyanın yolu. Varsayılan olarak 'logs/scraper.log'.
        log_level (int): Loglama düzeyi. Varsayılan olarak INFO düzeyinde loglanır.
                         Diğer seçenekler: DEBUG, WARNING, ERROR, CRITICAL.
    
    Raises:
        OSError: Log dosyasına erişim sağlanamazsa.
    
    Log Formatı:
        - [Tarih - Zaman] [Log Düzeyi]: Mesaj
    """
    try:
        # Log dizini yoksa oluşturulur
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        # Log formatı
        log_format = '[%(asctime)s] [%(levelname)s]: %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        
        # Root logger ayarları
        logging.basicConfig(
            level=log_level,
            format=log_format,
            datefmt=date_format,
            handlers=[
                logging.FileHandler(log_file),    # Log dosyasına yazmak için
                logging.StreamHandler()           # Konsola log yazmak için
            ]
        )
        logging.info("Loglama başarıyla ayarlandı.")
    except OSError as e:
        print(f"Log dosyasına erişim sağlanamadı: {e}")
    except Exception as e:
        print(f"Loglama ayarları yapılandırılırken bir hata oluştu: {e}")

def log_message(level, message):
    """
    Mesajı belirtilen düzeyde loglar.
    
    Args:
        level (str): Loglama düzeyi (INFO, DEBUG, WARNING, ERROR, CRITICAL).
        message (str): Loglanacak mesaj.
    
    Raises:
        ValueError: Desteklenmeyen bir log seviyesi girildiğinde.
    
    Kullanım Örneği:
        - log_message('INFO', 'Scraper başlatıldı.')
        - log_message('ERROR', 'Proxy hatası oluştu.')
    """
    # Log seviyesi doğrulama
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
    
    # Ekstra: Log mesajı, belirli bir kritik hata durumunda dosya adı ile yazılabilir
    if level in ['ERROR', 'CRITICAL']:
        with open(f'logs/critical_errors_{datetime.now().strftime("%Y%m%d")}.log', 'a') as critical_log_file:
            critical_log_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
