import pyqtgraph as pg
import numpy as np
from PySide6.QtWidgets import QApplication

class Plots(pg.GraphicsLayoutWidget):

    def __init__(self, main_window, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.main_window = main_window

        self.plot1 = self.addPlot()
        self.nextRow()
        self.plot2 = self.addPlot()
        self.plot1.setLabel('left', 'Amplitude', units='V')
        self.plot1.setLabel('bottom', 'Time', units='s')
        self.plot2.setLabel('left', 'PSD', units='V^2/Hz')
        self.plot2.setLabel('bottom', 'Frequency', units='Hz')
        self.plot2.setLogMode(x=False, y=True)

    def update_plots(self):
        print("Updating plots")
        data = self.main_window.data_handler.voltage_data
        time = self.main_window.data_handler.time_seq
        freq, psd = self.main_window.data_handler.calculate_psd()

        self.update_signal_plot(time, np.mean(data, axis=0))
        self.update_spectrum_plot(freq, psd)

    def update_signal_plot(self, x, y):
        # clear the plot
        self.plot1.clear()
        # plot the new data
        self.plot1.plot(x, y)

    def update_spectrum_plot(self, x, y):
        # clear the plot
        self.plot2.clear()
        # plot the new data
        self.plot2.plot(x, y)