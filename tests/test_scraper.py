# tests/test_scraper.py

import pytest
from scraper import Scraper

@pytest.fixture
def scraper_instance():
    url = "https://www.teknosa.com/akilli-saat-c-100004001"
    return Scraper(url)

def test_fetch_data(scraper_instance):
    # Veri çekme işlevinin doğru çalıştığını test eder
    response = scraper_instance.fetch_data()
    assert response.status_code == 200, "Veri çekme başarısız oldu."

def test_parse_response(scraper_instance):
    # Yanıtın doğru şekilde işlendiğini test eder
    response = scraper_instance.fetch_data()
    parsed_data = scraper_instance.parse_response(response)
    assert parsed_data is not None, "Yanıt işleme başarısız oldu."
    assert isinstance(parsed_data, dict), "İşlenen yanıt yanlış formatta döndü."
