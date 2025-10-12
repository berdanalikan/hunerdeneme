# Reçete Analiz API

Bu API, el yazısı reçete görsellerini analiz ederek yapılandırılmış bilgi çıkaran bir sistemdir.

## 🚀 Özellikler

- **OCR Analizi**: Mevcut CRNN modeli ile metin çıkarımı
- **OpenAI Entegrasyonu**: GPT-4 Vision ile akıllı reçete analizi
- **Web Arayüzü**: Kullanıcı dostu HTML arayüzü
- **Yapılandırılmış Çıktı**: JSON formatında düzenli reçete bilgileri
- **Fallback Sistemi**: OpenAI çalışmazsa OCR kullanımı

## 📋 Gereksinimler

1. **Python 3.8+**
2. **Eğitilmiş CRNN modeli** (`checkpoints/crnn_ctc_best.pdparams`)
3. **OpenAI API Key** (opsiyonel, OCR fallback mevcut)

## 🛠️ Kurulum

1. **Bağımlılıkları yükle:**
```bash
pip install -r requirements.txt
```

2. **OpenAI API Key ayarla (opsiyonel):**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

3. **Model dosyalarını kontrol et:**
```bash
ls checkpoints/
# crnn_ctc_best.pdparams ve charset.txt olmalı
```

## 🚀 Kullanım

### API'yi Başlat

```bash
# Basit başlatma
python api/start_api.py

# Veya doğrudan
cd api
python main.py
```

### Web Arayüzü

Tarayıcıda `http://localhost:8000` adresine gidin.

### API Endpoint'leri

#### 1. Health Check
```bash
GET /health
```

#### 2. Reçete Analizi
```bash
POST /analyze-prescription
Content-Type: multipart/form-data

file: [reçete görseli]
user_question: "Bu reçetedeki ilaçları listele"
use_ocr_fallback: true
```

#### 3. Sadece Metin Çıkarımı
```bash
POST /extract-text
Content-Type: multipart/form-data

file: [görsel]
use_ocr: true
```

## 📊 Response Formatı

### Reçete Analizi Response
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

## 🧪 Test

```bash
# API testleri
python api/test_api.py
```

## 🔧 Yapılandırma

### Environment Variables
- `OPENAI_API_KEY`: OpenAI API anahtarı
- `OPENAI_MODEL`: Kullanılacak model (varsayılan: gpt-4-vision-preview)

### Model Ayarları
- OCR modeli: `checkpoints/crnn_ctc_best.pdparams`
- Karakter seti: `checkpoints/charset.txt`

## 📁 Dosya Yapısı

```
api/
├── main.py              # FastAPI ana uygulama
├── ocr_service.py       # OCR servisi
├── openai_service.py    # OpenAI entegrasyonu
├── start_api.py         # API başlatma scripti
├── test_api.py          # Test scripti
├── static/
│   └── index.html       # Web arayüzü
└── README.md           # Bu dosya
```

## 🚨 Sorun Giderme

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
- Görsel kalitesi yeterli olmalı

## 🔒 Güvenlik

- Production'da CORS ayarlarını kısıtlayın
- API key'leri environment variable'da saklayın
- Dosya yükleme limitlerini ayarlayın

## 📈 Performans

- OCR: ~1-2 saniye
- OpenAI analizi: ~3-5 saniye
- Toplam işlem süresi: ~5-7 saniye

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Pull request gönderin
