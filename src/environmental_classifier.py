from __future__ import annotations
from pathlib import Path
import joblib, pandas as pd, numpy as np


def _frame_for(model, features: dict) -> pd.DataFrame:
    names = list(getattr(model, "feature_names_in_", []))
    if not names and hasattr(model, "named_steps"):
        names = list(getattr(model, "feature_names_in_", []))
    if names:
        return pd.DataFrame([{name: features.get(name, np.nan) for name in names}])
    return pd.DataFrame([features])


class EnvironmentalClassifier:
    def __init__(self,model_path:str|Path|None=None):
        self.model=joblib.load(model_path) if model_path and Path(model_path).exists() else None
    def predict(self,features:dict)->dict:
        if self.model is None:
            diff=float(features.get("turbidity_difference",0)); tb=float(features.get("turbidity_b",features.get("turbidity_current",0)) or 0)
            if diff>30: label="DOWNSTREAM_DISTURBANCE"; conf=min(.95,.55+diff/150)
            elif tb>50: label="SUDDEN_TURBIDITY_EVENT"; conf=.7
            else: label="NORMAL_RIVER"; conf=.8
            return {"environment_class":label,"confidence":float(conf),"probabilities":{label:float(conf)}}
        X=_frame_for(self.model, features); proba=self.model.predict_proba(X)[0]; idx=int(np.argmax(proba)); classes=list(self.model.classes_)
        return {"environment_class":str(classes[idx]),"confidence":float(proba[idx]),"probabilities":{str(c):float(proba[i]) for i,c in enumerate(classes)}}
