from __future__ import annotations

import contextlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Literal, Sequence

from pymmcore_plus import CMMCorePlus

from pymmcore_midi import Button

from ._device import MidiDevice

if TYPE_CHECKING:
    from pymmcore_midi import Knob

MsgType = Literal["note_on", "note_off", "control_change"]
VALID_MESSAGE_TYPES = {"note_on", "note_off", "control_change", "button", "knob"}
TYPE_ALIASES: dict[str, MsgType] = {
    "button": "note_on",
    "knob": "control_change",
    "slider": "control_change",
}


@dataclass
class Mapping:
    message_type: MsgType
    control_id: int
    device_label: str | None = None
    property_name: str | None = None
    core_method: str | None = None

    def __post_init__(self) -> None:
        self.message_type = TYPE_ALIASES.get(self.message_type, self.message_type)
        if self.message_type not in VALID_MESSAGE_TYPES:
            raise ValueError(  # pragma: no cover
                "message_type must be one of "
                f"{', '.join(VALID_MESSAGE_TYPES)}, not {self.message_type!r}"
            )
        if self.core_method is None and (
            self.property_name is None or self.device_label is None
        ):
            raise ValueError(  # pragma: no cover
                "Either core_method must be specified or both "
                "property_name and device_label must be specified."
            )

    def device_obj(self, device: MidiDevice) -> Knob | Button:
        """Return the knob or button object from the device."""
        if self.message_type == "control_change":
            return device.knob[self.control_id]
        else:
            return device.button[self.control_id]

    def connect_device_to_core(self, device: MidiDevice, core: CMMCorePlus) -> Callable:
        """Connect device to core.

        This makes the connection between an individual knob/button on device, and a
        specific device property on core.
        """
        from ._core_connect import connect_button_to_property, connect_knob_to_property

        midi_obj = self.device_obj(device)

        if self.core_method is not None:
            # special case.... look for core method
            method = getattr(core, self.core_method, None)
            if not callable(method):  # pragma: no cover
                raise ValueError(f"MMCore object has no method {self.core_method!r}")

            if isinstance(midi_obj, Button):
                signal = midi_obj.pressed
            else:
                # NOTE: connecting a callback to a knob may be a bad idea
                # without checking the method signature?
                signal = midi_obj.changed
            signal.connect(method, check_nargs=False)
            return lambda: signal.disconnect(method)

        else:
            if self.message_type == "control_change":
                func: Callable[..., Callable] = connect_knob_to_property
            else:
                func = connect_button_to_property

            return func(midi_obj, core, self.device_label, self.property_name)

    @classmethod
    def from_obj(cls, obj: Mapping | dict | Sequence[str]) -> Mapping:
        """Initialize Mapping from an object."""
        if isinstance(obj, Mapping):
            obj = asdict(obj)  # pragma: no cover
        if isinstance(obj, dict):
            return cls(**obj)
        elif isinstance(obj, (list, tuple)):
            return cls(*obj)
        raise TypeError(  # pragma: no cover
            "Mapping.from_obj() requires a Mapping, dict, or tuple, not "
            f"{type(obj).__name__}"
        )


@dataclass
class DeviceMap:
    device_name: str
    mappings: list[Mapping]

    def __post_init__(self) -> None:
        self.mappings = [Mapping.from_obj(m) for m in self.mappings]

    @classmethod
    def from_file(cls, path: str | Path) -> DeviceMap:
        """Read path to DeviceMap instance.

        Must be json or yaml.
        """
        data = Path(path).read_bytes()
        if str(path).endswith(".json"):
            return cls(**json.loads(data))
        elif str(path).endswith((".yaml", ".yml")):
            try:
                import yaml  # type: ignore
            except ImportError as e:
                raise ImportError("You must install pyyaml to use yaml files.") from e

            return cls(**yaml.safe_load(data))
        raise ValueError(  # pragma: no cover
            f"File type not recognized. Must be .json, .yaml, or .yml, not {path!r}"
        )

    def connect_to_core(
        self, core: CMMCorePlus | None = None, device: MidiDevice | None = None
    ) -> Callable:
        """Connect device mappings to core instance.

        Returns a function that can be called to disconnect the device from core.
        """
        device = device or MidiDevice.from_name(self.device_name)
        core = core or CMMCorePlus.instance()
        disconnecters = [m.connect_device_to_core(device, core) for m in self.mappings]

        def disconnect() -> None:
            for d in disconnecters:
                with contextlib.suppress(Exception):
                    d()

        return disconnect
