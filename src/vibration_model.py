from __future__ import annotations
import torch
from torch import nn


class VibrationCNN(nn.Module):
    def __init__(self,num_classes:int=13):
        super().__init__()
        self.net=nn.Sequential(
            nn.Conv1d(1,16,9,padding=4),nn.BatchNorm1d(16),nn.ReLU(),nn.MaxPool1d(4),
            nn.Conv1d(16,32,7,padding=3),nn.BatchNorm1d(32),nn.ReLU(),nn.MaxPool1d(4),
            nn.Conv1d(32,64,5,padding=2),nn.BatchNorm1d(64),nn.ReLU(),nn.AdaptiveAvgPool1d(1),
            nn.Flatten(),nn.Dropout(0.25),nn.Linear(64,num_classes)
        )
    def forward(self,x): return self.net(x)
