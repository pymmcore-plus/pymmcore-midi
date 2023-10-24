from pathlib import Path

import pytest
from pymmcore_plus import CMMCorePlus

from pymmcore_midi import DeviceMap

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
"""


def test_spec(tmp_path: Path) -> None:
    (f := tmp_path / "spec.yaml").write_text(YAML)
    assert f.read_text() == YAML
    map_ = DeviceMap.from_file(f)
    assert map_.device_name == "X-TOUCH MINI"

    core = CMMCorePlus()
    with pytest.raises(RuntimeError, match='No device with label "Camera"'):
        map_.connect_to_core(core)

    core.loadSystemConfiguration()
    map_.connect_to_core(core)
