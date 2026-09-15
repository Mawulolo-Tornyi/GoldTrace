from datetime import datetime, timezone
from src.sensor_validator import validate_packet

def packet():
    return {"node_id":"NODE_A","timestamp":datetime.now(timezone.utc).isoformat(),"turbidity_ntu":20,"water_temperature_c":26,"audio_samples":[0.1,-0.1,0.05,-0.05]*20,"vibration_samples":[0.1,-0.1,0.02,-0.02]*20,"battery_voltage":12.4,"lora_rssi":-70}

def test_healthy_packet(): assert validate_packet(packet())["health"] in {"HEALTHY","DEGRADED"}
def test_invalid_turbidity_fails():
    p=packet(); p["turbidity_ntu"]=99999; assert validate_packet(p)["health"]=="FAILED"
