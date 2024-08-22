"""This module contains a function to run the measurement. 
But also the Worker class to run the measurement in a separate thread."""

from . import log, ureg
from .daq import DAQ
import numpy as np
from PySide6.QtCore import Signal, Slot, QObject
from datetime import datetime

def run_measurement(driver_instance:DAQ, config:dict, main_window, progress_callback:Signal):
    """
    Start a measurement with the current configuration
    and writes into voltage_data inplace.
    """
    log.info("Starting Measurement")
    
    duration = config["duration"].to(ureg.second).magnitude
    sample_rate = config["sample_rate"].to(ureg.Hz).magnitude
    config["start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    device = config["device"]
    log.info(f"Getting sequence from {device} for {duration} s at {sample_rate} Hz")
    
    # create space for data
    voltage_data = np.empty((config["averages"], int(duration * sample_rate)))

    for i in range(config["averages"]):
        if main_window.stopped:
            log.info("Measurement stopped")
            # return the data that has been measured
            return voltage_data[:i]
        
        driver_instance.get_sequence(
            voltage_data,
            i,
            config,
            plotting_signal=progress_callback)
        
    # driver_instance.get_sequence(
    #     voltage_data, 
    #     config, 
    #     plotting_signal=progress_callback)
    
    return voltage_data


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int, object)


from PySide6.QtCore import QRunnable, Slot, Signal, QObject

import sys
import traceback

class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @Slot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done