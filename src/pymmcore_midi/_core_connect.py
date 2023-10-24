from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from pymmcore_plus import CMMCorePlus

    from pymmcore_midi import Button, Knob


def connect_knob_to_property(
    knob: Knob, core: CMMCorePlus, device_label: str, property_name: str
) -> Callable[[], None]:
    """Connect a knob to a property controlled by MMCore.

    Parameters
    ----------
    knob : Knob
        The knob to connect
    core : CMMCorePlus
        The MMCorePlus instance
    device_label : str
        The label of the device that owns the property
    property_name : str
        The name of the property to connect to

    Returns
    -------
    Callable[[], None]
        A function that can be called to disconnect the knob from the property
    """
    if not core.hasPropertyLimits(device_label, property_name):
        warnings.warn(
            f"Property {device_label}.{property_name} has no limits and "
            "cannot be connected to a MIDI knob",
            stacklevel=2,
        )
        return lambda: None

    prop_lower = core.getPropertyLowerLimit(device_label, property_name)
    prop_range = core.getPropertyUpperLimit(device_label, property_name) - prop_lower
    knob_lower = 0
    knob_upper = 127
    knob_range = knob_upper - knob_lower

    def knob2value(value: float) -> float:
        """Convert value from knob range to property range."""
        v = (value - knob_lower) / knob_range * prop_range + prop_lower
        return float(v)

    def value2knob(value: float | str) -> int:
        """Convert value from property range to knob range."""
        out = (float(value) - prop_lower) / prop_range * knob_range + knob_lower
        # Make sure the value is in the range [knob_lower, knob_upper]
        return min(max(int(out), knob_lower), knob_upper)

    # set knob value to the current value of the property
    knob.set_value(value2knob(float(core.getProperty(device_label, property_name))))

    # connect knob change events to update core
    @knob.changed.connect
    def _update_core_value(value: float) -> None:
        core.setProperty(device_label, property_name, knob2value(value))

    # connect core property change events to update knob
    def _update_knob_value(dev: str, prop: str, value: str) -> None:
        if dev == device_label and prop == property_name:
            knob.set_value(value2knob(value))

    core.events.propertyChanged.connect(_update_knob_value)

    def disconnect() -> None:
        knob.changed.disconnect(_update_core_value)
        core.events.propertyChanged.disconnect(_update_knob_value)

    return disconnect


def connect_button_to_property(
    button: Button, core: CMMCorePlus, device_label: str, property_name: str
) -> Callable[[], None]:
    """Connect a button to a property controlled by MMCore.

    Parameters
    ----------
    button : Button
        The button to connect
    core : CMMCorePlus
        The MMCorePlus instance
    device_label : str
        The label of the device that owns the property
    property_name : str
        The name of the property to connect to

    Returns
    -------
    Callable[[], None]
        A function that can be called to disconnect the knob from the property
    """
    # set knob value to the current value of the property
    # .set_value(value2knob(float(core.getProperty(device_label, property_name))))

    allowed = core.getAllowedPropertyValues(device_label, property_name)
    is_bool = set(allowed) == {"0", "1"}
    if not allowed:  # pragma: no cover
        warnings.warn(
            f"Property {device_label}.{property_name} has no allowed values and "
            "cannot be connected to a MIDI button",
            stacklevel=2,
        )
        return lambda: None

    def set_button_state(val: Any) -> None:
        if val in ("0", False, 0):
            button.release()  # ensure the button is not highlighted
        elif is_bool:
            button.press()  # keep the button highlighted

    set_button_state(core.getProperty(device_label, property_name))

    # connect knob change events to update core
    @button.released.connect
    def _update_core_value() -> None:
        current = core.getProperty(device_label, property_name)
        next_val = allowed[(allowed.index(current) + 1) % len(allowed)]
        core.setProperty(device_label, property_name, next_val)
        set_button_state(next_val)

    # connect core property change events to update knob
    def _update_button_value(dev: str, prop: str, value: str) -> None:
        if dev == device_label and prop == property_name:
            set_button_state(value)

    core.events.propertyChanged.connect(_update_button_value)

    def disconnect() -> None:
        button.released.disconnect(_update_core_value)
        core.events.propertyChanged.disconnect(_update_button_value)

    return disconnect
