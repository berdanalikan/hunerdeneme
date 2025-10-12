from pathlib import Path
from scripts.data_pipeline import JsonlDataset, make_batch, save_grid

TRAIN_JSONL = Path("data/labels/train.jsonl")
OUT_IMG = Path("data/processed/preview.jpg")

if __name__ == "__main__":
    ds = JsonlDataset(TRAIN_JSONL, shuffle=True)
    batch, labels = make_batch(ds, batch_size=16, augment=True)
    save_grid(batch, labels, OUT_IMG, cols=4)
    print(f"Saved preview to {OUT_IMG}")

