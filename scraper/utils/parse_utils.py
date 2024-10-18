from bs4 import BeautifulSoup

def clean_data(data):
    """
    Ham veriyi temizler ve normalize eder.
    
    Args:
        data (str): Temizlenecek ham veri.
    
    Returns:
        str: Temizlenmiş ve normalize edilmiş veri.
    """
    # Verideki fazladan boşlukları, satır sonlarını ve istenmeyen karakterleri kaldır
    cleaned_data = ' '.join(data.split())
    cleaned_data = cleaned_data.replace('\n', '').replace('\r', '').strip()
    return cleaned_data

def extract_data(html_content, selectors):
    """
    Belirtilen CSS seçiciler ile veriyi çıkarır.
    
    Args:
        html_content (str): HTML içeriği.
        selectors (dict): Çıkarılacak verinin CSS seçicileri. Örneğin {'title': 'h1.title'}.
    
    Returns:
        dict: Seçicilere göre çıkarılan veriler.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    extracted_data = {}
    
    for key, selector in selectors.items():
        element = soup.select_one(selector)
        extracted_data[key] = clean_data(element.text) if element else None

    return extracted_data
