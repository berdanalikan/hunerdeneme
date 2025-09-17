# OpenAI Assistant Eğitim Sistemi

Bu sistem Supabase'deki feedback verilerini kullanarak OpenAI Assistant'ınızı sürekli iyileştirir.

## 🎯 Yaklaşımlar

### 1. **Fine-tuning (En Etkili)**
```bash
# Training data oluştur
python training_data_generator.py

# OpenAI platformunda fine-tuning yap:
# 1. https://platform.openai.com/finetuning
# 2. training_data.jsonl dosyasını yükle
# 3. Model eğitimi başlat
# 4. Yeni model ID'sini OPENAI_ASSISTANT_ID olarak güncelle
```

### 2. **Dinamik Instructions Güncelleme**
```bash
# Feedback analizi yap ve instructions güncelle
python instruction_updater.py
```

### 3. **Otomatik Eğitim Sistemi**
```bash
# Tek seferlik kontrol
python automated_training.py --once

# Sürekli çalışan sistem (cron job)
python automated_training.py
```

## 📊 Sistem Bileşenleri

### `training_data_generator.py`
- Supabase'den feedback verilerini çeker
- Pozitif feedback: Mevcut yanıtları doğru kabul eder
- Negatif feedback: Yanıtları düzeltir
- OpenAI fine-tuning formatında training data oluşturur

### `instruction_updater.py`
- Feedback verilerini analiz eder
- Yaygın hataları tespit eder
- System instructions'ı dinamik olarak günceller
- Başarı oranına göre ek talimatlar ekler

### `automated_training.py`
- Günlük performans kontrolü yapar
- Başarı oranı < %70 ise eğitim tetikler
- Trend analizi yapar
- Cron job olarak çalışabilir

## 🚀 Kurulum

### 1. Gerekli Paketler
```bash
pip install schedule
```

### 2. Environment Variables
`.env` dosyasına ekleyin:
```
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key
OPENAI_API_KEY=your_openai_key
OPENAI_ASSISTANT_ID=your_assistant_id
```

### 3. Cron Job (Opsiyonel)
```bash
# Her gün saat 09:00'da çalıştır
0 9 * * * cd /path/to/project && python automated_training.py --once
```

## 📈 Performans Metrikleri

### Başarı Oranı Hesaplama
```
Başarı Oranı = (Pozitif Feedback / Toplam Feedback) × 100
```

### Eğitim Tetikleme Kriterleri
- Minimum 10 feedback
- Başarı oranı < %70
- Son 3 günün ortalaması < %75

## 🔄 Eğitim Döngüsü

1. **Veri Toplama**: Kullanıcı feedback'leri Supabase'e kaydedilir
2. **Analiz**: Sistem performansı analiz edilir
3. **Karar**: Eğitim gerekli mi kontrol edilir
4. **Eğitim**: Training data oluşturulur ve model güncellenir
5. **Değerlendirme**: Yeni performans ölçülür

## 📝 Training Data Formatı

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Sen Türk sağlık mevzuatına göre tıbbi raporları değerlendiren bir uzmansın."
    },
    {
      "role": "user",
      "content": "Rapor metni..."
    },
    {
      "role": "assistant", 
      "content": "Değerlendirme sonucu..."
    }
  ]
}
```

## 🎛️ Konfigürasyon

### Fine-tuning Parametreleri
- **Model**: gpt-3.5-turbo veya gpt-4
- **Epochs**: 3-5 (overfitting'i önlemek için)
- **Learning Rate**: 0.1-0.3
- **Batch Size**: 4-8

### Instruction Güncelleme
- Minimum feedback: 50
- Analiz periyodu: 7 gün
- Güncelleme sıklığı: Haftalık

## 🔍 Monitoring

### Log Dosyaları
- `training_log.json`: Eğitim geçmişi
- `training_data_YYYYMMDD_HHMM.jsonl`: Training verileri

### Metrikler
- Günlük başarı oranı
- Hata türü dağılımı
- Feedback sayısı
- Eğitim tetikleme sıklığı

## 🚨 Sorun Giderme

### Yaygın Hatalar
1. **Supabase bağlantı hatası**: Service key kontrolü
2. **OpenAI API hatası**: API key ve rate limit kontrolü
3. **Training data boş**: Feedback verisi kontrolü

### Debug
```bash
# Verbose çıktı için
python training_data_generator.py --verbose
python instruction_updater.py --debug
```

## 📊 Örnek Çıktı

```
=== Günlük Eğitim Kontrolü - 2025-01-16 09:00 ===
Toplam feedback: 150
Başarı oranı: %68.0
Eğitim gerekli: Evet
Sebep: Düşük başarı oranı (%68.0 < %70)

🔄 Eğitim başlatılıyor...
Training data oluşturuluyor...
120 training örneği oluşturuldu.
Training data training_data_20250116_0900.jsonl dosyasına kaydedildi.
```

Bu sistem sayesinde Assistant'ınız kullanıcı feedback'lerine göre sürekli öğrenir ve iyileşir!
