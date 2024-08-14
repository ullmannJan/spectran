"""This module contains all functionality regarding communication with the DAQ device.
"""

from ..main_window import log

from abc import ABC, abstractmethod

class DAQ(ABC):
    
    connected_device: str = None
    
    @abstractmethod
    def list_devices(self) -> list[str]:
        """List devices picked up by driver

        Returns:
            list[str]: list of names of devices
        """
    
    def connect_device(self, resource_name):
        """Connect to the device

        Args:
            resource_name (str): name of the device to connect to
        """
        self.connected_device = resource_name
        return self.connected_device
    
    @abstractmethod
    def get_sequence(self, channels, options, length, voltage):
        """Get a sequence of data from the device

        Args:
            resource_name (str): device to connect to
            channels (_type_): _description_
            options (_type_): _description_
            length (float): time in seconds
            voltage (_type_): _description_
        """

import numpy as np
import time
class DummyDAQ(DAQ):
     
    def list_devices(self):
        return ["Dev1", "Dev2", "Dev3"]
    
    def get_sequence(self, data_holder:np.ndarray, 
                     duration:float, 
                     sample_rate:float, 
                     averages:int,
                     plotting_signal) -> np.ndarray:
        
        for i in range(averages):
            print(f"Acquiring data {i+1}/{averages}")
            data_holder[i] = self.acquire(duration, sample_rate)
            plotting_signal.emit(data_holder)

        return data_holder
            
        
    def acquire(self, duration, sample_rate) -> np.ndarray:
        
        # time.sleep(duration)
        t = np.linspace(0, duration, int(duration * sample_rate))
        s = np.sin(2*np.pi*35_000*t) + 0.5*np.sin(2*np.pi*12_000*t) + 0.1*np.random.normal(0, 2, t.shape)
        return s
