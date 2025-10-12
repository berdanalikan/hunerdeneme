from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple

import numpy as np
import paddle
import paddle.nn as nn
import paddle.optimizer as optim

from scripts.data_pipeline import JsonlDataset, make_batch
from scripts.model_crnn import CRNNCTC

TRAIN_JSONL = Path("data/labels/train.jsonl")
VAL_JSONL = Path("data/labels/val.jsonl")
CHECKPOINT_DIR = Path("checkpoints")
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
METRICS_FILE = CHECKPOINT_DIR / "metrics.json"

H = 48
W = 512
BATCH_SIZE = 8
STEPS = 80
LR = 1e-3
VAL_EVERY = 10
PATIENCE = 3


def build_charset(paths: List[Path]) -> str:
    charset = set()
    for p in paths:
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                for ch in rec.get("label", ""):
                    charset.add(ch)
    # sort for determinism; index 0 is CTC blank
    chars = sorted(list(charset))
    return "".join(chars)


def encode_labels(labels: List[str], charset: str) -> Tuple[paddle.Tensor, paddle.Tensor]:
    char_to_idx = {c: i + 1 for i, c in enumerate(charset)}  # +1 to reserve 0 for blank
    seqs = []
    lengths = []
    for s in labels:
        indices = [char_to_idx.get(c, 0) for c in s]  # unknown -> blank
        seqs.append(indices)
        lengths.append(len(indices))
    max_len = max(1, max(lengths))
    padded = np.full((len(labels), max_len), fill_value=-1, dtype=np.int32)  # -1 padding for Paddle CTC
    for i, indices in enumerate(seqs):
        padded[i, : len(indices)] = np.array(indices, dtype=np.int32)
    labels_t = paddle.to_tensor(padded)  # [N, max_L]
    lengths_t = paddle.to_tensor(np.array(lengths, dtype=np.int64))  # [N]
    return labels_t, lengths_t


def greedy_decode(logits: paddle.Tensor, charset: str) -> List[str]:
    # logits: (T, N, C)
    probs = logits.argmax(axis=2)  # (T, N)
    seqs = probs.transpose([1, 0]).numpy().tolist()  # N x T
    results = []
    for seq in seqs:
        prev = -1
        out = []
        for idx in seq:
            if idx != prev and idx != 0:
                if 1 <= idx <= len(charset):
                    out.append(charset[idx - 1])
            prev = idx
        results.append("".join(out))
    return results


def cer(ref: str, hyp: str) -> float:
    # Levenshtein distance / len(ref)
    m, n = len(ref), len(hyp)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if ref[i - 1] == hyp[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    return dp[m][n] / max(1, m)


def eval_cer(model: nn.Layer, charset: str, val_ds: JsonlDataset) -> float:
    model.eval()
    with paddle.no_grad():
        val_batch, val_labels = make_batch(val_ds, batch_size=16, augment=False, seed=999)
        x = paddle.to_tensor(val_batch.transpose(0, 3, 1, 2).astype("float32") / 255.0)
        logits = model(x)
        preds = greedy_decode(logits, charset)
        cers = [cer(r, h) for r, h in zip(val_labels, preds)]
        return float(np.mean(cers))


def main() -> None:
    paddle.seed(123)
    train_ds = JsonlDataset(TRAIN_JSONL, shuffle=True)
    val_ds = JsonlDataset(VAL_JSONL, shuffle=False)

    charset = build_charset([TRAIN_JSONL, VAL_JSONL])
    num_classes = len(charset) + 1  # +blank

    model = CRNNCTC(num_classes)
    criterion = nn.CTCLoss(blank=0)
    optimizer = optim.Adam(learning_rate=LR, parameters=model.parameters())

    best_cer = 1e9
    bad_epochs = 0
    history = {"train_loss": [], "val_cer": []}

    model.train()
    step = 0
    while step < STEPS:
        batch_np, labels = make_batch(train_ds, batch_size=BATCH_SIZE, augment=True, seed=123 + step)
        # HWC->CHW and to tensor
        x = paddle.to_tensor(batch_np.transpose(0, 3, 1, 2).astype("float32") / 255.0)
        logits = model(x)  # (T, N, C)
        T, N, C = logits.shape
        input_lengths = paddle.to_tensor(np.full((N,), T, dtype=np.int64))
        labels_padded, label_lengths = encode_labels(labels, charset)
        loss = criterion(logits, labels_padded, input_lengths, label_lengths)
        loss = loss.mean()

        loss.backward()
        optimizer.step()
        optimizer.clear_grad()

        if step % 10 == 0:
            print(f"step {step} loss {float(loss.numpy()):.4f}")
        history["train_loss"].append(float(loss.numpy()))

        if (step + 1) % VAL_EVERY == 0:
            val_mean_cer = eval_cer(model, charset, val_ds)
            history["val_cer"].append(val_mean_cer)
            print(f"val CER @ step {step+1}: {val_mean_cer:.4f}")
            # early stopping + best checkpoint
            if val_mean_cer + 1e-6 < best_cer:
                best_cer = val_mean_cer
                bad_epochs = 0
                paddle.save(model.state_dict(), str(CHECKPOINT_DIR / "crnn_ctc_best.pdparams"))
                with open(CHECKPOINT_DIR / "charset.txt", "w", encoding="utf-8") as f:
                    f.write(charset)
            else:
                bad_epochs += 1
                if bad_epochs >= PATIENCE:
                    print("Early stopping triggered.")
                    break
            model.train()
        step += 1

    # save last checkpoint and metrics
    paddle.save(model.state_dict(), str(CHECKPOINT_DIR / "crnn_ctc_last.pdparams"))
    with open(CHECKPOINT_DIR / "charset.txt", "w", encoding="utf-8") as f:
        f.write(charset)
    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump({"best_val_cer": best_cer, **history}, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
