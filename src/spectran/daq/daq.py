"""This module contains all functionality regarding communication with the DAQ device.
"""

from .. import log, ureg

from abc import ABC, abstractmethod
import numpy as np
from PySide6.QtCore import Signal

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
    def get_sequence(self, data_holder:np.ndarray, 
                     average_index:int,
                     config:dict,
                     plotting_signal:Signal) -> np.ndarray:
        """Get data from DAQ device

        Args:
            data_holder (np.ndarray): array to store data
            average_index (int): index of average
            config (dict): configuration dictionary
            plotting_signal (Signal): signal to emit when to plot. 
                    This is filled automatically by the Worker class 

        Returns:
            np.ndarray: data_holder with data
        """
import time
class DummyDAQ(DAQ):
     
    def list_devices(self):
        return ["Dev1", "Dev2", "Dev3"]
    
    def get_sequence(self, data_holder:np.ndarray,
                     average_index:int, 
                     config:dict,
                     plotting_signal:Signal):
        
        duration = config["duration"].to(ureg.second).magnitude
        sample_rate = config["sample_rate"].to(ureg.Hz).magnitude
        averages = config["averages"]
        
        start_time = time.time()
        # this is where the data is acquired
        data_holder[average_index] = self.acquire(duration, sample_rate)
        
        if average_index % 1 == 0:
            log.info(f"Emit at {average_index+1}/{averages} - {(time.time()-start_time)*1e3:.2f} ms")
            plotting_signal.emit(average_index, data_holder)
        else:
            log.info(f"Updating at {average_index+1}/{averages} - {(time.time()-start_time)*1e3:.2f} ms")

        
    def acquire(self, duration, sample_rate) -> np.ndarray:
        """A wrapper function to simulate data acquisition. 
        You don't need to use such a function in your implementation.
        """
        
        t = np.linspace(0, duration, int(duration * sample_rate))
        num_freqs = 100
        rand = 1e6 * np.sort(np.random.random(num_freqs))
        decrease = np.logspace(10, 0.1, num_freqs)
        s = np.random.normal(0, 0.1, len(t))
        s += np.sum(decrease[:, np.newaxis] * np.sin(2 * np.pi * rand[:, np.newaxis] * t), axis=0)
       
        return s
