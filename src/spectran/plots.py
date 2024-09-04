import pyqtgraph as pg
import numpy as np
from . import log, ureg


class Plots(pg.GraphicsLayoutWidget):

    def __init__(self, main_window, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.main_window = main_window

        self.addItem(pg.LabelItem("Signal", justify="center", size="large"), col=0)
        self.coords_plot1 = pg.LabelItem(text="x = 0, y = 0", justify="right", color="w")
        self.addItem(self.coords_plot1, col=0)
        self.nextRow()
        self.plot1 = self.addPlot()
        self.nextRow()
        self.addItem(pg.LabelItem("PSD", justify="center", size="large"), col=0)
        self.coords_plot2 = pg.LabelItem(text="x = 0, y = 0", justify="right", color="w")
        self.addItem(self.coords_plot2, col=0)
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


        self.proxy = pg.SignalProxy(self.plot2.scene().sigMouseMoved, rateLimit=60, slot=self.on_mouse_move)

    def on_mouse_move(self, event):
        pos = event[0]
        if self.plot1.sceneBoundingRect().contains(pos):
            mousePoint = self.plot1.vb.mapSceneToView(pos)
            x = 10 ** mousePoint.x() if self.plot1.ctrl.logXCheck.isChecked() else mousePoint.x()
            y = 10 ** mousePoint.y() if self.plot1.ctrl.logYCheck.isChecked() else mousePoint.y()
            self.coords_plot1.setText(f"x = {x:.3g}, y = {y:.3g}")
        if self.plot2.sceneBoundingRect().contains(pos):
            mousePoint = self.plot2.vb.mapSceneToView(pos)
            x = 10 ** mousePoint.x() if self.plot2.ctrl.logXCheck.isChecked() else mousePoint.x()
            y = 10 ** mousePoint.y() if self.plot2.ctrl.logYCheck.isChecked() else mousePoint.y()
            self.coords_plot2.setText(f"x = {x:.3e}, y = {y:.3e}")

    def update_plots(self, index=None):
        
        log.debug("Updating plots to index {}".format(index))
        
        if self.main_window.main_ui.stop_plotting and index is not None:
            log.debug("Stop plotting at index {}".format(index))
            return
                
        if index is None:
            index = -1
        
        self.update_signal_plot(
            self.main_window.data_handler.time_seq, 
            self.main_window.data_handler.voltage_data[index,:]
        )
        
        if (self.main_window.data_handler.psd is not None
            and self.main_window.data_handler.frequencies is not None):
            self.update_spectrum_plot(
                # we don't plot the first frequency (0 Hz)
                self.main_window.data_handler.frequencies[1:],
                self.main_window.data_handler.psd[1:],
            )

    def update_signal_plot(self, x, y, force_draw=False):
        # clear the plot
        self.plot1.clear()
        
        if force_draw or self.main_window.main_ui.plot_signal_cb.isChecked():        
            # plot the new data
            self.plot1.plot(x, y,
                            pen=pg.mkPen(width=.5, color="w"))

    def update_spectrum_plot(self, x, y, force_draw=False):
        # clear the plot
        self.plot2.clear()
        # plot the new data
        if force_draw or self.main_window.main_ui.plot_spectrum_cb.isChecked():
            self.plot2.plot(x, y,
                            pen=pg.mkPen(width=.5, color="w"))
                
    def clear_plots(self):
        self.plot1.clear()
        self.plot2.clear()
