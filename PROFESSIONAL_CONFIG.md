# Hüner AI Assistant Profesyonel Konfigürasyon Rehberi
# Environment variables ve sistem ayarları

## 🔧 Temel Konfigürasyon

### OpenAI Ayarları
```bash
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
OPENAI_ASSISTANT_ID=asst_your-assistant-id-here
```

### Supabase Ayarları
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-key-here
```

### Django Ayarları
```bash
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-domain.com
```

## 🤖 Eğitim Sistemi Konfigürasyonu

### Eğitim Parametreleri
```bash
# Minimum feedback sayısı (eğitim tetikleme için)
TRAINING_MIN_FEEDBACK=5

# Başarı oranı eşiği (%)
TRAINING_SUCCESS_THRESHOLD=70.0

# Analiz periyodu (gün)
TRAINING_ANALYSIS_DAYS=7

# Otomatik güncelleme
TRAINING_AUTO_UPDATE=True
```

### Monitoring Ayarları
```bash
# Monitoring sistemi
MONITORING_ENABLED=True
MONITORING_MIN_SUCCESS_RATE=60.0
MONITORING_MIN_DAILY_FEEDBACK=3
MONITORING_MAX_ERROR_RATE=30.0
MONITORING_MIN_WEEKLY_FEEDBACK=20
```

## 📧 Alert Sistemi Konfigürasyonu

### Email Alerting
```bash
# Email alerting aktif/pasif
ALERT_EMAIL_ENABLED=True

# SMTP ayarları
ALERT_SMTP_SERVER=smtp.gmail.com
ALERT_SMTP_PORT=587
ALERT_EMAIL_USER=your-email@gmail.com
ALERT_EMAIL_PASS=your-app-password
ALERT_TO_EMAIL=admin@your-domain.com
```

### Slack Entegrasyonu
```bash
INTEGRATION_SLACK_ENABLED=True
INTEGRATION_SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/webhook/url
```

## ⏰ Cron Job Konfigürasyonu

### Zamanlama Ayarları
```bash
# Cron job aktif/pasif
CRON_ENABLED=True

# Zamanlama (her gün saat 09:00)
CRON_SCHEDULE="0 9 * * *"

# Log seviyesi
CRON_LOG_LEVEL=INFO

# Maksimum deneme sayısı
CRON_MAX_RETRIES=3

# Deneme aralığı (saniye)
CRON_RETRY_DELAY=300
```

## 🔒 Güvenlik Konfigürasyonu

### SSL ve HTTPS
```bash
# SSL yönlendirme
SSL_REDIRECT=True

# HSTS ayarları
HSTS_SECONDS=31536000
HSTS_INCLUDE_SUBDOMAINS=True
HSTS_PRELOAD=True

# Cookie güvenliği
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
CSRF_COOKIE_SECURE=True
```

### CORS Ayarları
```bash
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

## 📊 Performans Konfigürasyonu

### API Timeout Ayarları
```bash
# OpenAI API timeout (saniye)
OPENAI_TIMEOUT=120

# Supabase API timeout (saniye)
SUPABASE_TIMEOUT=30
```

### Rate Limiting
```bash
# Rate limiting aktif/pasif
RATE_LIMIT_ENABLED=True

# Dakika başına istek
RATE_LIMIT_REQUESTS_PER_MINUTE=60

# Saat başına istek
RATE_LIMIT_REQUESTS_PER_HOUR=1000

# Burst boyutu
RATE_LIMIT_BURST_SIZE=10
```

### Cache Ayarları
```bash
# Cache aktif/pasif
CACHE_ENABLED=True

# Cache TTL (saniye)
CACHE_TTL_SECONDS=3600

# Maksimum cache boyutu (MB)
CACHE_MAX_SIZE_MB=100
```

## 📝 Logging Konfigürasyonu

### Log Seviyeleri
```bash
# Log seviyesi (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Maksimum log dosyası boyutu (MB)
LOG_MAX_SIZE_MB=10

# Log saklama süresi (gün)
LOG_RETENTION_DAYS=30
```

## 🔄 Backup Konfigürasyonu

