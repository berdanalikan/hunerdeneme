"""
FastAPI Ana Uygulama - Reçete Analiz API
"""
import base64
import io
import os
from typing import Optional

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from api.ocr_service import get_ocr_service
from api.openai_service import get_openai_service, PrescriptionAnalysis


# FastAPI app
app = FastAPI(
    title="Reçete Analiz API",
    description="El yazısı reçete görsellerini analiz eden API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da spesifik domain'ler kullan
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="api/static"), name="static")


# Request/Response Models
class PrescriptionRequest(BaseModel):
    """Reçete analiz request modeli"""
    user_question: Optional[str] = "Bu reçeteyi analiz et"
    use_ocr_fallback: bool = True


class PrescriptionResponse(BaseModel):
    """Reçete analiz response modeli"""
    success: bool
    analysis: Optional[PrescriptionAnalysis] = None
    ocr_text: Optional[str] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    ocr_model_loaded: bool
    openai_configured: bool


# Global services
ocr_service = None
openai_service = None


@app.on_event("startup")
async def startup_event():
    """Uygulama başlangıcında servisleri yükle"""
    global ocr_service, openai_service
    
    try:
        # OCR servisini yükle
        ocr_service = get_ocr_service()
        print("✅ OCR service loaded successfully")
    except Exception as e:
        print(f"❌ OCR service loading failed: {e}")
        ocr_service = None
    
    try:
        # OpenAI servisini yükle
        openai_service = get_openai_service()
        print("✅ OpenAI service loaded successfully")
    except Exception as e:
        print(f"❌ OpenAI service loading failed: {e}")
        openai_service = None


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Sistem durumu kontrolü"""
    return HealthResponse(
        status="healthy" if (ocr_service and openai_service) else "degraded",
        ocr_model_loaded=ocr_service is not None,
        openai_configured=openai_service is not None
    )


@app.post("/analyze-prescription", response_model=PrescriptionResponse)
async def analyze_prescription(
    file: UploadFile = File(...),
    user_question: str = Form("Bu reçeteyi analiz et"),
    use_ocr_fallback: bool = Form(True)
):
    """
    Reçete görselini analiz et
    
    Args:
        file: Yüklenen reçete görseli
        user_question: Kullanıcının sorusu
        use_ocr_fallback: OCR fallback kullanılsın mı
        
    Returns:
        Yapılandırılmış reçete analizi
    """
    import time
    start_time = time.time()
    
    try:
        # Dosya validasyonu
        if file.content_type and not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Sadece görsel dosyaları kabul edilir")
        
        # Dosyayı oku
        file_content = await file.read()
        
        # Base64'e çevir
        image_base64 = base64.b64encode(file_content).decode('utf-8')
        
        # OpenAI ile analiz et
        analysis = None
        ocr_text = None
        
        if openai_service:
            try:
                analysis = openai_service.analyze_prescription(
                    image_base64=image_base64,
                    user_question=user_question
                )
            except Exception as e:
                print(f"OpenAI analysis failed: {e}")
                analysis = None
        
        # OCR fallback
        if (not analysis or use_ocr_fallback) and ocr_service:
            try:
                ocr_text = ocr_service.predict_from_base64(image_base64)
                print(f"OCR result: {ocr_text}")
            except Exception as e:
                print(f"OCR failed: {e}")
                ocr_text = None
        
        # Eğer hiçbir servis çalışmıyorsa
        if not analysis and not ocr_text:
            raise HTTPException(
                status_code=503, 
                detail="Hem OpenAI hem de OCR servisleri kullanılamıyor"
            )
        
        processing_time = time.time() - start_time
        
        return PrescriptionResponse(
            success=True,
            analysis=analysis,
            ocr_text=ocr_text,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        return PrescriptionResponse(
            success=False,
            error=str(e),
            processing_time=processing_time
        )


@app.post("/extract-text", response_model=dict)
async def extract_text_only(
    file: UploadFile = File(...),
    use_ocr: bool = Form(True)
):
    """
    Sadece metin çıkarımı yap
    
    Args:
        file: Yüklenen görsel
        use_ocr: OCR kullanılsın mı (True) yoksa OpenAI kullanılsın mı (False)
        
    Returns:
        Çıkarılan metin
    """
    try:
        # Dosya validasyonu
        if file.content_type and not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Sadece görsel dosyaları kabul edilir")
        
        # Dosyayı oku
        file_content = await file.read()
        image_base64 = base64.b64encode(file_content).decode('utf-8')
        
        text = ""
        method = ""
        
        if use_ocr and ocr_service:
            try:
                text = ocr_service.predict_from_base64(image_base64)
                method = "OCR"
            except Exception as e:
                print(f"OCR failed: {e}")
                text = ""
        
        if not text and openai_service:
            try:
                text = openai_service.extract_text_only(image_base64)
                method = "OpenAI"
            except Exception as e:
                print(f"OpenAI text extraction failed: {e}")
                text = ""
        
        if not text:
            raise HTTPException(
                status_code=503,
                detail="Metin çıkarımı başarısız"
            )
        
        return {
            "success": True,
            "text": text,
            "method": method
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/")
async def root():
    """Ana sayfa - Web arayüzüne yönlendir"""
    from fastapi.responses import FileResponse
    return FileResponse("api/static/index.html")


if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
