from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List, Tuple

import cv2  # type: ignore
import numpy as np

RNG_SEED = 1234


def _set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


@dataclass
class Sample:
    image_path: str
    label: str


class JsonlDataset:
    def __init__(self, jsonl_path: Path, shuffle: bool = False, seed: int = RNG_SEED) -> None:
        self.jsonl_path = jsonl_path
        self.shuffle = shuffle
        self.seed = seed
        self.samples: List[Sample] = []
        self._load()

    def _load(self) -> None:
        with open(self.jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                self.samples.append(Sample(rec["image_path"], rec["label"]))
        if self.shuffle:
            rnd = random.Random(self.seed)
            rnd.shuffle(self.samples)

    def __len__(self) -> int:
        return len(self.samples)

    def __iter__(self) -> Iterator[Sample]:
        return iter(self.samples)


def read_image_bgr(path: str) -> np.ndarray:
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(path)
    return img


def resize_keep_ratio(img: np.ndarray, target_h: int = 48, max_w: int = 512) -> np.ndarray:
    h, w = img.shape[:2]
    scale = target_h / float(h)
    new_w = min(int(w * scale), max_w)
    out = cv2.resize(img, (new_w, target_h), interpolation=cv2.INTER_AREA)
    return out


def pad_to_width(img: np.ndarray, width: int = 512) -> np.ndarray:
    h, w = img.shape[:2]
    if w >= width:
        return img[:, :width]
    pad = np.full((h, width - w, 3), 255, dtype=np.uint8)
    return np.concatenate([img, pad], axis=1)


def basic_augment(img: np.ndarray, rng: random.Random) -> np.ndarray:
    # light blur
    if rng.random() < 0.3:
        k = rng.choice([3, 5])
        img = cv2.GaussianBlur(img, (k, k), 0)
    # brightness/contrast
    if rng.random() < 0.5:
        alpha = rng.uniform(0.9, 1.1)
        beta = rng.uniform(-12, 12)
        img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    return img


def make_batch(dataset: JsonlDataset, batch_size: int = 16, augment: bool = True, seed: int = RNG_SEED) -> Tuple[np.ndarray, List[str]]:
    _set_seed(seed)
    rng = random.Random(seed)
    imgs: List[np.ndarray] = []
    labels: List[str] = []

    for i, s in enumerate(dataset):
        if i >= batch_size:
            break
        img = read_image_bgr(s.image_path)
        if augment:
            img = basic_augment(img, rng)
        img = resize_keep_ratio(img, target_h=48, max_w=512)
        img = pad_to_width(img, width=512)
        imgs.append(img)
        labels.append(s.label)

    batch = np.stack(imgs, axis=0)  # (N, H, W, C)
    return batch, labels


def save_grid(batch_bgr: np.ndarray, labels: List[str], out_path: Path, cols: int = 4) -> None:
    n, h, w, c = batch_bgr.shape
    rows = (n + cols - 1) // cols
    pad = 8
    grid_h = rows * h + (rows + 1) * pad
    grid_w = cols * w + (cols + 1) * pad

    canvas = np.full((grid_h, grid_w, 3), 255, dtype=np.uint8)
    font = cv2.FONT_HERSHEY_SIMPLEX

    for idx in range(n):
        r = idx // cols
        cidx = idx % cols
        y = pad + r * (h + pad)
        x = pad + cidx * (w + pad)
        canvas[y:y + h, x:x + w] = batch_bgr[idx]
        # put label (cropped)
        txt = labels[idx][:40]
        cv2.putText(canvas, txt, (x + 5, y + h - 8), font, 0.4, (0, 0, 0), 1, cv2.LINE_AA)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), canvas)

