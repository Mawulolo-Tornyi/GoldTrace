from __future__ import annotations
import numpy as np
from scipy import signal


def preprocess_audio(samples, sample_rate: int, target_rate: int = 16000, low_hz: float = 40.0, high_hz: float = 7500.0) -> tuple[np.ndarray, int, dict]:
    x = np.asarray(samples, dtype=np.float32).reshape(-1)
    if x.size == 0: raise ValueError("empty audio buffer")
    x = x - np.mean(x)
    clipped = bool(np.max(np.abs(x)) >= 0.999)
    if sample_rate != target_rate:
        g = np.gcd(sample_rate, target_rate)
        x = signal.resample_poly(x, target_rate // g, sample_rate // g).astype(np.float32)
        sample_rate = target_rate
    nyq = sample_rate / 2.0
    high = min(high_hz, nyq * 0.95)
    if low_hz < high and x.size > 32:
        sos = signal.butter(4, [low_hz, high], btype="bandpass", fs=sample_rate, output="sos")
        x = signal.sosfiltfilt(sos, x).astype(np.float32)
    peak = float(np.max(np.abs(x)))
    if peak > 1e-8: x = x / peak
    quality = {"clipped": clipped, "silent": float(np.sqrt(np.mean(x*x))) < 1e-4, "samples": int(x.size)}
    return x, sample_rate, quality


def make_windows(samples: np.ndarray, sample_rate: int, seconds: float = 2.0, overlap: float = 0.5) -> list[np.ndarray]:
    size = max(1, int(sample_rate * seconds)); hop = max(1, int(size * (1-overlap)))
    if len(samples) < size: return [np.pad(samples, (0, size-len(samples)))]
    return [samples[i:i+size] for i in range(0, len(samples)-size+1, hop)]
