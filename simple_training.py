#!/usr/bin/env python3
"""
Feedback verilerini kullanarak otomatik eğitim sistemi (Schedule olmadan)
Tek seferlik çalıştırma için optimize edilmiş
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from supabase import create_client, Client
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class SimpleTrainingSystem:
    def __init__(self):
        """Sistem bileşenlerini başlatır"""
        # Supabase
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_KEY')
        self.supabase: Client = create_client(url, key)
        
        # OpenAI
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.assistant_id = os.getenv('OPENAI_ASSISTANT_ID')
    
    def get_recent_feedback(self, days: int = 7) -> List[Dict[str, Any]]:
        """Son N günün feedback verilerini çeker"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            response = self.supabase.table('feedback').select('*').gte('olusturma_zamani', cutoff_date.isoformat()).execute()
            return response.data
        except Exception as e:
            print(f"Feedback verileri çekilemedi: {e}")
            return []
    
    def analyze_performance_trends(self, feedback_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Performans trendlerini analiz eder"""
        if not feedback_data:
            return {}
        
        # Günlük başarı oranları
        daily_performance = {}
        for feedback in feedback_data:
            date = feedback['olusturma_zamani'][:10]  # YYYY-MM-DD
            if date not in daily_performance:
                daily_performance[date] = {'total': 0, 'positive': 0}
            
            daily_performance[date]['total'] += 1
            if feedback.get('geri_bildirim') == 'dogru':
                daily_performance[date]['positive'] += 1
        
        # Başarı oranlarını hesapla
        for date in daily_performance:
            total = daily_performance[date]['total']
            positive = daily_performance[date]['positive']
            daily_performance[date]['success_rate'] = (positive / total) * 100 if total > 0 else 0
        
        # Genel istatistikler
        total_feedback = len(feedback_data)
        positive_feedback = sum(1 for f in feedback_data if f.get('geri_bildirim') == 'dogru')
        overall_success_rate = (positive_feedback / total_feedback) * 100 if total_feedback > 0 else 0
        
        return {
            'total_feedback': total_feedback,
            'positive_feedback': positive_feedback,
            'overall_success_rate': overall_success_rate,
            'daily_performance': daily_performance,
            'period_days': len(daily_performance),
            'feedback_data': feedback_data  # Dinamik analiz için eklendi
        }
    
    def should_trigger_training(self, analysis: Dict[str, Any]) -> Tuple[bool, str]:
        """Eğitim tetiklenmeli mi kontrol eder"""
        if not analysis:
            return False, "Analiz verisi yok"
        
        success_rate = analysis['overall_success_rate']
        total_feedback = analysis['total_feedback']
        
        # Minimum feedback sayısı kontrolü
        if total_feedback < 5:
            return False, f"Yetersiz feedback ({total_feedback} < 5)"
        
        # Başarı oranı kontrolü
        if success_rate < 70:
            return True, f"Düşük başarı oranı (%{success_rate:.1f} < %70)"
        
        return False, f"Performans yeterli (%{success_rate:.1f})"
    
    def update_assistant_instructions(self, analysis: Dict[str, Any]) -> bool:
        """Assistant'ın system instructions'ını günceller"""
        try:
            # Mevcut instructions'ı al
            assistant = self.openai_client.beta.assistants.retrieve(self.assistant_id)
            current_instructions = assistant.instructions or ""
            
            # Yeni instructions oluştur
            new_instructions = self._generate_improved_instructions(current_instructions, analysis)
            
            # Assistant'ı güncelle
            self.openai_client.beta.assistants.update(
                assistant_id=self.assistant_id,
                instructions=new_instructions
            )
            
            print("✅ Assistant instructions güncellendi!")
            return True
            
        except Exception as e:
            print(f"❌ Assistant güncellenemedi: {e}")
            return False
    
    def _generate_improved_instructions(self, current: str, analysis: Dict[str, Any]) -> str:
        """Feedback analizine göre dinamik instructions oluşturur"""
        base_instructions = """Sen Türk sağlık mevzuatına göre tıbbi raporları değerlendiren bir uzmansın. 
Gelen raporları şu kriterlere göre değerlendir:
- ICD kodlarının doğruluğu
- İlaç dozajlarının uygunluğu  
- Tanı-tedavi uyumluluğu
- Mevzuata uygunluk
- Eksik bilgilerin tespiti

Değerlendirme sonucunu detaylı ve yapıcı bir şekilde sun."""

        # Dinamik iyileştirmeler
        improvements = []
        
        # Başarı oranına göre genel uyarı
        success_rate = analysis.get('overall_success_rate', 0)
        if success_rate < 70:
            improvements.append(f"""
DİKKAT: Mevcut başarı oranı %{success_rate:.1f}. Daha dikkatli ve kapsamlı değerlendirme yap.""")
        
        # Feedback verilerinden dinamik talimatlar üret
        feedback_data = analysis.get('feedback_data', [])
        if feedback_data:
            # Negatif feedback'leri analiz et
            negative_feedback = [f for f in feedback_data if f.get('geri_bildirim') == 'yanlis']
            
            if negative_feedback:
                # Hata türlerini say
                error_patterns = {}
                for feedback in negative_feedback:
                    reason = feedback.get('neden', '')
                    if reason:
                        error_patterns[reason] = error_patterns.get(reason, 0) + 1
                
                # En yaygın hatalara göre özel talimatlar
                if error_patterns:
                    improvements.append("\nYAYGIN HATALAR VE ÇÖZÜMLERİ:")
                    
                    for error, count in sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)[:3]:
                        if error == 'Yanlış tanı-eşleşme':
                            improvements.append(f"""
• TANI KODLARI ({count} kez hata): ICD kodları ile tanı açıklamaları arasındaki uyumu mutlaka kontrol et.""")
                        elif error == 'Doz/şema hatası':
                            improvements.append(f"""
• DOZAJ HATALARI ({count} kez hata): İlaç dozajlarını SUT/SGK mevzuatına göre kontrol et.""")
                        elif error == 'Mevzuat dayanağı eksik':
                            improvements.append(f"""
• MEVZUAT EKSİKLİĞİ ({count} kez hata): Her değerlendirmende SUT/SGK mevzuatına dayalı gerekçelendirme sağla.""")
                        elif error == 'Eksik bilgi gözardı':
                            improvements.append(f"""
• EKSİK BİLGİ ({count} kez hata): Raporda eksik olan kritik bilgileri mutlaka tespit et ve belirt.""")
                        elif error == 'Dil/format sorunları':
                            improvements.append(f"""
• FORMAT SORUNLARI ({count} kez hata): Değerlendirmeni net, anlaşılır ve profesyonel bir dille yaz.""")
        
        # Genel durum bilgisi
        total_feedback = analysis.get('total_feedback', 0)
        if total_feedback > 0:
            improvements.append(f"\nGENEL DURUM: Son {total_feedback} feedback analiz edildi.")
            
            if success_rate < 50:
                improvements.append("ACİL: Performans kritik seviyede. Tüm kontrolleri sıkılaştır.")
            elif success_rate < 70:
                improvements.append("DİKKAT: Performans düşük. Daha dikkatli değerlendirme yap.")
            else:
                improvements.append("BAŞARI: Performans iyi. Mevcut yaklaşımı sürdür.")
        
        # Tüm iyileştirmeleri birleştir
        if improvements:
            return base_instructions + "\n".join(improvements)
        else:
            return base_instructions
    
    def daily_training_check(self):
        """Günlük eğitim kontrolü"""
        print(f"\n=== Otomatik Eğitim Kontrolü - {datetime.now().strftime('%Y-%m-%d %H:%M')} ===")
        
        # Son 7 günün feedback verilerini çek
        feedback_data = self.get_recent_feedback(days=7)
        
        if not feedback_data:
            print("Son 7 günde feedback verisi bulunamadı.")
            return
        
        # Performans analizi
        analysis = self.analyze_performance_trends(feedback_data)
        
        # Eğitim gerekli mi?
        should_train, reason = self.should_trigger_training(analysis)
        
        print(f"Toplam feedback: {analysis['total_feedback']}")
        print(f"Başarı oranı: %{analysis['overall_success_rate']:.1f}")
        print(f"Eğitim gerekli: {'Evet' if should_train else 'Hayır'}")
        print(f"Sebep: {reason}")
        
        if should_train:
            print("\n🔄 Assistant instructions güncelleniyor...")
            if self.update_assistant_instructions(analysis):
                print("✅ Eğitim tamamlandı!")
            else:
                print("❌ Eğitim başarısız!")
        else:
            print("\n✅ Performans yeterli, güncelleme gerekmiyor.")

def main():
    """Ana fonksiyon"""
    try:
        system = SimpleTrainingSystem()
        system.daily_training_check()
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    main()
