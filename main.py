#!/usr/bin/env python3
"""
Tıbbi Rapor Değerlendirme Sistemi
Bu script ham rapor metnini parse eder ve OpenAI Assistant'a gönderir.
"""

import json
import os
import sys
from typing import Optional
from parser import MedicalReportParser
from openai_client import MedicalReportAssistantClient
from models import MedicalReport

def load_report_from_file(file_path: str) -> str:
    """Dosyadan rapor metnini yükler"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Hata: {file_path} dosyası bulunamadı.")
        sys.exit(1)
    except Exception as e:
        print(f"Dosya okuma hatası: {str(e)}")
        sys.exit(1)

def save_structured_report(report: MedicalReport, output_file: str):
    """Yapılandırılmış raporu dosyaya kaydeder"""
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(report.to_dict(), file, ensure_ascii=False, indent=2)
        print(f"Yapılandırılmış rapor kaydedildi: {output_file}")
    except Exception as e:
        print(f"Rapor kaydetme hatası: {str(e)}")

def save_evaluation_result(result: dict, output_file: str):
    """Değerlendirme sonucunu dosyaya kaydeder"""
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(result, file, ensure_ascii=False, indent=2)
        print(f"Değerlendirme sonucu kaydedildi: {output_file}")
    except Exception as e:
        print(f"Sonuç kaydetme hatası: {str(e)}")

def main():
    """Ana fonksiyon"""
    print("=== Tıbbi Rapor Değerlendirme Sistemi ===\n")
    
    # Komut satırı argümanlarını kontrol et
    if len(sys.argv) < 2:
        print("Kullanım: python main.py <rapor_dosyası> [çıktı_dosyası]")
        print("Örnek: python main.py rapor.txt")
        print("Örnek: python main.py rapor.txt sonuc.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Rapor dosyasını yükle
    print(f"Rapor dosyası yükleniyor: {input_file}")
    report_text = load_report_from_file(input_file)
    
    # Parser ile raporu parse et
    print("Rapor parse ediliyor...")
    parser = MedicalReportParser()
    try:
        medical_report = parser.parse(report_text)
        print("✓ Rapor başarıyla parse edildi")
    except Exception as e:
        print(f"✗ Parse hatası: {str(e)}")
        sys.exit(1)
    
    # Parse edilen raporu göster
    print("\n=== PARSE EDİLEN RAPOR BİLGİLERİ ===")
    report_dict = medical_report.to_dict()
    
    print(f"Rapor Numarası: {report_dict['report_info']['report_number']}")
    print(f"Rapor Tarihi: {report_dict['report_info']['report_date']}")
    print(f"Tesis: {report_dict['report_info']['facility_name']}")
    print(f"Tanı Sayısı: {len(report_dict['diagnoses'])}")
    print(f"İlaç Sayısı: {len(report_dict['medications'])}")
    print(f"Doktor: {report_dict['doctor']['name']}")
    
    # Yapılandırılmış raporu kaydet
    if output_file:
        save_structured_report(medical_report, output_file)
    else:
        # Varsayılan dosya adı
        base_name = os.path.splitext(input_file)[0]
        structured_file = f"{base_name}_structured.json"
        save_structured_report(medical_report, structured_file)
    
    # OpenAI Assistant ile değerlendirme
    print("\n=== OPENAI ASSISTANT DEĞERLENDİRMESİ ===")
    
    # Environment variables kontrolü
    if not os.getenv('OPENAI_API_KEY'):
        print("Uyarı: OPENAI_API_KEY environment variable ayarlanmamış.")
        print("Değerlendirme yapılamayacak.")
        return
    
    if not os.getenv('OPENAI_ASSISTANT_ID'):
        print("Uyarı: OPENAI_ASSISTANT_ID environment variable ayarlanmamış.")
        print("Değerlendirme yapılamayacak.")
        return
    
    try:
        # Assistant client'ını başlat
        client = MedicalReportAssistantClient()
        
        # Raporu değerlendir
        print("Rapor OpenAI Assistant'a gönderiliyor...")
        evaluation_result = client.evaluate_report(medical_report)
        
        if evaluation_result['status'] == 'success':
            print("✓ Değerlendirme tamamlandı")
            print("\n=== DEĞERLENDİRME SONUCU ===")
            print(evaluation_result['evaluation'])
            
            # Sonucu kaydet
            base_name = os.path.splitext(input_file)[0]
            evaluation_file = f"{base_name}_evaluation.json"
            save_evaluation_result(evaluation_result, evaluation_file)
            
        else:
            print(f"✗ Değerlendirme hatası: {evaluation_result['message']}")
            
    except Exception as e:
        print(f"✗ Assistant değerlendirme hatası: {str(e)}")
    
    print("\n=== İŞLEM TAMAMLANDI ===")

def demo_with_sample_data():
    """Örnek veri ile demo çalıştırır"""
    print("=== DEMO MODU ===")
    
    # Örnek rapor metni
    sample_report = """
