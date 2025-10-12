## Handwritten OCR (PaddleOCR Fine-tuning)

Bu proje, PaddleOCR tabanlı el yazısı tanıma sistemi için veri hazırlama, model fine-tuning, değerlendirme, entegrasyon ve yayınlama adımlarını içerir.

- docs/goals-metrics.md: Proje hedefleri, başarı metrikleri, kapsam ve riskler
- requirements.txt: Uygulama bağımlılıkları
- scripts/setup_env.sh: Ortam kurulum betiği (venv + bağımlılıklar)
- scripts/verify_env.py: GPU ve Paddle doğrulama testi

### Hızlı Başlangıç

1) Ortamı kurun:
```bash
bash scripts/setup_env.sh
```

2) Ortamı doğrulayın:
```bash
source .venv/bin/activate
python scripts/verify_env.py
```

3) Sonraki adımlar:
- Veri toplama/etiketleme
- Fine-tuning ve değerlendirme
- API ve basit UI
- Docker ile paketleme ve staging dağıtım

