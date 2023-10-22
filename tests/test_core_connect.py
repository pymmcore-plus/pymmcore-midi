from unittest.mock import Mock, call

import mido
import pytest
from pymmcore_plus import CMMCorePlus

from pymmcore_midi import XTouchMini, connect_device_to_core, connect_knob_to_property


def test_core_connect(mock_xtouch) -> None:
    mock_in, mock_out = mock_xtouch
    device = XTouchMini()

    core = CMMCorePlus.instance()
    core.loadSystemConfiguration()
    core.setProperty("Camera", "AllowMultiROI", 1)  # show that it highlights the button

    CONNECTIONS = [
        ("button", 8, "Camera", "AllowMultiROI"),
        ("button", 9, "Camera", "Binning"),
        ("knob", 1, "Camera", "Exposure"),
        ("knob", 2, "Camera", "Gain"),
        ("knob", 9, "Camera", "CCDTemperature"),
        ("button", 22, "Core", "startContinuousSequenceAcquisition"),
    ]

    disconnect = connect_device_to_core(device, core, CONNECTIONS)

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
