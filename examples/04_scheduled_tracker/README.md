### 2.1 Otomatik Fiyat İzleyici (Scheduled)
**Amaç:** Belirli aralıklarla fiyatları takip etmek

**Senaryo:**
- Kullanıcı izlenecek ürünleri bir listeye ekler
- Her 6 saatte bir fiyatlar kontrol edilir
- Fiyat değişikliği olduğunda bildirim gönderir
- Geçmiş fiyat trendlerini gösterir

**Özellikler:**
- Scheduled tasks (APScheduler)
- Time-series data
- E-posta veya Telegram bildirimleri
- Basit trend analizi
