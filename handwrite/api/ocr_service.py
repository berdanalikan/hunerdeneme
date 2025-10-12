"""
OCR Service - Mevcut CRNN modelini kullanarak OCR işlemleri
"""
import base64
import io
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np
import paddle
from PIL import Image

from scripts.model_crnn import CRNNCTC
from scripts.data_pipeline import resize_keep_ratio, pad_to_width


class OCRService:
    def __init__(self, checkpoint_path: str = "checkpoints/crnn_ctc_best.pdparams"):
        self.checkpoint_path = Path(checkpoint_path)
        self.charset_path = Path("checkpoints/charset.txt")
        self.model = None
        self.charset = ""
        self.char_to_idx = {}
        self.idx_to_char = {}
        self._load_model()
    
    def _load_model(self):
        """Model ve charset'i yükle"""
        # Charset'i yükle
        with open(self.charset_path, 'r', encoding='utf-8') as f:
            self.charset = f.read().strip()
        
        # Karakter mapping'leri oluştur
        self.char_to_idx = {c: i + 1 for i, c in enumerate(self.charset)}  # +1 for CTC blank
        self.idx_to_char = {i + 1: c for i, c in enumerate(self.charset)}
        self.idx_to_char[0] = ''  # CTC blank
        
        # Model'i yükle
        num_classes = len(self.charset) + 1  # +1 for CTC blank
        self.model = CRNNCTC(num_classes)
        
        # Checkpoint'i yükle
        if self.checkpoint_path.exists():
            state_dict = paddle.load(str(self.checkpoint_path))
            self.model.set_state_dict(state_dict)
            self.model.eval()
            print(f"Model loaded from {self.checkpoint_path}")
        else:
            raise FileNotFoundError(f"Checkpoint not found: {self.checkpoint_path}")
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Görüntüyü model için hazırla"""
        # BGR'den RGB'ye çevir
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Boyutlandır ve pad'le
        image = resize_keep_ratio(image, target_h=48, max_w=512)
        image = pad_to_width(image, width=512)
        
        # Normalize et (0-1 arası)
        image = image.astype(np.float32) / 255.0
        
        # Batch dimension ekle ve channel first yap
        image = np.transpose(image, (2, 0, 1))  # (C, H, W)
        image = np.expand_dims(image, axis=0)  # (1, C, H, W)
        
        return image
    
    def decode_ctc(self, logits: np.ndarray) -> str:
        """CTC çıktısını metne çevir"""
        # Greedy decoding
        predictions = np.argmax(logits, axis=-1)  # (T,)
        
        # CTC decoding - blank'leri ve tekrarları kaldır
        decoded = []
        prev_char = -1
        
        for char_idx in predictions:
            if char_idx != prev_char and char_idx != 0:  # 0 is blank
                decoded.append(self.idx_to_char.get(char_idx, ''))
            prev_char = char_idx
        
        return ''.join(decoded)
    
    def predict(self, image: np.ndarray) -> str:
        """Görüntüden metin çıkar"""
        # Preprocess
        processed_image = self.preprocess_image(image)
        
        # Paddle tensor'a çevir
        input_tensor = paddle.to_tensor(processed_image)
        
        # Inference
        with paddle.no_grad():
            logits = self.model(input_tensor)  # (T, 1, num_classes)
            logits = logits.squeeze(1)  # (T, num_classes)
            logits_np = logits.numpy()
        
        # Decode
        text = self.decode_ctc(logits_np)
        return text.strip()
    
    def predict_from_base64(self, base64_image: str) -> str:
        """Base64 encoded görüntüden metin çıkar"""
        # Base64'ü decode et
        image_data = base64.b64decode(base64_image)
        image = Image.open(io.BytesIO(image_data))
        image_np = np.array(image)
        
        return self.predict(image_np)
    
    def predict_from_file(self, image_path: str) -> str:
        """Dosyadan görüntü okuyup metin çıkar"""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        return self.predict(image)


# Global OCR service instance
ocr_service = None

def get_ocr_service() -> OCRService:
    """Singleton OCR service instance"""
    global ocr_service
    if ocr_service is None:
        ocr_service = OCRService()
    return ocr_service
