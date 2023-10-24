# pymmcore-midi

[![License](https://img.shields.io/pypi/l/pymmcore-midi.svg?color=green)](https://github.com/pymmcore-plus/pymmcore-midi/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/pymmcore-midi.svg?color=green)](https://pypi.org/project/pymmcore-midi)
[![Python
Version](https://img.shields.io/pypi/pyversions/pymmcore-midi.svg?color=green)](https://python.org)
[![CI](https://github.com/pymmcore-plus/pymmcore-midi/actions/workflows/ci.yml/badge.svg)](https://github.com/pymmcore-plus/pymmcore-midi/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/pymmcore-plus/pymmcore-midi/branch/main/graph/badge.svg)](https://codecov.io/gh/pymmcore-plus/pymmcore-midi)

MIDI Device control for microscopes using pymmcore

## Installation

```bash
pip install pymmcore-midi
```

## Usage

Create a `pymmcore_midi.DeviceMap` object (can be done from a YAML/JSON file),
then connect it to a [pymmcore-plus
`CMMCorePlus`](https://pymmcore-plus.github.io/pymmcore-plus/api/cmmcoreplus/)
object.

```yaml
device_name: X-TOUCH MINI
mappings:
  - [button, 8, Camera, AllowMultiROI]
  - [button, 9, Camera, Binning]
  - [knob, 2, Camera, Gain]
  - [knob, 9, Camera, CCDTemperature]
  # can also use this form
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
```

```python
core = CMMCorePlus()
core.loadSystemConfiguration()

dev_map = DeviceMap.from_file(f)
dev_map.connect_to_core(core)
```

Now when you move a knob or press a button on your MIDI device, the
corresponding property/method will be updated/called on the `CMMCorePlus`
object. :tada:

## Debugging/Development

Use the environment variable `PYMMCORE_MIDI_DEBUG=1` to print out the MIDI
messages that are being received from your device. (This is useful to determine
the appropriate message type and control ID for your device map.)
