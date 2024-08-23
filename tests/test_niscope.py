from spectran.daq import NISCOPE
from spectran import ureg
from spectran.settings import DEFAULT_VALUES
import numpy as np
import logging
import niscope

logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s  %(levelname)-10s %(name)s: %(message)s",
)

def test_list_devices():
    driver = NISCOPE()
    return driver.list_devices()

def test_connection():

    driver = NISCOPE()
    devices = driver.list_devices()

    config = DEFAULT_VALUES.copy()
    config['device'] = devices[0]
    duration = config["duration"].to(ureg.second).magnitude
    sample_rate = config["sample_rate"].to(ureg.Hz).magnitude
        
        # niscope configuration

    data_holder = np.empty((1, duration*sample_rate))

    driver.get_sequence(data_holder,
                        0,
                        config,
                        )
    
if __name__ == '__main__':

    test_connection()