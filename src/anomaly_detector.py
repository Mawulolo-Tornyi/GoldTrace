from __future__ import annotations
from pathlib import Path
import joblib, numpy as np, pandas as pd
from sklearn.ensemble import IsolationForest


def _frame_for(model, features: dict) -> pd.DataFrame:
    names=list(getattr(model,"feature_names_in_",[]))
    return pd.DataFrame([{n:features.get(n,np.nan) for n in names}]) if names else pd.DataFrame([features])


class AnomalyDetector:
    def __init__(self,model_path:str|Path|None=None): self.model=joblib.load(model_path) if model_path and Path(model_path).exists() else None
    def fit(self,X): self.model=IsolationForest(n_estimators=200,contamination=.08,random_state=42).fit(X); return self
    def predict(self,features:dict)->dict:
        if self.model is None: return {"anomaly_score":0.0,"is_anomaly":False}
        X=_frame_for(self.model,features); decision=float(self.model.decision_function(X)[0]); score=float(np.clip(.5-decision,0,1)); return {"anomaly_score":score,"is_anomaly":bool(self.model.predict(X)[0]==-1)}
