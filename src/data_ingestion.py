from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd
from scipy.io import wavfile


def load_data(path: str | Path) -> Any:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".csv": return pd.read_csv(p)
    if suffix == ".json": return json.loads(p.read_text(encoding="utf-8"))
    if suffix == ".jsonl": return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
    if suffix == ".npy": return np.load(p, allow_pickle=False)
    if suffix == ".npz": return dict(np.load(p, allow_pickle=False))
    if suffix == ".wav":
        rate, samples = wavfile.read(p)
        return {"sample_rate": int(rate), "samples": samples.astype(float)}
    raise ValueError(f"Unsupported data format: {suffix}")
