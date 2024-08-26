"""This class should contain all data related functionality."""
from . import log, ureg
from scipy.signal import welch, periodogram
import numpy as np 
from PySide6.QtWidgets import QFileDialog
from pathlib import Path

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

    def calculate_psd(self, index):
            if index is None:
                voltages = self.voltage_data
            else:
                voltages = self.voltage_data[:index+1]
            # self.frequencies, psds = welch(voltages,
            #                         fs=self._config["sample_rate"].to(ureg.Hz).magnitude)
            self.frequencies, psds = periodogram(voltages, 
                                                 fs=self._config["sample_rate"].to(ureg.Hz).magnitude)
            self.psd = np.mean(psds, axis=0)
            log.debug("PSD calculated until index {}".format(index))
            
            return self.frequencies, self.psd
        
    def calculate_data(self, data, index, progress_callback):
        if data is not None:
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
            + f"Sample Rate: {self._config['sample_rate_real']}\n"
            + f"Averages: {self._config['averages']}\n"
            + f"Unit for Data: {self._config['unit']}\n"
            + f"Signal Range: {self._config['signal_range_min_real']}, {self._config['signal_range_max_real']}")

        np.savetxt(self.file_path, self.voltage_data.T, 
                   delimiter="\t",
                   header=header_text)
        
        # self.main_window.statusBar().showMessage(f"Data saved to {self.file_path}")
        log.info("Data saved to {}".format(self.file_path))
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
        