from __future__ import annotations
import argparse, json, time
from src.mock_sensor_stream import scenario_packets, SCENARIOS
from src.realtime_engine import RealtimeEngine


def print_result(result:dict):
    print('='*61); print('                         GOLDTRACE'); print('='*61)
    for node_id,node in result.get('node_results',{}).items():
        print(f"\n{node_id}\nEnvironment : {node.get('environment')}\nAudio       : {node.get('audio')}\nVibration   : {node.get('vibration')}\nTurbidity   : {node.get('turbidity_ntu')} NTU\nHealth      : {node.get('health')}")
    e=result.get('evidence',{}); loc=result.get('location') or {}; agency=result.get('agency_alert') or {}
    print('\n'+'-'*61)
    print(f"DETECTION: {result.get('human_description')}")
    print(f"TURBIDITY CHANGE: {float(e.get('turbidity_difference',0)):+.1f} NTU")
    print(f"ML CLASSIFICATION: {result.get('prediction')}")
    print(f"RISK LEVEL: {result.get('risk_level')}")
    print(f"CONFIDENCE: {100*float(result.get('confidence',0)):.0f}%")
    print(f"SUSPECTED ZONE: {result.get('suspected_zone')}")
    if loc:
        print(f"RIVER SEGMENT: {loc.get('segment_id')}")
        c=loc.get('centroid') or {}; print(f"APPROXIMATE CENTER: {c.get('latitude')}, {c.get('longitude')}")
    print('WHY:')
    for reason in e.get('reasons',[]): print(f'- {reason}')
    print('-'*61)
    print('SECURITY ALERT:')
    print(f"Eligibility: {'YES' if agency.get('eligible') else 'NO'}")
    print(f"Dispatch: {agency.get('dispatch_status','N/A')}")
    print(f"Authorized Recipients: {agency.get('recipient_count',0)}")
    print(f"Alert Location Included: {'YES' if loc else 'NO'}")
    print(f"Map Data Created: {'YES' if result.get('map') else 'NO'}")
    print('-'*61)
    print(f"RECOMMENDATION: {result.get('recommendation')}")
    print('='*61)


def run_demo(engine,scenario=None):
    scenarios=[scenario] if scenario else ['normal','heavy_rain','vehicle','water_pump','high_risk_mining','sensor_failure','mixed_rain_and_machinery']
    for s in scenarios:
        a,b=scenario_packets(s,seed=42); persistence=42 if s in {'high_risk_mining','possible_mining','mixed_rain_and_machinery'} else 8
        result=engine.process_pair(a,b,persistence_seconds=persistence); print(f"\nSCENARIO: {s.upper()}"); print_result(result)


def main():
    p=argparse.ArgumentParser(); p.add_argument('--mode',choices=['demo','live'],default='demo'); p.add_argument('--scenario',choices=SCENARIOS); p.add_argument('--interval',type=float,default=2.0); args=p.parse_args(); engine=RealtimeEngine()
    if args.mode=='demo': run_demo(engine,args.scenario); return
    print('GoldTrace mock live mode. Ctrl+C to stop.')
    i=0
    try:
        while True:
            scenario=args.scenario or ('high_risk_mining' if i%10>=7 else 'normal'); a,b=scenario_packets(scenario,seed=42+i); result=engine.process_pair(a,b,persistence_seconds=max(0,(i%10-7)*args.interval)); print(json.dumps({'prediction':result['prediction'],'risk':result['risk_level'],'confidence':result['confidence'],'zone':result['suspected_zone'],'agency':result.get('agency_alert',{}).get('dispatch_status')},indent=2)); time.sleep(args.interval); i+=1
    except KeyboardInterrupt: print('Stopped.')
if __name__=='__main__': main()
