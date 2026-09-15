from __future__ import annotations
from pathlib import Path
import joblib, pandas as pd, numpy as np


def _frame_for(model, features: dict) -> pd.DataFrame:
    names=list(getattr(model,"feature_names_in_",[]))
    return pd.DataFrame([{n:features.get(n,np.nan) for n in names}]) if names else pd.DataFrame([features])


class FusionClassifier:
    def __init__(self,model_path:str|Path|None=None): self.model=joblib.load(model_path) if model_path and Path(model_path).exists() else None
    def predict(self,features:dict)->dict:
        if self.model is None:
            t=float(features.get("turbidity_difference",0)); a=float(features.get("audio_machine_probability_b",0)); v=float(features.get("vibration_machinery_probability_b",0)); p=float(features.get("persistence_seconds",0))
            if t>50 and a>.75 and v>.75 and p>20: label="HIGH_RISK_MINING_ACTIVITY"; conf=.9
            elif t>25 and a>.6 and v>.55: label="POSSIBLE_MINING_ACTIVITY"; conf=.78
            elif a>.6 or v>.6: label="MACHINERY_ACTIVITY"; conf=.7
            elif t>20: label="SUSPICIOUS_ENVIRONMENTAL_CHANGE"; conf=.68
            else: label="SAFE"; conf=.82
            return {"class":label,"confidence":conf,"probabilities":{label:conf}}
        X=_frame_for(self.model,features); proba=self.model.predict_proba(X)[0]; idx=int(np.argmax(proba)); classes=list(self.model.classes_); return {"class":str(classes[idx]),"confidence":float(proba[idx]),"probabilities":{str(c):float(proba[i]) for i,c in enumerate(classes)}}
