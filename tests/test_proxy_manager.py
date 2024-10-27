# tests/test_proxy_manager.py

import pytest
from scraper.proxy_manager.proxy_manager import manage_proxies
from scraper.proxy_manager.proxy_validator import validate_proxy

def test_manage_proxies():
    # Proxy havuzunu yönetme fonksiyonunu test eder
    proxies = ["192.168.1.1:8080", "192.168.1.2:8080"]
    valid_proxies = manage_proxies(proxies)
    
    assert len(valid_proxies) <= len(proxies), "Geçersiz proxyler kaldırılmadı."

def test_validate_proxy():
    # Proxy doğrulama fonksiyonunu test eder
    valid_proxy = "192.168.1.1:8080"
    assert validate_proxy(valid_proxy) is True, "Geçerli proxy yanlış sonuç verdi."
    
    invalid_proxy = "192.168.1.999:8080"
    assert validate_proxy(invalid_proxy) is False, "Geçersiz proxy yanlış sonuç verdi."
