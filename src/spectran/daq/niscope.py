import niscope
import numpy as np
from PySide6.QtCore import Signal
import nisyscfg

from .daq import DAQ
from .. import log, ureg

class NISCOPE(DAQ):
    
    def list_devices(self) -> list[str]:
        output = []
        with nisyscfg.Session() as session:
            # Print user aliases for all National Instruments devices in the local system
            filter = session.create_filter()
            filter.is_present = True
            filter.is_ni_product = True
            filter.is_device = True
            for resource in session.find_hardware(filter):
                output.append(resource.expert_user_alias[0])

        return output
    
    def get_sequence(self, data_holder:np.ndarray, 
                     average_index: int,
                     config:dict,
                     plotting_signal:Signal = None) -> np.ndarray:
        
        log.debug("Test")
        # configuration
        duration = config["duration"].to(ureg.second).magnitude
        sample_rate = config["sample_rate"].to(ureg.Hz).magnitude
        averages = config["averages"]
        device = config["device"]
        
        # niscope configuration
        channel = config["input_channel"]
        num_records = 5

        with niscope.Session(resource_name=device) as session:
            session.channels[channel].configure_vertical(range=10, 
                                                         coupling=niscope.VerticalCoupling.AC)
            session.configure_horizontal_timing(min_sample_rate=sample_rate, 
                                                min_num_pts=int(sample_rate*duration), 
                                                # TODO: find out what these do
                                                ref_position=50.0, 
                                                num_records=num_records, 
                                                enforce_realtime=True)

            with session.initiate():
                log.debug(f'Starting acquisition')                
                waveforms = session.channels[channel].fetch_into(waveform=data_holder[average_index], 
                                                                 num_records=num_records,
                                                                 timeout=duration)
            for i in range(len(waveforms)):
                log.debug(f'Waveform {i} information:')
                log.debug(f'{waveforms[i]}\n\n')
                log.debug(f'Samples: {waveforms[i].samples.tolist()}')

            log.info(f"{average_index+1}/{averages} done.")
    
        if plotting_signal is not None:
            plotting_signal.emit(data_holder)
