from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
import sys
import json
import base64
import time
from pathlib import Path

# Handwrite modüllerini import et
handwrite_path = Path(__file__).parent.parent / 'handwrite'
sys.path.insert(0, str(handwrite_path))

try:
    from handwrite.api.ocr_service import get_ocr_service
    from handwrite.api.openai_service import get_openai_service, PrescriptionAnalysis
    OCR_AVAILABLE = True
except ImportError as e:
    print(f"Handwrite modules not available: {e}")
    OCR_AVAILABLE = False
except Exception as e:
    print(f"Handwrite modules failed to load: {e}")
    OCR_AVAILABLE = False


def index(request: HttpRequest):
    """Handwrite ana sayfası"""
    return render(request, 'handwrite_app/index.html')


@csrf_exempt
def analyze_prescription(request: HttpRequest):
    """Reçete analizi endpoint'i"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    
    if not OCR_AVAILABLE:
        return JsonResponse({
            'success': False,
            'error': 'OCR servisi kullanılamıyor. Handwrite modülleri yüklenemedi.'
        }, status=503)
    
    start_time = time.time()
    
    try:
        # Dosya kontrolü
        if 'file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Dosya yüklenmedi'
            }, status=400)
        
        uploaded_file = request.FILES['file']
        
        # Dosya validasyonu
        if uploaded_file.content_type and not uploaded_file.content_type.startswith('image/'):
            return JsonResponse({
                'success': False,
                'error': 'Sadece görsel dosyaları kabul edilir'
            }, status=400)
        
        # Dosyayı oku
        file_content = uploaded_file.read()
        
        # Base64'e çevir
        image_base64 = base64.b64encode(file_content).decode('utf-8')
        
        # Kullanıcı sorusu
        user_question = request.POST.get('user_question', 'Bu reçeteyi analiz et')
        use_ocr_fallback = request.POST.get('use_ocr_fallback', 'true').lower() == 'true'
        
        # OCR servisi
        ocr_service = get_ocr_service()
        
        # OpenAI servisi (opsiyonel)
        openai_service = None
        try:
            openai_service = get_openai_service()
        except Exception as e:
            print(f"OpenAI service not available: {e}")
        
        # Analiz
        analysis = None
        ocr_text = None
        
        # OpenAI ile analiz et
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
            return JsonResponse({
                'success': False,
                'error': 'Hem OpenAI hem de OCR servisleri kullanılamıyor'
            }, status=503)
        
        processing_time = time.time() - start_time
        
        return JsonResponse({
            'success': True,
            'analysis': analysis.dict() if analysis else None,
            'ocr_text': ocr_text,
            'processing_time': processing_time
        })
        
    except Exception as e:
        processing_time = time.time() - start_time
        return JsonResponse({
            'success': False,
            'error': str(e),
            'processing_time': processing_time
        }, status=500)


@csrf_exempt
def extract_text(request: HttpRequest):
    """Sadece metin çıkarımı endpoint'i"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    
    if not OCR_AVAILABLE:
        return JsonResponse({
            'success': False,
            'error': 'OCR servisi kullanılamıyor'
        }, status=503)
    
    try:
        # Dosya kontrolü
        if 'file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Dosya yüklenmedi'
            }, status=400)
        
        uploaded_file = request.FILES['file']
        
        # Dosya validasyonu
        if uploaded_file.content_type and not uploaded_file.content_type.startswith('image/'):
            return JsonResponse({
                'success': False,
                'error': 'Sadece görsel dosyaları kabul edilir'
            }, status=400)
        
        # Dosyayı oku
        file_content = uploaded_file.read()
        image_base64 = base64.b64encode(file_content).decode('utf-8')
        
        # OCR kullan
        use_ocr = request.POST.get('use_ocr', 'true').lower() == 'true'
        
        text = ""
        method = ""
        
        if use_ocr:
            try:
                ocr_service = get_ocr_service()
                text = ocr_service.predict_from_base64(image_base64)
                method = "OCR"
            except Exception as e:
                print(f"OCR failed: {e}")
                text = ""
        
        if not text:
            # OpenAI fallback
            try:
                openai_service = get_openai_service()
                text = openai_service.extract_text_only(image_base64)
                method = "OpenAI"
            except Exception as e:
                print(f"OpenAI text extraction failed: {e}")
                text = ""
        
        if not text:
            return JsonResponse({
                'success': False,
                'error': 'Metin çıkarımı başarısız'
            }, status=503)
        
        return JsonResponse({
            'success': True,
            'text': text,
            'method': method
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def health_check(request: HttpRequest):
    """Sistem durumu kontrolü"""
    ocr_loaded = False
    openai_configured = False
    
    if OCR_AVAILABLE:
        try:
            ocr_service = get_ocr_service()
            ocr_loaded = ocr_service is not None
        except Exception:
            ocr_loaded = False
        
        try:
            openai_service = get_openai_service()
            openai_configured = openai_service is not None
        except Exception:
            openai_configured = False
    
    status = "healthy" if (ocr_loaded and openai_configured) else "degraded"
    if not ocr_loaded and not openai_configured:
        status = "unavailable"
    
    return JsonResponse({
        'status': status,
        'ocr_model_loaded': ocr_loaded,
        'openai_configured': openai_configured,
        'handwrite_available': OCR_AVAILABLE
    })