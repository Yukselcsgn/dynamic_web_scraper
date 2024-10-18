from bs4 import BeautifulSoup

def parse_html(html, element='div', class_name=None):
    """
    HTML içeriğini analiz eder ve istenilen HTML elementini döner.
    
    Args:
        html (str): HTML içeriği.
        element (str): Aranacak HTML elemanı. Varsayılan olarak 'div' elementi aranır.
        class_name (str, optional): Spesifik bir sınıfa sahip elementleri arar.
        
    Returns:
        list of BeautifulSoup objects: Bulunan HTML elemanlarının listesi.
    
    Raises:
        ValueError: Eğer geçerli bir HTML içeriği verilmezse.
    """
    if not html:
        raise ValueError("Geçersiz HTML içeriği.")
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        if class_name:
            elements = soup.find_all(element, class_=class_name)
        else:
            elements = soup.find_all(element)
        
        print(f"{len(elements)} adet '{element}' elemanı bulundu.")
        return elements
    except Exception as e:
        print(f"HTML analizi sırasında bir hata oluştu: {e}")
        return []

def extract_text_from_element(element):
    """
    HTML elementinden metni çıkartır.
    
    Args:
        element (BeautifulSoup object): Bir BeautifulSoup HTML elementi.
        
    Returns:
        str: HTML elementinin içindeki metin.
    """
    try:
        return element.get_text(strip=True)
    except AttributeError:
        print("Geçersiz HTML elemanı.")
        return ""

def find_links(html, base_url=None):
    """
    HTML içeriğinde bulunan tüm bağlantıları bulur ve döner.
    
    Args:
        html (str): HTML içeriği.
        base_url (str, optional): Bağlantıların görece (relative) olduğu durumlarda tam URL oluşturmak için kullanılır.
        
    Returns:
        list: HTML'deki tüm tam URL'lerin listesi.
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        for a_tag in soup.find_all('a', href=True):
            link = a_tag['href']
            # Eğer relative bir link varsa base_url ile birleştirilir
            if base_url and not link.startswith(('http://', 'https://')):
                link = base_url + link
            links.append(link)
        print(f"{len(links)} adet link bulundu.")
        return links
    except Exception as e:
        print(f"Bağlantıları bulma sırasında bir hata oluştu: {e}")
        return []
