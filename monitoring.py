#!/usr/bin/env python3
"""
Hüner AI Assistant Eğitim Sistemi Monitoring
Profesyonel monitoring ve alerting sistemi
"""

import os
import json
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class TrainingMonitor:
    def __init__(self):
        """Monitoring sistemi başlatır"""
        # Supabase
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_KEY')
        self.supabase: Client = create_client(url, key)
        
        # Monitoring ayarları
        self.alert_thresholds = {
            'min_success_rate': 60.0,
            'min_daily_feedback': 3,
            'max_error_rate': 30.0,
            'min_weekly_feedback': 20
        }
        
        # Alert ayarları
        self.email_config = {
            'enabled': os.getenv('ALERT_EMAIL_ENABLED', 'false').lower() == 'true',
            'smtp_server': os.getenv('ALERT_SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('ALERT_SMTP_PORT', '587')),
            'username': os.getenv('ALERT_EMAIL_USER'),
            'password': os.getenv('ALERT_EMAIL_PASS'),
            'to_email': os.getenv('ALERT_TO_EMAIL')
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Sistem sağlığını kontrol eder"""
        try:
            # Son 7 günün verilerini çek
            cutoff_date = datetime.now() - timedelta(days=7)
            response = self.supabase.table('feedback').select('*').gte('olusturma_zamani', cutoff_date.isoformat()).execute()
            feedback_data = response.data
            
            if not feedback_data:
                return {
                    'status': 'warning',
                    'message': 'Son 7 günde feedback verisi bulunamadı',
                    'metrics': {}
                }
            
            # Metrikleri hesapla
            total_feedback = len(feedback_data)
            positive_feedback = sum(1 for f in feedback_data if f.get('geri_bildirim') == 'dogru')
            negative_feedback = sum(1 for f in feedback_data if f.get('geri_bildirim') == 'yanlis')
            
            success_rate = (positive_feedback / total_feedback) * 100 if total_feedback > 0 else 0
            error_rate = (negative_feedback / total_feedback) * 100 if total_feedback > 0 else 0
            
            # Günlük dağılım
            daily_stats = {}
            for feedback in feedback_data:
                date = feedback['olusturma_zamani'][:10]
                if date not in daily_stats:
                    daily_stats[date] = {'total': 0, 'positive': 0, 'negative': 0}
                
                daily_stats[date]['total'] += 1
                if feedback.get('geri_bildirim') == 'dogru':
                    daily_stats[date]['positive'] += 1
                else:
                    daily_stats[date]['negative'] += 1
            
            # Sağlık durumu belirle
            health_status = 'healthy'
            issues = []
            
            if success_rate < self.alert_thresholds['min_success_rate']:
                health_status = 'critical'
                issues.append(f"Başarı oranı çok düşük: %{success_rate:.1f}")
            
            if total_feedback < self.alert_thresholds['min_weekly_feedback']:
                health_status = 'warning' if health_status == 'healthy' else health_status
                issues.append(f"Haftalık feedback yetersiz: {total_feedback}")
            
            if error_rate > self.alert_thresholds['max_error_rate']:
                health_status = 'critical'
                issues.append(f"Hata oranı çok yüksek: %{error_rate:.1f}")
            
            return {
                'status': health_status,
                'message': '; '.join(issues) if issues else 'Sistem sağlıklı',
                'metrics': {
                    'total_feedback': total_feedback,
                    'positive_feedback': positive_feedback,
                    'negative_feedback': negative_feedback,
                    'success_rate': success_rate,
                    'error_rate': error_rate,
                    'daily_stats': daily_stats,
                    'period_days': len(daily_stats)
                }
            }
            
        except Exception as e:
            return {
                'status': 'critical',
                'message': f'Monitoring hatası: {str(e)}',
                'metrics': {}
            }
    
    def send_alert(self, health_data: Dict[str, Any]):
        """Alert gönderir"""
        if not self.email_config['enabled']:
            print("📧 Email alerting devre dışı")
            return
        
        try:
            # Email içeriği oluştur
            subject = f"🚨 Hüner AI Assistant Alert - {health_data['status'].upper()}"
            
            body = f"""
Hüner AI Assistant Eğitim Sistemi Alert

Durum: {health_data['status'].upper()}
Mesaj: {health_data['message']}
Zaman: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Metrikler:
"""
            
            if health_data['metrics']:
                metrics = health_data['metrics']
                body += f"""
- Toplam Feedback: {metrics.get('total_feedback', 0)}
- Pozitif Feedback: {metrics.get('positive_feedback', 0)}
- Negatif Feedback: {metrics.get('negative_feedback', 0)}
- Başarı Oranı: %{metrics.get('success_rate', 0):.1f}
- Hata Oranı: %{metrics.get('error_rate', 0):.1f}
- Analiz Periyodu: {metrics.get('period_days', 0)} gün
"""
            
            body += f"""

Günlük İstatistikler:
"""
            
            if health_data['metrics'].get('daily_stats'):
                for date, stats in health_data['metrics']['daily_stats'].items():
                    daily_success = (stats['positive'] / stats['total']) * 100 if stats['total'] > 0 else 0
                    body += f"- {date}: {stats['total']} feedback, %{daily_success:.1f} başarı\n"
            
            body += f"""

Bu alert otomatik olarak gönderilmiştir.
Hüner AI Assistant Eğitim Sistemi
"""
            
            # Email gönder
            msg = MIMEMultipart()
            msg['From'] = self.email_config['username']
            msg['To'] = self.email_config['to_email']
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            text = msg.as_string()
            server.sendmail(self.email_config['username'], self.email_config['to_email'], text)
            server.quit()
            
            print(f"📧 Alert gönderildi: {health_data['status']}")
            
        except Exception as e:
            print(f"❌ Email gönderilemedi: {e}")
    
    def generate_report(self) -> str:
        """Detaylı rapor oluşturur"""
        health_data = self.get_system_health()
        
        report = f"""
# Hüner AI Assistant Eğitim Sistemi Raporu
**Tarih:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🎯 Sistem Durumu
**Durum:** {health_data['status'].upper()}
**Mesaj:** {health_data['message']}

## 📊 Metrikler
"""
        
        if health_data['metrics']:
            metrics = health_data['metrics']
            report += f"""
- **Toplam Feedback:** {metrics.get('total_feedback', 0)}
- **Pozitif Feedback:** {metrics.get('positive_feedback', 0)}
- **Negatif Feedback:** {metrics.get('negative_feedback', 0)}
- **Başarı Oranı:** %{metrics.get('success_rate', 0):.1f}
- **Hata Oranı:** %{metrics.get('error_rate', 0):.1f}
- **Analiz Periyodu:** {metrics.get('period_days', 0)} gün

## 📈 Günlük İstatistikler
"""
            
            if metrics.get('daily_stats'):
                for date, stats in sorted(metrics['daily_stats'].items()):
                    daily_success = (stats['positive'] / stats['total']) * 100 if stats['total'] > 0 else 0
                    report += f"- **{date}:** {stats['total']} feedback, %{daily_success:.1f} başarı\n"
        
        report += f"""

## ⚠️ Alert Eşikleri
- **Minimum Başarı Oranı:** %{self.alert_thresholds['min_success_rate']:.1f}
- **Minimum Haftalık Feedback:** {self.alert_thresholds['min_weekly_feedback']}
- **Maksimum Hata Oranı:** %{self.alert_thresholds['max_error_rate']:.1f}

## 🔧 Öneriler
"""
        
        if health_data['status'] == 'critical':
            report += """
- **ACİL:** Sistem performansı kritik seviyede
- Feedback kalitesini artırın
- Assistant instructions'ını gözden geçirin
- Daha fazla test verisi toplayın
"""
        elif health_data['status'] == 'warning':
            report += """
- Sistem performansı düşük
- Feedback sayısını artırın
- Eğitim sıklığını kontrol edin
"""
        else:
            report += """
- Sistem sağlıklı çalışıyor
- Mevcut performansı koruyun
- Düzenli monitoring yapın
"""
        
        return report
    
    def run_monitoring(self):
        """Ana monitoring fonksiyonu"""
        print("🔍 Hüner AI Assistant Monitoring başlatılıyor...")
        
        # Sistem sağlığını kontrol et
        health_data = self.get_system_health()
        
        print(f"📊 Sistem Durumu: {health_data['status'].upper()}")
        print(f"📝 Mesaj: {health_data['message']}")
        
        # Alert gönder (gerekirse)
        if health_data['status'] in ['critical', 'warning']:
            self.send_alert(health_data)
        
        # Rapor oluştur
        report = self.generate_report()
        
        # Raporu kaydet
        report_file = f"monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Rapor kaydedildi: {report_file}")
        
        return health_data

def main():
    """Ana fonksiyon"""
    try:
        monitor = TrainingMonitor()
        health_data = monitor.run_monitoring()
        
        # Exit code belirle
        if health_data['status'] == 'critical':
            exit(2)
        elif health_data['status'] == 'warning':
            exit(1)
        else:
            exit(0)
            
    except Exception as e:
        print(f"❌ Monitoring hatası: {e}")
        exit(3)

if __name__ == "__main__":
    main()
