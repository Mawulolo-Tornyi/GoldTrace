from src.fusion_classifier import FusionClassifier

def test_fusion_high_risk_heuristic():
    f=FusionClassifier().predict({"turbidity_difference":70,"audio_machine_probability_b":.9,"vibration_machinery_probability_b":.9,"persistence_seconds":40}); assert f["class"]=="HIGH_RISK_MINING_ACTIVITY"
