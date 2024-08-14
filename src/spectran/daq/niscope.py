from .daq import DAQ
import niscope
import numpy as np
import time

class NISCOPE(DAQ):
    
    def list_devices(self):
        return ["Dev1", "Dev2", "Dev3"]
        return niscope.Session.list_resources()
    
    def get_sequence(self, duration, sample_rate, averages) -> np.ndarray:
        output = np.empty((duration * sample_rate, averages))
        for i in range(averages):
            
            data = self.acquire(duration, sample_rate)
            output[:, i] = data
            # time.sleep(duration)
            
        return output
        
    def acquire(self, duration, sample_rate) -> np.ndarray:
        t = np.linspace(0, duration, int(duration * sample_rate))
        return np.sin(2*np.pi*50*t) + 0.5*np.sin(2*np.pi*120*t) + np.random.normal(0, 2, t.shape)
