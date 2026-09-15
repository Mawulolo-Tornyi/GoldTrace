from __future__ import annotations
import time, statistics
from pathlib import Path
import psutil
from .config import ROOT
from .mock_sensor_stream import scenario_packets
from .realtime_engine import RealtimeEngine
from .utils import write_json


def main(iterations:int=20):
    engine=RealtimeEngine(); a,b=scenario_packets("high_risk_mining")
    timings=[]
    for _ in range(iterations):
        t=time.perf_counter(); engine.process_pair(a,b,persistence_seconds=42); timings.append((time.perf_counter()-t)*1000)
    result={"environment":"current machine (run again on Raspberry Pi 5 for real edge benchmark)","iterations":iterations,"average_ms":statistics.mean(timings),"p95_ms":sorted(timings)[max(0,int(.95*len(timings))-1)],"rss_mb":psutil.Process().memory_info().rss/1024/1024,"model_files":{p.name:p.stat().st_size for p in (ROOT/"models").glob("*.joblib")}}
    write_json("reports/edge_benchmark.json",result); print(result)
if __name__=="__main__": main()
