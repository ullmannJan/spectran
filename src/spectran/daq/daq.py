"""This module contains all functionality regarding communication with the DAQ device.
"""

from .. import log, ureg
from enum import Enum

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

    @abstractmethod
    def list_ports(self) -> list[str]:
        """List ports picked up by self.connected_device

        Returns:
            list[str]: list of names of ports
        """

    @abstractmethod
    def list_term_configs(self) -> tuple[Enum, int]:
        """List of Terminal configurations and the default element"""
    
    def connect_device(self, resource_name):
        """Connect to the device

        Args:
            resource_name (str): name of the device to connect to
        """
        self.connected_device = resource_name
        return self.connected_device
    
    @abstractmethod
    def get_properties(self) -> dict:
        """Returns properties of self.connected_device in a dict"""
    
    @abstractmethod
    def get_sequence(self, data_holder:np.ndarray, 
                     average_index:int,
                     config:dict,
                     main_window,
                     plotting_signal:Signal) -> np.ndarray:
        """Get data from DAQ device

        Args:
            data_holder (np.ndarray): array to store data, one-dimensional
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
        return ["Dev1", "Dev2"]
    
    def list_ports(self):
        return ["ai1", "ai2", "ai3"]
    
    def list_term_configs(self):
        TEST = Enum("Test", names='RED GREEN BLUE')
        return TEST, TEST.RED 
    
    def get_properties(self):
        return super().get_properties()
    
    def get_sequence(self, data_holder:np.ndarray,
                     average_index:int, 
                     config:dict,
                     main_window,
                     plotting_signal:Signal):
        
        start_time = time.time()
        duration = config["duration"].to(ureg.second).magnitude
        sample_rate = config["sample_rate"].to(ureg.Hz).magnitude
        averages = config["averages"]
        
         # set gui information
        config["sample_rate_real"] = config["sample_rate"]
        main_window.main_ui.sample_rate_status.setText(f"{config['sample_rate_real'].to(ureg.Hz).magnitude:6g}")

        config["signal_range_min_real"] = config["signal_range_min"]
        config["signal_range_max_real"] = config["signal_range_max"]
        main_window.main_ui.range_min_status.setText(f"{config['signal_range_min_real'].to(ureg.volt).magnitude:.6g}")
        main_window.main_ui.range_max_status.setText(f"{config['signal_range_max_real'].to(ureg.volt).magnitude:.6g}")
        
        # this is where the data is acquired
        data_holder = self.acquire(duration, sample_rate)
        end_time = time.time()
        
        # simulate length
        waiting_time = duration - (end_time - start_time)
        if waiting_time > 0:
            time.sleep(waiting_time)
        
        log.info(f"Emit at {average_index+1}/{averages} - {(time.time()-start_time)*1e3:.2f} ms")
        plotting_signal.emit(average_index, data_holder)
        
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
