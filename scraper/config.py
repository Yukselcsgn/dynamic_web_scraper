import json
import os
import sqlite3
import requests

CONFIG_FILE = 'config.json'
DB_FILE = 'scraper_data.db'

def load_config():
    """
    Konfigürasyon ayarlarını dosyadan okur.
    
    Returns:
        dict: Konfigürasyon ayarlarını içeren sözlük.
    """
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"Config dosyası bulunamadı: {CONFIG_FILE}")
    
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    # Proxy kullanımı ayarını kontrol et
    if 'use_proxy' in config and config['use_proxy']:
        if not config.get('proxies'):
            raise ValueError("Proxy kullanımı seçildi ancak proxy listesi boş!")
    
    return config

def save_config(config):
    """
    Güncellenmiş konfigürasyonu dosyaya kaydeder.
    
    Args:
        config (dict): Güncellenmiş konfigürasyon sözlüğü.
    """
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def save_data_to_db(data):
    """
    Veriyi SQLite veritabanına kaydeder.
    
    Args:
        data (list): Kaydedilecek ürün verileri.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Eğer tablo yoksa oluştur
    cursor.execute('''CREATE TABLE IF NOT EXISTS products 
                      (id INTEGER PRIMARY KEY, name TEXT, price TEXT)''')
    
    for item in data:
        cursor.execute('INSERT INTO products (name, price) VALUES (?, ?)', (item['name'], item['price']))
    
    conn.commit()
    conn.close()

def send_data_to_api(data, api_endpoint):
    """
    Veriyi API'ye gönderir.
    
    Args:
        data (list): Gönderilecek ürün verileri.
        api_endpoint (str): API'nin URL'si.
    """
    response = requests.post(api_endpoint, json=data)
    if response.status_code == 200:
        print("Veri başarıyla API'ye gönderildi.")
    else:
        print(f"API isteği başarısız oldu: {response.status_code}")
