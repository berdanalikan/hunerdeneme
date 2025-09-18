# Tıbbi Rapor Değerlendirme Sistemi

Bu sistem, ham tıbbi rapor/reçete metnini parse ederek yapılandırılmış veriye dönüştürür ve OpenAI Assistant API'sine göndererek mevzuata uygunluk değerlendirmesi yapar.

## Özellikler

- Ham rapor metnini yapılandırılmış JSON formatına dönüştürme
- Rapor bilgileri, tanılar, doktor bilgileri ve ilaç bilgilerini ayrıştırma
- OpenAI Assistant API ile mevzuata uygunluk değerlendirmesi
- JSON formatında sonuç kaydetme

## Kurulum

### 1. Gerekli Paketleri Yükleyin
```bash
pip install -r requirements.txt
```

### 2. OpenAI Assistant API Kurulumu

#### API Key Alma:
1. [OpenAI Platform](https://platform.openai.com/) adresine gidin
2. Hesabınızla giriş yapın (yoksa kayıt olun)
3. Sol menüden "API Keys" bölümüne gidin
4. "Create new secret key" butonuna tıklayın
5. Key'inizi kopyalayın ve güvenli bir yerde saklayın

#### Assistant Oluşturma:
1. Sol menüden "Assistants" bölümüne gidin
2. "Create" butonuna tıklayın
3. Assistant'ınıza bir isim verin (örn: "Tıbbi Rapor Değerlendirici")
4. Instructions kısmına şu talimatları yazın:
```
Sen Türk sağlık mevzuatına göre tıbbi raporları değerlendiren bir uzmansın. 
Gelen raporları şu kriterlere göre değerlendir:
- ICD kodlarının doğruluğu
- İlaç dozajlarının uygunluğu
- Tanı-tedavi uyumluluğu
- Mevzuata uygunluk
- Eksik bilgilerin tespiti

Değerlendirme sonucunu detaylı ve yapıcı bir şekilde sun.
```
5. Model olarak GPT-4'ü seçin
6. "Create" butonuna tıklayın
7. Oluşturulan Assistant'ın ID'sini kopyalayın

### 3. Environment Variables Ayarlama

#### Yöntem 1: .env Dosyası (Önerilen)
```bash
# .env dosyasını düzenleyin
nano .env
```

`.env` dosyasına şu değerleri yazın:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_ASSISTANT_ID=asst-your-assistant-id-here
```

#### Yöntem 2: Environment Variables
```bash
export OPENAI_API_KEY="sk-your-actual-api-key-here"
export OPENAI_ASSISTANT_ID="asst-your-assistant-id-here"
```

### 4. API Bağlantısını Test Etme
```bash
python test_api.py
```

Bu script API bağlantınızı test eder ve Assistant'ınızın çalışıp çalışmadığını kontrol eder.

### 5. Güvenlik
- `.env` dosyası `.gitignore`'da tanımlıdır ve git'e commit edilmez
- API key'inizi asla kod içinde yazmayın
- API key'inizi güvenli bir yerde saklayın

## Kullanım

### Temel Kullanım
```bash
python main.py rapor_dosyasi.txt
```

### Çıktı dosyası belirterek
```bash
python main.py rapor_dosyasi.txt sonuc.json
```

### Demo Modu
```bash
python main.py --demo
```

## Dosya Yapısı

- `models.py`: Veri modelleri (ReportInfo, Diagnosis, Medication, vb.)
- `parser.py`: Ham metni parse eden sınıf
- `openai_client.py`: OpenAI Assistant API client'ı
- `main.py`: Ana script
- `requirements.txt`: Python paket gereksinimleri

## Mimari ve İş Akışları

Detaylı mimari ve uçtan uca iş akış diyagramları için:

- `docs/ARCHITECTURE.md` dosyasını açın (GitHub üzerinde Mermaid diyagramları doğrudan görüntülenir).

## Rapor Formatı

Sistem şu formatları destekler:

### Rapor Bilgileri
- Rapor numarası, tarihi
- Protokol numarası
- Tesis bilgileri
- Kullanıcı bilgileri

### Tanı Bilgileri
- ICD kodları
- Tanı açıklamaları
- Başlangıç/bitiş tarihleri

### Doktor Bilgileri
- Diploma numarası
- Branş bilgileri
- Ad soyad

### İlaç Bilgileri
- İlaç kodu ve adı
- Form ve dozaj bilgileri
- Tedavi şeması

## Çıktı Formatı

Sistem iki tür çıktı üretir:

1. **Yapılandırılmış Rapor**: `*_structured.json`
2. **Değerlendirme Sonucu**: `*_evaluation.json`

## Örnek Kullanım

```python
from parser import MedicalReportParser
from openai_client import MedicalReportAssistantClient

# Rapor metnini parse et
parser = MedicalReportParser()
report = parser.parse(rapor_metni)

# OpenAI Assistant ile değerlendir
client = MedicalReportAssistantClient()
result = client.evaluate_report(report)

print(result['evaluation'])
```

## Hata Ayıklama

- API key ve Assistant ID'nin doğru ayarlandığından emin olun
- Rapor formatının beklenen yapıya uygun olduğunu kontrol edin
- Network bağlantısını kontrol edin

## Uzakta (bilgisayar kapalıyken) zamanlanmış eğitim

Depoda `.github/workflows/train.yml` ile bir GitHub Actions iş akışı eklidir. Bu iş akışı her 12 saatte bir çalışır, modeli eğitir/günceller ve Telegram'a özet gönderir.

1) GitHub Secrets ekleyin (Repo Settings → Secrets and variables → Actions):
   - `OPENAI_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

2) Actions sekmesinden manuel tetikleme de yapabilirsiniz ("Run workflow").

3) `main` dalında çalışırken oluşan değişiklikleri (örn. `instruction_update_history.json`, `training.log`) otomatik commit/push eder.
