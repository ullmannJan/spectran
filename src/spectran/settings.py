from PySide6.QtCore import QSettings
from . import log, ureg

DEFAULT_VALUES = {
    "input_channel": "",
    "sample_rate": 100_000 * ureg.Hz,
    "duration": 2 * ureg.second,
    "averages": 1,
    "signal_range_min": -5 * ureg.volt, 
    "signal_range_max":  5 * ureg.volt,
    "unit": "Volt",
}

DEFAULT_SETTINGS = {
    "graphics/style": "Fusion",
    "misc/file_extensions": [".txt", ".csv"],
    "api/host": "127.0.0.1",
    "api/port": 8111,    
}

class Settings(QSettings):

    def __init__(self, parent, organization: str, application: str):
        super().__init__(organization, application)
        self.parent = parent

    def load_defaults(self):
        """Manage loading all the settings."""
        log.info("Loading default settings")
        for key, value in DEFAULT_SETTINGS.items():
            self.setValue(key, value)
        self.sync()

    def load_settings(self):
        """Load all the settings."""
        log.info("Loading settings")
        for key in DEFAULT_SETTINGS.keys():
            if self.value(key) is None:
                # No settings exist, load the default settings
                self.load_defaults()

    def save(self, key, value):
        """Manage saving all the settings."""
        log.info("Saving setting: {}".format(key))
        self.setValue(key, value)
        self.sync()

    @property
    def is_default(self):
        """Test if the settings are the default values."""
        return self.equals_settings(DEFAULT_SETTINGS)

    def equals_settings(self, settings: dict):
        """Compare the settings to the default settings."""
        # check if the keys are the same
        if set(self.allKeys()) != set(settings.keys()):
            log.info(
                f"Settings not equal: {set(self.allKeys())} {set(settings.keys())}"
            )
            return False
        # check if the values are the same
        for key in settings.keys():
            # for lists we need to compare the sets
            if isinstance(settings.get(key), list):
                if set(self.value(key)) != set(settings.get(key)):
                    log.info(
                        f"Settings not equal: {set(self.allKeys())} {set(settings.keys())}"
                    )
                    return False
            # for boolean we need to set the type
            elif isinstance(settings.get(key), bool):
                if self.value(key, type=bool) != settings.get(key):
                    log.debug(
                        f"Setting not equal: {key} {self.value(key)} {settings.get(key)}"
                    )
                    return False
            # otherwise simply compare the values
            elif self.value(key) != settings.get(key):
                log.debug(
                    f"Setting not equal: {key} {self.value(key)} {settings.get(key)}"
                )
                return False
        return True