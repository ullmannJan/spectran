import nidaqmx as ni
from nidaqmx.stream_readers import AnalogSingleChannelReader
from nidaqmx.constants import AcquisitionType, READ_ALL_AVAILABLE
import numpy as np

from .. import log, ureg
from .daq import DAQ

class NIDAQMX(DAQ):

    def list_devices(self) -> list[str]:
        
        local_system = ni.system.System.local()
        driver_version = local_system.driver_version

        log.debug("DAQmx {}.{}.{}".format(driver_version.major_version, 
                                          driver_version.minor_version, 
                                          driver_version.update_version)
        )

        return [d.name for d in local_system.devices]
    

    def get_sequence(self, data_holder: np.ndarray, 
                     average_index: int, 
                     config: dict, 
                     plotting_signal) -> np.ndarray:
        
        duration = config["duration"].to(ureg.second).magnitude
        sample_rate = config["sample_rate"].to(ureg.Hz).magnitude
        averages = config["averages"]
        
        with ni.Task() as read_task:
            # add inputs
            log.debug(f'Starting acquisition')

            aichan = read_task.ai_channels.add_ai_voltage_chan(f'{config["device"]}/ai{config["input_channel"]}')
            aichan.ai_min = config["signal_range_min"].to(ureg.volt).magnitude
            aichan.ai_max = config["signal_range_max"].to(ureg.volt).magnitude
        
            read_task.timing.cfg_samp_clk_timing(
                rate=sample_rate, 
                source="OnboardClock", 
                samps_per_chan=int(sample_rate*duration),
            )

            reader = AnalogSingleChannelReader(task_in_stream=read_task.in_stream)

            reader.read_many_sample(data=data_holder[average_index],
                                    number_of_samples_per_channel=READ_ALL_AVAILABLE)
            
            log.info(f"{average_index+1}/{averages} done.")

        plotting_signal.emit(average_index, data_holder)

            


        