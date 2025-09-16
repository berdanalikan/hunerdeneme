#!/usr/bin/env python3
"""
OpenAI Assistant API bağlantısını test eden script
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

def test_api_connection():
    """API bağlantısını test eder"""
    print("=== OpenAI Assistant API Bağlantı Testi ===\n")
    
    # .env dosyasını yükle
    load_dotenv()
    
    # API key kontrolü
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ HATA: OPENAI_API_KEY bulunamadı!")
        print("Lütfen .env dosyasında OPENAI_API_KEY'i ayarlayın.")
        return False
    
    if api_key == "your_openai_api_key_here":
        print("❌ HATA: OPENAI_API_KEY henüz ayarlanmamış!")
        print("Lütfen .env dosyasında gerçek API key'inizi yazın.")
        return False
    
    print(f"✅ API Key bulundu: {api_key[:10]}...")
    
    # Assistant ID kontrolü
    assistant_id = os.getenv('OPENAI_ASSISTANT_ID')
    if not assistant_id:
        print("❌ HATA: OPENAI_ASSISTANT_ID bulunamadı!")
        print("Lütfen .env dosyasında OPENAI_ASSISTANT_ID'i ayarlayın.")
        return False
    
    if assistant_id == "your_assistant_id_here":
        print("❌ HATA: OPENAI_ASSISTANT_ID henüz ayarlanmamış!")
        print("Lütfen .env dosyasında gerçek Assistant ID'nizi yazın.")
        return False
    
    print(f"✅ Assistant ID bulundu: {assistant_id[:10]}...")
    
    try:
        # OpenAI client'ını başlat
        client = OpenAI(api_key=api_key)
        
        # Assistant'ı kontrol et
        print("\n🔍 Assistant bilgileri kontrol ediliyor...")
        assistant = client.beta.assistants.retrieve(assistant_id)
        
        print(f"✅ Assistant bulundu: {assistant.name}")
        print(f"   Model: {assistant.model}")
        print(f"   Oluşturulma: {assistant.created_at}")
        
        # Basit bir test mesajı gönder
        print("\n📤 Test mesajı gönderiliyor...")
        
        # Thread oluştur
        thread = client.beta.threads.create()
        
        # Test mesajı gönder
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content="Merhaba, bu bir test mesajıdır. Lütfen 'Test başarılı' yanıtını verin."
        )
        
        # Assistant'ı çalıştır
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )
        
        # Sonucu bekle
        import time
        while run.status in ['queued', 'in_progress', 'cancelling']:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
        
        if run.status == 'completed':
            # Son mesajı al
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
            )
            
            if messages.data:
                response = messages.data[0].content[0].text.value
                print(f"✅ Test başarılı! Assistant yanıtı: {response}")
                return True
            else:
                print("❌ Assistant'dan yanıt alınamadı")
                return False
        else:
            print(f"❌ Assistant çalıştırılamadı: {run.status}")
            if run.last_error:
                print(f"   Hata: {run.last_error}")
            return False
            
    except Exception as e:
        print(f"❌ API bağlantı hatası: {str(e)}")
        return False

def main():
    """Ana fonksiyon"""
    success = test_api_connection()
    
    if success:
        print("\n🎉 Tüm testler başarılı! Sistem kullanıma hazır.")
        print("\nArtık şu komutu çalıştırabilirsiniz:")
        print("python main.py --demo")
    else:
        print("\n❌ Test başarısız! Lütfen ayarları kontrol edin.")
        print("\nKontrol edilecekler:")
        print("1. .env dosyasında OPENAI_API_KEY doğru mu?")
        print("2. .env dosyasında OPENAI_ASSISTANT_ID doğru mu?")
        print("3. OpenAI hesabınızda kredi var mı?")
        print("4. Assistant aktif mi?")

if __name__ == "__main__":
    main()
