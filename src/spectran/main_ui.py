from PySide6.QtWidgets import (
    QPushButton, QVBoxLayout, QWidget, 
    QGroupBox, QLabel, QGridLayout, 
    QLineEdit, QComboBox
    )

from PySide6.QtGui import QIntValidator, QRegularExpressionValidator

from scipy.signal import periodogram, welch
import numpy as np

from .settings import DEFAULT_VALUES
from .main_window import log
from .daq import DAQs, DAQ

class MainUI(QWidget):
    
    driver_instance: DAQ = None

    def __init__(self, main_window, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.main_window = main_window

        self.setMinimumWidth(200)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.add_driver_box()
        
        self.add_settings_box()

        self.layout.addStretch()

        self.button = QPushButton("Start Measurement")
        self.button.clicked.connect(self.start_measurement)
        self.layout.addWidget(self.button)
        
    def add_driver_box(self):
        
        # Driver Settings
        self.driver_gbox = QGroupBox("Driver Settings")
        self.layout.addWidget(self.driver_gbox)

        driver_layout = QGridLayout()
        self.driver_gbox.setLayout(driver_layout)

        # Driver
        driver_layout.addWidget(QLabel("Driver: "), 0, 0)
        self.driver_dd = QComboBox()
        driver_layout.addWidget(self.driver_dd, 0, 1)

        # Device
        driver_layout.addWidget(QLabel("Device: "), 1, 0)
        self.device_dd = QComboBox()
        driver_layout.addWidget(self.device_dd, 1, 1)

        # Connect Button
        self.connect_button = QPushButton("Connect")
        driver_layout.addWidget(self.connect_button, 2, 0, 1, 2)
        self.connect_button.clicked.connect(self.connect_device)
        
        # Connect Signals
        self.driver_dd.currentTextChanged.connect(self.list_devices)
        self.driver_dd.addItems([daq.__name__ for daq in DAQs])

    def add_settings_box(self):

       # Channel Settings
        channels_gbox = QGroupBox("Channel Settings")
        self.layout.addWidget(channels_gbox)

        self.settings_layout = QGridLayout()
        channels_gbox.setLayout(self.settings_layout)
        
        # Input Channel
        self.settings_layout.addWidget(QLabel("Input Channel: "), 0, 0)
        self.input_channel_edit = QLineEdit(placeholderText=str(DEFAULT_VALUES["input_channel"]))
        self.input_channel_edit.setValidator(QIntValidator(0, 99, self))
        self.settings_layout.addWidget(self.input_channel_edit, 0, 1)

        # Output Channel
        self.settings_layout.addWidget(QLabel("Output Channel: "), 1, 0)
        self.output_channel_edit = QLineEdit(placeholderText=str(DEFAULT_VALUES["output_channel"]))
        self.output_channel_edit.setValidator(QIntValidator(0, 99, self))
        self.settings_layout.addWidget(self.output_channel_edit, 1, 1)

        # Sample Frequency
        self.settings_layout.addWidget(QLabel("Sample Frequency: "), 2, 0)
        self.sample_frequency_edit = QLineEdit(placeholderText=str(DEFAULT_VALUES["sample_frequency_Hz"]*1e-3))
        self.sample_frequency_edit.setValidator(QRegularExpressionValidator(r"^[+-]?(\d+(\.\d*)?|\.\d+)$", self))
        self.settings_layout.addWidget(self.sample_frequency_edit, 2, 1)
        self.settings_layout.addWidget(QLabel("kHz"), 2, 2)

        # Duration
        self.settings_layout.addWidget(QLabel("Duration: "), 3, 0)
        self.duration_edit = QLineEdit(placeholderText=str(DEFAULT_VALUES["duration_s"]))
        self.duration_edit.setValidator(QRegularExpressionValidator(r"^[+-]?(\d+(\.\d*)?|\.\d+)$", self))
        self.settings_layout.addWidget(self.duration_edit, 3, 1)
        self.settings_layout.addWidget(QLabel("s"), 3, 2)

        # Averages
        self.settings_layout.addWidget(QLabel("Averages: "), 4, 0)
        self.averages_edit = QLineEdit(placeholderText=str(DEFAULT_VALUES["averages"]))
        self.sample_frequency_edit.setValidator(QRegularExpressionValidator(r"\d", self))
        self.settings_layout.addWidget(self.averages_edit, 4, 1)

    def start_measurement(self):

        log.info("Starting Measurement")

        config = self.get_config()

        t = np.linspace(0, config['duration_s'], int(config['duration_s'] * config['sample_frequency_Hz']), endpoint=False)
        signal = self.driver_instance.get_sequence(t)

        freq, psd = welch(signal, config['sample_frequency_Hz'])

        self.main_window.plots.update_signal_plot(t, signal)
        self.main_window.plots.update_spectrum_plot(freq, psd)
        
    def get_config(self):
        
        output = DEFAULT_VALUES.copy()
        if self.input_channel_edit.text():
            output["input_channel"] = int(self.input_channel_edit.text())
        if self.output_channel_edit.text():
            output["output_channel"] = int(self.output_channel_edit.text())
        if self.sample_frequency_edit.text():
            output["sample_frequency"] = float(self.sample_frequency_edit.text())
        if self.duration_edit.text():
            output["duration"] = float(self.duration_edit.text())
        if self.averages_edit.text():
            output["averages"] = int(self.duration_edit.text())

        return output
    
    def list_devices(self):
        log.info("Looking for devices")
        driver_instance = DAQs[self.driver_dd.currentIndex()]()
        self.device_dd.clear()
        self.device_dd.addItems(driver_instance.list_devices())

    def connect_device(self):
        self.driver_instance = DAQs[self.driver_dd.currentIndex()]()
        self.driver_instance.connect_device(self.device_dd.currentText())
        # change Text
        if self.driver_instance.get_connected_device() is None:
            self.driver_gbox.setTitle("Connected")
        else:
            self.driver_gbox.setTitle(f"Connected to {self.driver_instance.__class__.__name__}/{self.driver_instance.get_connected_device()}")
        
        log.info(f"Connected to {self.driver_instance.get_connected_device()}")