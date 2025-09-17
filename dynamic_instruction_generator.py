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
                # Free-text neden_aciklama içeriğinden kategori çıkarımı (basit anahtar kelime haritalama)
                if comment:
                    lc = str(comment).lower()
                    keyword_to_bucket = [
                        (['icd', 'tanı', 'tani', 'kod'], 'Yanlış tanı-eşleşme'),
                        (['doz', 'dozaj', 'şema', 'tedavi şema', 'titrasyon'], 'Doz/şema hatası'),
                        (['sut', 'mevzuat', 'sgk', 'dayanak', 'kılavuz', 'kilavuz'], 'Mevzuat dayanağı eksik'),
                        (['eksik', 'bilgi eksik', 'belirsiz', 'tamamlanmalı', 'tamamlanmali'], 'Eksik bilgi gözardı'),
                        (['dil', 'format', 'biçim', 'bicim', 'anlaşılır', 'anlasilir'], 'Dil/format sorunları'),
                    ]
                    matched = False
                    for keywords, bucket in keyword_to_bucket:
                        if any(k in lc for k in keywords):
                            analysis['error_patterns'][bucket] = analysis['error_patterns'].get(bucket, 0) + 1
                            matched = True
                    # Eşleşme yoksa genel eksik bilgiye at
                    if not matched:
                        analysis['error_patterns']['Eksik bilgi gözardı'] = analysis['error_patterns'].get('Eksik bilgi gözardı', 0) + 1
                
                # Spesifik feedback topla
                analysis['specific_feedback'].append({
                    'reason': reason,
                    'comment': comment,
                    'user_input': feedback.get('kullanici_girdisi', '')[:200],  # İlk 200 karakter
                    'assistant_response': feedback.get('asistan_cevabi', '')[:200]
                })
        
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
    
    def generate_dynamic_instructions(self, analysis: Dict[str, Any]) -> str:
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
        
        # 4. Spesifik feedback'lere göre özel talimatlar
        specific_feedback = analysis.get('specific_feedback', [])
        if specific_feedback:
            improvements.append("\nSPESİFİK İYİLEŞTİRME ÖNERİLERİ:")
            
            # Son 3 negatif feedback'i analiz et
            recent_negative = [f for f in specific_feedback if f['reason']][-3:]
            
            for feedback in recent_negative:
                if feedback['comment']:
                    improvements.append(f"• {feedback['comment'][:100]}...")
        
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
        if improvements:
            dynamic_instructions = base_instructions + "\n".join(improvements)
        else:
            dynamic_instructions = base_instructions
        
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

    def _build_openai_prompt(self, analysis: Dict[str, Any]) -> list:
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

        # Spesifik örnekler (maks 3 adet)
        examples_lines = ["Negatif feedback örnekleri (maskelenmiş):"]
        for ex in specific[:3]:
            ex_reason = ex.get('reason') or "(belirtilmemiş)"
            ex_comment = self._mask_text(ex.get('comment') or "")
            ex_user = self._mask_text(ex.get('user_input') or "", max_len=300)
            ex_assistant = self._mask_text(ex.get('assistant_response') or "", max_len=300)
            examples_lines.append("---")
            examples_lines.append(f"Neden: {ex_reason}")
            if ex_comment:
                examples_lines.append(f"Yorum: {ex_comment}")
            examples_lines.append(f"Kullanıcı girdisi: {ex_user}")
            examples_lines.append(f"Asistan cevabı: {ex_assistant}")

        user_payload = "\n".join(summary_lines + [""] + examples_lines)

        system_msg = (
            "Sen 'Instruction Optimizer' rolündesin. Görevin: Bir tıbbi rapor değerlendirme asistanının"
            " system instructions metnini, verilen feedback analizine göre PROFESYONEL ve SALT TÜRKÇE"
            " olacak şekilde GÜNCELLEMEKTİR.\n\n"
            "Kurallar:\n"
            "- ÇIKTI SADECE yeni system instructions metni olmalı. Ek açıklama, başlık, markdown, JSON istemiyorum.\n"
            "- Amaç: Asistanın SUT/SGK mevzuatına göre daha doğru, gerekçeli ve tutarlı sonuç vermesi.\n"
            "- Kısa değil; ancak gereksiz tekrar içermeyecek kadar öz, net ve uygulanabilir talimatlar yaz.\n"
            "- Yaygın hatalara (ör. tanı-eşleşme, doz/şema, mevzuat dayanağı) yönelik kesin talimatlar ekle.\n"
            "- Dili kesin: 'Mutlaka', 'Her zaman', 'Önce', 'Daha sonra' gibi yönlendirici ifadeler kullan.\n"
            "- Çıktı tamamen TÜRKÇE olmalı.\n"
        )

        base_instructions = (
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
            "Aşağıdaki bilgiler son günlerdeki feedback analizidir. Bu analizden hareketle üstte verdiğim"
            " temel yönergeyi (system instructions) iyileştir ve tam metin yeni instructions üret.\n\n"
            f"[Temel yönerge]\n{base_instructions}\n\n[Analiz]\n{user_payload}"
        )

        return [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]

    def generate_instructions_with_openai(self, analysis: Dict[str, Any]) -> str:
        """OpenAI'ya feedback analizini verip yeni instructions'ı doğrudan yazdırır."""
        messages = self._build_openai_prompt(analysis)
        # openai >=1.0 Chat Completions
        resp = self.openai_client.chat.completions.create(
            model=os.getenv('OPENAI_INSTRUCTION_MODEL', 'gpt-4o-mini'),
            messages=messages,
            temperature=0.2,
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
                new_instructions = self.generate_instructions_with_openai(analysis)
                # Güvenlik: Boş dönerse heuristik üreticiye düş
                if not new_instructions or len(new_instructions.strip()) < 40:
                    raise ValueError("Boş veya çok kısa çıktı")
            except Exception as oe:
                print(f"⚠️ OpenAI üretimi başarısız, yerel üreticiye geçiliyor: {oe}")
                new_instructions = self.generate_dynamic_instructions(analysis)
            
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
