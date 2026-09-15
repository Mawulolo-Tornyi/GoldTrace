from __future__ import annotations
from pathlib import Path
import json
from .config import ROOT, load_settings
from .audio_classifier import AudioClassifier
from .vibration_classifier import VibrationClassifier
from .environmental_classifier import EnvironmentalClassifier
from .anomaly_detector import AnomalyDetector
from .fusion_classifier import FusionClassifier


class ModelManager:
    def __init__(self):
        cfg=load_settings()["models"]
        def p(k):
            v=Path(cfg[k]); return v if v.is_absolute() else ROOT/v
        self.audio=AudioClassifier(p("audio_classical"),p("audio_onnx"))
        self.vibration=VibrationClassifier(p("vibration_classical"),p("vibration_onnx"))
        self.environment=EnvironmentalClassifier(p("environment"))
        self.anomaly=AnomalyDetector(p("anomaly"))
        self.fusion=FusionClassifier(p("fusion"))
        reg=p("registry"); self.registry=json.loads(reg.read_text()) if reg.exists() else {"models":[]}
    def status(self):
        return {"audio_loaded":self.audio.onnx_session is not None or self.audio.model is not None,"audio_runtime":"onnx" if self.audio.onnx_session is not None else ("sklearn" if self.audio.model is not None else "heuristic"),"vibration_loaded":self.vibration.onnx_session is not None or self.vibration.model is not None,"vibration_runtime":"onnx" if self.vibration.onnx_session is not None else ("sklearn" if self.vibration.model is not None else "heuristic"),"environment_loaded":self.environment.model is not None,"anomaly_loaded":self.anomaly.model is not None,"fusion_loaded":self.fusion.model is not None}
