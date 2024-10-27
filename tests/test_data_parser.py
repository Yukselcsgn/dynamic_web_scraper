import pytest
import sys
import os

# Proje kök dizinini (dynamic-ecommerce-scraper/) Python'un arama yollarına ekle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Modülleri doğru şekilde import et
from data_parser import save_data, process_data
from html_parser import parse_html

def test_save_data(tmpdir):
    # Verinin CSV formatında kaydedildiğini test eder
    data = [{"name": "Product 1", "price": "$10"}, {"name": "Product 2", "price": "$20"}]
    file_path = tmpdir.join("test_data.csv")
    save_data(data, format="csv", file_path=str(file_path))

    with open(str(file_path), 'r') as f:
        lines = f.readlines()
        assert len(lines) > 1, "Veri dosyaya kaydedilmedi."

def test_process_data():
    # Ham veriyi işleme fonksiyonunu test eder
    raw_data = [{"name": " Product 1 ", "price": "$10.00"}, {"name": " Product 2 ", "price": "$20.00"}]
    processed_data = process_data(raw_data)

    assert all(" " not in item['name'] for item in processed_data), "İşlenen veri temizlenmedi."
