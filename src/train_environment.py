from __future__ import annotations
import argparse, joblib, pandas as pd
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, HistGradientBoostingClassifier, GradientBoostingClassifier
from sklearn.metrics import f1_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from .config import ROOT
from .utils import write_json

FEATURES=['turbidity_a','turbidity_b','turbidity_difference','turbidity_ratio','turbidity_percent_increase','temp_a','temp_b','temperature_difference','persistence_seconds']

def split_groups(df):
    gss=GroupShuffleSplit(n_splits=1,test_size=.2,random_state=42); tr,te=next(gss.split(df,groups=df['event_id'])); train=df.iloc[tr]; test=df.iloc[te]
    gss2=GroupShuffleSplit(n_splits=1,test_size=.2,random_state=43); tr2,va=next(gss2.split(train,groups=train['event_id'])); return train.iloc[tr2],train.iloc[va],test

def _candidate_subset(df, max_rows=2000):
    if len(df)<=max_rows: return df
    # Event-aware subset: take complete events until the target size is reached.
    events=df['event_id'].drop_duplicates().sample(frac=1,random_state=42)
    selected=[]; count=0
    sizes=df.groupby('event_id').size()
    for e in events:
        selected.append(e); count += int(sizes.loc[e])
        if count>=max_rows: break
    return df[df['event_id'].isin(selected)]

def train(path:str='data/synthetic/goldtrace_sensor_windows.csv'):
    df=pd.read_csv(ROOT/path); candidate_df=_candidate_subset(df); tr,va,_=split_groups(candidate_df)
    cands={'random_forest':RandomForestClassifier(n_estimators=80,class_weight='balanced',n_jobs=-1,random_state=42),'extra_trees':ExtraTreesClassifier(n_estimators=80,class_weight='balanced',n_jobs=-1,random_state=42),'hist_gb':HistGradientBoostingClassifier(max_iter=80,random_state=42),'gradient_boosting':GradientBoostingClassifier(n_estimators=50,random_state=42)}
    scores={}; best_name=None; best_score=-1
    for name,m in cands.items():
        pipe=Pipeline([('imputer',SimpleImputer(strategy='median')),('model',m)]); pipe.fit(tr[FEATURES],tr['environment_label']); s=f1_score(va['environment_label'],pipe.predict(va[FEATURES]),average='macro'); scores[name]=float(s)
        if s>best_score: best_score=s; best_name=name
    factory={'random_forest':lambda:RandomForestClassifier(n_estimators=100,class_weight='balanced',n_jobs=-1,random_state=42),'extra_trees':lambda:ExtraTreesClassifier(n_estimators=100,class_weight='balanced',n_jobs=-1,random_state=42),'hist_gb':lambda:HistGradientBoostingClassifier(max_iter=100,random_state=42),'gradient_boosting':lambda:GradientBoostingClassifier(n_estimators=70,random_state=42)}
    production_df=_candidate_subset(df, 5000); full_train,_,_=split_groups(production_df); best=Pipeline([('imputer',SimpleImputer(strategy='median')),('model',factory[best_name]())]); best.fit(full_train[FEATURES],full_train['environment_label'])
    out=ROOT/'models/goldtrace_environment_v1.joblib'; joblib.dump(best,out,compress=3); write_json('reports/environment_training.json',{'best_model':best_name,'validation_macro_f1':best_score,'candidates':scores,'features':FEATURES,'dataset_rows':len(df),'candidate_comparison_rows':len(candidate_df),'production_training_pool_rows':len(production_df),'split_by_event_id':True}); print(f'Environment model: {best_name} macro-F1={best_score:.3f} -> {out}'); return best

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--data',default='data/synthetic/goldtrace_sensor_windows.csv'); a=p.parse_args(); train(a.data)
