## Hünerdeneme - Sistem Mimarisi ve İş Akışları

Bu doküman, depo içeriğinden otomatik çıkarılan yüksek seviyeli mimariyi ve uçtan uca iş akışlarını içerir. Diyagramlar Mermaid sözdizimi ile verilmiştir ve GitHub üzerinde doğrudan görüntülenebilir.

### 1) Yüksek Seviye Mimarî
```mermaid
flowchart LR
  subgraph Client[Istemci]
    UI[Web Arayuzu]
    CLI[Komut Satiri]
  end

  subgraph Django[Django Uygulamasi]
    V1[GET ana sayfa]
    V2[POST evaluate]
    V3[POST feedback]
  end

  subgraph Core[Cekirdek Mantik]
    P[parser py Rapor Ayristirici]
    M[models py MedicalReport ve DTOLAR]
    OA[openai client py Asistan Istemcisi]
  end

  subgraph Ops[Operasyonlar]
    DIG[dinamik talimat olusturucu]
    MON[izleme]
    CRON[cron yonetimi]
  end

  subgraph Ext[Dis Servisler]
    SB[Supabase]
    OAI[OpenAI API]
    FS[Yerel Dosyalar]
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
  A[Web veya CLI girdisi] --> B{Kaynak}
  B -- Web --> C1[POST evaluate]
  B -- CLI --> C2[CLI main]

  subgraph Parse[Parse ve Yapilandirma]
    P1[parser metni ayrisir]
    P2[MedicalReport modelleri]
  end

  C1 --> P1 --> P2
  C2 --> P1 --> P2

  subgraph Eval[OpenAI Degerlendirme opsiyonel]
    E1{Env anahtarlari mevcut mu}
    E2[mesaj icerigi hazirla]
    E3[thread ve kullanici mesaji olustur]
    E4[assistant calistir yaniti cek]
  end

  P2 --> E1
  E1 -- Hayir --> S1[Degerlendirme atlanir]
  E1 -- Evet --> E2 --> E3 --> E4

  subgraph Out[Ciktilar ve Kayitlar]
    O1[Web JSON sonucu]
    O2[CLI json dosyalari]
    O3[Supabase istek gunlugu]
  end

  E4 --> O1
  S1 --> O1
  C2 --> O2
  C1 --> O3

  subgraph FB[Geribildirim Dongusu]
    F1[POST feedback]
    F2[dogru veya yanlis]
    F3[feedback tablosuna ekle]
  end

  O1 --> F1 --> F2 --> F3

  subgraph DynIns[Dinamik Talimat Guncelleme]
    D1[7 gun geribildirim analiz]
    D2{OpenAI uretim basarili mi}
    D3[OpenAI ile uret]
    D4[heuristic uretim]
    D5[assistant guncelle]
    D6[gecmis dosyasina yaz]
  end

  F3 --> D1
  D1 --> D2
  D2 -- Evet --> D3 --> D5 --> D6
  D2 -- Hayir --> D4 --> D5 --> D6

  subgraph Mon[Izleme ve Uyarilar]
    M1[Metrikleri hesapla]
    M2{Esikler asildi mi}
    M3[Uyari gonder]
    M4[Rapor yaz]
    M5[Cikis kodlari]
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


