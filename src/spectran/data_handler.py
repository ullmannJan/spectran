"""This class should contain all data related functionality."""

from enum import Enum
from pathlib import Path

import h5py
import numpy as np
from PySide6.QtWidgets import QFileDialog
from scipy.signal import periodogram

from . import log, ureg

SAVING_MODES = Enum("SavingModes", "PLAIN_TEXT NP_BINARY NP_COMPRESSED HDF5")


class DataHandler:
    """This class should contain all data related functionality. It also contains 
    all variables that need to be shared between the different classes.
    """

    voltage_data:np.ndarray|None = None
    # set of indices where PSD has been calculated
    done_indices: set = set()  
    time_seq:np.ndarray|None = None
    frequencies:np.ndarray|None = None
    psd:np.ndarray|None = None
    _config:dict = dict()
    use_memory_optimization:bool = False

    
    # Memory optimization settings
    MAX_STORED_MEASUREMENTS:int = 2  # Can be configured as needed
    
    # Average voltage data for optimized mode
    average_voltage_data:np.ndarray|None = None
    
    # Average PSD data for optimized mode (changed from voltage to PSD averaging)
    average_psd_data:np.ndarray|None = None

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
        self.time_seq = np.linspace(
            0,
            self._config["duration"].to(ureg.second).magnitude,
            int(
                self._config["duration"].to(ureg.second).magnitude
                * self._config["sample_rate"].to(ureg.Hz).magnitude
            ),
        )

    def set_max_stored_measurements(self, max_stored_measurements):
        """Configure memory optimization settings.
        
        Args:
            max_stored_measurements (int): Maximum number of measurements to keep in memory.
                                         Useful for large average counts to save memory.
        """
        self.MAX_STORED_MEASUREMENTS = max_stored_measurements
        log.info("Memory optimization configured: storing max {} measurement iterations".format(max_stored_measurements))


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
                # Only set n for traditional mode (optimized mode doesn't need it)
                if not self.use_memory_optimization:
                    n = self.voltage_data.shape[0]

        # Choose calculation method based on optimization setting
        if self.use_memory_optimization:
            # Memory-optimized version: return the averaged PSD directly
            if self.average_psd_data is not None:
                self.psd = self.average_psd_data
                log.debug("PSD returned from averaged PSD data (optimized mode, index: {})".format(index))
                return self.frequencies, self.psd
            else:
                log.warning("No average PSD data available")
                return self.frequencies, self.psd
        else:
            # Traditional version: store all data
            # if all have been calculated
            if n == self.voltage_data.shape[0]:
                # calculate psds for all averages that have not been calculated at the end
                undone_idxs = list(
                    set(range(self.voltage_data.shape[0])) - self.done_indices
                )
                if not undone_idxs:
                    log.debug("Nothing undone")
                    return self.frequencies, self.psd
                self.frequencies, self.psds[undone_idxs] = periodogram(
                    self.voltage_data[undone_idxs],
                    fs=self._config["sample_rate"].to(ureg.Hz).magnitude,
                )
                self.psd = np.mean(self.psds, axis=0)
                index = self.psds.shape[0] - 1

                log.debug(
                    "All PSDs calculated ({}/{} at the end)".format(len(undone_idxs), n)
                )

            else:
                # calculate the psd for current index
                if self.main_window.main_ui.plot_spectrum_cb.isChecked():
                    self.frequencies, self.psds[index] = periodogram(
                        self.voltage_data[index],
                        fs=self._config["sample_rate"].to(ureg.Hz).magnitude,
                    )
                    # calculate the average from previous psd
                    if index is not None:
                        self.done_indices.add(index)

                    # iterative average
                    self.psd = self.psd * (n / (n + 1)) + self.psds[index] / (n + 1)

                log.debug("PSD calculated at index {} (traditional)".format(index))

        return self.frequencies, self.psd
    
    def get_measurement_storage_index(self, measurement_index):
        """Get the correct storage index for a measurement based on optimization mode.
        
        Args:
            measurement_index (int): The global measurement index (0 to averages-1)
            
        Returns:
            int: The array index where this measurement should be stored
        """
        if hasattr(self, 'use_memory_optimization') and self.use_memory_optimization:
            # Circular buffer: map measurement index to storage index
            storage_index = measurement_index % self.voltage_data.shape[0]
            return storage_index
        else:
            # Traditional: direct mapping
            return measurement_index
    
    def update_average_voltage_data(self, measurement_index):
        """Update the average voltage data for optimized mode.
        
        Args:
            measurement_index (int): The current measurement index (0 to averages-1)
        """
        # Early return if not in optimized mode
        if not self.use_memory_optimization:
            return
            
        if self.average_voltage_data is None:
            log.warning("Average voltage data not initialized")
            return
        
        # Get the storage index where the current measurement is stored
        storage_index = self.get_measurement_storage_index(measurement_index)
        current_voltage = self.voltage_data[storage_index]
        
        # Update iterative average: new_avg = old_avg * (n-1)/n + new_value/n
        measurement_count = measurement_index + 1  # measurement_index is 0-based
        self.average_voltage_data = (self.average_voltage_data * (measurement_count - 1) / measurement_count + 
                                   current_voltage / measurement_count)
        
        log.debug("Updated average voltage data with measurement {} (count: {})".format(
            measurement_index, measurement_count))

    def update_average_psd_data(self, measurement_index):
        """Update the average PSD data for optimized mode.
        
        Args:
            measurement_index (int): The current measurement index (0 to averages-1)
        """
        # Early return if not in optimized mode
        if not self.use_memory_optimization:
            return
            
        # Get the storage index where the current measurement is stored
        storage_index = self.get_measurement_storage_index(measurement_index)
        current_voltage = self.voltage_data[storage_index]
        
        # Calculate frequencies only once (they're the same for all measurements)
        if self.frequencies is None:
            self.frequencies, _ = periodogram(
                current_voltage,
                fs=self._config["sample_rate"].to(ureg.Hz).magnitude,
            )
        
        # Calculate PSD for current measurement (we only need the PSD values, frequencies are already stored)
        _, current_psd = periodogram(
            current_voltage,
            fs=self._config["sample_rate"].to(ureg.Hz).magnitude,
        )
        
        # Initialize average PSD data on first measurement
        if self.average_psd_data is None:
            self.average_psd_data = np.zeros_like(current_psd)
        
        # Update iterative average: new_avg = old_avg * (n-1)/n + new_value/n
        measurement_count = measurement_index + 1  # measurement_index is 0-based
        self.average_psd_data = (self.average_psd_data * (measurement_count - 1) / measurement_count + 
                               current_psd / measurement_count)
        
        log.debug("Updated average PSD data with measurement {} (count: {})".format(
            measurement_index, measurement_count))

    def initialize(self, averages, duration, sample_rate):
        # delete old data
        self.voltage_data = None
        self.psds = None
        self.psd = None
        self.frequencies = None
        self.average_voltage_data = None
        self.average_psd_data = None

        self.use_memory_optimization = self._config.get("optimized_measurement", False)

        # Check if memory optimization is enabled via config
        if self.use_memory_optimization:
            # For memory optimization: only store limited data
            # Get max stored measurements from config (set by GUI)
            config_max_stored = self._config.get("max_stored_measurements", 2)
            # Update the class variable with the config value
            self.MAX_STORED_MEASUREMENTS = config_max_stored

            max_stored_measurements = self.MAX_STORED_MEASUREMENTS  # Use configured value without limit
            log.info("Memory optimization enabled: storing max {} measurements for {} averages"
                    .format(max_stored_measurements, averages))
            
            # Initialize average voltage data for optimized mode (legacy - keep for compatibility)
            self.average_voltage_data = np.zeros((int(duration * sample_rate)))
            # average_psd_data will be initialized dynamically when first PSD is calculated
            
        else:
            # Traditional approach: store all measurements
            max_stored_measurements = averages
            log.info("Memory optimization disabled: storing all {} measurements".format(averages))
        
        # create space for new measurements
        self.voltage_data = np.empty((max_stored_measurements, int(duration * sample_rate)))
        self.psds = np.empty((max_stored_measurements, int(duration * sample_rate) // 2 + 1))
        self.psd = np.zeros((int(duration * sample_rate) // 2 + 1))
        self.done_indices = set()
        
        # Store total number of averages and optimization flag for proper averaging
        self.total_averages = averages
        self.current_measurement_index = 0

    def calculate_data(
        self, index: int, ignore_check: bool = True, progress_callback=None
    ):
        """Calculates the PSD of the data and stores it in the
        psd attribute only if the plotting of psd is enabled.

        Args:
            data (np.ndarray): one dimensional array of data
                if data is None, only the psd is calculated
            index (int): average index of data
            ignore_check (bool): if True, the psd is calculated regardless of the plotting setting
            progress_callback (Signal): _description_
        """
        # Check if there is data to calculate PSD from
        if self.use_memory_optimization:
            # Optimized mode: check if average voltage data exists
            if self.average_voltage_data is None:
                raise ValueError("No average voltage data to calculate PSD from (optimized mode)")
        else:
            # Traditional mode: check if voltage data exists
            if self.voltage_data is None:
                raise ValueError("No voltage data to calculate PSD from (traditional mode)")

        if ignore_check or self.main_window.main_ui.plot_spectrum_cb.isChecked():
            self.calculate_psd(index)

    def save_file(
        self,
        file_path: str | Path = None,
        mode: SAVING_MODES = SAVING_MODES.PLAIN_TEXT,
        save_psds: bool = False,
        save_time_line: bool = False,
    ):
        """Saves the data to a file. If no file_path is given, a file dialog is opened.

        Args:
            file_path (str|Path, optional): where to save file. Defaults to None.
            mode: SAVING_MODES: how to save the file. Defaults to SAVING_MODES.PLAIN_TEXT.
            save_psd (bool, optional): save the psd data. Defaults to False. Not Implemented.
            save_time_line (bool, optional): save the time line. Defaults to False. Not Implemented.
        """
        if not self.main_window.measurement_stopped:
            self.main_window.raise_error("Measurement is still running. Stop it first.")
            return

        if self.voltage_data is None:
            self.main_window.raise_error("No data to save")
            return

        if self.frequencies is None and save_psds:
            self.main_window.raise_error(
                "No PSDs calculated, probably because you choose not to plot them"
            )
            return

        if file_path is None:
            file_name = "output.txt"
            match mode:
                case SAVING_MODES.NP_BINARY:
                    file_name = "output.npy"
                case SAVING_MODES.NP_COMPRESSED:
                    file_name = "output.npz"
                case SAVING_MODES.HDF5:
                    file_name = "output.h5"
            file_path = self.save_file_dialog(file_name)
        if file_path is None:
            return

        self.file_path = Path(file_path)
        header_text = (
            f"Measurement with Driver:{self._config['driver']} on Device:{self._config['device']}\n"
            + f"Date: {self._config['start_time']}\n"
            + f"Input Channel: {self._config['input_channel']} with {self._config['terminal_config']}\n"
            + f"Duration: {self._config['duration']}\n"
            + f"Sample Rate: {self._config['sample_rate_real']}\n"
            + f"Signal Range: {self._config['signal_range_min_real']}, {self._config['signal_range_max_real']}\n"
            + f"Averages: {self._config['averages']}\n"
            + f"Unit of Data: {self._config['unit']}\n"
            + f"Optimized Mode: {self._config.get('optimized_measurement', False)}\n"
        )

        match mode:
            case SAVING_MODES.PLAIN_TEXT:
                # Check if we're in optimized mode
                if self.use_memory_optimization and self.average_psd_data is not None:
                    # Optimized mode: Save average PSD data and frequencies
                    data_to_save = np.column_stack((self.frequencies, self.average_psd_data))
                    np.savetxt(
                        self.file_path,
                        data_to_save,
                        delimiter="\t",
                        header=header_text + "\nColumns: Frequency [Hz], Average PSD (optimized mode - contains average of all {} measurements)".format(self.total_averages),
                    )
                else:
                    # Traditional mode: Save all voltage data
                    np.savetxt(
                        self.file_path,
                        self.voltage_data.T,
                        delimiter="\t",
                        header=header_text,
                    )

            case SAVING_MODES.NP_BINARY:
                self.file_path = self.file_path.with_suffix(".npy")
                if self.use_memory_optimization and self.average_psd_data is not None:
                    # Optimized mode: Save both frequencies and average PSD data
                    data_to_save = {'frequencies': self.frequencies, 'average_psd': self.average_psd_data}
                    np.save(self.file_path, data_to_save)
                    header_text += "\nSaved frequencies and average PSD data (optimized mode - contains average of all {} measurements)\n".format(self.total_averages)
                else:
                    # Traditional mode: Save all voltage data
                    np.save(self.file_path, self.voltage_data)
                meta_file = str(self.file_path) + ".metadata"
                with open(meta_file, "w") as f:
                    f.write(header_text)

            case SAVING_MODES.NP_COMPRESSED:
                self.file_path = self.file_path.with_suffix(".npz")
                if self.use_memory_optimization and self.average_psd_data is not None:
                    # Optimized mode: Save average PSD data with metadata
                    np.savez_compressed(
                        self.file_path, 
                        frequencies=self.frequencies,
                        average_psd_data=self.average_psd_data,
                        total_averages=self.total_averages,
                        optimized_mode=True
                    )
                    header_text += "\nSaved frequencies and average PSD data (optimized mode - contains average of all {} measurements)\n".format(self.total_averages)
                else:
                    # Traditional mode: Save all voltage data
                    np.savez_compressed(self.file_path, voltage_data=self.voltage_data, optimized_mode=False)
                meta_file = str(self.file_path) + ".metadata"
                with open(meta_file, "w") as f:
                    f.write(header_text)

            case SAVING_MODES.HDF5:
                self.file_path = self.file_path.with_suffix(".h5")
                log.debug(
                    "Saving to {}, save_time_line={}, save_psds={}".format(
                        self.file_path, save_time_line, save_psds
                    )
                )
                with h5py.File(self.file_path, "w") as f:
                    if save_time_line:
                        f.create_dataset("time_seq", data=self.time_seq)
                        f["time_seq"].attrs["unit"] = str(ureg.second)
                    f.create_dataset("voltage_data", data=self.voltage_data)
                    f["voltage_data"].attrs["unit"] = str(self._config["unit"])
                    
                    # Save average PSD data if available (optimized mode)
                    if hasattr(self, 'average_psd_data') and self.average_psd_data is not None:
                        f.create_dataset("average_psd_data", data=self.average_psd_data)
                        f["average_psd_data"].attrs["unit"] = str(self._config["unit"]) + "^2/Hz"
                        f["average_psd_data"].attrs["description"] = "Average PSD of all measurements (optimized mode)"

                    if save_psds:
                        f.create_dataset("frequencies", data=self.frequencies)
                        f["frequencies"].attrs["unit"] = str(ureg.hertz)  # typecorrection !! frequencies not frequency
                        f.create_dataset("psds", data=self.psds)
                        f["psds"].attrs["unit"] = str(self._config["unit"]) + "^2/Hz"
                        f.create_dataset("psd", data=self.psd)
                        f["psd"].attrs["unit"] = str(self._config["unit"]) + "^2/Hz"

                    # Add header information as attributes
                    for key, value in self._config.items():
                        f.attrs[key] = str(value)

        # self.main_window.statusBar().showMessage(f"Data saved to {self.file_path}")
        log.info("Data saved to {} with {}".format(self.file_path, mode))
        return self.file_path

    def save_file_dialog(
        self,
        file_name="output.txt",
        extensions="Data-File (*.txt *.dat *.npy *.npz *.h5);;All Files (*)",
    ):
        """Opens a file dialog to save the file.
        """
        filename, _ = QFileDialog.getSaveFileName(
            self.main_window.main_ui, "Save", file_name, extensions
        )
        if filename:
            return filename

    def cut_data(self, index):
        """cuts data self.voltage_data[:index] and self.psds[:index].
           This is useful if the measurement was interrupted and the
           data is not complete.

        Args:
            index (int): Last valid measurement index
        """
        if self.use_memory_optimization:
            # With circular buffer, we can't cut data in the traditional sense.
            # Instead, we update the total_averages count.
            if hasattr(self, 'total_averages') and index < self.total_averages:
                self.total_averages = index
                # Remove indices beyond the cut point
                self.done_indices = {i for i in self.done_indices if i < index}
                log.debug("Cut data at index {} (optimized). New total averages: {}".format(index, self.total_averages))
        else:
            # Traditional mode: actually cut the arrays
            if self.voltage_data.shape[0] > index + 1:
                self.voltage_data = self.voltage_data[:index]
                self.psds = self.psds[:index]
                log.debug("Cut data at index {} (traditional)".format(index))
