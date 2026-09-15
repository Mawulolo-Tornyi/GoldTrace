from __future__ import annotations
import numpy as np
from scipy import signal
from scipy.fft import dct


def _spectral(x: np.ndarray, sr: int):
    freqs, psd = signal.welch(x, fs=sr, nperseg=min(1024, max(64, len(x))))
    psd = np.maximum(psd, 1e-12); total = psd.sum()
    centroid = float((freqs*psd).sum()/total)
    bandwidth = float(np.sqrt((((freqs-centroid)**2)*psd).sum()/total))
    csum = np.cumsum(psd); roll = float(freqs[min(len(freqs)-1, np.searchsorted(csum, .85*csum[-1]))])
    dominant = float(freqs[int(np.argmax(psd))])
    flatness = float(np.exp(np.mean(np.log(psd)))/np.mean(psd))
    return freqs, psd, centroid, bandwidth, roll, dominant, flatness


def log_mel_spectrogram(x: np.ndarray, sr: int, n_mels: int = 40, n_fft: int = 512, hop: int = 160) -> np.ndarray:
    _, _, z = signal.stft(x, fs=sr, nperseg=n_fft, noverlap=n_fft-hop, nfft=n_fft, boundary=None)
    power = np.abs(z)**2
    freqs = np.linspace(0, sr/2, power.shape[0])
    mel_min, mel_max = 2595*np.log10(1+0/700), 2595*np.log10(1+(sr/2)/700)
    mel_pts = np.linspace(mel_min, mel_max, n_mels+2)
    hz = 700*(10**(mel_pts/2595)-1)
    bins = np.searchsorted(freqs, hz)
    fb = np.zeros((n_mels, len(freqs)))
    for m in range(1, n_mels+1):
        l,c,r = bins[m-1], bins[m], bins[m+1]
        if c>l: fb[m-1,l:c] = (np.arange(l,c)-l)/max(c-l,1)
        if r>c: fb[m-1,c:r] = (r-np.arange(c,r))/max(r-c,1)
    mel = fb @ power
    return np.log10(np.maximum(mel, 1e-10)).astype(np.float32)


def extract_audio_features(samples, sample_rate: int) -> dict[str,float]:
    x=np.asarray(samples,dtype=float).reshape(-1)
    if x.size < 8: raise ValueError("audio buffer too short")
    rms=float(np.sqrt(np.mean(x*x))); peak=float(np.max(np.abs(x))); mean=float(np.mean(x)); std=float(np.std(x)); energy=float(np.sum(x*x))
    zcr=float(np.mean(np.signbit(x[1:]) != np.signbit(x[:-1])))
    freqs,psd,centroid,bw,roll,dom,flat=_spectral(x,sample_rate)
    def band(lo,hi):
        mask=(freqs>=lo)&(freqs<hi); return float(psd[mask].sum()/psd.sum()) if mask.any() else 0.0
    mel=log_mel_spectrogram(x,sample_rate,n_mels=26)
    mfcc=dct(mel, type=2, axis=0, norm="ortho")[:13]
    flux=float(np.mean(np.maximum(0,np.diff(np.abs(signal.stft(x,fs=sample_rate,nperseg=min(512,len(x)))[2]),axis=1)))) if len(x)>64 else 0.0
    out={"audio_rms":rms,"audio_peak":peak,"audio_mean":mean,"audio_std":std,"audio_energy":energy,"audio_zero_crossing_rate":zcr,"audio_dominant_frequency":dom,"audio_spectral_centroid":centroid,"audio_spectral_bandwidth":bw,"audio_spectral_rolloff":roll,"audio_spectral_flatness":flat,"audio_spectral_flux":flux,"audio_low_frequency_energy":band(20,300),"audio_mid_frequency_energy":band(300,2000),"audio_high_frequency_energy":band(2000,sample_rate/2),"audio_machine_band_energy":band(50,1500)}
    for i in range(13): out[f"mfcc_{i+1}_mean"]=float(mfcc[i].mean()); out[f"mfcc_{i+1}_std"]=float(mfcc[i].std())
    return out
