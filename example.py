from pymmcore_plus import CMMCorePlus
from pymmcore_widgets import ImagePreview, PropertyBrowser
from qtpy.QtWidgets import QApplication

from pymmcore_midi import XTouchMini, connect_device_to_core

app = QApplication([])

device = XTouchMini()

core = CMMCorePlus.instance()
core.loadSystemConfiguration()

# Create a PropertyBrowser widget
browser = PropertyBrowser()
browser.show()

core.setProperty("Camera", "AllowMultiROI", 1)  # show that it highlights the button

CONNECTIONS = [
    ("button", 8, "Camera", "AllowMultiROI"),
    ("button", 9, "Camera", "Binning"),
    ("knob", 1, "Camera", "Exposure"),
    ("knob", 2, "Camera", "Gain"),
    ("knob", 3, "Camera", "TestProperty5"),
    ("knob", 9, "Camera", "CCDTemperature"),
    ("button", 21, "Core", "stopSequenceAcquisition"),
    ("button", 22, "Core", "startContinuousSequenceAcquisition"),
]


preview = ImagePreview(mmcore=core)
preview.show()
connect_device_to_core(device, core, CONNECTIONS)

app.exec_()
device.reset()
