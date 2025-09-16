from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class ReportInfo:
    """Rapor temel bilgileri"""
    report_number: Optional[str] = None
    report_date: Optional[str] = None
    protocol_number: Optional[str] = None
    report_type: Optional[str] = None
    description: Optional[str] = None
    record_type: Optional[str] = None
    facility_code: Optional[str] = None
    tracking_number: Optional[str] = None
    facility_name: Optional[str] = None
    username: Optional[str] = None

@dataclass
class PatientInfo:
    """Hasta demografik bilgileri"""
    gender: Optional[str] = None
    birth_date: Optional[str] = None

@dataclass
class Note:
    """Açıklama notları"""
    content: str
    date: Optional[str] = None
    time: Optional[str] = None

@dataclass
class Diagnosis:
    """Tanı bilgileri"""
    code: str
    description: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

@dataclass
class Doctor:
    """Doktor bilgileri"""
    diploma_number: Optional[str] = None
    registration_number: Optional[str] = None
    specialty: Optional[str] = None
    name: Optional[str] = None

@dataclass
class Medication:
    """İlaç bilgileri"""
    code: str
    name: str
    form: str
    treatment_scheme: str
    quantity: str
    content: Optional[str] = None
    added_time: Optional[str] = None

@dataclass
class AdditionalValue:
    """Rapor ilave değer bilgileri (örn. Kilo, HbA1c)"""
    type: str
    value: str
    note: Optional[str] = None
    added_time: Optional[str] = None

@dataclass
class MedicalReport:
    """Tam rapor yapısı"""
    report_info: ReportInfo
    patient_info: Optional[PatientInfo]
    notes: List[Note]
    diagnoses: List[Diagnosis]
    doctors: List[Doctor]
    medications: List[Medication]
    additional_values: List[AdditionalValue]
    
    def to_dict(self):
        """Raporu dictionary formatına dönüştür"""
        return {
            "report_info": {
                "report_number": self.report_info.report_number,
                "report_date": self.report_info.report_date,
                "protocol_number": self.report_info.protocol_number,
                "report_type": self.report_info.report_type,
                "description": self.report_info.description,
                "record_type": self.report_info.record_type,
                "facility_code": self.report_info.facility_code,
                "tracking_number": self.report_info.tracking_number,
                "facility_name": self.report_info.facility_name,
                "username": self.report_info.username
            },
            "patient_info": {
                "gender": self.patient_info.gender if self.patient_info else None,
                "birth_date": self.patient_info.birth_date if self.patient_info else None,
            },
            "notes": [
                {
                    "content": note.content,
                    "date": note.date,
                    "time": note.time
                } for note in self.notes
            ],
            "diagnoses": [
                {
                    "code": diag.code,
                    "description": diag.description,
                    "start_date": diag.start_date,
                    "end_date": diag.end_date
                } for diag in self.diagnoses
            ],
            "doctors": [
                {
                    "diploma_number": d.diploma_number,
                    "registration_number": d.registration_number,
                    "specialty": d.specialty,
                    "name": d.name
                } for d in self.doctors
            ],
            "medications": [
                {
                    "code": med.code,
                    "name": med.name,
                    "form": med.form,
                    "treatment_scheme": med.treatment_scheme,
                    "quantity": med.quantity,
                    "content": med.content,
                    "added_time": med.added_time
                } for med in self.medications
            ],
            "additional_values": [
                {
                    "type": av.type,
                    "value": av.value,
                    "note": av.note,
                    "added_time": av.added_time
                } for av in self.additional_values
            ]
        }
