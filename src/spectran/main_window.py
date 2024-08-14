from PySide6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QSplitter, QStyle
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction
import sys

from pint import UnitRegistry
ureg = UnitRegistry()
import logging
log = logging.getLogger("spectran")
logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-10s %(name)s: %(message)s",
)

from .plots import Plots
from .main_ui import MainUI


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.plots = Plots(self)
        self.main_ui = MainUI(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Spectrum Analyzer")
        self.setMinimumSize(800, 600)
        self.setWindowIcon(QIcon("icon.png"))

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
    
         # actions for menu bar
        saveAction = QAction(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton),
            "Save File",
            self,
        )
        saveAction.setShortcut("Ctrl+S")
        saveAction.setStatusTip("Save Data")
        saveAction.triggered.connect(self.save_data)
        
        # menu bar
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu("&File")
        editMenu = menuBar.addMenu("&Edit")
        viewMenu = menuBar.addMenu("&Settings")
        aboutMenu = menuBar.addMenu("&About")
        fileMenu.addAction(saveAction)
        
    def save_data(self):
        raise NotImplementedError("Save data not implemented yet")

def run():

    # This starts the application
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()
