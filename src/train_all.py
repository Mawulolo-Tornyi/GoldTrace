from __future__ import annotations
import hashlib, json
from pathlib import Path
from .config import ROOT
from .data_generator import generate_dataset
from .train_audio import train as train_audio
from .train_vibration import train as train_vibration
from .train_environment import train as train_environment
from .train_anomaly import train as train_anomaly
from .train_fusion import train as train_fusion
from .utils import write_json, utc_now_iso


def _load(path):
    p=ROOT/path
    return json.loads(p.read_text()) if p.exists() else {}

def _sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def main():
    data_path=ROOT/'data/synthetic/goldtrace_sensor_windows.csv'
    if not data_path.exists():
        print('Synthetic dataset missing; generating 100,000 windows...')
        generate_dataset(100_000,42).to_csv(data_path,index=False)
    train_audio(); train_vibration(); train_environment(); train_anomaly(); train_fusion()
    specs=[
        ('audio','scikit-learn ExtraTrees + PyTorch CNN candidate','models/goldtrace_audio_classical_v1.joblib','models/edge/goldtrace_audio_v1.torchscript.pt','reports/audio_training.json'),
        ('vibration','scikit-learn ExtraTrees + PyTorch CNN candidate','models/goldtrace_vibration_classical_v1.joblib','models/edge/goldtrace_vibration_v1.torchscript.pt','reports/vibration_training.json'),
        ('environment','scikit-learn','models/goldtrace_environment_v1.joblib',None,'reports/environment_training.json'),
        ('anomaly','scikit-learn IsolationForest','models/goldtrace_anomaly_v1.joblib',None,'reports/anomaly_training.json'),
        ('fusion','scikit-learn','models/goldtrace_fusion_v1.joblib',None,'reports/fusion_training.json'),
    ]
    models=[]
    for name,framework,model_path,edge_path,report in specs:
        p=ROOT/model_path
        item={'name':name,'version':'v1','framework':framework,'dataset':'synthetic development data','synthetic_or_real':'synthetic','model_path':model_path,'edge_model_path':edge_path,'metrics':_load(report),'file_size_bytes':p.stat().st_size,'sha256':_sha(p)}
        if edge_path and (ROOT/edge_path).exists(): item['edge_file_size_bytes']=(ROOT/edge_path).stat().st_size; item['edge_sha256']=_sha(ROOT/edge_path)
        models.append(item)
    registry={'generated_at':utc_now_iso(),'warning':'Synthetic metrics validate software architecture only; they are not real-world field performance.','models':models}
    write_json('models/model_registry.json',registry)
    print('Training complete. Synthetic metrics are development-only.')

if __name__=='__main__': main()
