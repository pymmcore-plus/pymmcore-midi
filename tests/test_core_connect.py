from pathlib import Path
from unittest.mock import Mock, call

import mido
import pytest
from pymmcore_plus import CMMCorePlus

from pymmcore_midi import DeviceMap, XTouchMini, connect_knob_to_property

YAML = """
device_name: X-TOUCH MINI
mappings:
  - [button, 8, Camera, AllowMultiROI]
  - [button, 9, Camera, Binning]
  - [knob, 2, Camera, Gain]
  - [knob, 9, Camera, CCDTemperature]
  - message_type: control_change
    control_id: 1
    device_label: Camera
    property_name: Exposure
  - message_type: button
    control_id: 10
    core_method: snap
  - message_type: knob
    control_id: 17
    core_method: setAutoFocusOffset
"""


def test_core_connect(mock_xtouch, tmp_path: Path) -> None:
    (spec := tmp_path / "spec.yaml").write_text(YAML)
    dev_map = DeviceMap.from_file(spec)
    assert dev_map.device_name == "X-TOUCH MINI"

    mock_in, mock_out = mock_xtouch
    device = XTouchMini()

    core = CMMCorePlus.instance()
    with pytest.raises(RuntimeError, match='No device with label "Camera"'):
        dev_map.connect_to_core(core, device)

    core.loadSystemConfiguration()
    core.setProperty("Camera", "AllowMultiROI", 1)  # show that it highlights the button
    disconnect = dev_map.connect_to_core(core, device)

    # button value was set during connection
    msg = mido.Message("note_on", channel=10, note=8, velocity=64, time=0)
    assert call(msg) in mock_out.send.call_args_list

    with pytest.warns(match="has no limits"):
        connect_knob_to_property(device.knob[3], core, "Camera", "TestProperty5")

    mock = Mock()
    device.knob[2].changed.connect(mock)
    msg = mido.Message("control_change", channel=10, control=4, value=127, time=0)
    mock_in.callback(msg)

    # turn knob
    device.knob[2].changed.emit(127)
    assert core.getProperty("Camera", "Gain") == "8"

    # click button
    assert core.getProperty("Camera", "Binning") == "1"
    device.button[9].released.emit()
    assert core.getProperty("Camera", "Binning") == "2"

    disconnect()
