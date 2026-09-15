from __future__ import annotations
import argparse, shutil, tempfile
from datetime import datetime, timezone
from pathlib import Path
from .config import ROOT
from .train_environment import train as train_environment
from .train_anomaly import train as train_anomaly
from .train_fusion import train as train_fusion
from .utils import write_json

PRODUCTION=[
    ROOT/"models/goldtrace_environment_v1.joblib",
    ROOT/"models/goldtrace_anomaly_v1.joblib",
    ROOT/"models/goldtrace_fusion_v1.joblib",
]


def main():
    p=argparse.ArgumentParser(description="Train candidate models without automatically replacing production")
    p.add_argument("--data",required=True); args=p.parse_args(); source=Path(args.data).resolve()
    if not source.exists(): raise SystemExit(f"Missing dataset: {source}")
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"); candidate_dir=ROOT/"models/candidates"/stamp; candidate_dir.mkdir(parents=True,exist_ok=True)
    staged=ROOT/"data/processed/retrain_input.csv"; staged.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(source,staged)
    backups={}
    for prod in PRODUCTION:
        if prod.exists():
            backup=candidate_dir/(prod.name+".production_backup"); shutil.copy2(prod,backup); backups[prod]=backup
    try:
        train_environment("data/processed/retrain_input.csv"); train_anomaly("data/processed/retrain_input.csv"); train_fusion("data/processed/retrain_input.csv")
        for prod in PRODUCTION:
            if prod.exists(): shutil.copy2(prod,candidate_dir/prod.name)
        write_json(candidate_dir/"candidate_manifest.json",{"created":stamp,"source":str(source),"status":"REVIEW_REQUIRED","automatic_promotion":False,"requirements":["minimum macro F1","minimum mining recall","maximum high-risk false-positive rate","acceptable Raspberry Pi latency","acceptable model size"]})
    finally:
        for prod in PRODUCTION:
            if prod in backups: shutil.copy2(backups[prod],prod)
            elif prod.exists(): prod.unlink()
    print(f"Candidate models saved to {candidate_dir}. Production models were not automatically promoted.")

if __name__=="__main__": main()
