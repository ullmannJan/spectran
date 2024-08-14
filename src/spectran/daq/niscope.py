from .daq import DAQ
import niscope
import numpy as np

class NISCOPE(DAQ):
    
    def list_devices(self) -> list[str]:
        return []
        return niscope.Session.list_resources()
    
    def get_sequence(self, duration, sample_rate, averages) -> np.ndarray:
        pass