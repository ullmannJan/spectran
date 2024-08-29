"""This module contains the main window of the application. 
This means that it contains the main layout and the menu bar.
Everything displayed in the GUI is managed by .main_ui.py and .plots.py."""

from PySide6.QtWidgets import (QApplication, QMainWindow, 
QHBoxLayout, QWidget, QSplitter, QStyle, QMessageBox)
from PySide6.QtCore import Qt, QThreadPool, QMetaObject, Q_ARG, Slot
from PySide6.QtGui import QIcon, QAction, QPalette
import sys

from .plots import Plots
from .main_ui import MainUI
from .data_handler import DataHandler
from .settings import Settings
from .windows import AboutWindow, SettingsWindow, SaveWindow
from . import spectran_path, log

class MainWindow(QMainWindow):

    measurement_stopped = True # The status of the measurement

    def __init__(self):
        super(MainWindow, self).__init__()

        # created gui
        self.plots = Plots(self)
        self.main_ui = MainUI(self)
        self.data_handler = DataHandler(self)
        self.api_server = None

        # qt stuff
        self.threadpool = QThreadPool.globalInstance()
        log.info("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        self.settings = Settings(self, "spectran", "Spectran")
        self.settings.load_settings()
        # set style
        QApplication.setStyle(self.settings.value("graphics/style"))

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Spectran")
        self.setMinimumSize(800, 600)
        self.setWindowIcon(QIcon(str(spectran_path / "data/osci_128.ico")))
        
        self.statusBar().showMessage("Ready for measurement")

        self.add_menu_bar()

        # layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.main_ui)
        self.splitter.addWidget(self.plots)

        main_layout.addWidget(self.splitter)
        
    def add_menu_bar(self):
    
        # Save
        saveAction = QAction(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton),
            "Save File",
            self,
        )
        saveAction.setShortcut("Ctrl+S")
        saveAction.setStatusTip("Save Data")
        saveAction.triggered.connect(self.open_save_page)

        # Settings
        settingsAction = QAction(
            QIcon(str(spectran_path / "data/gear_icon.png")), "Settings", self
        )
        settingsAction.setShortcut("Ctrl+I")
        settingsAction.setStatusTip("Open settings page")
        settingsAction.triggered.connect(self.open_settings_page)

        resetSettingsAction = QAction(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogResetButton),
            "Reset Settings",
            self,
        )
        resetSettingsAction.setStatusTip("Clear Settings")
        resetSettingsAction.triggered.connect(self.settings.clear)

        # About
        aboutAction = QAction(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation),
            "About",
            self,
        )
        aboutAction.setStatusTip("Show information about Measury")
        aboutAction.triggered.connect(self.open_about_page)
        
        # menu bar
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu("&File")
        fileMenu.addAction(saveAction)
        editMenu = menuBar.addMenu("&Edit")
        editMenu.addAction(settingsAction)
        editMenu.addAction(resetSettingsAction)
        aboutMenu = menuBar.addMenu("&About")
        aboutMenu.addAction(aboutAction)

    def update_style(self):
        log.info("Updating style to {} dark_mode = {}".format(
                self.settings.value("graphics/style"), self.is_dark_mode()))
        QApplication.setStyle(self.settings.value("graphics/style"))

    
    def closeEvent(self, event):
        # close all threads
        self.threadpool.clear() # this simply raises an error when closing unexpectedly
        
        QApplication.closeAllWindows()

    def raise_error(self, error):
        if isinstance(error, tuple):
            # when it is raised from a worker thread
            error = error[1]
            
        log.error(str(error).replace("\n", " "))
        if "pytest" in sys.modules:
            raise Exception(error)
        else:
            QMetaObject.invokeMethod(self, "show_critical_message", 
                                     Qt.ConnectionType.QueuedConnection, Q_ARG(str, str(error)))
    @Slot(str)
    def show_critical_message(self, error_message):
        QMessageBox.critical(self, "Error", error_message)

    def raise_info(self, error):
        log.info(str(error).replace("\n", " "))
        QMessageBox.information(self, "Info", str(error))

    def open_about_page(self):
        self.about_window = AboutWindow(parent=self)
        self.about_window.show()
        self.about_window.activateWindow()

    def open_settings_page(self):
        self.get_bg_color()
        self.about_window = SettingsWindow(parent=self)
        self.about_window.show()
        self.about_window.activateWindow()

    def open_save_page(self):
        self.save_window = SaveWindow(parent=self)
        self.save_window.show()
        self.save_window.activateWindow()

    def get_bg_color(self):
        QApplication.processEvents()
        color = self.palette().color(QPalette.ColorRole.Window)
        return color
    
    def is_dark_mode(self):
        app = (
            QApplication.instance()
        )  # Ensures it works with the current QApplication instance
        if not app:  # If the application does not exist, create a new instance
            app = QApplication([])
        return app.palette().color(QPalette.ColorRole.Window).lightness() < 128
    
