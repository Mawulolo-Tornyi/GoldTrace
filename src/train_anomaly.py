from __future__ import annotations
import argparse, joblib, pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from .config import ROOT
from .utils import write_json

FEATURES=["turbidity_difference","turbidity_ratio","audio_machine_probability_b","vibration_machinery_probability_b","audio_rms_difference","vibration_rms_difference","persistence_seconds"]

def train(path="data/synthetic/goldtrace_sensor_windows.csv"):
    df=pd.read_csv(ROOT/path); normal=df[df["fusion_label"]=="SAFE"]
    pipe=Pipeline([("imputer",SimpleImputer(strategy="median")),("model",IsolationForest(n_estimators=250,contamination=.08,random_state=42,n_jobs=-1))]); pipe.fit(normal[FEATURES])
    out=ROOT/"models/goldtrace_anomaly_v1.joblib"; joblib.dump(pipe,out,compress=3); write_json("reports/anomaly_training.json",{"normal_samples":len(normal),"features":FEATURES}); print(f"Anomaly model -> {out}"); return pipe
if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--data",default="data/synthetic/goldtrace_sensor_windows.csv"); a=p.parse_args(); train(a.data)
