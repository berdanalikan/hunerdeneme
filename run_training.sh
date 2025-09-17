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

# Telegram config (optional)
TELEGRAM_ENABLED=${TELEGRAM_ENABLED:-false}
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-}
TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID:-}

send_telegram() {
  local TEXT="$1"
  if [ "$TELEGRAM_ENABLED" = "true" ] && [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d chat_id="${TELEGRAM_CHAT_ID}" \
      -d parse_mode="HTML" \
      --data-urlencode text="$TEXT" >/dev/null 2>&1 || true
  fi
}

# Log başlangıcı
# Mevcut log boyutunu kaydet (sonradan eklenen kısmı Telegram'a göndermek için)
if [ -f "$LOG_FILE" ]; then
  LOG_SIZE_BEFORE=$(wc -c < "$LOG_FILE" 2>/dev/null || echo 0)
else
  LOG_SIZE_BEFORE=0
fi

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
    send_telegram "✅ Hüner AI eğitim tamamlandı\n<b>Zaman:</b> $END_TIME\n<b>Durum:</b> Başarılı"
else
    echo "❌ Eğitim sistemi hata ile sonuçlandı (Exit Code: $EXIT_CODE): $END_TIME" >> "$LOG_FILE"
    send_telegram "❌ Hüner AI eğitim HATA\n<b>Zaman:</b> $END_TIME\n<b>Exit Code:</b> $EXIT_CODE"
fi

# Log'ta bu çalışmada eklenen kısmı Telegram'a gönder
if [ -f "$LOG_FILE" ]; then
  LOG_SIZE_AFTER=$(wc -c < "$LOG_FILE" 2>/dev/null || echo 0)
  if [ "$LOG_SIZE_AFTER" -gt "$LOG_SIZE_BEFORE" ]; then
    BYTES_NEW=$((LOG_SIZE_AFTER - LOG_SIZE_BEFORE))
    NEW_CONTENT=$(tail -c $BYTES_NEW "$LOG_FILE" 2>/dev/null || true)
    # Uzunsa kırp (Telegram ~4096 limit). 3500 char yeterli.
    NEW_TRIMMED=$(printf "%s" "$NEW_CONTENT" | tail -c 3500)
    # HTML escape
    ESCAPED=$(printf "%s" "$NEW_TRIMMED" | sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g')
    send_telegram "📒 Log güncellemesi (son çalıştırma):\n<pre>$ESCAPED</pre>"
  fi
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