Rapor Bilgileri 
 Rapor Numarası () :  79591   Rapor Tarihi () :  18/10/2023 
 Protokol No :  85741127    Düzenleme Türü :  Uzman Hekim Raporu 
 Açıklama :     Kayıt Şekli  :  Elektronik İmzalı Rapor  
 Tesis Kodu (*)  :  11330005    Rapor Takip No  :  434270698  
 Tesis Ünvanı  :  MERSIN TOROS DEVLET HASTANESİ(S)  
 Kullanıcı Adı  :  MUSTAFA AKCA  
Açıklamalar Eklenme Zamanı Not 
12/09/2019 TARİHLİ RAPORDA LDL: 97 idame tedavi 18/10/2023 14:30  
MONOTERAPİ İLE KAN BASINCI YETERLİ ORANDA KONTROL ALTINA ALINAMAMIŞTIR 18/10/2023 14:30  
 
 
Tanı Bilgileri 
Tanı   Başlangıç Bitiş 
04.02 - Koroner arter hastaligi(I20)(I21)(I25)(Z95.1)(Z95.5-Z95.9) 
I25.1 ATEROSKLEROTİK KALP HASTALIĞI 
  18/10/2023 16/10/2025 
04.05 - Arteriyel Hipertansiyon(I10 -I13)(I15) 
I10 ESANSİYEL (PRİMER) HİPERTANSİYON 
  18/10/2023 16/10/2025 
04.08 - Hiperkolesterolemi, Hiperlipidemi(E78) 
E78.4 HİPERLİPİDEMİ, DİĞER 
  18/10/2023 16/10/2025 
 
 
Doktor Bilgileri 
Dr. Diploma No Dip. Tescil No Branş Adı Soyadı 
12324 144070 Kardiyoloji ABDULLAH ZARARSIZ 
 
 
Rapor Etkin Madde Bilgileri 
Kodu Adı Form Tedavi Şema Adet / Miktar İçerik Mik. Eklenme Zamanı  
SGKESD ATORVASTATIN KALSIYUM Ağızdan katı Günde 1 x 1.0 Adet   18/10/2023 14:30  
SGKETJ BENIDIPIN HCL Ağızdan katı Günde 1 x 1.0 Adet   18/10/2023 14:30  
SGKERW ASETILSALISILIK ASIT Ağızdan katı Günde 1 x 1.0 Adet   18/10/2023 14:30  
SGKFDX METOPROLOL Ağızdan katı Günde 1 x 1.0 Adet   18/10/2023 14:30  
SGKFRU TELMISARTAN+HIDROKLOROTIAZID Ağızdan katı Günde 1 x 1.0 Adet   18/10/2023 14:30 
"""
    
    # Parser ile parse et
    parser = MedicalReportParser()
    medical_report = parser.parse(sample_report)
    
    print("✓ Örnek rapor parse edildi")
    print(f"Rapor Numarası: {medical_report.report_info.report_number}")
    print(f"Tanı Sayısı: {len(medical_report.diagnoses)}")
    print(f"İlaç Sayısı: {len(medical_report.medications)}")
    
    # JSON olarak kaydet
    with open('demo_report.json', 'w', encoding='utf-8') as f:
        json.dump(medical_report.to_dict(), f, ensure_ascii=False, indent=2)
    
    print("✓ Demo raporu demo_report.json olarak kaydedildi")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_with_sample_data()
    else:
        main()
