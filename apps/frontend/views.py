from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path
import os
import json
from parser import MedicalReportParser
from openai_client import MedicalReportAssistantClient
from models import MedicalReport
from typing import Optional

try:
    from supabase import create_client, Client as SupabaseClient
except Exception:
    create_client = None
    SupabaseClient = None


def _get_supabase_client() -> Optional["SupabaseClient"]:
    url = os.getenv('SUPABASE_URL')
    # Tercihen sunucu tarafında SERVICE_KEY kullan (RLS'i aşmak için güvenli yöntem)
    key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_KEY')
    if not (url and key) or not create_client:
        return None
    try:
        return create_client(url, key)
    except Exception:
        return None


def index(request: HttpRequest):
    return render(request, 'index.html')


@csrf_exempt
def evaluate_report(request: HttpRequest):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    text = request.POST.get('report_text', '')
    if not text:
        upload = request.FILES.get('report_file')
        if upload:
            try:
                text = upload.read().decode('utf-8', errors='ignore')
            except Exception:
                return JsonResponse({'error': 'Dosya okunamadı. UTF-8 metin bekleniyor.'}, status=400)

    if not text.strip():
        return JsonResponse({'error': 'Rapor metni boş. Metin yapıştırın veya bir dosya yükleyin.'}, status=400)

    parser = MedicalReportParser()
    try:
        report = parser.parse(text)
    except Exception as e:
        return JsonResponse({'error': f'Parse hatası: {str(e)}'}, status=500)

    result = {
        'structured': report.to_dict(),
    }

    api_key = os.getenv('OPENAI_API_KEY')
    assistant_id = os.getenv('OPENAI_ASSISTANT_ID')
    try:
        if api_key and assistant_id:
            client = MedicalReportAssistantClient()
            evaluation = client.evaluate_report(report)
            result['assistant'] = evaluation
        else:
            result['assistant'] = {'status': 'skipped', 'message': 'API credentials missing'}
    except Exception as e:
        result['assistant'] = {'status': 'error', 'message': str(e)}

    # Supabase'e konuşma kaydı (opsiyonel)
    # Not: Artık konuşma kaydı eklemiyoruz; sadece /feedback üzerinde minimal alanlar kaydedilecek

    return JsonResponse(result)


@csrf_exempt
def submit_feedback(request: HttpRequest):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        payload = {}

    status_val = payload.get('status')  # 'correct' | 'incorrect'
    reasons = payload.get('reasons', [])  # list[str]
    comment = payload.get('comment')  # optional str
    context = payload.get('context', {})  # structured report/evaluation/thread ids
    input_text = (context or {}).get('input_text')
    assistant_text = (context or {}).get('assistant_text')

    if status_val not in ['correct', 'incorrect']:
        return JsonResponse({'error': 'status must be correct|incorrect'}, status=400)

    # Zorunlu alan: tablo şemasında kullanici_girdisi NOT NULL
    if not input_text or not str(input_text).strip():
        return JsonResponse({'error': 'input_text missing in context for feedback'}, status=400)

    sb = _get_supabase_client()
    if not sb:
        return JsonResponse({'error': 'Supabase not configured'}, status=500)

    try:
        # Tablo: huner_feedback, kolonlar Türkçe enum/değerler bekliyor
        tr_status = 'dogru' if status_val == 'correct' else 'yanlis'
        # Minimal tablo: kullanıcı mesajı, dönen cevap, feedback durumu, nedeni (negatifse)
        # Tablo artık minimal: kullanici_girdisi, asistan_cevabi, geri_bildirim, neden
        data = {
            'kullanici_girdisi': input_text,
            'asistan_cevabi': assistant_text,
            'geri_bildirim': tr_status,
        }
        if tr_status == 'yanlis':
            data['neden'] = (', '.join(reasons) if reasons else None)
            if comment and str(comment).strip():
                data['neden_aciklama'] = comment.strip()
        sb.table('feedback').insert(data).execute()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'error': f'Supabase insert failed: {str(e)}'}, status=500)

# Create your views here.
