"""
API Başlatma Scripti
"""
import os
import sys
from pathlib import Path

# Proje root'unu Python path'ine ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Environment variables
os.environ.setdefault("OPENAI_API_KEY", "")

def check_environment():
    """Ortam kontrolü"""
    print("🔍 Ortam kontrolü yapılıyor...")
    
    # Gerekli dosyalar
    required_files = [
        "checkpoints/crnn_ctc_best.pdparams",
        "checkpoints/charset.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Eksik dosyalar:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    # OpenAI API key kontrolü
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY environment variable ayarlanmamış")
        print("   OCR fallback kullanılacak")
    else:
        print("✅ OpenAI API key mevcut")
    
    print("✅ Ortam kontrolü tamamlandı")
    return True


def start_api():
    """API'yi başlat"""
    if not check_environment():
        print("❌ Ortam kontrolü başarısız, API başlatılamıyor")
        return
    
    print("🚀 API başlatılıyor...")
    print("📍 URL: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    print("🛑 Durdurmak için Ctrl+C")
    
    try:
        import uvicorn
        from api.main import app
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 API durduruldu")
    except Exception as e:
        print(f"❌ API başlatma hatası: {e}")


if __name__ == "__main__":
    start_api()
