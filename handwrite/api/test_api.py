"""
API Test Scripti
"""
import requests
import base64
import json
from pathlib import Path


def test_health():
    """Health check testi"""
    print("🔍 Health check testi...")
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_extract_text(image_path: str):
    """Metin çıkarım testi"""
    print(f"\n📝 Metin çıkarım testi: {image_path}")
    
    if not Path(image_path).exists():
        print(f"❌ Görsel bulunamadı: {image_path}")
        return False
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {'use_ocr': True}
            
            response = requests.post(
                "http://localhost:8000/extract-text",
                files=files,
                data=data
            )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Success: {result.get('success')}")
        print(f"Method: {result.get('method')}")
        print(f"Text: {result.get('text', '')[:100]}...")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Metin çıkarım testi failed: {e}")
        return False


def test_prescription_analysis(image_path: str, question: str = "Bu reçeteyi analiz et"):
    """Reçete analiz testi"""
    print(f"\n💊 Reçete analiz testi: {image_path}")
    print(f"Soru: {question}")
    
    if not Path(image_path).exists():
        print(f"❌ Görsel bulunamadı: {image_path}")
        return False
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {
                'user_question': question,
                'use_ocr_fallback': True
            }
            
            response = requests.post(
                "http://localhost:8000/analyze-prescription",
                files=files,
                data=data
            )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Success: {result.get('success')}")
        print(f"Processing time: {result.get('processing_time')}s")
        
        if result.get('analysis'):
            analysis = result['analysis']
            print(f"Patient name: {analysis.get('patient_name')}")
            print(f"Doctor name: {analysis.get('doctor_name')}")
            print(f"Medications count: {len(analysis.get('medications', []))}")
            print(f"Confidence: {analysis.get('confidence_score')}")
        
        if result.get('ocr_text'):
            print(f"OCR text: {result['ocr_text'][:100]}...")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Reçete analiz testi failed: {e}")
        return False


def main():
    """Ana test fonksiyonu"""
    print("🚀 API Test Başlatılıyor...")
    
    # Health check
    if not test_health():
        print("❌ API çalışmıyor, testleri durduruyorum")
        return
    
    # Test görselleri
    test_images = [
        "data/raw/001.jpg",
        "data/raw/002.jpg",
        "data/raw/003.jpg"
    ]
    
    # Mevcut görselleri bul
    available_images = []
    for img_path in test_images:
        if Path(img_path).exists():
            available_images.append(img_path)
    
    if not available_images:
        print("❌ Test için görsel bulunamadı")
        return
    
    print(f"✅ {len(available_images)} test görseli bulundu")
    
    # Testleri çalıştır
    success_count = 0
    total_tests = 0
    
    for img_path in available_images[:2]:  # İlk 2 görseli test et
        total_tests += 1
        if test_extract_text(img_path):
            success_count += 1
        
        total_tests += 1
        if test_prescription_analysis(img_path, "Bu reçetedeki ilaçları listele"):
            success_count += 1
    
    print(f"\n📊 Test Sonuçları: {success_count}/{total_tests} başarılı")


if __name__ == "__main__":
    main()
