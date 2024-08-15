"""This module contains functions to run the program."""

from PySide6.QtWidgets import QApplication
import warnings
import sys
from .main_window import MainWindow

def run():

    # This starts the application
    app = QApplication(sys.argv)
    w = MainWindow()
    sys.excepthook = lambda *args: exception_hook(w, *args)
    warnings.showwarning = warning_handler
    w.show()
    app.exec()


def exception_hook(main_window, exception_type, exception_value: Exception, traceback):
    """
    Exception hook for the application.

    Args:
        exception_type (type): Type of the exception.
        exception_value (Exception): The exception.
        traceback (traceback): The traceback of the exception.
    """
    # Display an error message box
    main_window.raise_error(exception_value)
    sys.__excepthook__(exception_type, exception_value, traceback)

   
def warning_handler(message, category, filename, lineno, file=None, line=None):
    """
    Custom warning handler.

    Args:
        message (Warning): The warning message.
        category (Warning): The category of the warning.
        filename (str): The file name where the warning occurred.
        lineno (int): The line number where the warning occurred.
        file (file object, optional): The file object to write the warning to.
        line (str, optional): The line of code where the warning occurred.
    """
    warning_message = f"{filename}:{lineno}: {category.__name__}: {message}"
    print(warning_message)