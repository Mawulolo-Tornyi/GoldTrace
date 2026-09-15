from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from .vibration_preprocessing import preprocess_vibration
from .vibration_features import extract_vibration_features

VIBRATION_CLASSES=["NORMAL_GROUND","FOOTSTEPS","ANIMAL_MOVEMENT","MOTORBIKE","VEHICLE_PASSING","TRUCK","CONSTRUCTION_ACTIVITY","WATER_PUMP_VIBRATION","HEAVY_MACHINERY","EXCAVATOR_LIKE_VIBRATION","CONTINUOUS_ENGINE","IMPACT_EVENT","UNKNOWN_VIBRATION"]
MACHINERY={"MOTORBIKE","VEHICLE_PASSING","TRUCK","CONSTRUCTION_ACTIVITY","WATER_PUMP_VIBRATION","HEAVY_MACHINERY","EXCAVATOR_LIKE_VIBRATION","CONTINUOUS_ENGINE"}


class VibrationClassifier:
    def __init__(self,model_path:str|Path|None=None,onnx_path:str|Path|None=None):
        self.model=joblib.load(model_path) if model_path and Path(model_path).exists() else None
        self.onnx_session=None
        if onnx_path and Path(onnx_path).exists():
            try:
                import onnxruntime as ort
                self.onnx_session=ort.InferenceSession(str(onnx_path),providers=["CPUExecutionProvider"])
            except Exception:
                self.onnx_session=None
    def predict(self,samples,sample_rate:int)->dict:
        x,_=preprocess_vibration(samples,sample_rate); feats=extract_vibration_features(x,sample_rate)
        if self.onnx_session is not None:
            arr=x.astype(np.float32)[None,None,:]; input_name=self.onnx_session.get_inputs()[0].name; logits=self.onnx_session.run(None,{input_name:arr})[0][0]; logits=logits-np.max(logits); proba=np.exp(logits)/np.exp(logits).sum(); idx=int(np.argmax(proba)); label=VIBRATION_CLASSES[idx]; machine=sum(float(proba[i]) for i,c in enumerate(VIBRATION_CLASSES) if c in MACHINERY)
            return {"vibration_class":label,"confidence":float(proba[idx]),"machinery_probability":machine,"probabilities":{c:float(proba[i]) for i,c in enumerate(VIBRATION_CLASSES)},"features":feats,"runtime":"onnx"}
        if self.model is None:
            p=float(np.clip(0.05 + 0.95*max(feats["vibration_band_energy_low"], feats["vibration_band_energy_mid"]),0,1)); label="HEAVY_MACHINERY" if p>0.7 else "NORMAL_GROUND"
            return {"vibration_class":label,"confidence":max(p,1-p),"machinery_probability":p,"probabilities":{label:max(p,1-p)},"features":feats,"runtime":"heuristic"}
        proba=self.model.predict_proba(pd.DataFrame([feats]))[0]; classes=list(self.model.classes_); idx=int(np.argmax(proba)); label=str(classes[idx]); machine=sum(float(proba[i]) for i,c in enumerate(classes) if str(c) in MACHINERY)
        return {"vibration_class":label,"confidence":float(proba[idx]),"machinery_probability":float(machine),"probabilities":{str(c):float(proba[i]) for i,c in enumerate(classes)},"features":feats,"runtime":"sklearn"}
