"""Midi control for microscopes using pymmcore."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("pymmcore-midi")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "uninstalled"
__author__ = "Talley Lambert"
__email__ = "talley.lambert@gmail.com"

from ._device import MidiDevice
from ._xtouch import XTouchMini

__all__ = ["MidiDevice", "XTouchMini"]
