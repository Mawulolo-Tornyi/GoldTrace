from __future__ import annotations


def lcd_pages(result:dict)->list[list[str]]:
    a=result.get('node_results',{}).get('NODE_A',{})
    b=result.get('node_results',{}).get('NODE_B',{})
    e=result.get('evidence',{})
    pages=[
        ['GOLDTRACE ACTIVE',f"A: {a.get('health','?')[:12]}",f"B: {b.get('health','?')[:12]}",f"RISK: {result.get('risk_level','?')[:11]}"],
        [f"TURB {float(e.get('turbidity_difference',0)):+.1f} NTU",f"AUDIO {100*float(e.get('audio_machine_probability',0)):.0f}%",f"VIB   {100*float(e.get('vibration_machinery_probability',0)):.0f}%",f"ZONE {result.get('suspected_zone','?')[:14]}"],
    ]
    agency=result.get('agency_alert',{})
    if agency:
        pages.append([f"ALERT {agency.get('dispatch_status','N/A')[:13]}",f"RECIP {agency.get('recipient_count',0)}",f"EVENT {(result.get('event_id') or 'NONE')[-9:]}",f"LOC {'YES' if result.get('location') else 'NO'}"])
    return [[str(x)[:20] for x in p] for p in pages]
