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
        "input_channel": "ai0",
        "sample_rate": 50_000 * ureg.Hz,
        "duration": 0.05 * ureg.second,
        "averages": 4,
        "signal_range_min": -3 * ureg.volt, 
        "signal_range_max":  3 * ureg.volt,
        "unit": "Volt",
    }
    
    api.connect_device("DummyDAQ", 'Dev1')
    api.set_config(CONFIG)    
    for i in range(1, 8):
        api.set_config(dict(sample_rate=500_000*i * ureg.Hz))
        api.start_measurement()
        api.wait_for_measurement()
        # api.save_file(f"a_{i}.txt")
    
    