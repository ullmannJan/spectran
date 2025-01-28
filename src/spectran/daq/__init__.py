"""
Spectran DAQ package initialization.

This module imports the necessary DAQ classes and sets up the DAQs list.
All available DAQs should be imported here. All communication of drivers 
with the DAQs should be done through the DAQ class.
"""

from .daq import DAQ
from .niscope import NISCOPE
from .nidaqmx import NIDAQMX
from .daq import DummyDAQ

# List of available DAQs which can be used
DAQs = [NISCOPE, NIDAQMX, DummyDAQ]
