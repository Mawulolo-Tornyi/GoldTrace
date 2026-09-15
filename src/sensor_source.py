from __future__ import annotations
from abc import ABC, abstractmethod
import json
from pathlib import Path
from typing import Iterator

class SensorSource(ABC):
    @abstractmethod
    def packets(self)->Iterator[dict]: ...

class MockSensorSource(SensorSource):
    def __init__(self,packets_list:list[dict]): self.items=packets_list
    def packets(self): yield from self.items

class FileSensorSource(SensorSource):
    def __init__(self,path:str|Path): self.path=Path(path)
    def packets(self):
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip(): yield json.loads(line)

class APIInputSensorSource(SensorSource):
    def __init__(self): self.queue=[]
    def push(self,packet:dict): self.queue.append(packet)
    def packets(self):
        while self.queue: yield self.queue.pop(0)

class LoRaSensorSource(SensorSource):
    """Hardware adapter interface. Implement radio-specific code outside the ML core."""
    def packets(self):
        raise NotImplementedError("Attach an RFM95/SX1276 driver implementation for deployment")
