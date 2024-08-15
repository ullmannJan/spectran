"""This module contains all functionality regarding communication with the DAQ device.
"""

from ..main_window import log, ureg

from abc import ABC, abstractmethod
import numpy as np
from PySide6.QtCore import Signal, QThread

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
                     config:dict,
                     plotting_signal:Signal) -> np.ndarray:
        """Get data from DAQ device

        Args:
            data_holder (np.ndarray): array to store data
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
                     config:dict,
                     plotting_signal:Signal) -> np.ndarray:
        
        duration = config["duration"].to(ureg.second).magnitude
        sample_rate = config["sample_rate"].to(ureg.Hz).magnitude
        averages = config["averages"]
        device = config["device"]
        log.info(f"Getting sequence from {device} for {duration} s at {sample_rate} kHz")
        
        old_time = time.time()
        for i in range(averages):
            data_holder[i] = self.acquire(duration, sample_rate)
            if i % 1 == 0:
                log.info(f"Emitting at {i+1}/{averages} - {(time.time()-old_time)*1e3:.2f} ms")
                plotting_signal.emit(data_holder)
            else:
                log.info(f"Updating at {i+1}/{averages} - {(time.time()-old_time)*1e3:.2f} ms")
            old_time = time.time()

        return data_holder
            
        
    def acquire(self, duration, sample_rate) -> np.ndarray:
        
        time.sleep(0.2)
        t = np.linspace(0, duration, int(duration * sample_rate))
        s = np.sin(2*np.pi*35_000*t) + 0.5*np.sin(2*np.pi*12_000*t) + 0.1*np.random.normal(0, 2, t.shape)
        return s
