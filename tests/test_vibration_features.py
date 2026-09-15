import numpy as np
from src.vibration_features import extract_vibration_features

def test_vibration_dominant_frequency():
    sr=1000; t=np.arange(2000)/sr; x=np.sin(2*np.pi*10*t); f=extract_vibration_features(x,sr); assert 7 < f["vibration_dominant_frequency"] < 13
