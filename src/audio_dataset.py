from __future__ import annotations
import numpy as np
import torch
from torch.utils.data import Dataset
from .audio_features import log_mel_spectrogram


class AudioWaveDataset(Dataset):
    def __init__(self, waveforms, labels, sample_rate: int = 16000, n_mels: int = 40):
        self.waveforms = waveforms; self.labels = labels; self.sample_rate=sample_rate; self.n_mels=n_mels
    def __len__(self): return len(self.labels)
    def __getitem__(self, idx):
        spec=log_mel_spectrogram(np.asarray(self.waveforms[idx],dtype=np.float32),self.sample_rate,self.n_mels)
        x=torch.from_numpy(spec).unsqueeze(0)
        return x, torch.tensor(int(self.labels[idx]),dtype=torch.long)
