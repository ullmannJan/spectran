from .main_window import ureg

DEFAULT_VALUES = {
    "input_channel": 0,
    "output_channel": 0,
    "sample_rate": 100000 * ureg.Hz,
    "duration": 2 * ureg.second,
    "averages": 1
}