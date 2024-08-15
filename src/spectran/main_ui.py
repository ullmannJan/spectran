""""This module contains the main UI class for the Spectran application."""

from PySide6.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QWidget,
    QGroupBox,
    QLabel,
    QGridLayout,
    QLineEdit,
    QComboBox,
)

from PySide6.QtGui import QRegularExpressionValidator

from .settings import DEFAULT_VALUES
from .main_window import log, ureg
from .daq import DAQs, DAQ
from .measurement import Worker, run_measurement


class MainUI(QWidget):

    driver_instance: DAQ = None

    def __init__(self, main_window, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.main_window = main_window

        self.setMinimumWidth(300)
        self.setMaximumWidth(400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.add_driver_box()

        self.add_settings_box()

        self.layout.addStretch()
        
        self.stop_button = QPushButton("Stop Measurement")
        self.stop_button.clicked.connect(self.stop_measurement)
        self.stop_button.setEnabled(False)
        self.layout.addWidget(self.stop_button)

        self.start_button = QPushButton("Start Measurement")
        self.start_button.clicked.connect(self.start_measurement)
        self.layout.addWidget(self.start_button)

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
        row = 0
        self.settings_layout.addWidget(QLabel("Input Channel: "), row, 0)
        self.input_channel_edit = QLineEdit(
            placeholderText=str(DEFAULT_VALUES["input_channel"])
        )
        self.input_channel_edit.setValidator(
            QRegularExpressionValidator(r"^\d+$", self)
        )
        self.settings_layout.addWidget(self.input_channel_edit, row, 1)

        # Sample Rate
        row = 1
        self.settings_layout.addWidget(QLabel("Sample Rate: "), row, 0)
        self.sample_rate_edit = QLineEdit(
            placeholderText=str(DEFAULT_VALUES["sample_rate"].to(ureg.kHz).magnitude)
        )
        self.sample_rate_edit.setValidator(
            QRegularExpressionValidator(r"^[+-]?(\d+(\.\d*)?|\.\d+)$", self)
        )
        self.settings_layout.addWidget(self.sample_rate_edit, row, 1)
        self.settings_layout.addWidget(QLabel("kHz"), row, 2)

        # Duration
        row = 2
        self.settings_layout.addWidget(QLabel("Duration: "), row, 0)
        self.duration_edit = QLineEdit(
            placeholderText=str(DEFAULT_VALUES["duration"].to(ureg.second).magnitude)
        )
        self.duration_edit.setValidator(
            QRegularExpressionValidator(r"^[+-]?(\d+(\.\d*)?|\.\d+)$", self)
        )
        self.settings_layout.addWidget(self.duration_edit, row, 1)
        self.settings_layout.addWidget(QLabel("s"), row, 2)

        # Averages
        row = 3
        self.settings_layout.addWidget(QLabel("Averages: "), row, 0)
        self.averages_edit = QLineEdit(placeholderText=str(DEFAULT_VALUES["averages"]))
        self.averages_edit.setValidator(QRegularExpressionValidator(r"^\d+$", self))
        self.settings_layout.addWidget(self.averages_edit, row, 1)

    def get_config(self):

        output = DEFAULT_VALUES.copy()
        if self.input_channel_edit.text():
            output["input_channel"] = int(self.input_channel_edit.text())
        if self.sample_rate_edit.text():
            output["sample_rate"] = float(self.sample_rate_edit.text()) * ureg.kHz
        if self.duration_edit.text():
            output["duration"] = float(self.duration_edit.text()) * ureg.second
        if self.averages_edit.text():
            output["averages"] = int(self.averages_edit.text())
        if self.driver_instance is not None:
            output["driver"] = self.driver_instance.__class__.__name__
        if self.driver_instance.connected_device is not None:
            output["device"] = self.driver_instance.connected_device

        return output
    
    def stop_measurement(self):
        self.main_window.threadpool.clear()
        self.start_button.setEnabled(True)

    def start_measurement(self):

        if self.driver_instance is None:
            self.main_window.raise_error("No driver selected")
            return
        if self.driver_instance.connected_device is None:
            self.main_window.raise_error("No device connected")
            return
        
        config = self.get_config()
        self.main_window.data_handler.config = config
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        worker = Worker(run_measurement, self.driver_instance, config)
        worker.signals.finished.connect(
            lambda: self.start_button.setEnabled(True)
            )
        worker.signals.finished.connect(
            lambda: self.stop_button.setEnabled(False)
            )
        worker.signals.progress.connect(self.get_data_and_plot)
        worker.signals.finished.connect(
            lambda: log.info("Measurement finished")
            )
        worker.signals.result.connect(self.get_data_and_plot)

        # Execute
        self.main_window.threadpool.start(worker)
        
    def get_data_and_plot(self, data):
        # log.info("Getting data and plotting")
        plot_worker = Worker(self.main_window.data_handler.calculate_data, data)
        plot_worker.signals.finished.connect(self.main_window.plots.update_plots)
        self.main_window.threadpool.start(plot_worker)

    def list_devices(self):
        log.info(f"Looking for devices on {self.driver_dd.currentText()}")
        driver_instance = DAQs[self.driver_dd.currentIndex()]()
        self.device_dd.clear()
        self.device_dd.addItems(driver_instance.list_devices())

    def connect_device(self):
        self.driver_instance = DAQs[self.driver_dd.currentIndex()]()
        if not self.device_dd.currentText():
            raise ValueError("No device selected")
        
        self.driver_instance.connect_device(self.device_dd.currentText())
        # change Text
        if self.driver_instance.connected_device is None:
            self.driver_gbox.setTitle("Driver Settings")
        else:
            self.driver_gbox.setTitle(
                f"Driver connected to {self.driver_instance.__class__.__name__}/{self.driver_instance.connected_device}"
            )

        log.info(f"Connected to {self.driver_instance.connected_device}")