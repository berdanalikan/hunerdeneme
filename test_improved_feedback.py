#!/usr/bin/env python3
"""
Geliştirilmiş feedback analiz sistemini test eder
"""

import os
import json
from datetime import datetime, timedelta
from dynamic_instruction_generator import DynamicInstructionGenerator
from dotenv import load_dotenv

load_dotenv()

def test_improved_feedback_analysis():
    """Geliştirilmiş feedback analizini test eder"""
    print("🧪 Geliştirilmiş Feedback Analiz Sistemi Test Ediliyor...")
    
    try:
        generator = DynamicInstructionGenerator()
        
        # Son 7 günün feedback verilerini analiz et
        print("\n📊 Feedback verileri analiz ediliyor...")
        analysis = generator.get_feedback_analysis(days=7)
        
        if not analysis:
            print("❌ Analiz yapılamadı!")
            return False
        
        print(f"\n📈 Analiz Sonuçları:")
        print(f"   - Toplam feedback: {analysis['total_feedback']}")
        print(f"   - Başarı oranı: %{analysis['success_rate']:.1f}")
        print(f"   - Pozitif feedback: {len(analysis['positive_feedback'])}")
        print(f"   - Negatif feedback: {len(analysis['negative_feedback'])}")
        
        # Hata pattern'larını göster
        if analysis['error_patterns']:
            print(f"\n🔍 Tespit Edilen Hata Türleri:")
            for error_type, count in analysis['error_patterns'].items():
                print(f"   • {error_type}: {count} kez")
        
        # Spesifik feedback'leri detaylı analiz et
        if analysis['specific_feedback']:
            print(f"\n📝 Spesifik Feedback Analizleri:")
            for i, feedback in enumerate(analysis['specific_feedback'][:3], 1):
                print(f"\n   {i}. Feedback:")
                print(f"      - Neden: {feedback.get('reason', 'Belirtilmemiş')}")
                print(f"      - Yorum: {feedback.get('comment', 'Yok')[:100]}...")
                
                detailed_analysis = feedback.get('detailed_analysis', {})
                if detailed_analysis:
                    print(f"      - Detaylı Analiz:")
                    if detailed_analysis.get('key_issues'):
                        print(f"        • Sorunlar: {', '.join(detailed_analysis['key_issues'])}")
                    if detailed_analysis.get('critical_points'):
                        print(f"        • Kritik Noktalar: {', '.join(detailed_analysis['critical_points'])}")
                    if detailed_analysis.get('suggested_improvements'):
                        print(f"        • Öneriler: {', '.join(detailed_analysis['suggested_improvements'])}")
        
        # Dinamik instructions üret
        print(f"\n🤖 Dinamik Instructions Üretiliyor...")
        previous_instructions = generator.load_last_instructions()
        new_instructions = generator.generate_dynamic_instructions(analysis, previous_instructions)
        
        print(f"\n📝 Yeni Instructions (İlk 500 karakter):")
        print("-" * 60)
        print(new_instructions[:500] + "..." if len(new_instructions) > 500 else new_instructions)
        print("-" * 60)
        
        # Test sonucunu kaydet
        test_result = {
            'timestamp': datetime.now().isoformat(),
            'analysis_summary': {
                'total_feedback': analysis['total_feedback'],
                'success_rate': analysis['success_rate'],
                'error_patterns': analysis['error_patterns'],
                'specific_feedback_count': len(analysis['specific_feedback'])
            },
            'instructions_length': len(new_instructions),
            'test_status': 'success'
        }
        
        with open('test_improved_feedback_result.json', 'w', encoding='utf-8') as f:
            json.dump(test_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Test başarıyla tamamlandı!")
        print(f"📄 Sonuçlar test_improved_feedback_result.json dosyasına kaydedildi.")
        
        return True
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        return False

def main():
    """Ana fonksiyon"""
    success = test_improved_feedback_analysis()
    
    if success:
        print("\n🎉 Geliştirilmiş feedback analiz sistemi başarıyla test edildi!")
        print("\n📋 Yapılan İyileştirmeler:")
        print("   • neden_aciklama alanındaki detaylı bilgiler daha etkili analiz ediliyor")
        print("   • Spesifik hata türleri daha detaylı kategorize ediliyor")
        print("   • Kritik noktalar ve öğrenme fırsatları belirleniyor")
        print("   • Prompt güncellemelerinde spesifik örnekler kullanılıyor")
        print("   • Aynı hataların tekrar etmesini önleyecek önlemler alınıyor")
    else:
        print("\n❌ Test başarısız oldu. Lütfen hataları kontrol edin.")

if __name__ == "__main__":
    main()

