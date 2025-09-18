## Hünerdeneme - Sistem Mimarisi ve İş Akışları

Bu doküman, depo içeriğinden otomatik çıkarılan yüksek seviyeli mimariyi ve uçtan uca iş akışlarını içerir. Diyagramlar Mermaid sözdizimi ile verilmiştir ve GitHub üzerinde doğrudan görüntülenebilir.

### 1) Yüksek Seviye Mimarî
```mermaid
flowchart LR
  subgraph Client["Kullanıcı (Tarayıcı/CLI)"]
    UI[Web UI (templates/index.html)]
    CLI[CLI (main.py)]
  end

  subgraph Django["Django Web Uygulaması"]
    V1[GET / (index)]
    V2[POST /evaluate/]
    V3[POST /feedback/]
  end

  subgraph Core["Çekirdek Mantık"]
    P[parser.py <br/> MedicalReportParser]
    M[models.py <br/> MedicalReport + DTOs]
    OA[openai_client.py <br/> MedicalReportAssistantClient]
  end

  subgraph Ops["Operasyonlar"]
    DIG[dynamic_instruction_generator.py]
    MON[monitoring.py]
    CRON[cron_manager.sh]
  end

  subgraph Ext["Dış Servisler / Artefaktlar"]
    SB[Supabase <br/> feedback, request_log]
    OAI[OpenAI API <br/> Assistants + Chat]
    FS[Yerel Dosyalar <br/> *_structured.json, *_evaluation.json, <br/> monitoring_report_*.md, <br/> instruction_update_history.json]
  end

  UI -->|form POST| V2
  V1 --> UI
  V2 --> P --> M
  V2 -->|opsiyonel| OA --> OAI
  V2 --> SB
  V3 --> SB

  CLI --> P --> M
  CLI -->|opsiyonel| OA --> OAI
  CLI --> FS

  DIG --> SB
  DIG --> OAI
  DIG --> FS

  MON --> SB
  MON --> OAI
  MON --> FS

  CRON --> MON
  CRON --> DIG
```

### 2) Uçtan Uca İş Akışı
```mermaid
flowchart TD
  A[Web veya CLI Girdi] --> B{Kaynak}
  B -- Web --> C1[POST /evaluate/]
  B -- CLI --> C2[main.py]

  subgraph Parse["Parse ve Yapılandırma"]
    P1[parser.parse(text)]
    P2[MedicalReport (models.py)]
  end

  C1 --> P1 --> P2
  C2 --> P1 --> P2

  subgraph Eval["OpenAI Değerlendirme (opsiyonel)"]
    E1{Env: OPENAI_API_KEY ve OPENAI_ASSISTANT_ID var mı}
    E2[_prepare_message_content (TR prompt)]
    E3[Threads.create -> messages.create(user)]
    E4[Runs.create -> poll -> messages.list(assistant)]
  end

  P2 --> E1
  E1 -- Hayır --> S1[Değerlendirme atlanır]
  E1 -- Evet --> E2 --> E3 --> E4

  subgraph Out["Çıktılar ve Kayıt"]
    O1[Web JSON: structured + assistant]
    O2[CLI: *_structured.json + *_evaluation.json]
    O3[request_log (Supabase)]
  end

  E4 --> O1
  S1 --> O1
  C2 --> O2
  C1 --> O3

  subgraph FB["Feedback Döngüsü"]
    F1[POST /feedback/]
    F2[Map: correct/incorrect -> dogru/yanlis]
    F3[feedback tablosuna insert]
  end

  O1 --> F1 --> F2 --> F3

  subgraph DynIns["Dinamik Instructions Güncelleme"]
    D1[Supabase feedback -> get_feedback_analysis(7g)]
    D2{OpenAI üretim başarılı mı}
    D3[generate_instructions_with_openai]
    D4[generate_dynamic_instructions (heuristic)]
    D5[assistants.update(instructions)]
    D6[instruction_update_history.json]
  end

  F3 --> D1
  D1 --> D2
  D2 -- Evet --> D3 --> D5 --> D6
  D2 -- Hayır --> D4 --> D5 --> D6

  subgraph Mon["Monitoring ve Alerting"]
    M1[Supabase son 7g feedback -> metrikler]
    M2{Eşikler aşıldı mı}
    M3[Alert: Telegram veya Email]
    M4[monitoring_report_YYYYMMDD_HHMM.md]
    M5[Exit: healthy=0 | warning=1 | critical=2 | hata=3]
  end

  M1 --> M2
  M2 -- Evet --> M3
  M1 --> M4 --> M5
```

### 3) HTTP Uç Noktaları
- GET `/` → `index.html`
- POST `/evaluate/` → `{ structured, assistant }`
- POST `/feedback/` → `{ ok: true }` ya da hata açıklaması

### 4) Ortam Değişkenleri (kritik)
- `OPENAI_API_KEY`, `OPENAI_ASSISTANT_ID`
- `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` (veya `SUPABASE_KEY`)
- (Monitoring) `ALERT_EMAIL_*`, `TELEGRAM_*`
- (Django) `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`

Bu dosya, deponun mevcut kodlarından otomatik çıkarılmıştır ve değişikliklerle birlikte güncellenmelidir.


