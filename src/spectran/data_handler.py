"""This class should contain all data related functionality."""
from .main_window import log, ureg
from scipy.signal import welch
import numpy as np 

class DataHandler():

    voltage_data = None
    data_has_changed = False
    time_seq = None
    frequencies = None
    psd = None
    _config = None

    def __init__(self, main_window) -> None:
        self.main_window = main_window

    # config setter and getter    
    @property
    def config(self):
        return self._config
    
    @config.setter
    def config(self, value):
        self._config = value

        # calculate time sequence
        self.time_seq = np.linspace(0, 
            self._config["duration"].to(ureg.second).magnitude, 
            int(self._config["duration"].to(ureg.second).magnitude * self._config["sample_rate"].to(ureg.Hz).magnitude))

    def calculate_psd(self):
        
            self.frequencies, self.psd = welch(np.mean(self.voltage_data, axis=0), 
                fs=self._config["sample_rate"].to(ureg.kHz).magnitude)
            log.debug("PSD calculated")
            
            return self.frequencies, self.psd
        
    def calculate_data(self, data, progress_callback):
        self.voltage_data = data
        self.data_has_changed = True
        self.calculate_psd()
