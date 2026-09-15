from __future__ import annotations
import argparse, math, time
import numpy as np, pandas as pd, joblib
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from .audio_features import extract_audio_features
from .audio_preprocessing import preprocess_audio
from .audio_model import AudioCNN
from .audio_dataset import AudioWaveDataset
from .config import ROOT
from .utils import set_seed, write_json

CLASSES=["NORMAL_ENVIRONMENT","FLOWING_WATER","RAIN","HEAVY_RAIN","WIND","HUMAN_ACTIVITY","MOTORBIKE","VEHICLE","TRUCK","BOAT","GENERATOR","FARM_MACHINERY","CONSTRUCTION_MACHINERY","WATER_PUMP","EXCAVATOR_LIKE","MULTIPLE_MACHINES","UNKNOWN_MACHINE","UNKNOWN_AUDIO"]
FREQ={"MOTORBIKE":120,"VEHICLE":90,"TRUCK":65,"BOAT":55,"GENERATOR":50,"FARM_MACHINERY":42,"CONSTRUCTION_MACHINERY":35,"WATER_PUMP":58,"EXCAVATOR_LIKE":28,"MULTIPLE_MACHINES":45}

def synth(label,sr,n,rng):
    t=np.arange(n)/sr; x=.025*rng.normal(size=n)
    if label in {"RAIN","HEAVY_RAIN"}: x+=rng.normal(scale=.12 if label=="RAIN" else .25,size=n)
    elif label=="WIND": x+=.12*signal_like_noise(n,rng)
    elif label in FREQ:
        f=FREQ[label]*(1+rng.normal(0,.06)); x += .35*np.sin(2*np.pi*f*t)+.18*np.sin(2*np.pi*2*f*t)+.08*np.sin(2*np.pi*3*f*t)
    elif label=="FLOWING_WATER": x += .06*rng.normal(size=n)+.04*np.sin(2*np.pi*220*t)
    elif label=="HUMAN_ACTIVITY": x += .1*np.sin(2*np.pi*180*t)*(rng.random(n)>.7)
    elif label in {"UNKNOWN_MACHINE","UNKNOWN_AUDIO"}: x += .15*rng.normal(size=n)
    return np.clip(x,-1,1).astype(np.float32)
def signal_like_noise(n,rng):
    y=np.cumsum(rng.normal(size=n)); return y/max(np.max(np.abs(y)),1e-6)

def make_dataset(samples_per_class=30,sr=16000,seconds=1.0,seed=42):
    rng=np.random.default_rng(seed); waves=[]; labels=[]; feats=[]
    for li,label in enumerate(CLASSES):
        for _ in range(samples_per_class):
            w=synth(label,sr,int(sr*seconds),rng); wp,_,_=preprocess_audio(w,sr); waves.append(wp); labels.append(li); feats.append(extract_audio_features(wp,sr))
    return waves,np.array(labels),pd.DataFrame(feats)

def train(samples_per_class=30,epochs=2):
    set_seed(42); waves,y,X=make_dataset(samples_per_class=samples_per_class); strat=y
    Xtr,Xv,ytr,yv=train_test_split(X,y,test_size=.2,random_state=42,stratify=strat); base=ExtraTreesClassifier(n_estimators=220,class_weight="balanced",n_jobs=-1,random_state=42); base.fit(Xtr,ytr); bp=base.predict(Xv); base_f1=f1_score(yv,bp,average="macro")
    class Wrapper:
        pass
    # Save with string classes for runtime wrapper compatibility.
    y_names=np.array([CLASSES[i] for i in y]); Xtr2,Xv2,ytr2,yv2=train_test_split(X,y_names,test_size=.2,random_state=42,stratify=y_names); prod=ExtraTreesClassifier(n_estimators=220,class_weight="balanced",n_jobs=-1,random_state=42); prod.fit(Xtr2,ytr2); joblib.dump(prod,ROOT/"models/goldtrace_audio_classical_v1.joblib",compress=3)
    cnn_f1=None
    try:
        import torch
        from torch.utils.data import DataLoader,random_split
        ds=AudioWaveDataset(waves,y); nval=max(1,int(.2*len(ds))); train_ds,val_ds=random_split(ds,[len(ds)-nval,nval],generator=torch.Generator().manual_seed(42)); model=AudioCNN(len(CLASSES)); dev=torch.device("cuda" if torch.cuda.is_available() else "cpu"); model.to(dev); opt=torch.optim.Adam(model.parameters(),lr=1e-3); loss_fn=torch.nn.CrossEntropyLoss()
        for _ in range(epochs):
            model.train()
            for xb,yb in DataLoader(train_ds,batch_size=16,shuffle=True):
                xb,yb=xb.to(dev),yb.to(dev); opt.zero_grad(); loss=loss_fn(model(xb),yb); loss.backward(); opt.step()
        model.eval(); yp=[]; yt=[]
        with torch.no_grad():
            for xb,yb in DataLoader(val_ds,batch_size=32): yp.extend(model(xb.to(dev)).argmax(1).cpu().numpy()); yt.extend(yb.numpy())
        cnn_f1=float(f1_score(yt,yp,average="macro")); torch.save({"state_dict":model.cpu().state_dict(),"classes":CLASSES,"sample_rate":16000},ROOT/"models/checkpoints/goldtrace_audio_v1.pt")
    except Exception as exc:
        cnn_f1=None
    write_json("reports/audio_training.json",{"classical_macro_f1":float(base_f1),"cnn_macro_f1":cnn_f1,"synthetic":True,"classes":CLASSES})
    print(f"Audio classical macro-F1={base_f1:.3f}; CNN={cnn_f1}")
if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--samples-per-class",type=int,default=30); p.add_argument("--epochs",type=int,default=2); a=p.parse_args(); train(a.samples_per_class,a.epochs)
