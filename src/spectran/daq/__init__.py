from .daq import DAQ
from .niscope import NISCOPE
from .nidaqmx import NIDAQMX
from .daq import DummyDAQ

DAQs = [NISCOPE, NIDAQMX, DummyDAQ]