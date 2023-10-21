"""Midi control for microscopes using pymmcore"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("pymmcore-midi")
except PackageNotFoundError:
    __version__ = "uninstalled"
__author__ = "Talley Lambert"
__email__ = "talley.lambert@gmail.com"
