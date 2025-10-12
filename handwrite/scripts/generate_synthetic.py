import os
import json
import random
import string
from pathlib import Path

import cv2  # type: ignore
import numpy as np
from PIL import Image, ImageDraw, ImageFont

DATA_ROOT = Path("data")
RAW_DIR = DATA_ROOT / "raw"
LABELS_DIR = DATA_ROOT / "labels"
LABELS_FILE = LABELS_DIR / "label.jsonl"

# A small pool of Turkish phrases and words
TURKISH_PHRASES = [
    "merhaba dunya",
    "el yazisi ornek",
    "paddle ocr",
    "hizli kahverengi tilki",
    "bugun hava guzel",
    "istanbul ankara izmir",
    "ogrenci karti",
    "fatura numarasi 12345",
    "tarih 09.10.2025",
    "turkce karakterler cigosu",
    "sifre 4bC9x",
    "ev adresi sokak no 5",
    "telefon 5551234567",
    "yapay zeka",
    "optik karakter tanima",
]

# Fallback font (PIL default). Optionally try some common system fonts on macOS.
CANDIDATE_FONTS = [
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Courier New.ttf",
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
    "/System/Library/Fonts/Supplemental/Verdana.ttf",
]


def pick_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in CANDIDATE_FONTS:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def random_text() -> str:
    # 70% phrases, 30% random word/numeric mix
    if random.random() < 0.7:
        return random.choice(TURKISH_PHRASES)
    # random short token
    token_len = random.randint(4, 10)
    alphabet = string.ascii_lowercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(token_len))


def render_text_image(text: str, img_w: int = 512, img_h: int = 128) -> Image.Image:
    bg = Image.new("RGB", (img_w, img_h), (255, 255, 255))
    draw = ImageDraw.Draw(bg)

    # random font size, position, color
    font_size = random.randint(28, 44)
    font = pick_font(font_size)
    text_color = (0, 0, 0)

    # compute text size and center-left alignment with some padding
    tw, th = draw.textbbox((0, 0), text, font=font)[2:]
    pad_x = random.randint(10, 30)
    pad_y = max(0, (img_h - th) // 2 + random.randint(-10, 10))
    draw.text((pad_x, pad_y), text, fill=text_color, font=font)

    return bg


def to_cv(image: Image.Image) -> np.ndarray:
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def augment(img: np.ndarray) -> np.ndarray:
    # random small rotation, perspective, blur, noise, brightness/contrast
    h, w = img.shape[:2]

    # rotation
    if random.random() < 0.7:
        angle = random.uniform(-5, 5)
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        img = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR, borderValue=(255, 255, 255))

    # blur
    if random.random() < 0.4:
        k = random.choice([3, 5])
        img = cv2.GaussianBlur(img, (k, k), 0)

    # brightness/contrast
    if random.random() < 0.5:
        alpha = random.uniform(0.9, 1.1)  # contrast
        beta = random.uniform(-15, 15)    # brightness
        img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

    # noise
    if random.random() < 0.4:
        noise = np.random.normal(0, random.uniform(3, 8), img.shape).astype(np.float32)
        img = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)

    # slight perspective warp
    if random.random() < 0.3:
        margin = 10
        src = np.float32([[0, 0], [w - 1, 0], [0, h - 1], [w - 1, h - 1]])
        dst = src.copy()
        dst += np.float32([
            [random.uniform(-margin, margin), random.uniform(-margin, margin)],
            [random.uniform(-margin, margin), random.uniform(-margin, margin)],
            [random.uniform(-margin, margin), random.uniform(-margin, margin)],
            [random.uniform(-margin, margin), random.uniform(-margin, margin)],
        ])
        M = cv2.getPerspectiveTransform(src, dst)
        img = cv2.warpPerspective(img, M, (w, h), borderValue=(255, 255, 255))

    return img


def main(num_samples: int = 200) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    LABELS_DIR.mkdir(parents=True, exist_ok=True)

    with open(LABELS_FILE, "w", encoding="utf-8") as f:
        for idx in range(num_samples):
            text = random_text()
            pil_img = render_text_image(text)
            img = augment(to_cv(pil_img))

            img_name = f"synth_{idx:04d}.jpg"
            img_path = RAW_DIR / img_name
            cv2.imwrite(str(img_path), img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

            record = {
                "image_path": str(img_path.as_posix()),
                "label": text,
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Generated {num_samples} samples.")
    print(f"Images in: {RAW_DIR}")
    print(f"Labels at: {LABELS_FILE}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--num", type=int, default=200, help="Number of samples to generate")
    args = parser.parse_args()
    main(args.num)

