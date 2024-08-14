from .main_window import log, ureg
from scipy.signal import welch
from .daq import DAQ
import numpy as np

def start_measurement(driver_instance:DAQ, config:dict, plots):
    """
    Start a measurement with the current configuration
    """
    log.info("Starting Measurement")
    
    duration = config["duration"].to(ureg.second).magnitude
    sample_rate = config["sample_rate"].to(ureg.Hz).magnitude
    
    
    signal = driver_instance.get_sequence(duration, sample_rate, config["averages"])
    
    freq, psd = welch(signal[:,0], sample_rate)

    time_seq = np.linspace(0, duration, int(duration * sample_rate))
    plots.update_signal_plot(time_seq, signal[:, 0])
    plots.update_spectrum_plot(freq, psd)