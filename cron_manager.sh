#!/bin/bash
# Hüner AI Assistant Cron Job Yönetim Sistemi
# Profesyonel cron job kurulum ve yönetimi

PROJECT_DIR="/Users/berdanalikan/Desktop/hunerdeneme"
SCRIPT_NAME="run_training.sh"
MONITORING_SCRIPT="monitoring.py"

# Renkli çıktı için
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logo
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                HÜNER AI ASSISTANT                          ║"
echo "║              CRON JOB YÖNETİM SİSTEMİ                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Fonksiyonlar
show_menu() {
    echo -e "\n${YELLOW}📋 MENÜ:${NC}"
    echo "1. 🔧 Cron Job Kur"
    echo "2. 📊 Cron Job Durumunu Kontrol Et"
    echo "3. 🗑️  Cron Job Kaldır"
    echo "4. 📝 Log Dosyalarını Görüntüle"
    echo "5. 🔍 Sistem Testi Yap"
    echo "6. 📈 Monitoring Raporu Oluştur"
    echo "7. ⚙️  Cron Job Ayarlarını Düzenle"
    echo "8. ❌ Çıkış"
    echo -e "\n${BLUE}Seçiminizi yapın (1-8):${NC} "
}

install_cron() {
    echo -e "\n${GREEN}🔧 Cron Job Kurulumu Başlatılıyor...${NC}"
    
    # Script dosyasının varlığını kontrol et
    if [ ! -f "$PROJECT_DIR/$SCRIPT_NAME" ]; then
        echo -e "${RED}❌ Script dosyası bulunamadı: $PROJECT_DIR/$SCRIPT_NAME${NC}"
        return 1
    fi
    
    # Script'i executable yap
    chmod +x "$PROJECT_DIR/$SCRIPT_NAME"
    
    # Cron job'ı ekle
    CRON_JOB="0 */12 * * * $PROJECT_DIR/$SCRIPT_NAME"
    
    # Mevcut cron job'ları kontrol et
    if crontab -l 2>/dev/null | grep -q "$SCRIPT_NAME"; then
        echo -e "${YELLOW}⚠️  Cron job zaten mevcut!${NC}"
        echo -e "${BLUE}Mevcut cron job:${NC}"
        crontab -l | grep "$SCRIPT_NAME"
        echo -e "\n${YELLOW}Yeniden kurmak istiyor musunuz? (y/n):${NC} "
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            remove_cron
        else
            return 0
        fi
    fi
    
    # Yeni cron job ekle
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Cron job başarıyla kuruldu!${NC}"
        echo -e "${BLUE}📅 Çalışma Zamanı:${NC} 12 saatte bir (00:00, 12:00)"
        echo -e "${BLUE}📁 Script:${NC} $PROJECT_DIR/$SCRIPT_NAME"
        echo -e "${BLUE}📝 Log:${NC} $PROJECT_DIR/training.log"
    else
        echo -e "${RED}❌ Cron job kurulamadı!${NC}"
        return 1
    fi
}

check_cron_status() {
    echo -e "\n${GREEN}📊 Cron Job Durumu Kontrol Ediliyor...${NC}"
    
    # Cron job'ları listele
    echo -e "${BLUE}📋 Mevcut Cron Job'lar:${NC}"
    if crontab -l 2>/dev/null | grep -q "$SCRIPT_NAME"; then
        echo -e "${GREEN}✅ Hüner AI Assistant cron job aktif${NC}"
        crontab -l | grep "$SCRIPT_NAME"
        
        # Son çalışma zamanını kontrol et
        if [ -f "$PROJECT_DIR/training.log" ]; then
            echo -e "\n${BLUE}📝 Son Log Girişleri:${NC}"
            tail -n 5 "$PROJECT_DIR/training.log"
        else
            echo -e "${YELLOW}⚠️  Log dosyası henüz oluşturulmamış${NC}"
        fi
    else
        echo -e "${RED}❌ Hüner AI Assistant cron job bulunamadı${NC}"
    fi
    
    # Sistem durumu
    echo -e "\n${BLUE}🔍 Sistem Durumu:${NC}"
    echo -e "📁 Proje Dizini: $PROJECT_DIR"
    echo -e "🐍 Python3: $(which python3)"
    echo -e "📄 Script: $([ -f "$PROJECT_DIR/$SCRIPT_NAME" ] && echo "✅ Mevcut" || echo "❌ Eksik")"
    echo -e "🔑 .env: $([ -f "$PROJECT_DIR/.env" ] && echo "✅ Mevcut" || echo "❌ Eksik")"
}

