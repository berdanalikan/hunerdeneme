## Hünerdeneme - Sistem Mimarisi ve İş Akışları

Bu doküman, depo içeriğinden otomatik çıkarılan yüksek seviyeli mimariyi ve uçtan uca iş akışlarını içerir. Diyagramlar Mermaid sözdizimi ile verilmiştir ve GitHub üzerinde doğrudan görüntülenebilir.

### 1) Yüksek Seviye Mimarî
```mermaid
flowchart LR
  subgraph Client[Client]
    UI[Web UI]
    CLI[CLI]
  end

  subgraph Django[Django App]
    V1[GET root]
    V2[POST evaluate]
    V3[POST feedback]
  end

  subgraph Core[Core Logic]
    P[parser py MedicalReportParser]
    M[models py MedicalReport and DTOs]
    OA[openai client py AssistantClient]
  end

  subgraph Ops[Operations]
    DIG[dynamic instruction generator]
    MON[monitoring]
    CRON[cron manager]
  end

  subgraph Ext[External Services]
    SB[Supabase]
    OAI[OpenAI API]
    FS[Local Files]
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
  A[Input from Web or CLI] --> B{Source}
  B -- Web --> C1[POST evaluate]
  B -- CLI --> C2[CLI main]

  subgraph Parse[Parse and Structure]
    P1[parser parse text]
    P2[MedicalReport models]
  end

  C1 --> P1 --> P2
  C2 --> P1 --> P2

  subgraph Eval[OpenAI Evaluation optional]
    E1{Env keys present}
    E2[prepare message content]
    E3[create thread and user message]
    E4[run assistant and fetch reply]
  end

  P2 --> E1
  E1 -- No --> S1[Skip evaluation]
  E1 -- Yes --> E2 --> E3 --> E4

  subgraph Out[Outputs and Logging]
    O1[Web JSON result]
    O2[CLI json files]
    O3[Supabase request log]
  end

  E4 --> O1
  S1 --> O1
  C2 --> O2
  C1 --> O3

  subgraph FB[Feedback Loop]
    F1[POST feedback]
    F2[Map to dogru or yanlis]
    F3[Insert to feedback table]
  end

  O1 --> F1 --> F2 --> F3

  subgraph DynIns[Dynamic Instructions Update]
    D1[Analyze feedback 7d]
    D2{OpenAI generation ok}
    D3[generate with OpenAI]
    D4[heuristic generation]
    D5[update assistant]
    D6[write history file]
  end

  F3 --> D1
  D1 --> D2
  D2 -- Yes --> D3 --> D5 --> D6
  D2 -- No --> D4 --> D5 --> D6

  subgraph Mon[Monitoring and Alerts]
    M1[Compute metrics]
    M2{Thresholds violated}
    M3[Send alert]
    M4[Write monitoring report]
    M5[Exit codes]
  end

  M1 --> M2
  M2 -- Yes --> M3
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


