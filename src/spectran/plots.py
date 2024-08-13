import pyqtgraph as pg    

class Plots(pg.GraphicsLayoutWidget):

    def __init__(self, main_window, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.main_window = main_window

        self.plot1 = self.addPlot()
        self.nextRow()
        self.plot2 = self.addPlot()
        self.plot1.setLabel('left', 'Amplitude', units='V')
        self.plot1.setLabel('bottom', 'Time', units='s')
        self.plot2.setLabel('left', 'Power', units='V^2/Hz')
        self.plot2.setLabel('bottom', 'Frequency', units='Hz')
        self.plot2.setLogMode(x=False, y=True)

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