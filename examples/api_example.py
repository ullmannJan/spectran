from spectran.api import API_Connection
from spectran import ureg
from spectran.data_handler import SAVING_MODES
import logging
import time
logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s  %(levelname)-10s %(name)s: %(message)s",
        )

if __name__ == "__main__":
    # connect to the API Server
    # the api_key has to be specified 
    # if it is not the DEFAULT_API_KEY
    api = API_Connection(host="134.2.51.4")
    
    # create a configuration dictionary
    CONFIG = {
        "input_channel": "ai0",
        "sample_rate": 1_000 * ureg.Hz,
        "duration": 1 * ureg.second,
        "averages": 4,
        "signal_range_min": -3 * ureg.volt, 
        "signal_range_max":  3 * ureg.volt,
        "unit": "Volt",
    }
    
    # enable plotting / this can also be done by setting the 
    # config keys "plot_signal" = True/False
    # and "plot_spectrum" = True/False
    api.enable_plotting(signal_enabled=False, 
                        spectrum_enabled=False)
    
    # connect to a device, it is the same as selecting 
    # the device in the GUI and clicking connect
    api.connect_device("NISCOPE", 'PXIe-5122')
    # this sets all parameters in the GUI
    api.set_config(CONFIG)    
    
    # make 7 measurements
    for i in range(1, 4):
        # each with a different sample rate
        # api.set_config(dict(sample_rate=500_000*i * ureg.Hz))
        # start the measurement
        api.start_measurement()
        # this waits for the measurement to finish
        api.wait_for_measurement()
        # save the measured data to a file
        print(f"Saving data_{i}.txt")
        start = time.time()
        api.save_file(f"D:\JanUllmann[Jan]\data_{i}.txt", mode=SAVING_MODES.HDF5, save_psds=True)
        end = time.time()
        print(f"Saved data_{i}.txt in {end-start} seconds")
    
    