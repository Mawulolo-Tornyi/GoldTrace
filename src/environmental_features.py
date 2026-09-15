from __future__ import annotations
import numpy as np


def extract_environmental_features(turbidity_values, temperature_values=None, baseline:dict|None=None, sample_period:float=1.0)->dict[str,float]:
    t=np.asarray(turbidity_values,dtype=float); t=t[np.isfinite(t)]
    if t.size==0: raise ValueError("no valid turbidity values")
    temp=np.asarray(temperature_values if temperature_values is not None else [],dtype=float); temp=temp[np.isfinite(temp)]
    baseline=baseline or {}
    current=float(t[-1]); mean=float(t.mean()); std=float(t.std()); med=float(np.median(t)); mn=float(t.min()); mx=float(t.max()); slope=float(np.polyfit(np.arange(len(t))*sample_period,t,1)[0]) if len(t)>1 else 0.0
    base=baseline.get("turbidity_ntu"); diff=current-float(base) if base is not None else 0.0; ratio=current/max(float(base),1e-6) if base is not None else 1.0
    out={"turbidity_current":current,"turbidity_mean":mean,"turbidity_median":med,"turbidity_std":std,"turbidity_min":mn,"turbidity_max":mx,"turbidity_range":mx-mn,"turbidity_rate_of_change":slope,"turbidity_percent_change":100*(current-t[0])/max(abs(t[0]),1e-6),"turbidity_moving_average":float(t[-min(5,len(t)):].mean()),"turbidity_ema":float(_ema(t,0.3)),"turbidity_baseline_difference":diff,"turbidity_baseline_ratio":ratio,"turbidity_spike_count":float(np.sum(np.abs(np.diff(t))>max(10,2*std))),"turbidity_event_duration":float(len(t)*sample_period),"turbidity_slope":slope}
    if temp.size:
        base_temp=baseline.get("temperature_c"); out.update({"temperature_current":float(temp[-1]),"temperature_mean":float(temp.mean()),"temperature_std":float(temp.std()),"temperature_min":float(temp.min()),"temperature_max":float(temp.max()),"temperature_baseline_difference":float(temp[-1]-base_temp) if base_temp is not None else 0.0,"temperature_rate_of_change":float(np.polyfit(np.arange(len(temp))*sample_period,temp,1)[0]) if len(temp)>1 else 0.0})
    return out


def _ema(x,alpha):
    v=float(x[0])
    for item in x[1:]: v=alpha*float(item)+(1-alpha)*v
    return v
