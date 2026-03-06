"""Functionality for handling forcing data"""

__version__ = "0.1.0"

from .process import ProcessMAR, ProcessRACMO
from .melt import MeltMar

__all__ = ["ProcessMAR", "ProcessRACMO", "MeltMar"]
