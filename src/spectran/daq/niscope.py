from .daq import DAQ
import niscope
import numpy as np

class NISCOPE(DAQ):
    
    def list_devices(self):
        return ["Dev1", "Dev2", "Dev3"]
        return niscope.Session.list_resources()
    
    def get_sequence(self, t) -> np.ndarray:
        print(self.connected_device)
        return np.sin(2*np.pi*50*t) + 0.5*np.sin(2*np.pi*120*t) + np.random.normal(0, 2, t.shape)
            
