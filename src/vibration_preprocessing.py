from __future__ import annotations
import numpy as np
from scipy import signal


def preprocess_vibration(samples, sample_rate: int, low_hz: float = 1.0, high_hz: float = 200.0) -> tuple[np.ndarray, dict]:
    x=np.asarray(samples,dtype=np.float32).reshape(-1)
    if x.size==0: raise ValueError("empty vibration buffer")
    x=signal.detrend(x).astype(np.float32)
    hi=min(high_hz,sample_rate*0.45)
    if x.size>32 and low_hz<hi:
        sos=signal.butter(4,[low_hz,hi],btype="bandpass",fs=sample_rate,output="sos")
        x=signal.sosfiltfilt(sos,x).astype(np.float32)
    scale=float(np.std(x))
    if scale>1e-8: x=x/scale
    return x,{"samples":int(len(x)),"flat":bool(np.std(x)<1e-7)}
