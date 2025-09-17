#!/bin/bash
# Hüner AI Assistant Otomatik Eğitim Scripti
# Profesyonel cron job için optimize edilmiş

# Script başlangıç zamanı
START_TIME=$(date '+%Y-%m-%d %H:%M:%S')

# Proje dizinine git
cd /Users/berdanalikan/Desktop/hunerdeneme

# Log dosyası
LOG_FILE="/Users/berdanalikan/Desktop/hunerdeneme/training.log"

# Python path'i ayarla
export PATH="/Library/Frameworks/Python.framework/Versions/3.12/bin:$PATH"

# Log başlangıcı
echo "===========================================" >> "$LOG_FILE"
echo "🚀 Hüner AI Assistant Eğitim Başlatıldı (12s periyodik): $START_TIME" >> "$LOG_FILE"
echo "===========================================" >> "$LOG_FILE"

# Sistem kontrolü
echo "🔍 Sistem kontrolü yapılıyor..." >> "$LOG_FILE"
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 bulunamadı!" >> "$LOG_FILE"
    exit 1
fi

if [ ! -f "simple_training.py" ]; then
    echo "❌ simple_training.py bulunamadı!" >> "$LOG_FILE"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "❌ .env dosyası bulunamadı!" >> "$LOG_FILE"
    exit 1
fi

echo "✅ Sistem kontrolü başarılı" >> "$LOG_FILE"

# Eğitim sistemini çalıştır
echo "🤖 Otomatik eğitim sistemi başlatılıyor..." >> "$LOG_FILE"
python3 simple_training.py >> "$LOG_FILE" 2>&1

# Dinamik instructions güncelleme (opsiyonel)
echo "🔄 Dinamik instructions kontrolü yapılıyor..." >> "$LOG_FILE"
python3 dynamic_instruction_generator.py >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

# Sonuç kontrolü
END_TIME=$(date '+%Y-%m-%d %H:%M:%S')
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Eğitim sistemi başarıyla tamamlandı: $END_TIME" >> "$LOG_FILE"
else
    echo "❌ Eğitim sistemi hata ile sonuçlandı (Exit Code: $EXIT_CODE): $END_TIME" >> "$LOG_FILE"
fi

echo "===========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Log dosyası boyut kontrolü (max 10MB)
if [ -f "$LOG_FILE" ]; then
    LOG_SIZE=$(stat -f%z "$LOG_FILE" 2>/dev/null || echo "0")
    if [ "$LOG_SIZE" -gt 10485760 ]; then
        echo "📝 Log dosyası çok büyük, temizleniyor..." >> "$LOG_FILE"
        tail -n 1000 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"
    fi
fi

exit $EXIT_CODE
