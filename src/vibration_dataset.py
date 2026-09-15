from __future__ import annotations
import numpy as np
import torch
from torch.utils.data import Dataset


class VibrationDataset(Dataset):
    def __init__(self, windows, labels): self.windows=windows; self.labels=labels
    def __len__(self): return len(self.labels)
    def __getitem__(self,idx):
        x=np.asarray(self.windows[idx],dtype=np.float32)
        return torch.from_numpy(x).unsqueeze(0), torch.tensor(int(self.labels[idx]),dtype=torch.long)
