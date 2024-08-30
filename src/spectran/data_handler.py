"""This class should contain all data related functionality."""
from . import log, ureg
from scipy.signal import welch, periodogram
import numpy as np 
from PySide6.QtWidgets import QFileDialog
from pathlib import Path

class DataHandler():

    voltage_data = None
    done_indices:set = set() # set of indices that have been calculated
    time_seq = None
    frequencies = None
    psd = None
    _config = dict()

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
        # if index is None, calculate the psd for all averages
        # but only if the psd has not been calculated yet 
        n = len(self.done_indices)
        
        # if the user wants to stop plotting, calculate the psd for all averages
        if self.main_window.main_ui.stop_plotting:
            if index is not None:
                log.debug("Abort calculating PSD at index {}".format(index))
                return
            else:
                log.debug("calculate PSD for all averages")
                n = self.voltage_data.shape[0]
        
        # if all have been calculated       
        if n == self.voltage_data.shape[0]:
            # calculate psds for all averages at the end
            self.frequencies, self.psds = periodogram(self.voltage_data, 
                                                fs=self._config["sample_rate"].to(ureg.Hz).magnitude)
            self.psd = np.mean(self.psds, axis=0)
            index = self.psds.shape[0]-1
            
            log.debug("All PSDs calculated")
            
        else:
            # calculate the psd for current index
            if self.main_window.main_ui.plot_spectrum_cb.isChecked():
                self.frequencies, self.psds[index] = periodogram(self.voltage_data[index], 
                                                    fs=self._config["sample_rate"].to(ureg.Hz).magnitude)
                # calculate the average from previous psd
                if index is not None:
                    self.done_indices.add(index)
                
                # iterative average
                self.psd = self.psd * (n / (n+1)) + self.psds[index] / (n+1)

            log.debug("PSD calculated at index {}".format(index))

        return self.frequencies, self.psd

    def initialize(self, averages, duration, sample_rate):
        self.voltage_data = None
        self.psds = None
        self.psd = None
        
        self.voltage_data = np.empty((averages, int(duration * sample_rate)))
        self.psds = np.empty(((averages, int(duration * sample_rate)//2+1)))
        self.psd = np.zeros((int(duration * sample_rate)//2+1))
        self.done_indices = set()
        
    def calculate_data(self, data:np.ndarray, index:int, progress_callback):
        """Calculates the PSD of the data and stores it in the 
        psd attribute.

        Args:
            data (np.ndarray): one dimensional array of data 
                if data is None, only the psd is calculated
            index (int): average index of data
            progress_callback (Signal): _description_
        """
        if data is not None:
            self.voltage_data[index] = data
        self.calculate_psd(index)

    def save_file(self, file_path:str|Path=None):
        """Saves the data to a file. If no file_path is given, a file dialog is opened.

        Args:
            file_path (str|Path, optional): where to save file. Defaults to None.
        """
        if not self.main_window.measurement_stopped:
            self.main_window.raise_error("Measurement is still running. Stop it first.")            
            return 
        
        if self.voltage_data is None:
            self.main_window.raise_error("No data to save")
            return
        
        if file_path is None:
            file_path = self.save_file_dialog()
        if file_path is None:
            return
        
        
        self.file_path = Path(file_path)
        header_text = (f"Measurement with Driver:{self._config['driver']} on Device:{self._config['device']}\n"
            + f"Date: {self._config['start_time']}\n"
            + f"Input Channel: {self._config['input_channel']} with {self._config['terminal_config']}\n"
            + f"Duration: {self._config['duration']}\n"
            + f"Sample Rate: {self._config['sample_rate_real']}\n"
            + f"Signal Range: {self._config['signal_range_min_real']}, {self._config['signal_range_max_real']}\n"
            + f"Averages: {self._config['averages']}\n"
            + f"Unit of Data: {self._config['unit']}\n"
            )

        np.savetxt(self.file_path, self.voltage_data.T, 
                   delimiter="\t",
                   header=header_text)
        
        # self.main_window.statusBar().showMessage(f"Data saved to {self.file_path}")
        log.info("Data saved to {}".format(self.file_path))
        return self.file_path
    
    def save_file_dialog(
        self, file_name="output.dat", extensions="Data-File (*.dat *.txt);;All Files (*)"
    ):
        filename, _ = QFileDialog.getSaveFileName(
            self.main_window.main_ui, "Save", file_name, extensions
        )
        if filename:
            return filename
        
    def cut_data(self, index):
        """cuts data self.voltage_data[:index] and self.psds[:index]

        Args:
            index (_type_): _description_
        """
        if self.voltage_data.shape[0] > index+1:
            self.voltage_data = self.voltage_data[:index]
            self.psds = self.psds[:index]
        