from src.risk_engine import assess_risk

def test_high_risk_requires_multiple_signals():
    r=assess_risk("HIGH_RISK_MINING_ACTIVITY",.9,{"turbidity_difference":70,"turbidity_a":18,"turbidity_b":88,"audio_machine_probability_b":.9,"vibration_machinery_probability_b":.9,"persistence_seconds":40},["HEALTHY","HEALTHY"]); assert r["risk_level"]=="CRITICAL"
def test_muddy_without_machine_not_critical():
    r=assess_risk("SAFE",.8,{"turbidity_difference":40,"turbidity_a":50,"turbidity_b":90,"audio_machine_probability_b":.1,"vibration_machinery_probability_b":.1,"persistence_seconds":40},["HEALTHY","HEALTHY"]); assert r["risk_level"]=="MEDIUM"
