## Proje Hedefleri ve Başarı Metrikleri

- Amaç: El yazısı metinlerin OCR ile doğru ve hızlı çıkarılması.
- Kapsam: Türkçe ağırlıklı; latin charset (+ gerekiyorsa özel karakterler).
- Riskler: Düşük kaliteli görüntüler, farklı yazı stilleri, veri dengesizliği.

### Metrikler (hedef örnekleri)
- CER (Character Error Rate) ≤ X
- WER (Word Error Rate) ≤ Y
- p95 gecikme (tek görsel) ≤ Z ms
- Throughput ≥ T RPS (batch=1, FP16/INT8 duruma göre)

### Onay Kriterleri
- Hedefler ve kapsam bu dosyada netleştirildi.
- Varsayımlar ve riskler listelendi.
- Değerlendirme planı: train/val/test ayrımı ve raporlama formatı tanımlı.

