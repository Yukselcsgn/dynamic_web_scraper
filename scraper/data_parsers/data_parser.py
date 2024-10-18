import csv
import json
import os

def save_data(data, file_name, format='csv'):
    """
    Kazınan veriyi belirli bir formatta kaydeder. CSV ve JSON formatları desteklenir.
    
    Args:
        data (list of dict): İşlenmiş veri. Her bir dict, bir veri kaydını temsil eder.
        file_name (str): Kaydedilecek dosyanın ismi.
        format (str): Kaydedilecek dosyanın formatı. 'csv' veya 'json' olabilir.
    
    Raises:
        ValueError: Desteklenmeyen bir format girilirse.
    """
    if format == 'csv':
        file_path = f"data/processed_data/{file_name}.csv"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            print(f"Veri başarıyla {file_name}.csv olarak kaydedildi.")
        except Exception as e:
            print(f"Veri kaydedilirken bir hata oluştu: {e}")
    elif format == 'json':
        file_path = f"data/processed_data/{file_name}.json"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            print(f"Veri başarıyla {file_name}.json olarak kaydedildi.")
        except Exception as e:
            print(f"Veri kaydedilirken bir hata oluştu: {e}")
    else:
        raise ValueError("Desteklenmeyen format: Lütfen 'csv' veya 'json' kullanın.")

def process_data(raw_data):
    """
    Ham veriyi işler, temizler ve normalize eder. Veriyi analiz ve kaydetmeye hazır hale getirir.
    
    Args:
        raw_data (list of dict): Kazınan ham veri.
        
    Returns:
        list of dict: Temizlenmiş ve işlenmiş veri.
    
    İşlem Adımları:
        - Boş veya eksik değerlerin temizlenmesi.
        - Verilerin normalleştirilmesi ve formatlanması.
        - İlgili olmayan verilerin çıkarılması.
    """
    processed_data = []
    for entry in raw_data:
        # Eksik veya geçersiz değerleri temizleme
        if not entry or any(value is None for value in entry.values()):
            continue
        
        # Örneğin, fiyat bilgisini sayısal bir değere dönüştürme
        if 'price' in entry:
            try:
                entry['price'] = float(entry['price'].replace(',', '').replace('$', ''))
            except ValueError:
                entry['price'] = None
        
        # Verilerin diğer alanları için de gerekli dönüşümleri yapın.
        # Örneğin, tarih formatı düzeltme veya metinleri küçük harfe çevirme
        if 'date' in entry:
            entry['date'] = entry['date'].strip()
        
        processed_data.append(entry)
    
    print(f"İşlenmiş {len(processed_data)} veri kaydı.")
    return processed_data
