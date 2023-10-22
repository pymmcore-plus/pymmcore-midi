from typing import (
    Iterable,
    Iterator,
    Mapping,
    TypeVar,
)

import mido
import mido.backends
from psygnal import Signal

T = TypeVar("T")


# just a read-only mapping
class _Map(Mapping[int, T]):
    def __init__(self, data: Mapping[int, T]) -> None:
        self._data = data

    def __getitem__(self, key: int) -> T:
        return self._data[key]

    def __iter__(self) -> Iterator[int]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return repr(self._data)

    def __contains__(self, key: object) -> bool:
        return key in self._data


class Button:
    """A button on a midi device."""

    pressed = Signal()
    released = Signal()

    def __init__(self, note: int, output: mido.ports.BaseOutput, channel: int = 10):
        self._note = note
        self._channel = channel
        self._output = output

    def press(self) -> None:
        """Send a note_on message."""
        msg = mido.Message("note_on", channel=self._channel, note=self._note)
        self._output.send(msg)

    def release(self) -> None:
        """Send a note_off message."""
        msg = mido.Message("note_off", channel=self._channel, note=self._note)
        self._output.send(msg)


class Knob:
    """A knob/slider on a midi device."""

    changed = Signal(float)

    def __init__(self, control: int, output: mido.ports.BaseOutput, channel: int = 10):
        self._control = control
        self._channel = channel
        self._output = output

    def set_value(self, val: float) -> None:
        """Send a control_change message."""
        msg = mido.Message(
            "control_change", channel=self._channel, control=self._control, value=val
        )
        self._output.send(msg)

    def __repr__(self) -> str:
        return f"Knob({self._control!r})"


class Buttons(_Map[Button]):
    """A group of buttons. Allows connecting to any button change."""

    pressed = Signal(str)
    released = Signal(str)

    def __init__(
        self, button_ids: Iterable[int], output: mido.ports.BaseOutput
    ) -> None:
        super().__init__({x: Button(x, output) for x in button_ids})
        # connect to any button press/release
        for k, v in self.items():
            v.pressed.connect(lambda k=k: self.pressed.emit(k))
            v.released.connect(lambda k=k: self.released.emit(k))


class Knobs(_Map[Knob]):
    """A group of knobs. Allows connecting to any knob change."""

    changed = Signal(str, float)

    def __init__(self, knob_ids: Iterable[int], output: mido.ports.BaseOutput) -> None:
        super().__init__({x: Knob(x, output) for x in knob_ids})
        # connect to any knob change
        for k, v in self.items():
            v.changed.connect(lambda value, k=k: self.changed.emit(k, value))


class MidiDevice:
    """Generic midi device.

    Parameters
    ----------
    device_name : str
        The name of the midi device to connect to.
    button_ids : Iterable[int]
        The ids of the buttons on the device. (These correspond to the note numbers.)
    knob_ids : Iterable[int]
        The ids of the knobs on the device. (These correspond to the control numbers.)
    """

    def __init__(
        self,
        device_name: str,
        button_ids: Iterable[int] = (),
        knob_ids: Iterable[int] = (),
    ):
        try:
            self._input: mido.ports.BaseInput = mido.open_input(device_name)
            self._output: mido.ports.BaseOutput = mido.open_output(device_name)
        except OSError as e:  # pragma: no cover
            raise OSError(
                f"Could not open input device {device_name!r}. "
                f"Available device names are: {set(mido.get_input_names())}"
            ) from e
        self._input.callback = self._on_msg

        self.device_name = device_name
        self._buttons = Buttons(button_ids, self._output)
        self._knobs = Knobs(knob_ids, self._output)

    @property
    def knob(self) -> Knobs:
        """The knobs on the device.

        Examples
        --------
        >>> x.knob[1].changed.connect(lambda v: print(f"knob 1 changed to {v}"))
        >>> x.knob.changed.connect(lambda k, v: print(f"knob {k} changed to {v}"))
        """
        return self._knobs

    @property
    def button(self) -> Buttons:
        """The buttons on the device.

        Examples
        --------
        >>> x.button[1].pressed.connect(lambda: print("button 1 pressed"))
        >>> x.button[1].released.connect(lambda: print("button 1 released"))
        >>> x.button.pressed.connect(lambda k: print(f"button {k} pressed"))
        >>> x.button.released.connect(lambda k: print(f"button {k} released"))
        """
        return self._buttons

    def close(self) -> None:
        """Close the midi device."""
        self._input.close()
        self._output.close()

    def _on_msg(self, message: mido.Message) -> None:
        if message.type == "control_change":
            self._knobs[message.control].changed.emit(message.value)
        elif message.type == "note_on":
            self._buttons[message.note].pressed.emit()
        elif message.type == "note_off":
            self._buttons[message.note].released.emit()

    def reset(self) -> None:
        """Set all knobs/sliders to 0 and make sure buttons are unpressed."""
        for knob in self._knobs.values():
            knob.set_value(0)
        for button in self._buttons.values():
            button.release()
