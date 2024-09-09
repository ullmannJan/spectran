from PySide6.QtCore import QThread
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import FileResponse, HTMLResponse
import uvicorn
import requests
from time import sleep
from pathlib import Path
from . import log, ureg, spectran_path

DEFAULT_API_KEY = "12345678910111213"

class FastAPIServer(QThread):
    
    def __init__(self, main_window, api_key=DEFAULT_API_KEY, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = main_window
        self.api_key = api_key
        self.host = self.main_window.settings.value("api/host")
        self.port = self.main_window.settings.value("api/port")
    
    def run(self):
        
        oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
        app = FastAPI()
        
        async def api_key_auth(api_key: str = Depends(oauth2_scheme)):
            if api_key != self.api_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="Could not validate credentials"
                )
                
        @app.get("/ping")
        def ping():
            return {"message": "pong"}
        
        @app.get("/favicon.ico")
        @app.get("/osci_128.ico")
        def return_logo():
            return FileResponse(spectran_path / "data/osci_128.ico")

        @app.get("/", response_class=HTMLResponse)
        def homepage():
            return FileResponse(spectran_path / "data/api.html")

        @app.get("/alive")
        def alive():
            return {"message": "API Server Running"}

        @app.post("/start_measurement", dependencies=[Depends(api_key_auth)])
        def start_measurement():
            status = self.main_window.main_ui.start_measurement()
            if status is None:
                return {"message": "Measurement started"}
            else:
                return {"message": f"Measurement failed: {status}"}
            
        @app.post("/stop_measurement", dependencies=[Depends(api_key_auth)])
        def stop_measurement():
            self.main_window.main_ui.stop_measurement()
            return {"message": "Measurement stopped"}
            
        @app.post("/config", dependencies=[Depends(api_key_auth)])
        def set_config(config:dict):

            def serial_dict_to_config(d):
                """Convert dictionary with magnitude and unit to pint quantities."""
                def convert_value(v):
                    if isinstance(v, dict):
                        return ureg.Quantity(v["magnitude"], v["unit"])
                    return v
                
                return {k: convert_value(v) for k, v in d.items()}
            
            config = serial_dict_to_config(config)
            self.main_window.main_ui.set_config(config)
            return {"message": f"Configuration {config}"}
        
        @app.post("/save_file", dependencies=[Depends(api_key_auth)])
        def save_file(json:dict):
            self.main_window.data_handler.save_file(json["file_path"]) 
            return {"message": f"File saved to {json['file_path']}"}
          
        @app.post("/running", dependencies=[Depends(api_key_auth)])
        def running():
            return {"message": not self.main_window.measurement_stopped}
        
        @app.post("/connect_device", dependencies=[Depends(api_key_auth)])
        def connect_device(json:dict):
            driver = json["driver"]
            device = json["device"]
            self.main_window.main_ui.connect_device_manual(driver, device)
            return {"message": f"Connected to {driver} on {device}"}
         
        @app.post("/enable_plotting", dependencies=[Depends(api_key_auth)])
        def enable_plotting(json:dict):
            signal_enable = json["signal"]
            spectrum_enable = json["spectrum"]
            self.main_window.main_ui.enable_plotting(signal_enable, spectrum_enable)
            return {"message": f"Plotting set to signal:{signal_enable} and spectrum:{spectrum_enable}"}
        
        uvicorn.run(app, host=self.host, port=self.port)
        

class API_Connection():
    """This class handles the connection to the API Server.

    Raises:
        ConnectionError: If the connection to the API Server fails
    """
       
    def __init__(self, 
                 host:str = "127.0.0.1",
                 port: int = 8111,
                 api_key:str = DEFAULT_API_KEY):
        self.api_key = api_key
        self.host = host
        self.port = port
        self.url = f"http://{host}:{port}"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        
        self.test_connection()

    @staticmethod
    def response_handler(response:requests.Response) -> str:
        """Handle the response from the API Server by trying to read 'message' key.
        Otherwise raise an error.
        """
        if response.status_code == 200:
            return response.json()["message"]
        else:
            if "detail" in response.json():
                error = response.json()["detail"]
            else: 
                error = response.json()
            log.error(error)
            raise ConnectionError(error)
        
    def test_connection(self):
        """Tests the connection to the API Server

        Raises:
            ConnectionError: If the connection to the API Server fails
        """
        r = requests.get(f"{self.url}/alive", 
                                 headers=self.headers)
        self.response_handler(r)
        
    def start_measurement(self):
        """Starts the measurement with settings from the GUI.
        """
        r = requests.post(f"{self.url}/start_measurement", 
                                 headers=self.headers)
        log.info(self.response_handler(r))
        
    def stop_measurement(self):
        """Starts the measurement with settings from the GUI.
        """
        r = requests.post(f"{self.url}/stop_measurement", 
                                 headers=self.headers)
        log.info(self.response_handler(r))
        
    def set_config(self, config:dict):
        """Sets GUI configuration with the given dictionary.

        Args:
            config (dict): Dictionary with configuration of GUI. See examples for details.
        """
        # convert pint quantities to serializable dictionary
        def convert_config_to_serial_dict(d):
            """Convert pint quantities to a dictionary with magnitude and unit."""
            def convert_value(v):
                if isinstance(v, ureg.Quantity):
                    return {"magnitude": v.magnitude, "unit": str(v.units)}
                return v
            
            return {k: convert_value(v) for k, v in d.items()}
        
        config_converted = convert_config_to_serial_dict(config)
        r = requests.post(f"{self.url}/config", 
                                 headers=self.headers,
                                 json=config_converted)
        message = self.response_handler(r)
        log.info("Configured Measurements with {}".format(message))
        
    def save_file(self, file_path:str, **save_kwargs):
        """Save data to a file with the given filename.

        Args:
            file_path (str): Filename where to save the data.
        """
        file_path = Path(file_path).resolve()
        r = requests.post(f"{self.url}/save_file", 
                                 headers=self.headers,
                                 json={"file_path": str(file_path)})
        message = self.response_handler(r)
        log.info("Saved file to {} with {}".format(file_path, message))
        
    def enable_plotting(self, signal_enabled:bool, spectrum_enabled:bool):
        """Enable or disable plotting of the data.

        Args:
            signal_enabled (bool): Enable plotting of the signal.
            spectrum_enabled (bool): Enable plotting of the spectrum.
        """
        r = requests.post(f"{self.url}/enable_plotting", 
                                 headers=self.headers,
                                 json={"signal": signal_enabled,
                                       "spectrum": spectrum_enabled})
        message = self.response_handler(r)
        log.info(message)

    def wait_for_measurement(self, update_interval:float = 0.1):
        """Wait for the measurement to finish."""
        running = True
        while running:
            r = requests.post(f"{self.url}/running", 
                                 headers=self.headers)
            if r.status_code == 200:
                # returns True if it is still runnning
                running = self.response_handler(r)
                
            sleep(update_interval)
        
        log.info("Measurement finished")
            
    def connect_device(self, driver:str, device:str):
        """Connect to the device with the given driver.

        Args:
            driver (str): Name of the driver to connect to.
            device (str): Name of the device to connect to.
        """
        r = requests.post(f"{self.url}/connect_device", 
                                 headers=self.headers,
                                 json={"driver": driver,
                                       "device": device})
        log.info(self.response_handler(r))