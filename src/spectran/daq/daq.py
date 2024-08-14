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
    
    def get_connected_device(self) -> str:
        """Get the name of the connected device

        Returns:
            str: name of the connected device
        """
        return self.connected_device
    
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
