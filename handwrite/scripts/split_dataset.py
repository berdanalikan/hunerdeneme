import json
import random
from collections import Counter
from pathlib import Path

DATA_ROOT = Path("data")
LABELS_DIR = DATA_ROOT / "labels"
FULL_LABELS = LABELS_DIR / "label.jsonl"

TRAIN_FILE = LABELS_DIR / "train.jsonl"
VAL_FILE = LABELS_DIR / "val.jsonl"
TEST_FILE = LABELS_DIR / "test.jsonl"

STATS_FILE = LABELS_DIR / "split_stats.json"

RNG_SEED = 42


def read_jsonl(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def write_jsonl(path: Path, records):
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main():
    assert FULL_LABELS.exists(), f"Missing {FULL_LABELS}"

    records = list(read_jsonl(FULL_LABELS))
    # Deduplicate by image_path to avoid leakage
    seen = set()
    unique_records = []
    for r in records:
        key = r.get("image_path")
        if key not in seen:
            seen.add(key)
            unique_records.append(r)

    random.Random(RNG_SEED).shuffle(unique_records)
    n = len(unique_records)
    n_train = int(n * 0.70)
    n_val = int(n * 0.15)
    n_test = n - n_train - n_val

    train = unique_records[:n_train]
    val = unique_records[n_train:n_train + n_val]
    test = unique_records[n_train + n_val:]

    write_jsonl(TRAIN_FILE, train)
    write_jsonl(VAL_FILE, val)
    write_jsonl(TEST_FILE, test)

    # Simple "class" proxy: first token; plus length buckets
    def summarize(split):
        labels = [r.get("label", "") for r in split]
        first_token = [s.split(" ")[0] if s else "" for s in labels]
        lengths = [len(s) for s in labels]
        buckets = Counter(
            "0-5" if l <= 5 else "6-10" if l <= 10 else "11-20" if l <= 20 else ">20"
            for l in lengths
        )
        return {
            "count": len(labels),
            "first_token_top5": Counter(first_token).most_common(5),
            "length_buckets": dict(buckets),
        }

    stats = {
        "total": len(unique_records),
        "train": summarize(train),
        "val": summarize(val),
        "test": summarize(test),
        "leakage_check": {
            "train_val_intersection": len({r["image_path"] for r in train} & {r["image_path"] for r in val}),
            "train_test_intersection": len({r["image_path"] for r in train} & {r["image_path"] for r in test}),
            "val_test_intersection": len({r["image_path"] for r in val} & {r["image_path"] for r in test}),
        },
    }

    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print("Split complete:")
    print(f"  Train: {len(train)} -> {TRAIN_FILE}")
    print(f"  Val:   {len(val)}   -> {VAL_FILE}")
    print(f"  Test:  {len(test)}  -> {TEST_FILE}")
    print(f"Stats at: {STATS_FILE}")


if __name__ == "__main__":
    main()

