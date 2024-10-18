import logging
from bs4 import BeautifulSoup

def detect_site_structure(html_content):
    """
    HTML içeriğini analiz eder ve site yapısına dair bilgi verir.
    :param html_content: İndirilen HTML içeriği (string).
    :return: Site yapısı hakkında bilgi içeren bir sözlük.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Genel site özelliklerini tespit etme
        site_structure = {
            'title': soup.title.string if soup.title else 'Bilinmiyor',
            'meta_description': soup.find('meta', {'name': 'description'})['content']
            if soup.find('meta', {'name': 'description'}) else 'Bilinmiyor',
            'main_sections': [section['id'] for section in soup.find_all('section') if 'id' in section.attrs],
            'product_containers': [div['class'] for div in soup.find_all('div') if 'class' in div.attrs],
            'links': [a['href'] for a in soup.find_all('a', href=True)],
        }

        # Potansiyel ürün listesi ve fiyat bilgisi içeren elementleri arama
        product_containers = soup.find_all('div', class_=['product', 'item', 'product-item'])
        if product_containers:
            site_structure['product_containers'] = [container['class'] for container in product_containers]
        else:
            site_structure['product_containers'] = []

        # Ürün adlarını ve fiyatlarını bulma
        product_titles = soup.find_all('h2', class_='product-title')
        product_prices = soup.find_all('span', class_='price')

        site_structure['product_titles'] = [title.get_text() for title in product_titles]
        site_structure['product_prices'] = [price.get_text() for price in product_prices]

        logging.info(f"Site yapısı başarıyla tespit edildi: {site_structure['title']}")
        return site_structure

    except Exception as e:
        logging.error(f"Site yapısı tespit edilirken hata oluştu: {e}")
        return {}

