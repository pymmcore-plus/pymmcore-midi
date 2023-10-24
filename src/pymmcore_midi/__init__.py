"""Midi control for microscopes using pymmcore."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("pymmcore-midi")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "uninstalled"

from ._core_connect import connect_button_to_property, connect_knob_to_property
from ._device import Button, Knob, MidiDevice
from ._map_spec import DeviceMap, Mapping
from ._xtouch import XTouchMini

__all__ = [
    "Button",
    "connect_button_to_property",
    "connect_knob_to_property",
    "DeviceMap",
    "Knob",
    "Mapping",
    "MidiDevice",
    "XTouchMini",
]
