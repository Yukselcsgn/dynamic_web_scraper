import logging
from bs4 import BeautifulSoup
import re


def detect_site_structure(html_content, site_config=None):
    """
    HTML içeriğini analiz eder ve site yapısına dair bilgi verir.

    Args:
        html_content (str): İndirilen HTML içeriği.
        site_config (dict, optional): Siteye özgü konfigürasyon ayarları.

    Returns:
        dict: Site yapısı hakkında bilgi içeren bir sözlük.
    """
    try:
        soup = BeautifulSoup(html_content, "html.parser")

        # Genel site özelliklerini tespit etme
        site_structure = {
            "site_title": (
                soup.title.string.strip() if soup.title else "Başlık Bulunamadı"
            ),
            "meta_description": (
                soup.find("meta", {"name": "description"})["content"].strip()
                if soup.find("meta", {"name": "description"})
                else "Açıklama Bulunamadı"
            ),
            "main_sections": [
                section["id"]
                for section in soup.find_all("section")
                if "id" in section.attrs
            ],
            "links": [
                a["href"]
                for a in soup.find_all("a", href=True)
                if "javascript" not in a["href"].lower()
            ],
            "header_present": soup.find("header") is not None,
            "footer_present": soup.find("footer") is not None,
        }

        # Ürün bilgileri
        product_titles = []
        product_prices = []

        if site_config:
            logging.info("Siteye özgü seçiciler kullanılıyor.")
            # Siteye özgü ürün seçicileri uygula
            product_containers = soup.select(
                site_config.get("product_container", "div")
            )
            title_selector = site_config.get("title_selector")
            price_selector = site_config.get("price_selector")

            for container in product_containers:
                if title_selector:
                    product_titles += [
                        title.get_text(strip=True)
                        for title in container.select(title_selector)
                    ]
                if price_selector:
                    product_prices += [
                        price.get_text(strip=True)
                        for price in container.select(price_selector)
                    ]
        else:
            logging.warning(
                "Site konfigürasyonu bulunamadı. Varsayılan seçicilerle devam ediliyor."
            )
            # Varsayılan ürün bilgisi tespiti
            product_containers = soup.find_all(
                "div", class_=lambda cls: cls and "product" in cls.lower()
            )
            product_titles = [
                title.get_text(strip=True)
                for container in product_containers
                for title in container.find_all(
                    ["h2", "span", "p"], class_=lambda cls: cls and "title" in cls
                )
            ]
            product_prices = [
                price.get_text(strip=True)
                for container in product_containers
                for price in container.find_all(
                    ["span", "p"], class_=lambda cls: cls and "price" in cls
                )
            ]

        # Regex ile fiyat kontrolü (yedek)
        if not product_prices:
            product_prices += re.findall(
                r"\d+[\.,]?\d*\s?(?:₺|TL|USD|EUR)", html_content
            )

        # Sonuçları ekliyoruz
        site_structure["product_titles"] = product_titles or [
            "Ürün başlıkları bulunamadı"
        ]
        site_structure["product_prices"] = product_prices or [
            "Fiyat bilgisi bulunamadı"
        ]

        logging.info(
            f"Site yapısı başarıyla tespit edildi: {site_structure['site_title']}"
        )
        return site_structure

    except Exception as e:
        logging.error(f"Site yapısı tespit edilirken hata oluştu: {e}")
        return {}


def auto_detect_selectors(html_content):
    """
    HTML içeriğine dayanarak otomatik olarak CSS seçicileri tespit eder.

    Args:
        html_content (str): İndirilen HTML içeriği.

    Returns:
        dict: Otomatik olarak algılanan CSS seçicileri içeren sözlük.
    """
    try:
        soup = BeautifulSoup(html_content, "html.parser")

        # Ürün kapsayıcılarını tespit et
        product_containers = soup.find_all(
            "div", class_=lambda cls: cls and "product" in cls.lower()
        )
        if not product_containers:
            logging.warning("Ürün kapsayıcıları bulunamadı.")
            return {}

        # Başlık ve fiyat seçicilerini tespit et
        sample_container = product_containers[0]
        title_element = sample_container.find(
            ["h1", "h2", "span", "p"], class_=lambda cls: cls and "title" in cls
        )
        price_element = sample_container.find(
            ["span", "p"], class_=lambda cls: cls and "price" in cls
        )

        selectors = {
            "product_container": 'div[class*="product"]',
            "title_selector": (
                f".{title_element['class'][0]}"
                if title_element and "class" in title_element.attrs
                else None
            ),
            "price_selector": (
                f".{price_element['class'][0]}"
                if price_element and "class" in price_element.attrs
                else None
            ),
        }

        return selectors

    except Exception as e:
        logging.error(f"CSS seçicileri otomatik tespit edilirken hata oluştu: {e}")
        return {}


def detect_and_extract(html_content, site_config=None):
    """
    Site yapısını tespit eder ve ürün bilgilerini çıkarır.

    Args:
        html_content (str): İndirilen HTML içeriği.
        site_config (dict, optional): Siteye özgü yapılandırma bilgileri.

    Returns:
        dict: Site yapısı ve çıkarılan veriler.
    """
    try:
        if not site_config:
            logging.info("Site yapılandırması bulunamadı, otomatik tespit uygulanıyor.")
            site_config = auto_detect_selectors(html_content)

        site_structure = detect_site_structure(html_content, site_config=site_config)
        return site_structure

    except Exception as e:
        logging.error(f"Site tespiti ve veri çıkarımı sırasında hata oluştu: {e}")
        return {}
