from ._device import Button, MidiDevice


class XTouchMini(MidiDevice):
    """X-TOUCH MINI midi controller.

    See https://www.behringer.com/product.html?modelCode=P0B3M

    This device has 8 knobs (each of which is also a button), 16 buttons, and 1 sliders.

    Button Indices:

    Layer A:
    --------
    [ 0] [ 1] [ 2] [ 3] [ 4] [ 5] [ 6] [ 7]   (Top Row of Knobs)
    [ 8] [ 9] [10] [11] [12] [13] [14] [15]   (Top Row of Buttons)
    [16] [17] [18] [19] [20] [21] [22] [23]   (Bottom Row of Buttons)

    Layer B:
    --------
    [24] [25] [26] [27] [28] [29] [30] [31]   (Top Row of Knobs)
    [32] [33] [34] [35] [36] [37] [38] [39]   (Top Row of Buttons)
    [40] [41] [42] [43] [44] [45] [46] [47]   (Bottom Row of Buttons)

    Knob/Slider Indices:

    Layer A:
    --------
    [ 1] [ 2] [ 3] [ 4] [ 5] [ 6] [ 7] [ 8]   (Knobs)
                                              [ 9]  (Slider)

    Layer B:
    --------
    [11] [12] [13] [14] [15] [16] [17] [18]   (Knobs)
                                              [11]  (Slider)
    """

    DEVICE_NAME = "X-TOUCH MINI"

    def __init__(self) -> None:
        super().__init__(self.DEVICE_NAME, range(48), range(1, 19))

    @property
    def rewind(self) -> Button:
        return self._buttons[18]

    @property
    def fast_forward(self) -> Button:
        return self._buttons[19]

    @property
    def loop(self) -> Button:
        return self._buttons[20]

    @property
    def stop(self) -> Button:
        return self._buttons[21]

    @property
    def play(self) -> Button:
        return self._buttons[22]

    @property
    def record(self) -> Button:
        return self._buttons[23]
