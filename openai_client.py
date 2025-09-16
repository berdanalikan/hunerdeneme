import json
import os
from typing import Dict, Any, Optional
from openai import OpenAI
from models import MedicalReport
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

class MedicalReportAssistantClient:
    """OpenAI Assistant API ile rapor değerlendirme client'ı"""
    
    def __init__(self, api_key: Optional[str] = None, assistant_id: Optional[str] = None):
        """
        OpenAI client'ını başlatır
        
        Args:
            api_key: OpenAI API anahtarı (None ise OPENAI_API_KEY env var kullanılır)
            assistant_id: Assistant ID'si (None ise OPENAI_ASSISTANT_ID env var kullanılır)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.assistant_id = assistant_id or os.getenv('OPENAI_ASSISTANT_ID')
        
        if not self.api_key:
            raise ValueError("OpenAI API key bulunamadı. OPENAI_API_KEY environment variable'ını ayarlayın.")
        
        if not self.assistant_id:
            raise ValueError("Assistant ID bulunamadı. OPENAI_ASSISTANT_ID environment variable'ını ayarlayın.")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def evaluate_report(self, medical_report: MedicalReport) -> Dict[str, Any]:
        """
        Tıbbi raporu değerlendirir
        
        Args:
            medical_report: Değerlendirilecek tıbbi rapor
            
        Returns:
            Değerlendirme sonucu
        """
        try:
            # Raporu JSON formatına dönüştür
            report_data = medical_report.to_dict()
            
            # Assistant'a gönderilecek mesajı hazırla
            message_content = self._prepare_message_content(report_data)
            
            # Thread oluştur
            thread = self.client.beta.threads.create()
            
            # Mesaj gönder
            message = self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=message_content
            )
            
            # Assistant'ı çalıştır
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.assistant_id
            )
            
            # Sonucu bekle
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            
            # Tamamlanana kadar bekle
            while run.status in ['queued', 'in_progress', 'cancelling']:
                import time
                time.sleep(1)
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
            
            if run.status == 'completed':
                # Assistant yanıtını al (assistant rolündeki ilk mesaj)
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread.id
                )

                assistant_text = None
                for msg in messages.data:
                    if getattr(msg, 'role', None) == 'assistant' and msg.content:
                        # Metin içeriğini birleştir
                        parts = []
                        for c in msg.content:
                            if getattr(c, 'type', '') == 'text':
                                parts.append(c.text.value)
                        assistant_text = "\n\n".join(parts).strip() if parts else None
                        if assistant_text:
                            break

                if assistant_text:
                    return {
                        "status": "success",
                        "evaluation": assistant_text,
                        "thread_id": thread.id
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Assistant yanıtı bulunamadı (assistant rolü).",
                        "thread_id": thread.id
                    }
            else:
                return {
                    "status": "error",
                    "message": f"Assistant çalıştırılamadı: {run.status}",
                    "error": run.last_error
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Değerlendirme sırasında hata oluştu: {str(e)}"
            }
    
    def _prepare_message_content(self, report_data: Dict[str, Any]) -> str:
        """
        Rapor verilerini assistant'a düz metin (insan okunur) formatta gönderir.
        Yanıt dilinin Türkçe olması için yönerge ekler.
        """
        content = "Lütfen aşağıdaki yapılandırılmış tıbbi raporu SADECE TÜRKÇE olarak, SUT/SGK mevzuatına göre değerlendiriniz.\n\n"

        # Rapor bilgileri
        content += "=== RAPOR BİLGİLERİ ===\n"
        report_info = report_data.get("report_info", {})
        for key, value in report_info.items():
            if value:
                content += f"{key}: {value}\n"

        # Hasta bilgileri
        patient = report_data.get("patient_info", {})
        if patient:
            content += "\n=== HASTA BİLGİLERİ ===\n"
            for key, value in patient.items():
                if value:
                    content += f"{key}: {value}\n"

        # Tanılar
        content += "\n=== TANI BİLGİLERİ ===\n"
        for diag in report_data.get("diagnoses", []):
            content += f"Kod: {diag.get('code','')}\n"
            content += f"Açıklama: {diag.get('description','')}\n"
            if diag.get('start_date'):
                content += f"Başlangıç: {diag['start_date']}\n"
            if diag.get('end_date'):
                content += f"Bitiş: {diag['end_date']}\n"
            content += "\n"

        # Doktorlar
        if report_data.get("doctors"):
            content += "=== DOKTOR BİLGİLERİ ===\n"
            for d in report_data.get("doctors", []):
                line = []
                if d.get('name'): line.append(d['name'])
                if d.get('specialty'): line.append(d['specialty'])
                if d.get('diploma_number') or d.get('registration_number'):
                    line.append(f"({d.get('diploma_number','')}/{d.get('registration_number','')})")
                content += " ".join([p for p in line if p]) + "\n"
            content += "\n"

        # İlaçlar
        if report_data.get("medications"):
            content += "=== İLAÇLAR ===\n"
            for med in report_data.get("medications", []):
                content += f"{med.get('code','')} | {med.get('name','')} | {med.get('form','')} | {med.get('treatment_scheme','')} | {med.get('quantity','')}\n"
            content += "\n"

        # İlave değerler
        if report_data.get("additional_values"):
            content += "=== İLAVE DEĞERLER ===\n"
            for av in report_data.get("additional_values", []):
                content += f"{av.get('type')}: {av.get('value')} {f'({av.get("added_time")})' if av.get('added_time') else ''}\n"
            content += "\n"

        # Açıklamalar
        if report_data.get("notes"):
            content += "=== AÇIKLAMALAR ===\n"
            for note in report_data.get("notes", []):
                if note.get('content') and note.get('content') != ".":
                    content += f"- {note.get('date','')}: {note['content']}\n"

        content += "\nLütfen yanıtı sadece Türkçe verin ve şu başlıklarla raporlayın: Özet, Tanı Özeti, İlaç Bazlı Değerlendirme, Eksik Bilgi/Gerekli Belgeler, Mevzuat Dayanakları, Son Karar."
        return content
    
    def get_thread_messages(self, thread_id: str) -> list:
        """
        Thread'deki mesajları getirir
        
        Args:
            thread_id: Thread ID'si
            
        Returns:
            Mesaj listesi
        """
        try:
            messages = self.client.beta.threads.messages.list(
                thread_id=thread_id
            )
            return [msg.content[0].text.value for msg in messages.data]
        except Exception as e:
            print(f"Mesajlar alınırken hata: {str(e)}")
            return []
