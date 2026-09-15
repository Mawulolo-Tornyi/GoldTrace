import pandas as pd
from src.anomaly_detector import AnomalyDetector

def test_anomaly_detector_fit_predict():
    X=pd.DataFrame({"a":[0,0.1,-.1,.05,.02,0.0],"b":[1,1.1,.9,1.05,1.0,.95]}); d=AnomalyDetector().fit(X); r=d.predict({"a":10,"b":10}); assert 0<=r["anomaly_score"]<=1
