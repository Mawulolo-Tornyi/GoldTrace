import numpy as np
from src.audio_features import extract_audio_features, log_mel_spectrogram

def test_audio_features_finite():
    sr=16000; t=np.arange(sr)/sr; x=np.sin(2*np.pi*60*t); f=extract_audio_features(x,sr); assert f["audio_rms"]>0 and f["audio_dominant_frequency"]>0
def test_log_mel_shape():
    x=np.random.default_rng(1).normal(size=16000); s=log_mel_spectrogram(x,16000,40); assert s.shape[0]==40
