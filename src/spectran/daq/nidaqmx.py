from nidaqmx import Task
from nidaqmx.system import System, physical_channel
from nidaqmx.stream_readers import AnalogSingleChannelReader
from nidaqmx.constants import READ_ALL_AVAILABLE
import numpy as np

from .. import log, ureg
from .daq import DAQ

class NIDAQMX(DAQ):

    def list_devices(self) -> list[str]:
        try:
            local_system = System.local()
            driver_version = local_system.driver_version
            
        except Exception as e:
            log.info("No NIDAQmx driver installed")
            return []

        log.debug("DAQmx {}.{}.{}".format(driver_version.major_version, 
                                            driver_version.minor_version, 
                                            driver_version.update_version)
        )

        return [d.name for d in local_system.devices]
    
    def list_ports(self) -> list[str]:
        
        system = System.local()
        device = system.devices[self.connected_device]
        # remove the device name and the slash
        return [terminal.name.replace(self.connected_device, "")[1:] for terminal in device.ai_physical_chans]

    def get_properties(self):
        local_system = System.local()
        device = local_system.devices[self.connected_device]
        min_rate = device.ai_min_rate
        max_rate = device.ai_max_single_chan_rate
        
        return {"Sample rate": ("min", min_rate, "max", max_rate),
                }

    def get_sequence(self, data_holder: np.ndarray, 
                     average_index: int, 
                     config: dict, 
                     main_window,
                     plotting_signal) -> np.ndarray:
        
        duration = config["duration"].to(ureg.second).magnitude
        sample_rate = config["sample_rate"].to(ureg.Hz).magnitude
        averages = config["averages"]
        
        with Task() as read_task:
            # add inputs
            log.debug(f'Starting acquisition')

            aichan = read_task.ai_channels.add_ai_voltage_chan(f'{config["device"]}/{config["input_channel"]}')
            aichan.ai_min = config["signal_range_min"].to(ureg.volt).magnitude
            aichan.ai_max = config["signal_range_max"].to(ureg.volt).magnitude
        
            read_task.timing.cfg_samp_clk_timing(
                rate=sample_rate, 
                source="OnboardClock", 
                samps_per_chan=int(sample_rate*duration),
            )

            # Log the actual settings
            log.info("AI Min: {} V".format(aichan.ai_min))
            log.info("AI Max: {} V".format(aichan.ai_max))
            log.info("Sample Rate: {} Hz".format(read_task.timing.samp_clk_rate))

             # set gui information
            config["sample_rate_real"] = read_task.timing.samp_clk_rate
            main_window.main_ui.sample_rate_status.setText(f"{config['sample_rate_real']:6g}")

            config["signal_range_min_real"] = aichan.ai_min
            config["signal_range_max_real"] = aichan.ai_max
            main_window.main_ui.range_min_status.setText(f"{config['signal_range_min_real']:.6g}")
            main_window.main_ui.range_max_status.setText(f"{config['signal_range_max_real']:.6g}")

            reader = AnalogSingleChannelReader(task_in_stream=read_task.in_stream)

            reader.read_many_sample(data=data_holder[average_index],
                                    number_of_samples_per_channel=READ_ALL_AVAILABLE)
            
            log.info(f"{average_index+1}/{averages} done.")

        plotting_signal.emit(average_index, data_holder)

            


        