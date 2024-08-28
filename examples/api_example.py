from spectran.api import API_Connection
from spectran import ureg
import logging
logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s  %(levelname)-10s %(name)s: %(message)s",
        )

if __name__ == "__main__":
    api = API_Connection()
    
    CONFIG = {
        "input_channel": "ai2",
        "sample_rate": 50_000 * ureg.Hz,
        "duration": 1 * ureg.second,
        "averages": 1,
        "signal_range_min": -3 * ureg.volt, 
        "signal_range_max":  3 * ureg.volt,
        "unit": "Volt",
    }
    
    api.set_config(CONFIG)
    api.start_measurement()
    api.wait_for_measurement()
    api.save_file(r"C:\Users\ullmann\Desktop\output\a.txt")
    
    