from __future__ import annotations
import json
from pathlib import Path
import joblib, pandas as pd, numpy as np
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score, precision_recall_fscore_support
from sklearn.model_selection import GroupShuffleSplit
from .config import ROOT
from .train_fusion import FEATURES as FUSION_FEATURES
from .utils import write_json


def main(data_path="data/synthetic/goldtrace_sensor_windows.csv"):
    df=pd.read_csv(ROOT/data_path); model_path=ROOT/"models/goldtrace_fusion_v1.joblib"
    if not model_path.exists(): raise SystemExit("Train models first: python -m src.train_all")
    g=GroupShuffleSplit(n_splits=1,test_size=.2,random_state=99); _,ti=next(g.split(df,groups=df["event_id"])); test=df.iloc[ti]; model=joblib.load(model_path); pred=model.predict(test[FUSION_FEATURES]); y=test["fusion_label"]
    labels=sorted(set(y)|set(pred)); cm=confusion_matrix(y,pred,labels=labels).tolist(); report=classification_report(y,pred,output_dict=True,zero_division=0)
    high="HIGH_RISK_MINING_ACTIVITY"; mask=(y==high); fp=float(((pred==high)&(~mask)).sum()/max(1,(~mask).sum())); fn=float(((pred!=high)&mask).sum()/max(1,mask.sum()))
    result={"synthetic_data_warning":"These metrics validate software architecture only and are not real-world accuracy.","samples":len(test),"accuracy":float(accuracy_score(y,pred)),"macro_f1":float(f1_score(y,pred,average="macro")),"labels":labels,"confusion_matrix":cm,"classification_report":report,"high_risk_false_positive_rate":fp,"high_risk_false_negative_rate":fn}
    write_json("reports/model_evaluation.json",result); print(json.dumps(result,indent=2))

if __name__=="__main__": main()