### Otomatik Backup
```bash
# Backup aktif/pasif
BACKUP_ENABLED=True

# Backup zamanlaması (her gün saat 02:00)
BACKUP_SCHEDULE="0 2 * * *"

# Backup saklama süresi (gün)
BACKUP_RETENTION_DAYS=7
```

## 🎛️ Özellik Bayrakları

### Feature Flags
```bash
# Otomatik eğitim
FEATURE_AUTO_TRAINING=True

# Monitoring sistemi
FEATURE_MONITORING=True

# Alert sistemi
FEATURE_ALERTING=True

# Backup sistemi
FEATURE_BACKUP=True

# Analytics
FEATURE_ANALYTICS=True

# Feedback UI
FEATURE_FEEDBACK_UI=True
```

## 🔍 Health Check Konfigürasyonu

### Sistem Sağlık Kontrolü
```bash
# Health check aktif/pasif
HEALTH_CHECK_ENABLED=True

# Kontrol aralığı (saniye)
HEALTH_CHECK_INTERVAL_SECONDS=300

# Timeout (saniye)
HEALTH_CHECK_TIMEOUT_SECONDS=30

# Deneme sayısı
HEALTH_CHECK_RETRIES=3
```

## 🛠️ Bakım Modu

### Bakım Ayarları
```bash
# Bakım modu aktif/pasif
MAINTENANCE_MODE=False

# Bakım mesajı
MAINTENANCE_MESSAGE="Sistem bakımda. Lütfen daha sonra tekrar deneyin."

# Bakım sırasında erişim izni olan IP'ler
MAINTENANCE_ALLOWED_IPS=127.0.0.1,::1
```

## 🎨 Özelleştirme

### Branding Ayarları
```bash
# Özel tema
CUSTOM_THEME=huner-ai

# Özel branding
CUSTOM_BRANDING=True

# Logo URL
CUSTOM_LOGO_URL=/static/huner_ai.png

# Favicon URL
CUSTOM_FAVICON_URL=/static/favicon.ico
```

## 🧪 Deneysel Özellikler

### Experimental Features
```bash
# Deneysel özellikler aktif/pasif
EXPERIMENTAL_FEATURES_ENABLED=False

# AI model
EXPERIMENTAL_AI_MODEL=gpt-4-turbo

# Fine-tuning
EXPERIMENTAL_FINE_TUNING=False

# Vector database
EXPERIMENTAL_VECTOR_DB=False

# Real-time training
EXPERIMENTAL_REAL_TIME_TRAINING=False
```

## 📋 Kurulum Adımları

### 1. Environment Dosyası Oluştur
```bash
# .env dosyasını oluştur
cp .env.professional .env

# Gerekli değerleri doldur
nano .env
```

### 2. Güvenlik Kontrolü
```bash
# Dosya izinlerini kontrol et
chmod 600 .env

# .gitignore kontrolü
grep -q ".env" .gitignore || echo ".env" >> .gitignore
```

### 3. Sistem Testi
```bash
# Konfigürasyon testi
python test_training_system.py

# Eğitim sistemi testi
python simple_training.py

# Monitoring testi
python monitoring.py
```

### 4. Cron Job Kurulumu
```bash
# Cron job yöneticisini çalıştır
chmod +x cron_manager.sh
./cron_manager.sh
```

## ⚠️ Güvenlik Notları

1. **API Anahtarları**: Asla public repository'de paylaşmayın
2. **Service Key**: Sadece güvenilir ortamlarda kullanın
3. **SSL**: Production'da mutlaka HTTPS kullanın
4. **Backup**: Düzenli backup alın
5. **Monitoring**: Sistem durumunu sürekli izleyin

## 🔧 Sorun Giderme

### Yaygın Sorunlar
1. **Cron job çalışmıyor**: Script izinlerini kontrol edin
2. **API hatası**: Anahtarları kontrol edin
3. **Log dosyası büyük**: Log rotation ayarlayın
4. **Email gönderilmiyor**: SMTP ayarlarını kontrol edin

### Debug Komutları
```bash
# Cron job durumu
crontab -l

# Log kontrolü
tail -f training.log

# Sistem testi
python test_training_system.py

# Monitoring
python monitoring.py
```

Bu konfigürasyon ile Hüner AI Assistant sisteminiz tam profesyonel seviyede çalışacak! 🚀
