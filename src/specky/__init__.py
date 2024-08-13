from .main_window import MainWindow

try:
    from ._version import version as __version__
    from ._version import version_tuple
except ImportError:
    __version__ = "unknown version"
    version_tuple = (0, 0, "unknown version")

def run():
    main_window = MainWindow()
    main_window.run()