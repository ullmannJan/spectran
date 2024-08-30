import niscope
from niscope import TerminalConfiguration
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
            filter.has_driver = 1
            filter.is_chassis = False
            for resource in session.find_hardware(filter):
                output.append(resource.expert_user_alias[0])

        return output
    
    def list_ports(self) -> list[str]:
        with niscope.Session(self.connected_device) as session:
            return session.get_channel_names(f"0-{session.channel_count-1}")#[c.logical_name for c in session.channels]

    
    def get_properties(self):
        with niscope.Session(self.connected_device) as session:
            max_sample_rate = session.max_real_time_sampling_rate

        return {"Sample rate": ("max", max_sample_rate)}
    
    def list_term_configs(self):
        return TerminalConfiguration, TerminalConfiguration.SINGLE_ENDED
    
    def get_sequence(self, data_holder:np.ndarray, 
                     average_index: int,
                     config:dict,
                     main_window,
                     plotting_signal:Signal = None) -> np.ndarray:
        
        # configuration
        duration = config["duration"].to(ureg.second).magnitude
        sample_rate = config["sample_rate"].to(ureg.Hz).magnitude
        averages = config["averages"]
        device = config["device"]
        
        # niscope configuration
        channel = config["input_channel"]

        with niscope.Session(resource_name=device) as session:
            v_range = config["signal_range_max"].to(ureg.volt).magnitude - config["signal_range_min"].to(ureg.volt).magnitude
            v_offset = (config["signal_range_max"].to(ureg.volt).magnitude + config["signal_range_min"].to(ureg.volt).magnitude) / 2
            log.debug("Range: {} V with offset {} V".format(v_range, v_offset))
            
            session.channels[channel].channel_terminal_configuration = config["terminal_config"]
            session.channels[channel].configure_vertical(range=v_range,
                                                         offset=v_offset,
                                                         coupling=niscope.VerticalCoupling.DC)
            session.configure_horizontal_timing(min_sample_rate=sample_rate, 
                                                min_num_pts=int(sample_rate*duration), 
                                                num_records=1, 
                                                # TODO: find out what these do
                                                ref_position=50.0, 
                                                enforce_realtime=True)

            # set gui information
            config["sample_rate_real"] = session.horz_sample_rate * ureg.Hz
            log.debug("Sample Rate: {}".format(config["sample_rate_real"]))
            main_window.main_ui.sample_rate_status.setText(f"{session.horz_sample_rate:6g}")

            vertical_range = session.channels[channel].vertical_range
            vertical_offset = session.channels[channel].vertical_offset
            log.debug("Range of device: {} V with offset {} V".format(vertical_range, 
                                                        vertical_offset))
            config["signal_range_min_real"] = (vertical_offset - vertical_range / 2) * ureg.volt
            config["signal_range_max_real"] = (vertical_offset + vertical_range / 2) * ureg.volt
            main_window.main_ui.range_min_status.setText(f"{config['signal_range_min_real'].to(ureg.volt).magnitude:.6g}")
            main_window.main_ui.range_max_status.setText(f"{config['signal_range_max_real'].to(ureg.volt).magnitude:.6g}")
           
           # start measurement
            with session.initiate():
                log.debug(f'Starting acquisition')                
                waveforms = session.channels[channel].fetch_into(waveform=data_holder, 
                                                                 num_records=1,
                                                                 timeout=duration*2
                                                                )
            for i in range(len(waveforms)):
                log.debug(f'Waveform {i} information:')
                log.debug(f'{waveforms[i]}')
            

            log.info(f"{average_index+1}/{averages} done.")
    
        if plotting_signal is not None:
            plotting_signal.emit(average_index, data_holder)