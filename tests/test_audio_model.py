import torch
from src.audio_model import AudioCNN

def test_audio_model_output_shape():
    m=AudioCNN(18); y=m(torch.randn(2,1,40,97)); assert y.shape==(2,18)
