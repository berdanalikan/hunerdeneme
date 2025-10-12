# 🚀 Reçete Analiz API - Kullanım Kılavuzu

## 📋 Özet

Bu API, kullanıcıların el yazısı reçete görsellerini yükleyip, OpenAI API ile analiz ederek yapılandırılmış bilgi almasını sağlar.

## 🎯 Özellikler

- ✅ **OCR Analizi**: Mevcut CRNN modeli ile metin çıkarımı
- ✅ **OpenAI Entegrasyonu**: GPT-4 Vision ile akıllı reçete analizi  
- ✅ **Web Arayüzü**: Kullanıcı dostu HTML arayüzü
- ✅ **Fallback Sistemi**: OpenAI çalışmazsa OCR kullanımı
- ✅ **Yapılandırılmış Çıktı**: JSON formatında düzenli reçete bilgileri

## 🚀 Hızlı Başlangıç

### 1. API'yi Başlat
```bash
cd /Users/berdanalikan/Desktop/handwrite
source .venv/bin/activate
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Web Arayüzünü Aç
Tarayıcıda `http://localhost:8000` adresine gidin.

### 3. Reçete Analizi
1. Reçete görselinizi yükleyin
2. Sorunuzu yazın (opsiyonel)
3. "Reçeteyi Analiz Et" butonuna tıklayın

## 🔧 API Endpoint'leri

### Health Check
```bash
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "ocr_model_loaded": true,
  "openai_configured": true
}
```

### Reçete Analizi
```bash
POST /analyze-prescription
Content-Type: multipart/form-data

file: [reçete görseli]
user_question: "Bu reçetedeki ilaçları listele"
use_ocr_fallback: true
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "patient_name": "Ahmet Yılmaz",
    "patient_id": "12345678901", 
    "doctor_name": "Dr. Mehmet Kaya",
    "date": "15.10.2024",
    "medications": [
      {
        "name": "Parol",
        "dosage": "500mg",
        "usage": "Günde 3 kez, yemeklerden sonra"
      }
    ],
    "dosage_instructions": "İlaçları düzenli kullanın",
    "special_notes": "Alerji durumunda doktora başvurun",
    "requested_info": "Bu reçetede 2 farklı ilaç bulunmaktadır",
    "confidence_score": 0.95,
    "raw_text": "Ham metin çıkarımı..."
  },
  "ocr_text": "OCR ile çıkarılan metin",
  "processing_time": 2.34
}
```

### Sadece Metin Çıkarımı
```bash
POST /extract-text
Content-Type: multipart/form-data

file: [görsel]
use_ocr: true
```

## 🧪 Test Etme

### Demo Scripti
```bash
python demo.py
```

### Manuel Test
```bash
# OCR test
curl -X POST "http://localhost:8000/extract-text" \
  -F "file=@data/raw/synth_0000.jpg" \
  -F "use_ocr=true"

# Reçete analizi test
curl -X POST "http://localhost:8000/analyze-prescription" \
  -F "file=@data/raw/synth_0000.jpg" \
  -F "user_question=Bu reçetedeki metni analiz et" \
  -F "use_ocr_fallback=true"
```

## ⚙️ Yapılandırma

### OpenAI API Key
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Model Dosyaları
- OCR Model: `checkpoints/crnn_ctc_best.pdparams`
- Karakter Seti: `checkpoints/charset.txt`

## 📊 Mevcut Durum

### ✅ Çalışan Özellikler
- OCR servisi (CRNN modeli)
- Web arayüzü
- API endpoint'leri
- Dosya yükleme
- Fallback sistemi

### ⚠️ Geliştirilmesi Gerekenler
- OpenAI API key ayarlanması
- Model performansı iyileştirme
- Daha fazla test verisi

## 🔍 Sorun Giderme

### OCR Modeli Yüklenemiyor
- `checkpoints/crnn_ctc_best.pdparams` dosyasının varlığını kontrol edin
- Model dosyasının bozuk olmadığından emin olun

### OpenAI API Hatası
- API key'in doğru ayarlandığını kontrol edin
- Kredi limitinizi kontrol edin
- OCR fallback otomatik olarak devreye girer

### Görsel Yükleme Hatası
- Desteklenen formatlar: JPG, PNG, GIF
- Dosya boyutu 10MB'dan küçük olmalı

## 📈 Performans

- **OCR**: ~0.05 saniye
- **OpenAI analizi**: ~3-5 saniye (API key varsa)
- **Toplam işlem süresi**: ~5-7 saniye

## 🎯 Kullanım Senaryoları

1. **Eczacı**: Reçete doğrulama ve ilaç bilgisi çıkarma
2. **Hasta**: Reçete içeriğini anlama
3. **Doktor**: Reçete arşivleme ve analiz
4. **Araştırmacı**: Tıbbi veri analizi

## 🔒 Güvenlik

- Production'da CORS ayarlarını kısıtlayın
- API key'leri environment variable'da saklayın
- Dosya yükleme limitlerini ayarlayın

## 📞 Destek

- API dokümantasyonu: `http://localhost:8000/docs`
- Test scripti: `python api/test_api.py`
- Demo: `python demo.py`

---

**🎉 API başarıyla çalışıyor! Kullanıma hazır.**
