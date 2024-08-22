# absolute imports
from PySide6.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QWidget,
    QGroupBox,
    QPushButton,
    QCheckBox,
    QLineEdit,
    QHBoxLayout,
    QComboBox,
    QTabWidget,
    QStyleFactory,
)
from PySide6.QtGui import QIcon

# relative imports
from . import __version__ as spectran_version
from . import spectran_path
from .settings import Settings, DEFAULT_SETTINGS
from . import log


class Window(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """

    def __init__(self, parent, title="Window"):
        super().__init__()
        # this makes the main application unresponsive while using this window
        # self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.parent = parent

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setWindowTitle(f"Spectran: {title}")
        self.setWindowIcon(QIcon(str(spectran_path / "data/osci_128.ico")))
        self.setMinimumSize(300, 200)

    def closeEvent(self, event):
        """
        Override the close event to set focus back to the parent window.
        """
        if self.parent:
            self.parent.setFocus()
            self.parent.activateWindow()
        super().closeEvent(event)


class SaveWindow(Window):
    """
    The window displayed to save the data.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(title="Save Dialog", *args, **kwargs)

        # Save Options
        self.options_box = QGroupBox("Options", self)
        self.options_layout = QVBoxLayout()
        self.options_box.setLayout(self.options_layout)
        self.layout.addWidget(self.options_box)

        # Save Button
        self.saveButton = QPushButton("Save", self)
        self.saveButton.clicked.connect(self.save)
        self.layout.addWidget(self.saveButton)

    def save(self):
        return self.parent.data_handler.save_file()


class AboutWindow(Window):
    """
    The window displaying the about.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(title="About", *args, **kwargs)

        self.info_layout = QVBoxLayout()

        self.info_layout.addWidget(QLabel(f"<b>Spectran {spectran_version}</b>"))
        self.info_layout.addWidget(
            QLabel("A simple spectrum analyzer.")
        )
        self.info_layout.addWidget(QLabel("Developed by:"))
        self.info_layout.addWidget(QLabel("Jan Ullmann"))

        self.layout.addLayout(self.info_layout)

class SettingsWindow(Window):

    def __init__(self, *args, **kwargs):
        super().__init__(title="Settings", *args, **kwargs)

        self.settings: Settings = self.parent.settings
        self.settings.load_settings()

        self.main_layout = QVBoxLayout()
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        self.graphics = QWidget()
        self.misc = QWidget()

        self.tab_widget.addTab(self.graphics, "Graphics")
        self.tab_widget.addTab(self.misc, "Misc")
        self.tab_widget.setMinimumSize(350, 200)

        self.create_graphics_ui()
        self.create_misc_ui()

        # Resize the window to fit the contents of the tabs
        self.resize(self.tab_widget.sizeHint())

        # Buttons Layout
        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)

        # Save Button
        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save)
        self.save_button.setEnabled(self.changed)
        self.button_layout.addWidget(self.save_button)

        # reset button
        self.reset_button = QPushButton("Reset to defaults", self)
        self.reset_button.clicked.connect(self.reset_to_defaults)
        self.reset_button.setEnabled(not self.settings.is_default)
        self.button_layout.addWidget(self.reset_button)

        self.layout.addLayout(self.main_layout)
        self.adjustSize()

    def create_misc_ui(self):

        self.misc_layout = QVBoxLayout()
        self.misc.setLayout(self.misc_layout)

        self.file_extensions_layout = QHBoxLayout()
        self.file_extensions_label = QLabel("File Extensions", self)
        self.file_extensions_layout.addWidget(self.file_extensions_label)
        self.file_extensions = QLineEdit(self)
        self.file_extensions.setPlaceholderText(".dat;.txt")
        file_ext_string = ";".join(self.settings.value("misc/file_extensions"))
        self.file_extensions.setText(file_ext_string)
        self.file_extensions.textChanged.connect(self.update_window)
        self.file_extensions_layout.addWidget(self.file_extensions)
        self.misc_layout.addLayout(self.file_extensions_layout)

        self.misc_layout.addStretch()

    def create_graphics_ui(self):
        """Create the UI for the settings window."""

        # graphics style
        self.graphics_layout = QVBoxLayout()
        self.graphics_style_layout = QHBoxLayout()
        self.graphics_style_label = QLabel("Graphics Style", self)

        self.graphics_style_dd = QComboBox(self)

        available_styles = QStyleFactory.keys()

        self.graphics_style_dd.addItems(available_styles)
        self.graphics_style_dd.setCurrentText(self.settings.value("graphics/style"))
        self.graphics_style_dd.currentTextChanged.connect(self.update_window)

        self.graphics_style_layout.addWidget(self.graphics_style_label)
        self.graphics_style_layout.addWidget(self.graphics_style_dd)
        self.graphics_layout.addLayout(self.graphics_style_layout)

        self.graphics_layout.addStretch()

        self.graphics.setLayout(self.graphics_layout)

    def set_settings(self, settings: dict):
        """Set Settings to a value."""

        self.graphics_style_dd.setCurrentText(settings.get("graphics/style"))

        file_ext_string = ";".join(settings.get("misc/file_extensions"))
        self.file_extensions.setText(file_ext_string)
        self.update_window()

    def reset_to_defaults(self):
        """Reset the settings to the default values."""
        self.set_settings(DEFAULT_SETTINGS)
        self.reset_button.setEnabled(False)

    def update_window(self):
        """Update the windows with the new settings."""
        log.info("Updating settings window")
        # set button states
        self.reset_button.setEnabled(not self.settings.is_default)
        self.save_button.setEnabled(self.changed)

    @property
    def current_selection(self):
        return {
            "graphics/style": self.graphics_style_dd.currentText(),
            "misc/file_extensions": self.file_extensions.text().split(";"),
        }

    def save(self):
        for key in self.current_selection.keys():
            if key in DEFAULT_SETTINGS.keys():
                value = self.current_selection.get(key)
                self.settings.save(key, value)

        # update the window and the color palette
        self.parent.update_style()

        self.update_window()
       

    @property
    def changed(self):
        """Check if there is a change in the settings gui."""
        return not self.settings.equals_settings(self.current_selection)
