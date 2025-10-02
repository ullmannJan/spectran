"""Module for the Plots class, which is a subclass of pg.GraphicsLayoutWidget and contains the plots for the signal and the power spectral density (PSD).
It also contains all functions associated with plotting."""

import pyqtgraph as pg
from . import log


class Plots(pg.GraphicsLayoutWidget):
    """PyQt widget that contains the plots for the signal and the power spectral density (PSD)."""

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
        self.plot2.setLabel("left", "PSD (V^2/Hz)")
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

    def update_plots(self, index=None, force_draw=False, plot_signal=True, plot_spectrum=True):
        
        log.debug("Updating plots to index {}".format(index))
        
        # check if we should stop plotting (this is done to close threads that are still running)
        if self.main_window.main_ui.stop_plotting and index is not None:
            log.debug("Stop plotting at index {}".format(index))
            return
        
        # Check if there is data to plot based on optimization mode
        data_handler = self.main_window.data_handler
        if data_handler.use_memory_optimization:
            # Optimized mode: check for average voltage data and voltage data
            if data_handler.average_voltage_data is None and data_handler.voltage_data is None:
                log.debug("Nothing to plot (optimized mode)")
                return
        else:
            # Traditional mode: check for voltage data
            if data_handler.voltage_data is None:
                log.debug("Nothing to plot (traditional mode)")
                return
        
        if index is None:
            index = -1
        
        if plot_signal:
            # Choose the right signal data based on optimization mode
            data_handler = self.main_window.data_handler
            if data_handler.use_memory_optimization:
                # Optimized mode: use average voltage data
                if data_handler.average_voltage_data is not None:
                    signal_data = data_handler.average_voltage_data
                else:
                    log.debug("No average voltage data available for plotting")
                    return
            else:
                # Traditional mode: use voltage data at index
                signal_data = data_handler.voltage_data[index,:]
            
            self.update_signal_plot(
                data_handler.time_seq, 
                signal_data,
                force_draw=force_draw
            )
        if plot_spectrum:
            if (data_handler.psd is not None
                and data_handler.frequencies is not None):
                self.update_spectrum_plot(
                    # we don't plot the first frequency (0 Hz)
                    data_handler.frequencies[1:],
                    data_handler.psd[1:],
                    force_draw=force_draw
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
