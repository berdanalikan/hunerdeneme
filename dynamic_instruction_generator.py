#!/usr/bin/env python3
"""
Tam Dinamik Instructions Generator
Feedback verilerine göre gerçekten dinamik instructions üretir
"""

import os
import json
from typing import List, Dict, Any, Tuple
from supabase import create_client, Client
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

class DynamicInstructionGenerator:
    def __init__(self):
        """Supabase ve OpenAI client'larını başlatır"""
        # Supabase
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_KEY')
        self.supabase: Client = create_client(url, key)
        
        # OpenAI
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.assistant_id = os.getenv('OPENAI_ASSISTANT_ID')
    
    def get_feedback_analysis(self, days: int = 7) -> Dict[str, Any]:
        """Feedback verilerini detaylı analiz eder"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            response = self.supabase.table('feedback').select('*').gte('olusturma_zamani', cutoff_date.isoformat()).execute()
            feedback_data = response.data
        except Exception as e:
            print(f"Feedback verileri çekilemedi: {e}")
            return {}
        
        if not feedback_data:
            return {}
        
        # Detaylı analiz
        analysis = {
            'total_feedback': len(feedback_data),
            'positive_feedback': [],
            'negative_feedback': [],
            'error_patterns': {},
            'success_patterns': {},
            'common_issues': [],
            'success_rate': 0,
            'trend_analysis': {},
            'specific_feedback': []
        }
        
        for feedback in feedback_data:
            if feedback.get('geri_bildirim') == 'dogru':
                analysis['positive_feedback'].append(feedback)
            else:
                analysis['negative_feedback'].append(feedback)
                
                # Negatif feedback detayları
                reason = feedback.get('neden', '')
                comment = feedback.get('neden_aciklama', '')
                
                if reason:
                    analysis['error_patterns'][reason] = analysis['error_patterns'].get(reason, 0) + 1
                # Free-text neden_aciklama içeriğinden detaylı analiz ve kategori çıkarımı
                if comment:
                    lc = str(comment).lower()
                    
                    # Detaylı analiz için spesifik pattern'lar
                    detailed_patterns = [
                        # İlaç-endikasyon eşleşmeleri
                        (['amlodipin', 'norvasc', 'arteriyel hipertansiyon'], 'İlaç-Endikasyon Uyumsuzluğu'),
                        (['metformin', 'diabetes', 'şeker'], 'İlaç-Endikasyon Uyumsuzluğu'),
                        (['statin', 'kolesterol', 'lipid'], 'İlaç-Endikasyon Uyumsuzluğu'),
                        
                        # Mevzuat referansları
                        (['sut', 'sgk', 'mevzuat', 'dayanak', 'kılavuz', 'kilavuz'], 'Mevzuat Dayanağı Eksik'),
                        (['ödenir', 'ödeme', 'kapsam', 'kapsamında'], 'Mevzuat Dayanağı Eksik'),
                        
                        # Tanı kodları
                        (['icd', 'tanı', 'tani', 'kod', 'b18.1', 'i10'], 'Tanı Kodu Hatası'),
                        
                        # Dozaj sorunları
                        (['doz', 'dozaj', 'şema', 'tedavi şema', 'titrasyon', 'mg', 'günde'], 'Dozaj/Şema Hatası'),
                        
                        # Eksik bilgiler
                        (['eksik', 'bilgi eksik', 'belirsiz', 'tamamlanmalı', 'tamamlanmali'], 'Eksik Bilgi'),
                        
                        # Format sorunları
                        (['dil', 'format', 'biçim', 'bicim', 'anlaşılır', 'anlasilir'], 'Format Sorunları'),
                    ]
                    
                    matched = False
                    for keywords, bucket in detailed_patterns:
                        if any(k in lc for k in keywords):
                            analysis['error_patterns'][bucket] = analysis['error_patterns'].get(bucket, 0) + 1
                            matched = True
                    
                    # Eşleşme yoksa genel eksik bilgiye at
                    if not matched:
                        analysis['error_patterns']['Genel Bilgi Eksikliği'] = analysis['error_patterns'].get('Genel Bilgi Eksikliği', 0) + 1
                
                # Spesifik feedback topla - detaylı analiz ile
                specific_entry = {
                    'reason': reason,
                    'comment': comment,
                    'user_input': feedback.get('kullanici_girdisi', '')[:200],  # İlk 200 karakter
                    'assistant_response': feedback.get('asistan_cevabi', '')[:200],
                    'detailed_analysis': self._analyze_specific_feedback(comment, feedback.get('kullanici_girdisi', ''), feedback.get('asistan_cevabi', ''))
                }
                analysis['specific_feedback'].append(specific_entry)
        
        # Pozitif feedback analizi
        for feedback in analysis['positive_feedback']:
            # Başarılı yanıtların özelliklerini analiz et
            response = feedback.get('asistan_cevabi', '')
            if 'mevzuat' in response.lower():
                analysis['success_patterns']['mevzuat_reference'] = analysis['success_patterns'].get('mevzuat_reference', 0) + 1
            if 'icd' in response.lower():
                analysis['success_patterns']['icd_check'] = analysis['success_patterns'].get('icd_check', 0) + 1
            if 'dozaj' in response.lower():
                analysis['success_patterns']['dosage_check'] = analysis['success_patterns'].get('dosage_check', 0) + 1
        
        # Başarı oranı
        analysis['success_rate'] = (len(analysis['positive_feedback']) / len(feedback_data)) * 100 if feedback_data else 0
        
        # En yaygın sorunları belirle
        analysis['common_issues'] = sorted(analysis['error_patterns'].items(), key=lambda x: x[1], reverse=True)
        
        return analysis
    
    def _analyze_specific_feedback(self, comment: str, user_input: str, assistant_response: str) -> Dict[str, Any]:
        """Spesifik feedback'i detaylı analiz eder"""
        analysis = {
            'key_issues': [],
            'suggested_improvements': [],
            'critical_points': [],
            'learning_opportunities': []
        }
        
        if not comment:
            return analysis
        
        comment_lower = comment.lower()
        
        # İlaç-endikasyon analizi
        if any(drug in comment_lower for drug in ['amlodipin', 'norvasc', 'metformin', 'statin']):
            analysis['key_issues'].append('İlaç-endikasyon uyumsuzluğu tespit edildi')
            analysis['suggested_improvements'].append('İlaç-endikasyon eşleştirmelerini SUT kılavuzuna göre kontrol et')
            analysis['critical_points'].append('Mevzuat dayanağı eksikliği kritik hata')
        
        # Mevzuat analizi
        if any(term in comment_lower for term in ['ödenir', 'ödeme', 'kapsam', 'sut', 'sgk']):
            analysis['key_issues'].append('Mevzuat dayanağı eksikliği')
            analysis['suggested_improvements'].append('SUT/SGK mevzuatına dayalı gerekçelendirme sağla')
            analysis['learning_opportunities'].append('Mevzuat referanslarını açık belirt')
        
        # Tanı kodu analizi
        if any(term in comment_lower for term in ['icd', 'tanı', 'kod', 'b18.1', 'i10']):
            analysis['key_issues'].append('Tanı kodu uyumsuzluğu')
            analysis['suggested_improvements'].append('ICD kodları ile tanı açıklamaları arasındaki uyumu kontrol et')
        
        # Dozaj analizi
        if any(term in comment_lower for term in ['doz', 'dozaj', 'mg', 'günde']):
            analysis['key_issues'].append('Dozaj/şema sorunu')
            analysis['suggested_improvements'].append('İlaç dozajlarını SUT kılavuzuna göre kontrol et')
        
        return analysis
    
    def load_last_instructions(self) -> str:
        """Son kaydedilen instructions metnini döndürür (yoksa boş döner)."""
        try:
            history_file = 'instruction_update_history.json'
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f) or []
                if history:
                    return str(history[-1].get('instructions') or '').strip()
        except Exception:
            pass
        return ''

    def generate_dynamic_instructions(self, analysis: Dict[str, Any], previous_instructions: str | None = None) -> str:
        """Feedback analizine göre tamamen dinamik instructions üretir"""
        # Not: Bu yerel (heuristic) üretici, OpenAI tabanlı üretici bulunamazsa geri dönüş olarak kullanılır
        # Temel instructions
        base_instructions = """Sen Türk sağlık mevzuatına göre tıbbi raporları değerlendiren bir uzmansın. 
Gelen raporları şu kriterlere göre değerlendir:
- ICD kodlarının doğruluğu
- İlaç dozajlarının uygunluğu  
- Tanı-tedavi uyumluluğu
- Mevzuata uygunluk
- Eksik bilgilerin tespiti

Değerlendirme sonucunu detaylı ve yapıcı bir şekilde sun."""
        
        if not analysis:
            return base_instructions
        
        # Dinamik iyileştirmeler
        improvements = []
        
        # 1. Başarı oranına göre genel uyarı
        success_rate = analysis.get('success_rate', 0)
        if success_rate < 70:
            improvements.append(f"""
DİKKAT: Mevcut başarı oranı %{success_rate:.1f}. Daha dikkatli ve kapsamlı değerlendirme yap.""")
        
        # 2. En yaygın hatalara göre özel talimatlar
        common_issues = analysis.get('common_issues', [])
        if common_issues:
            improvements.append("\nYAYGIN HATALAR VE ÇÖZÜMLERİ:")
            
            for issue, count in common_issues[:3]:  # En yaygın 3 hata
                if issue == 'Yanlış tanı-eşleşme':
                    improvements.append(f"""
• TANI KODLARI ({count} kez hata): ICD kodları ile tanı açıklamaları arasındaki uyumu mutlaka kontrol et. 
  Kod ve açıklama tutarsızlığı tespit ettiğinde detaylı açıklama yap.""")
                
                elif issue == 'Doz/şema hatası':
                    improvements.append(f"""
• DOZAJ HATALARI ({count} kez hata): İlaç dozajlarını SUT/SGK mevzuatına göre kontrol et.
  Dozaj limitlerini ve tedavi protokollerini dikkatli değerlendir.""")
                
                elif issue == 'Mevzuat dayanağı eksik':
                    improvements.append(f"""
• MEVZUAT EKSİKLİĞİ ({count} kez hata): Her değerlendirmende SUT/SGK mevzuatına dayalı gerekçelendirme sağla.
  Mevzuat referanslarını açık bir şekilde belirt.""")
                
                elif issue == 'Eksik bilgi gözardı':
                    improvements.append(f"""
• EKSİK BİLGİ ({count} kez hata): Raporda eksik olan kritik bilgileri mutlaka tespit et ve belirt.
  Eksik bilgilerin önemini vurgula.""")
                
                elif issue == 'Dil/format sorunları':
                    improvements.append(f"""
• FORMAT SORUNLARI ({count} kez hata): Değerlendirmeni net, anlaşılır ve profesyonel bir dille yaz.
  Formatı tutarlı tut ve yapıcı öneriler sun.""")
        
        # 3. Başarılı pattern'lere göre öneriler
        success_patterns = analysis.get('success_patterns', {})
        if success_patterns:
            improvements.append("\nBAŞARILI YAKLAŞIMLAR:")
            
            if success_patterns.get('mevzuat_reference', 0) > 0:
                improvements.append("• Mevzuat referansları kullanmaya devam et")
            
            if success_patterns.get('icd_check', 0) > 0:
                improvements.append("• ICD kod kontrolünü sürdür")
            
            if success_patterns.get('dosage_check', 0) > 0:
                improvements.append("• Dozaj kontrollerini artır")
        
        # 4. Spesifik feedback'lere göre detaylı talimatlar
        specific_feedback = analysis.get('specific_feedback', [])
        if specific_feedback:
            improvements.append("\nSPESİFİK İYİLEŞTİRME ÖNERİLERİ:")
            
            # Son 3 negatif feedback'i detaylı analiz et
            recent_negative = [f for f in specific_feedback if f['reason']][-3:]
            
            for feedback in recent_negative:
                if feedback['comment']:
                    # Detaylı analiz sonuçlarını kullan
                    detailed_analysis = feedback.get('detailed_analysis', {})
                    
                    # Kritik noktaları vurgula
                    if detailed_analysis.get('critical_points'):
                        for point in detailed_analysis['critical_points']:
                            improvements.append(f"• KRİTİK: {point}")
                    
                    # Öğrenme fırsatlarını belirt
                    if detailed_analysis.get('learning_opportunities'):
                        for opportunity in detailed_analysis['learning_opportunities']:
                            improvements.append(f"• ÖĞRENME: {opportunity}")
                    
                    # Spesifik önerileri ekle
                    if detailed_analysis.get('suggested_improvements'):
                        for suggestion in detailed_analysis['suggested_improvements']:
                            improvements.append(f"• ÖNERİ: {suggestion}")
                    
                    # Orijinal yorumu da ekle (kısaltılmış)
                    improvements.append(f"• ÖRNEK HATA: {feedback['comment'][:80]}...")
        
        # 5. Trend analizi
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
        prior = (previous_instructions or '').strip()
        if not prior:
            base = base_instructions
        else:
            # Önceki sürümün üzerine katmanlı geliştirme: kısa revizyon bölümü ekle
            base = prior
        tail = "\n\n" + ("\n".join(improvements) if improvements else "")
        dynamic_instructions = (base + tail).strip()
        
        return dynamic_instructions
    
    def _mask_text(self, text: str, max_len: int = 600) -> str:
        """Basit PII maskeleme ve kısaltma (TC, protokol, telefon gibi uzun rakam serilerini yıldızla)"""
        try:
            import re
            masked = re.sub(r"\b(\d{6,})\b", lambda m: m.group(1)[:2] + "*" * (len(m.group(1)) - 4) + m.group(1)[-2:], text or "")
            # Fazla uzun metinleri kırp
            if len(masked) > max_len:
                masked = masked[:max_len] + "..."
            return masked
        except Exception:
            return (text or "")[:max_len]

    def _build_openai_prompt(self, analysis: Dict[str, Any], previous_instructions: str) -> list:
        """OpenAI'ya gönderilecek mesajları hazırlar (Chat formatı)."""
        total = analysis.get('total_feedback', 0)
        success_rate = analysis.get('success_rate', 0)
        common_issues = analysis.get('common_issues', [])
        specific = analysis.get('specific_feedback', [])

        # Özet blok
        summary_lines = [
            f"Toplam feedback: {total}",
            f"Başarı oranı: %{success_rate:.1f}",
        ]
        if common_issues:
            summary_lines.append("Yaygın hatalar:")
            for issue, count in common_issues[:5]:
                summary_lines.append(f"- {issue}: {count} kez")

        # Spesifik örnekler (maks 3 adet) - detaylı analiz ile
        examples_lines = ["Negatif feedback örnekleri (maskelenmiş):"]
        for ex in specific[:3]:
            ex_reason = ex.get('reason') or "(belirtilmemiş)"
            ex_comment = self._mask_text(ex.get('comment') or "")
            ex_user = self._mask_text(ex.get('user_input') or "", max_len=300)
            ex_assistant = self._mask_text(ex.get('assistant_response') or "", max_len=300)
            ex_analysis = ex.get('detailed_analysis', {})
            
            examples_lines.append("---")
            examples_lines.append(f"Neden: {ex_reason}")
            if ex_comment:
                examples_lines.append(f"Yorum: {ex_comment}")
            
            # Detaylı analiz sonuçlarını ekle
            if ex_analysis.get('key_issues'):
                examples_lines.append(f"Tespit edilen sorunlar: {', '.join(ex_analysis['key_issues'])}")
            if ex_analysis.get('critical_points'):
                examples_lines.append(f"Kritik noktalar: {', '.join(ex_analysis['critical_points'])}")
            if ex_analysis.get('suggested_improvements'):
                examples_lines.append(f"Önerilen iyileştirmeler: {', '.join(ex_analysis['suggested_improvements'])}")
            
            examples_lines.append(f"Kullanıcı girdisi: {ex_user}")
            examples_lines.append(f"Asistan cevabı: {ex_assistant}")

        user_payload = "\n".join(summary_lines + [""] + examples_lines)

        system_msg = (
            "Rolün: 'Instruction Optimizer'. Görev: Feedback analizine dayanarak bir tıbbi rapor değerlendirme"
            " asistanının system instructions metnini GELİŞTİRMEK. Özellikle 'neden_aciklama' alanındaki detaylı"
            " hata açıklamalarını analiz ederek spesifik iyileştirmeler öner. Yapı konusunda SERBESSİN; mevcut kalıbı"
            " yeniden düzenleyebilir, yeni bölümler tanımlayabilir, maddeleri birleştirebilir/çıkartabilirsin."
            " Çıktı SADECE TÜRKÇE olmalı ve sadece yeni system instructions metni olmalı."
            " ÖNEMLİ: Spesifik hata örneklerini ve kritik noktaları mutlaka dikkate al."
        )

        base_instructions = previous_instructions.strip() if previous_instructions else (
            "Sen Türk sağlık mevzuatına göre tıbbi raporları değerlendiren bir uzmansın.\n"
            "Gelen raporları şu kriterlere göre değerlendir:\n"
            "- ICD kodlarının doğruluğu\n"
            "- İlaç dozajlarının uygunluğu\n"
            "- Tanı-tedavi uyumluluğu\n"
            "- Mevzuata uygunluk\n"
            "- Eksik bilgilerin tespiti\n\n"
            "Değerlendirme sonucunu detaylı ve yapıcı bir şekilde sun."
        )

        user_msg = (
            "Aşağıda ÖNCEKİ system instructions ve SON DÖNEM FEEDBACK analiz özeti var. "
            "Amaç: Öncekini EVİRİP GELİŞTİREREK daha etkili bir metin üretmek. Özellikle 'neden_aciklama' "
            "alanındaki detaylı hata açıklamalarını analiz ederek spesifik iyileştirmeler öner. "
            "Yapı konusunda esneksin; madde sayısını/bölümleri değiştirebilirsin. "
            "Her sürüm bir öncekine göre İLERLEME içermeli.\n\n"
            f"[Önceki yönerge]\n{base_instructions}\n\n[Analiz]\n{user_payload}\n\n"
            "Yalnızca yeni system instructions metnini döndür. Spesifik hata örneklerini mutlaka dikkate al."
        )

        return [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]

    def generate_instructions_with_openai(self, analysis: Dict[str, Any], previous_instructions: str) -> str:
        """OpenAI'ya feedback analizini verip yeni instructions'ı doğrudan yazdırır."""
        messages = self._build_openai_prompt(analysis, previous_instructions)
        # openai >=1.0 Chat Completions
        resp = self.openai_client.chat.completions.create(
            model=os.getenv('OPENAI_INSTRUCTION_MODEL', 'gpt-4o-mini'),
            messages=messages,
            temperature=float(os.getenv('OPENAI_INSTRUCTION_TEMPERATURE', '0.4')),
            max_tokens=1200,
        )
        out = (resp.choices[0].message.content or "").strip()
        return out
    
    def update_assistant_with_dynamic_instructions(self) -> bool:
        """Assistant'ı dinamik instructions ile günceller"""
        try:
            print("🔍 Feedback verileri analiz ediliyor...")
            analysis = self.get_feedback_analysis(days=7)
            
            if not analysis:
                print("❌ Analiz yapılamadı!")
                return False
            
            # Önceki instructions'ı yükle ve evrimi buna göre yap
            previous_instructions = self.load_last_instructions()

            print(f"📊 Analiz Sonuçları:")
            print(f"   - Toplam feedback: {analysis['total_feedback']}")
            print(f"   - Başarı oranı: %{analysis['success_rate']:.1f}")
            print(f"   - Pozitif feedback: {len(analysis['positive_feedback'])}")
            print(f"   - Negatif feedback: {len(analysis['negative_feedback'])}")
            
            if analysis['common_issues']:
                print(f"   - En yaygın hatalar:")
                for issue, count in analysis['common_issues'][:3]:
                    print(f"     • {issue}: {count} kez")
            
            print("\n🤖 Dinamik instructions oluşturuluyor (OpenAI tarafından)...")
            try:
                new_instructions = self.generate_instructions_with_openai(analysis, previous_instructions)
                # Güvenlik: Boş dönerse heuristik üreticiye düş
                if not new_instructions or len(new_instructions.strip()) < 40:
                    raise ValueError("Boş veya çok kısa çıktı")
            except Exception as oe:
                print(f"⚠️ OpenAI üretimi başarısız, yerel üreticiye geçiliyor: {oe}")
                new_instructions = self.generate_dynamic_instructions(analysis, previous_instructions)
            
            print("\n📝 Yeni Instructions:")
            print("-" * 60)
            print(new_instructions)
            print("-" * 60)
            
            # Assistant'ı güncelle
            print("\n🔄 Assistant güncelleniyor...")
            self.openai_client.beta.assistants.update(
                assistant_id=self.assistant_id,
                instructions=new_instructions
            )
            
            print("✅ Assistant başarıyla dinamik instructions ile güncellendi!")
            
            # Güncelleme geçmişini kaydet
            self.save_update_history(analysis, new_instructions)
            
            return True
            
        except Exception as e:
            print(f"❌ Assistant güncellenemedi: {e}")
            return False
    
    def save_update_history(self, analysis: Dict[str, Any], instructions: str):
        """Güncelleme geçmişini kaydeder"""
        try:
            history_entry = {
                'timestamp': datetime.now().isoformat(),
                'analysis': analysis,
                'instructions': instructions,
                'success_rate': analysis.get('success_rate', 0),
                'total_feedback': analysis.get('total_feedback', 0)
            }
            
            # Geçmiş dosyasına ekle
            history_file = 'instruction_update_history.json'
            
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            else:
                history = []
            
            history.append(history_entry)
            
            # Son 50 güncellemeyi sakla
            if len(history) > 50:
                history = history[-50:]
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            
            print(f"📄 Güncelleme geçmişi kaydedildi: {history_file}")
            
        except Exception as e:
            print(f"⚠️ Geçmiş kaydedilemedi: {e}")

def main():
    """Ana fonksiyon"""
    try:
        generator = DynamicInstructionGenerator()
        generator.update_assistant_with_dynamic_instructions()
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    main()
