# tests/test_site_detector.py

from scraper.site_detection.site_detector import detect_site_structure

def test_detect_site_structure():
    # Site HTML yapısını tespit eden fonksiyonu test eder
    html_content = "<html><body><div class='product'>Sample Product</div></body></html>"
    structure = detect_site_structure(html_content)
    
    assert "product" in structure, "HTML yapısı doğru tespit edilmedi."
