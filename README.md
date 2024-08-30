# Spectran

![Spectran Logo](./src/spectran/data/osci_128.ico)

A simple spectrum analyzer. Read a voltage signal and perform a spectral analysis.

![grafik](https://github.com/user-attachments/assets/1652ff62-cc40-434a-b43d-1699b94ba99a)

## Usage

### Installation and Execution

Install via 

    pip install spectran

Run via

    import spectran
    spectran.run()

or in terminal 

    python -m spectran

### Workflow

1. First, select driver and device and click connect. 
This connects the device.
1. Then, select all other options like sample_rate, input_channel, etc.
1. Finally, start the measurement by clicking on `Start Measurement`.

## API Connection

It is possible to remotely control most of Spectran's features via an API. 
API key can be set with the environment variable `API_KEY`.
Default host is `127.0.0.1` on port `8111`.

A detailed example can be found in [this example](./examples/api_example.py).

First, the connection to the API has to be set up (you might have to input your api key):
```python
api = API_Connection()
```
Afterwards one can set up devices and measurements:

```python
api.connect_device("DummyDAQ", 'Dev1')

CONFIG = {
    "input_channel": "ai0",
    "sample_rate": 50_000 * ureg.Hz,
    "duration": 0.05 * ureg.second,
    "averages": 4,
    "signal_range_min": -3 * ureg.volt, 
    "signal_range_max":  3 * ureg.volt,
    "unit": "Volt",
}
api.set_config(CONFIG)    

# start the measurement
api.start_measurement()
# this waits for the measurement to finish
api.wait_for_measurement()
# this saves the data to a file
api.save_file(f"data.txt")
```

## Development

Spectran is written to provide extensive possibilities for extension. Just extend the `spectran.daq.DAQ` class for a new driver and implement all necessary functions.

Install module into environment 

    pip install -e .[dev]
