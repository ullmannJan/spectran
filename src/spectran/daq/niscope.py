from .daq import DAQ
import niscope
import numpy as np
from PySide6.QtCore import Signal
import time
from ..main_window import log, ureg

class NISCOPE(DAQ):
    
    def list_devices(self) -> list[str]:
        return []
        return niscope.Session.list_resources()
    
    def get_sequence(self, data_holder:np.ndarray, 
                     average_index: int,
                     config:dict,
                     plotting_signal:Signal) -> np.ndarray:
        
        # configuration
        duration = config["duration"].to(ureg.second).magnitude
        sample_rate = config["sample_rate"].to(ureg.Hz).magnitude
        averages = config["averages"]
        device = config["device"]
        log.info(f"Getting sequence from {device} for {duration} s at {sample_rate} kHz")
        
        # niscope configuration
        channels = [config["input_channel"]]
        
        with niscope.Session(resource_name=device) as session:
            session.configure_vertical(range=10, coupling=niscope.VerticalCoupling.AC)
            session.configure_horizontal_timing(min_sample_rate=50000000, min_num_pts=length, ref_position=50.0, num_records=num_records, enforce_realtime=True)
            with session.initiate():
                waveforms = session.channels[channels].fetch_into(waveform=wfm, num_records=num_records)
            for i in range(len(waveforms)):
                print(f'Waveform {i} information:')
                print(f'{waveforms[i]}\n\n')
                print(f'Samples: {waveforms[i].samples.tolist()}')
                
                data_holder[i] = waveforms[i].samples
        plotting_signal.emit(data_holder)