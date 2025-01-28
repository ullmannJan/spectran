"""
Spectran package initialization.

This module sets up the necessary paths, logging, units, and versioning for the Spectran package.
"""

from pathlib import Path
import logging
from pint import UnitRegistry

# Versions
try:
    from ._version import version as __version__
    from ._version import version_tuple
except ImportError:
    __version__ = "unknown version"
    version_tuple = (0, 0, "unknown version")


# This path is necessary for the package to find the data files
spectran_path = Path(__file__).parent

# Logger
log = logging.getLogger(__name__)

# Units setup using pint
ureg = UnitRegistry()

from .app import run