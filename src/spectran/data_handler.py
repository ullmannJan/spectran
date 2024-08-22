"""This class should contain all data related functionality."""
from . import log, ureg
from scipy.signal import welch, periodogram
import numpy as np 
from PySide6.QtWidgets import QFileDialog
from pathlib import Path

class DataHandler():

    voltage_data = None
    data_has_changed = False
    # the index that has already been measured 
    current_index = 0 
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

    def calculate_psd(self, index):
            if index is None:
                voltages = self.voltage_data
            else:
                voltages = self.voltage_data[:self.current_index+1]
            self.frequencies, psds = welch(voltages,
                                    fs=self._config["sample_rate"].to(ureg.Hz).magnitude)
            print(self.frequencies.shape)
            self.psd = np.mean(psds, axis=0) 
            # self.frequencies, self.psd = periodogram(np.mean(self.voltage_data, axis=0), fs=self._config["sample_rate"].to(ureg.kHz).magnitude)
            log.debug("PSD calculated")
            
            return self.frequencies, self.psd
        
    def calculate_data(self, data, index, progress_callback):
        self.voltage_data = data
        self.data_has_changed = True
        self.calculate_psd(index)

    def save_file(self):
        
        filename = self.save_file_dialog()
        if filename is None:
            return
        
        self.file_path = Path(filename)
        header_text = (f"Measurement with Driver:{self._config['driver']} on Device:{self._config['device']}\n"
            + f"Date: {self._config['start_time']}\n"
            + f"Input Channel: {self._config['input_channel']}\n"
            + f"Duration: {self._config['duration']}\n"
            + f"Sample Rate: {self._config['sample_rate']}\n"
            + f"Averages: {self._config['averages']}\n"
            + f"Unit for Data: {self._config['unit']}\n")

        np.savetxt(self.file_path, self.voltage_data.T, 
                   delimiter="\t",
                   header=header_text)
        
        # self.main_window.statusBar().showMessage(f"Data saved to {self.file_path}")
        log.info(f"Data saved to {self.file_path}")
        self.main_window.save_window.close()

        # raise NotImplementedError("Saving data not implemented yet")

    
    def save_file_dialog(
        self, file_name="output.dat", extensions="Data-File (*.dat *.txt);;All Files (*)"
    ):
        filename, _ = QFileDialog.getSaveFileName(
            self.main_window.main_ui, "Save", file_name, extensions
        )
        if filename:
            return filename
        