from pathlib import Path
spectran_path = Path(__file__).parent

# Logger
import logging
log = logging.getLogger(__name__)

# Units
from pint import UnitRegistry
ureg = UnitRegistry()

# Versions
try:
    from ._version import version as __version__
    from ._version import version_tuple
except ImportError:
    __version__ = "unknown version"
    version_tuple = (0, 0, "unknown version")

from .app import run