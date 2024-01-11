from pymmcore_plus import CMMCorePlus
from pymmcore_widgets import ImagePreview, PropertyBrowser
from qtpy.QtWidgets import QApplication

from pymmcore_midi import DeviceMap, XTouchMini

app = QApplication([])

# from pymmcore-plus
core = CMMCorePlus.instance()
core.loadSystemConfiguration()

# this library
mini = XTouchMini()
dev_map = DeviceMap.from_file("mini.yml")
dev_map.connect_to_core(core, mini)

# just stuff from widgets to show that it's responding
img = ImagePreview(mmcore=core)
img.show()
browser = PropertyBrowser(mmcore=core)
browser.show()
app.exec()
