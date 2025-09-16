import re
from typing import List, Optional, Tuple, Set
from models import (
    MedicalReport,
    ReportInfo,
    PatientInfo,
    Note,
    Diagnosis,
    Doctor,
    Medication,
    AdditionalValue,
)

class MedicalReportParser:
    """Ham rapor metnini yapılandırılmış veriye dönüştüren parser"""
    
    def __init__(self):
        self.current_section = None
        
    def parse(self, text: str) -> MedicalReport:
        """Ana parse fonksiyonu"""
        # Normalize common spacing glitches
        text = re.sub(r"\t+", " ", text)
        lines = [ln.rstrip() for ln in text.strip().split('\n')]
        
        report_info = self._parse_report_info(lines)
        patient_info = self._parse_patient_info(lines)
        notes = self._parse_notes(lines)
        diagnoses = self._parse_diagnoses(lines)
        doctors = self._parse_doctors(lines)
        medications = self._parse_medications(lines)
        additional_values = self._parse_additional_values(lines)
        
        return MedicalReport(
            report_info=report_info,
            patient_info=patient_info,
            notes=notes,
            diagnoses=diagnoses,
            doctors=doctors,
            medications=medications,
            additional_values=additional_values,
        )

    def _parse_patient_info(self, lines: List[str]) -> Optional[PatientInfo]:
        """Cinsiyet ve doğum tarihi"""
        gender = None
        birth_date = None
        for line in lines[:10]:
            if "Cinsiyeti" in line or "Cinsiyet" in line:
                # Cinsiyeti :  Erkek   Doğum Tarihi :  01/04/1947
                g = re.search(r"Cinsiyet[ıi]\s*:\s*([A-Za-zÇĞİÖŞÜçğıöşü]+)", line)
                if g:
                    gender = g.group(1).strip()
                d = re.search(r"Doğum\s*Tarihi\s*:\s*(\d{2}[\./-]\d{2}[\./-]\d{4})", line)
                if d:
                    birth_date = d.group(1).replace('-', '/').replace('.', '/')
                break
        if gender or birth_date:
            return PatientInfo(gender=gender, birth_date=birth_date)
        return None
    
    def _parse_report_info(self, lines: List[str]) -> ReportInfo:
        """Rapor bilgilerini parse eder"""
        report_info = ReportInfo()
        
        for i, line in enumerate(lines):
            if "Rapor Bilgileri" in line:
                # Sonraki satırları kontrol et
                for j in range(i+1, min(i+15, len(lines))):
                    next_line = lines[j].strip()
                    if not next_line or "Tanı Bilgileri" in next_line or "Açıklamalar" in next_line:
                        break
                        
                    # Rapor numarası
                    if "Rapor Numarası" in next_line:
                        match = re.search(r'Rapor Numarası.*?:\s*(\d+)', next_line)
                        if match:
                            report_info.report_number = match.group(1)
                    
                    # Rapor tarihi
                    if "Rapor Tarihi" in next_line:
                        match = re.search(r'Rapor Tarihi.*?:\s*(\d{2}/\d{2}/\d{4})', next_line)
                        if match:
                            report_info.report_date = match.group(1)
                    
                    # Protokol numarası
                    if "Protokol No" in next_line:
                        match = re.search(r'Protokol No\s*:\s*(\d+)', next_line)
                        if match:
                            report_info.protocol_number = match.group(1)
                    
                    # Düzenleme türü
                    if "Düzenleme Türü" in next_line:
                        match = re.search(r'Düzenleme Türü\s*:\s*(.+)', next_line)
                        if match:
                            report_info.report_type = match.group(1).strip()
                    
                    # Açıklama
                    if "Açıklama" in next_line and ":" in next_line:
                        match = re.search(r'Açıklama\s*:\s*(.+)', next_line)
                        if match:
                            report_info.description = match.group(1).strip()
                    
                    # Kayıt şekli
                    if "Kayıt Şekli" in next_line:
                        match = re.search(r'Kayıt Şekli\s*:\s*(.+)', next_line)
                        if match:
                            report_info.record_type = match.group(1).strip()
                    
                    # Tesis kodu
                    if "Tesis Kodu" in next_line:
                        match = re.search(r'Tesis Kodu.*?:\s*(\d+)', next_line)
                        if match:
                            report_info.facility_code = match.group(1)
                    
                    # Rapor takip no
                    if "Rapor Takip No" in next_line:
                        match = re.search(r'Rapor Takip No\s*:\s*(\d+)', next_line)
                        if match:
                            report_info.tracking_number = match.group(1)
                    
                    # Tesis ünvanı
                    if "Tesis Ünvanı" in next_line:
                        match = re.search(r'Tesis Ünvanı\s*:\s*(.+)', next_line)
                        if match:
                            report_info.facility_name = match.group(1).strip()
                    
                    # Kullanıcı adı
                    if "Kullanıcı Adı" in next_line:
                        match = re.search(r'Kullanıcı Adı\s*:\s*(.+)', next_line)
                        if match:
                            report_info.username = match.group(1).strip()
                
                break
        
        return report_info
    
    def _parse_notes(self, lines: List[str]) -> List[Note]:
        """Açıklamaları parse eder"""
        notes = []
        
        for i, line in enumerate(lines):
            if "Açıklamalar" in line and "Eklenme Zamanı" in line:
                # Sonraki satırları kontrol et
                for j in range(i+1, len(lines)):
                    next_line = lines[j].strip()
                    if not next_line or "Tanı Bilgileri" in next_line:
                        break
                    
                    # Tarih ve içerik içeren satırları bul
                    if re.match(r'\d{2}/\d{2}/\d{4}', next_line):
                        parts = next_line.split()
                        if len(parts) >= 2:
                            date = parts[0]
                            time = parts[1] if len(parts) > 1 and ':' in parts[1] else None
                            content = ' '.join(parts[2:]) if len(parts) > 2 else ""
                            
                            if content and content != ".":
                                notes.append(Note(content=content, date=date, time=time))
        
        return notes
    
    def _parse_diagnoses(self, lines: List[str]) -> List[Diagnosis]:
        """Tanı bilgilerini parse eder"""
        diagnoses: List[Diagnosis] = []
        seen: Set[Tuple[str, str]] = set()
        
        for i, line in enumerate(lines):
            if "Tanı Bilgileri" in line:
                # Sonraki satırları kontrol et
                for j in range(i+1, len(lines)):
                    next_line = lines[j].strip()
                    if not next_line or "Doktor Bilgileri" in next_line:
                        break
                    
                    # ICD kodu ile başlayan satırları bul
                    if re.match(r'\d{2}\.\d{2}', next_line):
                        parts = next_line.split(' - ', 1)
                        if len(parts) == 2:
                            code = parts[0].strip()
                            description = parts[1].strip()
                            
                            # Sonraki satırda ICD kodu olabilir
                            if j + 1 < len(lines):
                                next_line_content = lines[j + 1].strip()
                                if re.match(r'^[A-Z]\d{2}\.', next_line_content):
                                    description += " " + next_line_content
                            
                            # Başlangıç ve bitiş tarihlerini bul
                            start_date = None
                            end_date = None
                            
                            # Sonraki satırlarda tarih aralığı ara
                            for k in range(j+1, min(j+5, len(lines))):
                                date_line = lines[k].strip()
                                if re.match(r'\d{2}/\d{2}/\d{4}', date_line):
                                    dates = re.findall(r'\d{2}/\d{2}/\d{4}', date_line)
                                    if len(dates) >= 2:
                                        start_date = dates[0]
                                        end_date = dates[1]
                                    break
                            
                            key = (code, description)
                            if key not in seen:
                                diagnoses.append(Diagnosis(
                                    code=code,
                                    description=description,
                                    start_date=start_date,
                                    end_date=end_date
                                ))
                                seen.add(key)
        
        return diagnoses
    
    def _parse_doctors(self, lines: List[str]) -> List[Doctor]:
        """Doktor bilgilerini parse eder (çoklu)"""
        doctors: List[Doctor] = []
        in_section = False
        for i, line in enumerate(lines):
            if "Doktor Bilgileri" in line:
                in_section = True
                continue
            if in_section:
                if "Rapor Etkin Madde Bilgileri" in line or line.strip() == "":
                    # boş satırı atla ama devam et; gerçek bitiş başka başlıktır
                    # bitiş koşulu: diğer ana başlıklar
                    pass
                if any(h in line for h in ["Rapor Etkin Madde Bilgileri", "Rapor İlave Değer Bilgileri", "Rapor Bilgileri", "Tanı Bilgileri"]):
                    break
                # Başlık satırını atla
                if "Dr." in line and "Diploma No" in line:
                    continue
                row = line.strip()
                if not row:
                    continue
                # Expect: <diploma> <reg> <specialty possibly spaced> <NAME UPPER...>
                m = re.match(r"^(\S+)\s+(\S+)\s+(.+)$", row)
                if m:
                    diploma = m.group(1)
                    reg = m.group(2)
                    rest_str = m.group(3).strip()
                    tokens = rest_str.split()
                    # Identify trailing uppercase tokens (Turkish uppercase supported)
                    def is_upper(tok: str) -> bool:
                        return tok.upper() == tok and re.search(r"[A-ZÇĞİÖŞÜ]", tok) is not None
                    # Collect from end until a non-uppercase token
                    name_tokens_rev = []
                    for tok in reversed(tokens):
                        if is_upper(tok):
                            name_tokens_rev.append(tok)
                        else:
                            break
                    name_tokens = list(reversed(name_tokens_rev)) if name_tokens_rev else tokens[-2:]
                    specialty_tokens = tokens[:len(tokens)-len(name_tokens)]
                    name = ' '.join(name_tokens).strip() or None
                    specialty = ' '.join(specialty_tokens).strip() or None
                    doctors.append(Doctor(
                        diploma_number=diploma,
                        registration_number=reg,
                        specialty=specialty,
                        name=name,
                    ))
        return doctors
    
    def _parse_medications(self, lines: List[str]) -> List[Medication]:
        """İlaç bilgilerini parse eder"""
        medications = []
        
        for i, line in enumerate(lines):
            if "Rapor Etkin Madde Bilgileri" in line:
                # Sonraki satırları kontrol et
                for j in range(i+1, len(lines)):
                    next_line = lines[j].strip()
                    if not next_line:
                        break
                    
                    # Tablo başlığı satırını atla
                    if "Kodu" in next_line and "Adı" in next_line:
                        continue
                    
                    # İlaç bilgilerini parse et - esnek yaklaşım
                    parts = next_line.split()
                    if len(parts) >= 6:
                        code = parts[0]
                        
                        # Tarih bilgisini bul ve ayır
                        date_index = -1
                        for i, part in enumerate(parts):
                            if re.match(r'\d{2}/\d{2}/\d{4}', part):
                                date_index = i
                                break
                        
                        if date_index > 0:
                            # Tarih öncesi kısımları parse et
                            drug_parts = parts[1:date_index]
                            # Heuristics: form ve şema anahtar kelimeleri
                            join_str = ' '.join(drug_parts)
                            # Split by double space if exists
                            tokens = drug_parts
                            # Name: ilk büyük harfli blok
                            name = tokens[0]
                            k = 1
                            while k < len(tokens) and tokens[k].isupper() or re.search(r"\d", tokens[k]):
                                name += " " + tokens[k]
                                k += 1
                            # Kalanı form+şema olarak kabul et
                            form = ' '.join(tokens[k:k+2]) if k < len(tokens) else ''
                            treatment_scheme = ' '.join(tokens[k+2:]) if k+2 <= len(tokens) else ''
                            
                            # Miktar (tarih öncesi son kısım)
                            quantity = ""
                            content = ""
                            
                            # Tarih ve zaman
                            added_time = ' '.join(parts[date_index:])
                            
                        else:
                            # Tarih bulunamadıysa basit parsing
                            name = parts[1] if len(parts) > 1 else ""
                            form = parts[2] if len(parts) > 2 else ""
                            treatment_scheme = parts[3] if len(parts) > 3 else ""
                            quantity = parts[4] if len(parts) > 4 else ""
                            content = parts[5] if len(parts) > 5 else ""
                            added_time = ""
                        
                        medications.append(Medication(
                            code=code,
                            name=name,
                            form=form,
                            treatment_scheme=treatment_scheme,
                            quantity=quantity,
                            content=content,
                            added_time=added_time
                        ))
        
        return medications

    def _parse_additional_values(self, lines: List[str]) -> List[AdditionalValue]:
        """Rapor İlave Değer Bilgileri bölümünü parse eder"""
        values: List[AdditionalValue] = []
        in_section = False
        for i, line in enumerate(lines):
            if "Rapor İlave Değer Bilgileri" in line:
                in_section = True
                continue
            if in_section:
                if any(h in line for h in ["Rapor Bilgileri", "Tanı Bilgileri", "Doktor Bilgileri", "Rapor Etkin Madde Bilgileri"]):
                    break
                row = line.strip()
                if not row or row.startswith("Türü"):
                    continue
                # Örn: Kilo 80.00  23/09/2024 15:47
                m = re.match(r"(.+?)\s+([\d\.,]+)\s+(\d{2}/\d{2}/\d{4})(?:\s+(\d{2}:\d{2}))?", row)
                if m:
                    v = AdditionalValue(
                        type=m.group(1).strip(),
                        value=m.group(2).strip(),
                        note=None,
                        added_time=(m.group(3) + (" " + m.group(4) if m.group(4) else ""))
                    )
                    values.append(v)
        return values
