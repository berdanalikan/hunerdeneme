#!/usr/bin/env python3
"""
Reçete Analiz API Demo
"""
import requests
import json
from pathlib import Path


def demo_api():
    """API demo fonksiyonu"""
    print("🚀 Reçete Analiz API Demo")
    print("=" * 50)
    
    # API base URL
    base_url = "http://localhost:8000"
    
    # Health check
    print("\n1️⃣ Health Check")
    try:
        response = requests.get(f"{base_url}/health")
        health = response.json()
        print(f"   Status: {health['status']}")
        print(f"   OCR Model: {'✅' if health['ocr_model_loaded'] else '❌'}")
        print(f"   OpenAI: {'✅' if health['openai_configured'] else '❌'}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return
    
    # Test görselleri
    test_images = [
        "data/raw/synth_0000.jpg",
        "data/raw/synth_0001.jpg",
        "data/raw/synth_0002.jpg"
    ]
    
    available_images = [img for img in test_images if Path(img).exists()]
    
    if not available_images:
        print("\n❌ Test görselleri bulunamadı")
        return
    
    print(f"\n2️⃣ Test Görselleri: {len(available_images)} adet")
    
    # OCR Test
    print("\n3️⃣ OCR Test")
    for i, img_path in enumerate(available_images[:2]):
        try:
            with open(img_path, 'rb') as f:
                files = {'file': f}
                data = {'use_ocr': True}
                
                response = requests.post(
                    f"{base_url}/extract-text",
                    files=files,
                    data=data
                )
            
            result = response.json()
            if result['success']:
                text = result['text'][:50] + "..." if len(result['text']) > 50 else result['text']
                print(f"   Görsel {i+1}: '{text}' (Method: {result['method']})")
            else:
                print(f"   Görsel {i+1}: ❌ {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   Görsel {i+1}: ❌ {e}")
    
    # Reçete Analizi Test
    print("\n4️⃣ Reçete Analizi Test")
    for i, img_path in enumerate(available_images[:2]):
        try:
            with open(img_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'user_question': 'Bu reçetedeki metni analiz et',
                    'use_ocr_fallback': True
                }
                
                response = requests.post(
                    f"{base_url}/analyze-prescription",
                    files=files,
                    data=data
                )
            
            result = response.json()
            if result['success']:
                print(f"   Görsel {i+1}: ✅ Analiz tamamlandı")
                print(f"      İşlem süresi: {result['processing_time']:.2f}s")
                if result['analysis']:
                    analysis = result['analysis']
                    print(f"      OpenAI analizi: ✅")
                    print(f"      Güvenilirlik: {analysis.get('confidence_score', 0):.2f}")
                else:
                    print(f"      OpenAI analizi: ❌ (OCR fallback kullanıldı)")
                if result['ocr_text']:
                    ocr_text = result['ocr_text'][:30] + "..." if len(result['ocr_text']) > 30 else result['ocr_text']
                    print(f"      OCR metni: '{ocr_text}'")
            else:
                print(f"   Görsel {i+1}: ❌ {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   Görsel {i+1}: ❌ {e}")
    
    print("\n5️⃣ Web Arayüzü")
    print(f"   🌐 Tarayıcıda açın: {base_url}")
    print("   📁 Reçete görselinizi yükleyin")
    print("   ❓ Sorunuzu yazın")
    print("   🔍 Analiz butonuna tıklayın")
    
    print("\n✅ Demo tamamlandı!")
    print("\n💡 İpuçları:")
    print("   - OpenAI API key ayarlamak için: export OPENAI_API_KEY='your-key'")
    print("   - API dokümantasyonu: http://localhost:8000/docs")
    print("   - Daha fazla test için: python api/test_api.py")


if __name__ == "__main__":
    demo_api()
