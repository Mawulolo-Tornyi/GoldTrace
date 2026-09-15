import torch
from src.vibration_model import VibrationCNN

def test_vibration_model_output_shape():
    m=VibrationCNN(13); y=m(torch.randn(2,1,2000)); assert y.shape==(2,13)
