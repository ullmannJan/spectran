import pyqtgraph as pg
import numpy as np
from . import log, ureg


class Plots(pg.GraphicsLayoutWidget):

    def __init__(self, main_window, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.main_window = main_window

        self.plot1 = self.addPlot()
        self.nextRow()
        self.plot2 = self.addPlot()

        # Add gridlines to the plots
        self.plot1.showGrid(x=True, y=True, alpha=0.3)
        self.plot2.showGrid(x=True, y=True, alpha=0.3)

        # Labels
        self.plot1.setLabel("left", "Amplitude", units="V")
        self.plot1.setLabel("bottom", "Time", units="s")
        self.plot2.setLabel("left", "PSD (V/√Hz)")
        self.plot2.setLabel("bottom", "Frequency", units="Hz")
        self.plot2.setLogMode(x=True, y=True)
        self.plot2.getAxis("left").enableAutoSIPrefix(enable=False)
        self.plot2.getAxis("bottom").enableAutoSIPrefix(enable=False)

    def update_plots(self):
        
        log.debug("Updating plots")

        if self.main_window.data_handler.data_has_changed:
            self.main_window.data_handler.data_has_changed = False

            data = self.main_window.data_handler.voltage_data

            self.update_signal_plot(
                self.main_window.data_handler.time_seq, 
                np.mean(data, axis=0)
            )
            self.update_spectrum_plot(
                # we don't plot the first frequency (0 Hz)
                self.main_window.data_handler.frequencies[1:],
                np.sqrt(self.main_window.data_handler.psd[1:]),
            )

    def update_signal_plot(self, x, y):
        # clear the plot
        self.plot1.clear()
        # plot the new data
        self.plot1.plot(x, y,
                        pen=pg.mkPen(width=.5))

    def update_spectrum_plot(self, x, y):
        # clear the plot
        self.plot2.clear()
        # plot the new data
        self.plot2.plot(x, y,
                        pen=pg.mkPen(width=.5, color="w"))
                
    def clear_plots(self):
        self.plot1.clear()
        self.plot2.clear()
