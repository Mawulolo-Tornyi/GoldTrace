from __future__ import annotations
import argparse, numpy as np, pandas as pd, joblib
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from .vibration_features import extract_vibration_features
from .vibration_preprocessing import preprocess_vibration
from .vibration_model import VibrationCNN
from .vibration_dataset import VibrationDataset
from .config import ROOT
from .utils import set_seed, write_json

CLASSES=["NORMAL_GROUND","FOOTSTEPS","ANIMAL_MOVEMENT","MOTORBIKE","VEHICLE_PASSING","TRUCK","CONSTRUCTION_ACTIVITY","WATER_PUMP_VIBRATION","HEAVY_MACHINERY","EXCAVATOR_LIKE_VIBRATION","CONTINUOUS_ENGINE","IMPACT_EVENT","UNKNOWN_VIBRATION"]
FREQ={"MOTORBIKE":22,"VEHICLE_PASSING":14,"TRUCK":9,"CONSTRUCTION_ACTIVITY":11,"WATER_PUMP_VIBRATION":28,"HEAVY_MACHINERY":8,"EXCAVATOR_LIKE_VIBRATION":6,"CONTINUOUS_ENGINE":18}

def synth(label,sr,n,rng):
    t=np.arange(n)/sr; x=.02*rng.normal(size=n)
    if label in FREQ:
        f=FREQ[label]*(1+rng.normal(0,.08)); x += .6*np.sin(2*np.pi*f*t)+.2*np.sin(2*np.pi*2*f*t)
    elif label=="FOOTSTEPS":
        for idx in rng.integers(0,n,size=4): x[max(0,idx-3):min(n,idx+4)] += .8*signal_window(min(7,n-max(0,idx-3)))
    elif label=="IMPACT_EVENT":
        idx=int(rng.integers(n//4,3*n//4)); x[idx:idx+3]+=1.0
    elif label in {"ANIMAL_MOVEMENT","UNKNOWN_VIBRATION"}: x += .12*rng.normal(size=n)
    return x.astype(np.float32)
def signal_window(n): return np.hanning(max(2,n))[:n]
def make_dataset(samples_per_class=40,sr=1000,seconds=2,seed=42):
    rng=np.random.default_rng(seed); waves=[]; labels=[]; feats=[]
    for li,label in enumerate(CLASSES):
        for _ in range(samples_per_class):
            w=synth(label,sr,int(sr*seconds),rng); wp,_=preprocess_vibration(w,sr); waves.append(wp); labels.append(li); feats.append(extract_vibration_features(wp,sr))
    return waves,np.array(labels),pd.DataFrame(feats)
def train(samples_per_class=40,epochs=2):
    set_seed(42); waves,y,X=make_dataset(samples_per_class=samples_per_class); names=np.array([CLASSES[i] for i in y]); Xtr,Xv,ytr,yv=train_test_split(X,names,test_size=.2,random_state=42,stratify=names); model=ExtraTreesClassifier(n_estimators=220,class_weight="balanced",n_jobs=-1,random_state=42); model.fit(Xtr,ytr); f1=float(f1_score(yv,model.predict(Xv),average="macro")); joblib.dump(model,ROOT/"models/goldtrace_vibration_classical_v1.joblib",compress=3)
    cnn_f1=None
    try:
        import torch
        from torch.utils.data import DataLoader,random_split
        ds=VibrationDataset(waves,y); nval=max(1,int(.2*len(ds))); tr,val=random_split(ds,[len(ds)-nval,nval],generator=torch.Generator().manual_seed(42)); net=VibrationCNN(len(CLASSES)); dev=torch.device("cuda" if torch.cuda.is_available() else "cpu"); net.to(dev); opt=torch.optim.Adam(net.parameters(),lr=1e-3); loss_fn=torch.nn.CrossEntropyLoss()
        for _ in range(epochs):
            net.train()
            for xb,yb in DataLoader(tr,batch_size=32,shuffle=True): xb,yb=xb.to(dev),yb.to(dev); opt.zero_grad(); loss=loss_fn(net(xb),yb); loss.backward(); opt.step()
        yp=[]; yt=[]; net.eval()
        with torch.no_grad():
            for xb,yb in DataLoader(val,batch_size=64): yp.extend(net(xb.to(dev)).argmax(1).cpu().numpy()); yt.extend(yb.numpy())
        cnn_f1=float(f1_score(yt,yp,average="macro")); torch.save({"state_dict":net.cpu().state_dict(),"classes":CLASSES,"sample_rate":1000},ROOT/"models/checkpoints/goldtrace_vibration_v1.pt")
    except Exception: cnn_f1=None
    write_json("reports/vibration_training.json",{"classical_macro_f1":f1,"cnn_macro_f1":cnn_f1,"synthetic":True,"classes":CLASSES}); print(f"Vibration classical macro-F1={f1:.3f}; CNN={cnn_f1}")
if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--samples-per-class",type=int,default=40); p.add_argument("--epochs",type=int,default=2); a=p.parse_args(); train(a.samples_per_class,a.epochs)
