# tests/test_logging_manager.py

import pytest
import logging
from scraper.logging_manager.logging_manager import log_message, setup_logging

def test_log_message(tmpdir):
    # Loglama işlemini test eder
    log_file = tmpdir.join("test_log.log")
    setup_logging(str(log_file))
    
    log_message(logging.INFO, "Test log message")
    
    with open(str(log_file), 'r') as f:
        lines = f.readlines()
        assert len(lines) > 0, "Log dosyasına mesaj yazılmadı."
        assert "Test log message" in lines[0], "Log mesajı dosyada bulunamadı."
