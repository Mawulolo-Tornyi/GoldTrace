from __future__ import annotations
import argparse, joblib, pandas as pd
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, HistGradientBoostingClassifier, GradientBoostingClassifier
from sklearn.metrics import f1_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from .config import ROOT
from .utils import write_json

FEATURES=['turbidity_difference','turbidity_ratio','turbidity_percent_increase','temperature_difference','audio_rms_difference','vibration_rms_difference','audio_machine_probability_a','audio_machine_probability_b','vibration_machinery_probability_a','vibration_machinery_probability_b','audio_machine_probability_difference','vibration_machinery_probability_difference','persistence_seconds','anomaly_score','battery_voltage_a','battery_voltage_b','lora_rssi_a','lora_rssi_b']

def _split(df, seed=42):
    g=GroupShuffleSplit(n_splits=1,test_size=.2,random_state=seed); ti,vi=next(g.split(df,groups=df['event_id'])); return df.iloc[ti],df.iloc[vi]

def _candidate_subset(df,max_rows=2000):
    if len(df)<=max_rows: return df
    events=df['event_id'].drop_duplicates().sample(frac=1,random_state=42); sizes=df.groupby('event_id').size(); selected=[]; count=0
    for e in events:
        selected.append(e); count += int(sizes.loc[e])
        if count>=max_rows: break
    return df[df['event_id'].isin(selected)]

def train(path='data/synthetic/goldtrace_sensor_windows.csv'):
    df=pd.read_csv(ROOT/path); candidate=_candidate_subset(df); tr,va=_split(candidate)
    models={'random_forest':RandomForestClassifier(n_estimators=90,class_weight='balanced',n_jobs=-1,random_state=42),'extra_trees':ExtraTreesClassifier(n_estimators=90,class_weight='balanced',n_jobs=-1,random_state=42),'hist_gb':HistGradientBoostingClassifier(max_iter=90,random_state=42),'gradient_boosting':GradientBoostingClassifier(n_estimators=50,random_state=42)}
    best_name=''; best_score=-1; results={}
    for name,m in models.items():
        pipe=Pipeline([('imputer',SimpleImputer(strategy='median')),('model',m)]); pipe.fit(tr[FEATURES],tr['fusion_label']); pred=pipe.predict(va[FEATURES]); macro=f1_score(va['fusion_label'],pred,average='macro')
        high=va['fusion_label']=='HIGH_RISK_MINING_ACTIVITY'; high_recall=float(((pred=='HIGH_RISK_MINING_ACTIVITY')&high).sum()/max(1,high.sum())); fp=float(((pred=='HIGH_RISK_MINING_ACTIVITY')&~high).sum()/max(1,(~high).sum())); score=macro+.15*high_recall-.2*fp
        results[name]={'macro_f1':float(macro),'high_risk_recall':high_recall,'high_risk_false_positive_rate':fp,'selection_score':float(score)}
        if score>best_score: best_score=score; best_name=name
    factory={'random_forest':lambda:RandomForestClassifier(n_estimators=70,class_weight='balanced',n_jobs=-1,random_state=42),'extra_trees':lambda:ExtraTreesClassifier(n_estimators=70,class_weight='balanced',n_jobs=-1,random_state=42),'hist_gb':lambda:HistGradientBoostingClassifier(max_iter=120,random_state=42),'gradient_boosting':lambda:GradientBoostingClassifier(n_estimators=70,random_state=42)}
    production_df=_candidate_subset(df, 5000); full_train,_=_split(production_df,44); best=Pipeline([('imputer',SimpleImputer(strategy='median')),('model',factory[best_name]())]); best.fit(full_train[FEATURES],full_train['fusion_label'])
    out=ROOT/'models/goldtrace_fusion_v1.joblib'; joblib.dump(best,out,compress=3); write_json('reports/fusion_training.json',{'best_model':best_name,'candidates':results,'features':FEATURES,'dataset_rows':len(df),'candidate_comparison_rows':len(candidate),'production_training_pool_rows':len(production_df),'split_by_event_id':True}); print(f'Fusion model: {best_name} -> {out}'); return best

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--data',default='data/synthetic/goldtrace_sensor_windows.csv'); a=p.parse_args(); train(a.data)
