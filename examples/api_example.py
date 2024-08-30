from spectran.api import API_Connection
from spectran import ureg
import logging
logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s  %(levelname)-10s %(name)s: %(message)s",
        )

if __name__ == "__main__":
    # connect to the API Server
    # the api_key has to be specified 
    # if it is not the DEFAULT_API_KEY
    api = API_Connection(api_key="3824392043")
    
    # create a configuration dictionary
    CONFIG = {
        "input_channel": "ai0",
        "sample_rate": 50_000 * ureg.Hz,
        "duration": 0.05 * ureg.second,
        "averages": 4,
        "signal_range_min": -3 * ureg.volt, 
        "signal_range_max":  3 * ureg.volt,
        "unit": "Volt",
        "plot_signal": False,
    }
    
    # connect to a device, it is the same as selecting 
    # the device in the GUI and clicking connect
    api.connect_device("DummyDAQ", 'Dev1')
    # this sets all parameters in the GUI
    api.set_config(CONFIG)    
    
    # make 7 measurements
    for i in range(1, 8):
        # each with a different sample rate
        api.set_config(dict(sample_rate=500_000*i * ureg.Hz))
        # start the measurement
        api.start_measurement()
        # this waits for the measurement to finish
        api.wait_for_measurement()
        # save the measured data to a file
        api.save_file(f"data_{i}.txt")
    
    