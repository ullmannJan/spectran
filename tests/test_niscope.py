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
    
def test_sample_code():
    """from https://pypi.org/project/niscope/"""

    device = test_list_devices()[0]

    with niscope.Session(device) as session:
        session.channels[0].configure_vertical(range=1.0, coupling=niscope.VerticalCoupling.AC)
        session.channels[1].configure_vertical(range=10.0, coupling=niscope.VerticalCoupling.DC)
        session.configure_horizontal_timing(min_sample_rate=50000000, min_num_pts=1000, ref_position=50.0, num_records=5, enforce_realtime=True)
        with session.initiate():
            waveforms = session.channels[0,1].fetch(num_records=5)
        for wfm in waveforms:
            print('Channel {}, record {} samples acquired: {:,}\n'.format(wfm.channel, wfm.record, len(wfm.samples)))

        # Find all channel 1 records (Note channel name is always a string even if integers used in channel[])
        chan1 = [wfm for wfm in waveforms if wfm.channel == '0']

        # Find all record number 3
        rec3 = [wfm for wfm in waveforms if wfm.record == 3]

        print(chan1, rec3)
    
if __name__ == '__main__':

    test_connection()
    # test_sample_code()