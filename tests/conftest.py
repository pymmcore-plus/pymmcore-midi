from unittest.mock import MagicMock

import mido
import pytest


@pytest.fixture
def mock_xtouch(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_in = MagicMock()
    mock_out = MagicMock()

    def _mock_open_input(device_name: str) -> mido.ports.BaseInput:
        if device_name == "X-TOUCH MINI":
            return mock_in

    def _mock_open_output(device_name: str) -> mido.ports.BaseOutput:
        if device_name == "X-TOUCH MINI":
            return mock_out

    monkeypatch.setattr(mido, "open_input", _mock_open_input)
    monkeypatch.setattr(mido, "open_output", _mock_open_output)

    yield mock_in, mock_out
