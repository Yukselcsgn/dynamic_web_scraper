# Copyright 2024 Yüksel Coşgun
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import re

from bs4 import BeautifulSoup

# Logging ayarları
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def clean_data(data):
    """
    Ham veriyi temizler ve normalize eder.

    Args:
        data (str): Temizlenecek ham veri.

    Returns:
        str: Temizlenmiş ve normalize edilmiş veri.
    """
    try:
        cleaned_data = " ".join(data.split())
        cleaned_data = cleaned_data.replace("\n", "").replace("\r", "").strip()
        # Özel karakterleri kaldır
        cleaned_data = re.sub(r"[^\w\s,.₺€$]", "", cleaned_data)
        return cleaned_data
    except Exception as e:
        logging.error(f"Veri temizleme sırasında hata: {e}")
        return data


def extract_data(html_content, selectors, multiple=False):
    """
    Belirtilen CSS seçiciler ile veriyi çıkarır.

    Args:
        html_content (str): HTML içeriği.
        selectors (dict): Çıkarılacak verinin CSS seçicileri. Örneğin {'title': 'h1.title'}.
        multiple (bool): Birden fazla sonuç döndürmek için True.

    Returns:
        dict: Seçicilere göre çıkarılan veriler.
    """
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        extracted_data = {}

        for key, selector in selectors.items():
            if multiple:
                elements = soup.select(selector)
                extracted_data[key] = [clean_data(el.text) for el in elements if el]
            else:
                element = soup.select_one(selector)
                extracted_data[key] = clean_data(element.text) if element else None

        return extracted_data
    except Exception as e:
        logging.error(f"Veri çıkarımı sırasında hata: {e}")
        return {}


def extract_products(html_content, product_selector, title_selector, price_selector):
    """
    Ürün bilgilerini (başlıklar ve fiyatlar) çıkarır.

    Args:
        html_content (str): HTML içeriği.
        product_selector (str): Ürün kapsayıcısını belirten CSS seçici.
        title_selector (str): Ürün başlığını belirten CSS seçici.
        price_selector (str): Ürün fiyatını belirten CSS seçici.

    Returns:
        list: Her bir ürün için başlık ve fiyat bilgisi içeren sözlükler listesi.
    """
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        products = []

        containers = soup.select(product_selector)
        for container in containers:
            title = container.select_one(title_selector)
            price = container.select_one(price_selector)
            products.append(
                {
                    "title": clean_data(title.text) if title else "Başlık Bulunamadı",
                    "price": clean_data(price.text) if price else "Fiyat Bulunamadı",
                }
            )

        return products
    except Exception as e:
        logging.error(f"Ürün bilgisi çıkarımı sırasında hata: {e}")
        return []


def parse_with_config(html_content, site_config):
    """
    Siteye özel ayarlarla veriyi çıkarır.

    Args:
        html_content (str): HTML içeriği.
        site_config (dict): Siteye özgü yapılandırma. Örneğin:
            {
                'selectors': {
                    'title': 'h1.product-title',
                    'price': 'span.price'
                },
                'multiple': True
            }

    Returns:
        dict: Seçicilere göre çıkarılan veriler.
    """
    try:
        selectors = site_config.get("selectors", {})
        multiple = site_config.get("multiple", False)
        return extract_data(html_content, selectors, multiple=multiple)
    except Exception as e:
        logging.error(f"Siteye özel veri çıkarımı sırasında hata: {e}")
        return {}


def extract_links(html_content):
    """
    Sayfadan tüm bağlantıları çıkarır.

    Args:
        html_content (str): HTML içeriği.

    Returns:
        list: Tüm bağlantılar.
    """
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        links = [
            a["href"]
            for a in soup.find_all("a", href=True)
            if "javascript" not in a["href"].lower()
        ]
        return links
    except Exception as e:
        logging.error(f"Bağlantı çıkarımı sırasında hata: {e}")
        return []


def extract_meta_info(html_content):
    """
    Sayfanın meta bilgilerini çıkarır.

    Args:
        html_content (str): HTML içeriği.

    Returns:
        dict: Sayfa başlığı ve açıklaması.
    """
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        meta_info = {
            "title": soup.title.string.strip() if soup.title else "Başlık Bulunamadı",
            "description": (
                soup.find("meta", {"name": "description"})["content"].strip()
                if soup.find("meta", {"name": "description"})
                else "Açıklama Bulunamadı"
            ),
        }
        return meta_info
    except Exception as e:
        logging.error(f"Meta bilgi çıkarımı sırasında hata: {e}")
        return {}


def extract_all_text(html_content):
    """
    Sayfadaki tüm metni çıkarır.

    Args:
        html_content (str): HTML içeriği.

    Returns:
        str: Sayfadaki tüm metin.
    """
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        return clean_data(soup.get_text())
    except Exception as e:
        logging.error(f"Tüm metni çıkarma sırasında hata: {e}")
        return ""
