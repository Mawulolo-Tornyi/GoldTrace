from __future__ import annotations
import numpy as np


def node_comparison_features(a:dict,b:dict)->dict[str,float]:
    ta=float(a.get("turbidity_ntu",a.get("turbidity_current",0)) or 0); tb=float(b.get("turbidity_ntu",b.get("turbidity_current",0)) or 0)
    aa=float(a.get("audio_machine_probability",a.get("machine_probability",0)) or 0); ab=float(b.get("audio_machine_probability",b.get("machine_probability",0)) or 0)
    va=float(a.get("vibration_machinery_probability",0) or 0); vb=float(b.get("vibration_machinery_probability",0) or 0)
    ar=float(a.get("audio_rms",0) or 0); br=float(b.get("audio_rms",0) or 0); vr_a=float(a.get("vibration_rms",0) or 0); vr_b=float(b.get("vibration_rms",0) or 0)
    diff=tb-ta
    simultaneous_av=float(ab>0.65 and vb>0.65); simultaneous_at=float(ab>0.65 and diff>20); simultaneous_vt=float(vb>0.65 and diff>20)
    confirm=(simultaneous_av+simultaneous_at+simultaneous_vt)/3.0
    return {"turbidity_difference":diff,"turbidity_ratio":tb/max(ta,1e-6),"turbidity_percent_increase":100*diff/max(abs(ta),1e-6),"temperature_difference":float(b.get("water_temperature_c",0) or 0)-float(a.get("water_temperature_c",0) or 0),"audio_rms_difference":br-ar,"audio_machine_probability_difference":ab-aa,"vibration_rms_difference":vr_b-vr_a,"vibration_energy_difference":float(b.get("vibration_energy",0) or 0)-float(a.get("vibration_energy",0) or 0),"vibration_machinery_probability_difference":vb-va,"upstream_normal_downstream_abnormal":float(ta<35 and tb>50),"downstream_pollution_score":float(np.clip(diff/80,0,1)),"simultaneous_audio_vibration_flag":simultaneous_av,"simultaneous_audio_turbidity_flag":simultaneous_at,"simultaneous_vibration_turbidity_flag":simultaneous_vt,"multi_sensor_confirmation_score":confirm,"node_agreement_score":float(1-abs(ab-vb)),"node_disagreement_score":float(abs(ab-vb)),"machine_environment_correlation":float(np.clip((ab+vb)/2*np.clip(diff/50,0,1),0,1)),"spatial_change_score":float(np.clip(abs(diff)/100 + abs(ab-aa)/2 + abs(vb-va)/2,0,1))}