remove_cron() {
    echo -e "\n${YELLOW}🗑️  Cron Job Kaldırılıyor...${NC}"
    
    # Cron job'ı kaldır
    crontab -l 2>/dev/null | grep -v "$SCRIPT_NAME" | crontab -
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Cron job başarıyla kaldırıldı!${NC}"
    else
        echo -e "${RED}❌ Cron job kaldırılamadı!${NC}"
        return 1
    fi
}

view_logs() {
    echo -e "\n${GREEN}📝 Log Dosyaları Görüntüleniyor...${NC}"
    
    if [ -f "$PROJECT_DIR/training.log" ]; then
        echo -e "${BLUE}📄 Training Log (Son 20 satır):${NC}"
        tail -n 20 "$PROJECT_DIR/training.log"
        
        echo -e "\n${YELLOW}Log dosyasının tamamını görmek için:${NC}"
        echo "tail -f $PROJECT_DIR/training.log"
    else
        echo -e "${RED}❌ Log dosyası bulunamadı: $PROJECT_DIR/training.log${NC}"
    fi
}

run_system_test() {
    echo -e "\n${GREEN}🔍 Sistem Testi Yapılıyor...${NC}"
    
    cd "$PROJECT_DIR" || exit 1
    
    # Python testi
    echo -e "${BLUE}🐍 Python Testi:${NC}"
    python3 test_training_system.py
    
    # Manuel eğitim testi
    echo -e "\n${BLUE}🤖 Eğitim Sistemi Testi:${NC}"
    python3 simple_training.py
}

generate_monitoring_report() {
    echo -e "\n${GREEN}📈 Monitoring Raporu Oluşturuluyor...${NC}"
    
    cd "$PROJECT_DIR" || exit 1
    
    if [ -f "$MONITORING_SCRIPT" ]; then
        python3 "$MONITORING_SCRIPT"
        echo -e "${GREEN}✅ Monitoring raporu oluşturuldu!${NC}"
    else
        echo -e "${RED}❌ Monitoring script bulunamadı: $MONITORING_SCRIPT${NC}"
    fi
}

edit_cron_settings() {
    echo -e "\n${GREEN}⚙️  Cron Job Ayarları:${NC}"
    echo -e "${BLUE}Mevcut ayar:${NC} 12 saatte bir (00:00, 12:00)"
    echo -e "\n${YELLOW}Yeni zamanlama seçin:${NC}"
    echo "1. 12 saatte bir (00:00 ve 12:00) [varsayılan]"
    echo "2. Her gün saat 09:00"
    echo "3. Her gün saat 12:00"
    echo "4. Her gün saat 18:00"
    echo "5. Haftada 3 kez (Pzt/Çar/Cum 09:00)"
    echo "6. Özel zamanlama"
    echo -e "\n${BLUE}Seçiminizi yapın (1-5):${NC} "
    read -r choice
    
    case $choice in
        1) NEW_CRON="0 */12 * * * $PROJECT_DIR/$SCRIPT_NAME" ;;
        2) NEW_CRON="0 9 * * * $PROJECT_DIR/$SCRIPT_NAME" ;;
        3) NEW_CRON="0 12 * * * $PROJECT_DIR/$SCRIPT_NAME" ;;
        4) NEW_CRON="0 18 * * * $PROJECT_DIR/$SCRIPT_NAME" ;;
        5) NEW_CRON="0 9 * * 1,3,5 $PROJECT_DIR/$SCRIPT_NAME" ;;
        6)
            echo -e "${BLUE}Cron formatı girin (örn: 0 9 * * *):${NC} "
            read -r cron_time
            NEW_CRON="$cron_time $PROJECT_DIR/$SCRIPT_NAME"
            ;;
        *)
            echo -e "${RED}❌ Geçersiz seçim!${NC}"
            return 1
            ;;
    esac
    
    # Mevcut cron job'ı kaldır
    crontab -l 2>/dev/null | grep -v "$SCRIPT_NAME" | crontab -
    
    # Yeni cron job ekle
    (crontab -l 2>/dev/null; echo "$NEW_CRON") | crontab -
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Cron job ayarları güncellendi!${NC}"
        echo -e "${BLUE}Yeni ayar:${NC} $NEW_CRON"
    else
        echo -e "${RED}❌ Cron job ayarları güncellenemedi!${NC}"
    fi
}

# Ana döngü
while true; do
    show_menu
    read -r choice
    
    case $choice in
        1) install_cron ;;
        2) check_cron_status ;;
        3) remove_cron ;;
        4) view_logs ;;
        5) run_system_test ;;
        6) generate_monitoring_report ;;
        7) edit_cron_settings ;;
        8) 
            echo -e "${GREEN}👋 Görüşürüz!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Geçersiz seçim! Lütfen 1-8 arası bir sayı girin.${NC}"
            ;;
    esac
    
    echo -e "\n${YELLOW}Devam etmek için Enter'a basın...${NC}"
    read -r
done
