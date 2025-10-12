"""
OpenAI Service - Reçete analizi için OpenAI API entegrasyonu
"""
import json
import base64
from typing import Dict, Any, Optional
try:
    import openai
    from openai import OpenAI
except ImportError:
    openai = None
    OpenAI = None
from pydantic import BaseModel


class PrescriptionAnalysis(BaseModel):
    """Yapılandırılmış reçete analizi response modeli"""
    patient_name: Optional[str] = None
    patient_id: Optional[str] = None
    doctor_name: Optional[str] = None
    date: Optional[str] = None
    medications: list[Dict[str, Any]] = []
    dosage_instructions: Optional[str] = None
    special_notes: Optional[str] = None
    requested_info: Optional[str] = None
    confidence_score: float = 0.0
    raw_text: str = ""


class OpenAIService:
    def __init__(self, api_key: Optional[str] = None):
        """OpenAI servisini başlat"""
        if not openai or not OpenAI:
            raise ImportError("OpenAI library not available")
        
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            # Environment variable'dan al
            import os
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")
            self.client = OpenAI(api_key=api_key)
    
    def analyze_prescription(
        self, 
        image_base64: str, 
        user_question: str = "",
        model: str = "gpt-4o"
    ) -> PrescriptionAnalysis:
        """
        Reçete görselini ve kullanıcı sorusunu analiz et
        
        Args:
            image_base64: Base64 encoded reçete görseli
            user_question: Kullanıcının sorusu (opsiyonel)
            model: Kullanılacak OpenAI model
            
        Returns:
            Yapılandırılmış reçete analizi
        """
        
        # System prompt
        system_prompt = """Sen bir eczacı ve tıbbi doküman analiz uzmanısın. 
        Verilen reçete görselini analiz ederek yapılandırılmış bilgi çıkar.
        
        Önemli kurallar:
        1. Sadece görselde açıkça yazılı olan bilgileri kullan
        2. Tahmin yapma, belirsiz olanları "belirtilmemiş" olarak işaretle
        3. İlaç isimlerini doğru yazım ile ver
        4. Dozaj bilgilerini net şekilde belirt
        5. Kullanıcının sorusuna özel dikkat göster
        
        Response formatı JSON olmalı ve şu alanları içermeli:
        - patient_name: Hasta adı
        - patient_id: Hasta kimlik numarası
        - doctor_name: Doktor adı
        - date: Reçete tarihi
        - medications: İlaç listesi (isim, dozaj, kullanım şekli)
        - dosage_instructions: Genel kullanım talimatları
        - special_notes: Özel notlar
        - requested_info: Kullanıcının sorusuna özel cevap
        - confidence_score: Analiz güvenilirlik skoru (0-1)
        - raw_text: Ham metin çıkarımı"""
        
        # User prompt
        user_prompt = f"""
        Bu reçete görselini analiz et ve yapılandırılmış bilgi çıkar.
        
        Kullanıcı sorusu: {user_question if user_question else "Genel reçete analizi"}
        
        Lütfen JSON formatında cevap ver. Sadece JSON döndür, başka açıklama ekleme.
        """
        
        try:
            # OpenAI API çağrısı
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.1
            )
            
            # Response'u parse et
            content = response.choices[0].message.content.strip()
            
            # JSON'u parse et
            try:
                analysis_data = json.loads(content)
                return PrescriptionAnalysis(**analysis_data)
            except json.JSONDecodeError:
                # JSON parse edilemezse fallback
                return PrescriptionAnalysis(
                    raw_text=content,
                    confidence_score=0.5,
                    requested_info=content
                )
                
        except Exception as e:
            # Hata durumunda fallback response
            return PrescriptionAnalysis(
                raw_text=f"Analiz hatası: {str(e)}",
                confidence_score=0.0,
                requested_info=f"Reçete analizi sırasında hata oluştu: {str(e)}"
            )
    
    def extract_text_only(
        self, 
        image_base64: str, 
        model: str = "gpt-4o"
    ) -> str:
        """
        Sadece metin çıkarımı yap (OCR fallback)
        
        Args:
            image_base64: Base64 encoded görsel
            model: Kullanılacak model
            
        Returns:
            Çıkarılan metin
        """
        
        prompt = """
        Bu görseldeki tüm metni oku ve düz metin olarak ver.
        Sadece metni ver, başka açıklama ekleme.
        Metni olduğu gibi, boşlukları ve satır sonlarını koruyarak ver.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.0
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Metin çıkarımı hatası: {str(e)}"


# Global OpenAI service instance
openai_service = None

def get_openai_service() -> OpenAIService:
    """Singleton OpenAI service instance"""
    global openai_service
    if openai_service is None:
        openai_service = OpenAIService()
    return openai_service
