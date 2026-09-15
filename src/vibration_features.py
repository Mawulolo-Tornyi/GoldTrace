from __future__ import annotations
import numpy as np
from scipy import signal, stats


def extract_vibration_features(samples, sample_rate:int) -> dict[str,float]:
    x=np.asarray(samples,dtype=float).reshape(-1)
    if x.size<8: raise ValueError("vibration buffer too short")
    rms=float(np.sqrt(np.mean(x*x))); peak=float(np.max(np.abs(x))); mean=float(np.mean(x)); std=float(np.std(x)); var=float(np.var(x)); energy=float(np.sum(x*x)); zcr=float(np.mean(np.signbit(x[1:])!=np.signbit(x[:-1])))
    freqs,psd=signal.welch(x,fs=sample_rate,nperseg=min(512,max(32,len(x)))); psd=np.maximum(psd,1e-12); total=psd.sum(); dom=float(freqs[np.argmax(psd)]); centroid=float((freqs*psd).sum()/total); bw=float(np.sqrt((((freqs-centroid)**2)*psd).sum()/total))
    def band(lo,hi):
        m=(freqs>=lo)&(freqs<hi); return float(psd[m].sum()/total) if m.any() else 0.0
    crest=peak/max(rms,1e-8); impulse=peak/max(np.mean(np.abs(x)),1e-8)
    return {"vibration_rms":rms,"vibration_peak":peak,"vibration_mean":mean,"vibration_std":std,"vibration_variance":var,"vibration_energy":energy,"vibration_zero_crossing_rate":zcr,"vibration_dominant_frequency":dom,"vibration_spectral_centroid":centroid,"vibration_spectral_bandwidth":bw,"vibration_band_energy_low":band(1,15),"vibration_band_energy_mid":band(15,60),"vibration_band_energy_high":band(60,sample_rate/2),"vibration_kurtosis":float(stats.kurtosis(x,bias=False)) if len(x)>4 else 0.0,"vibration_skewness":float(stats.skew(x,bias=False)) if len(x)>4 else 0.0,"vibration_crest_factor":float(crest),"vibration_impulse_factor":float(impulse)}
