import logging

# Örnek siteye özgü konfigürasyonlar
SITE_CONFIGURATIONS = {
    "amazon.com": {
        "product_container": "div.s-main-slot div.s-result-item",
        "title_selector": "span.a-text-normal",
        "price_selector": "span.a-price-whole",
        "next_page_selector": "ul.a-pagination li.a-last a",
    },
    "ebay.com": {
        "product_container": "li.s-item",
        "title_selector": "h3.s-item__title",
        "price_selector": "span.s-item__price",
        "next_page_selector": "a.pagination__next",
    },
    "sahibinden.com": {
        "product_container": "tr.searchResultsItem",
        "title_selector": "td.searchResultsTitleValue a",
        "price_selector": "td.searchResultsPriceValue",
        "location_selector": "td.searchResultsLocationValue",
        "date_selector": "td.searchResultsDateValue",
        "next_page_selector": "a.prevNextBut",
    },
    # Daha fazla site eklenebilir
}


def get_site_specific_config(site):
    """
    Belirli bir site için konfigürasyon ayarlarını döner.
    :param site: Sitenin domain adı (ör. 'amazon.com').
    :return: Siteye özgü konfigürasyon ayarları (sözlük olarak).
    """
    try:
        config = SITE_CONFIGURATIONS.get(site, {})
        if config:
            logging.info(f"{site} için konfigürasyon başarıyla yüklendi.")
        else:
            logging.warning(
                f"{site} için konfigürasyon bulunamadı, varsayılan ayarlar kullanılacak."
            )
        return config
    except Exception as e:
        logging.error(f"{site} için konfigürasyon alınırken hata oluştu: {e}")
        return {}
