from __future__ import annotations
from pathlib import Path
import numpy as np
import joblib
from .audio_features import extract_audio_features, log_mel_spectrogram
from .audio_preprocessing import preprocess_audio

AUDIO_CLASSES=["NORMAL_ENVIRONMENT","FLOWING_WATER","RAIN","HEAVY_RAIN","WIND","HUMAN_ACTIVITY","MOTORBIKE","VEHICLE","TRUCK","BOAT","GENERATOR","FARM_MACHINERY","CONSTRUCTION_MACHINERY","WATER_PUMP","EXCAVATOR_LIKE","MULTIPLE_MACHINES","UNKNOWN_MACHINE","UNKNOWN_AUDIO"]
MACHINE_CLASSES={"MOTORBIKE","VEHICLE","TRUCK","BOAT","GENERATOR","FARM_MACHINERY","CONSTRUCTION_MACHINERY","WATER_PUMP","EXCAVATOR_LIKE","MULTIPLE_MACHINES","UNKNOWN_MACHINE"}


class AudioClassifier:
    def __init__(self, model_path: str|Path|None=None, onnx_path: str|Path|None=None):
        self.model=joblib.load(model_path) if model_path and Path(model_path).exists() else None
        self.onnx_session=None
        if onnx_path and Path(onnx_path).exists():
            try:
                import onnxruntime as ort
                self.onnx_session=ort.InferenceSession(str(onnx_path),providers=["CPUExecutionProvider"])
            except Exception:
                self.onnx_session=None

    def predict(self,samples,sample_rate:int)->dict:
        x,sr,_=preprocess_audio(samples,sample_rate)
        feats=extract_audio_features(x,sr)
        if self.onnx_session is not None:
            spec=log_mel_spectrogram(x,sr,n_mels=40).astype(np.float32)[None,None,:,:]
            input_name=self.onnx_session.get_inputs()[0].name
            logits=self.onnx_session.run(None,{input_name:spec})[0][0]
            logits=logits-np.max(logits); proba=np.exp(logits)/np.exp(logits).sum(); idx=int(np.argmax(proba)); label=AUDIO_CLASSES[idx]
            machine=sum(float(proba[i]) for i,c in enumerate(AUDIO_CLASSES) if c in MACHINE_CLASSES)
            return {"audio_class":label,"confidence":float(proba[idx]),"machine_probability":machine,"probabilities":{c:float(proba[i]) for i,c in enumerate(AUDIO_CLASSES)},"features":feats,"runtime":"onnx"}
        if self.model is None:
            p=float(np.clip(feats["audio_machine_band_energy"]*1.8 + feats["audio_rms"]*0.2,0,1)); label="UNKNOWN_MACHINE" if p>0.65 else "NORMAL_ENVIRONMENT"
            return {"audio_class":label,"confidence":max(p,1-p),"machine_probability":p,"probabilities":{label:max(p,1-p)},"features":feats,"runtime":"heuristic"}
        import pandas as pd
        X=pd.DataFrame([feats]); proba=self.model.predict_proba(X)[0]; classes=list(self.model.classes_); idx=int(np.argmax(proba)); label=str(classes[idx]); machine=sum(float(proba[i]) for i,c in enumerate(classes) if str(c) in MACHINE_CLASSES)
        return {"audio_class":label,"confidence":float(proba[idx]),"machine_probability":float(machine),"probabilities":{str(c):float(proba[i]) for i,c in enumerate(classes)},"features":feats,"runtime":"sklearn"}
