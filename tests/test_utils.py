# tests/test_utils.py

import pytest
from scraper.utils.request_utils import send_request
from scraper.utils.wait_utils import sleep_random

def test_send_request():
    # HTTP isteği gönderme fonksiyonunu test eder
    response = send_request("https://httpbin.org/get")
    assert response.status_code == 200, "HTTP isteği başarısız."

def test_sleep_random(mocker):
    # Rastgele bekleme fonksiyonunu test eder
    mock_sleep = mocker.patch("utils.wait_utils.time.sleep")
    sleep_random(1, 2)
    mock_sleep.assert_called_once_with(pytest.approx(1.5, rel=0.5))
