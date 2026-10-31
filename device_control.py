"""JSON device control payload builder."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


# Commands the manager panel may emit. This module only builds JSON; it does
# not call a device or write back to the spreadsheet.
VALID_COMMANDS = ("power_on", "power_off", "input_switch", "volume_set")


def build_device_command(
    command: str,
    device: str,
    requested_by: str,
    parameters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a simulated AV device control JSON payload."""
    if command not in VALID_COMMANDS:
        raise ValueError(f"Unsupported command: {command}")

    payload: dict[str, Any] = {
        "command": command,
        "device": device,
        "parameters": parameters or {},
        "requested_by": requested_by,
        # UTC, second precision, Z suffix so payloads compare and sort as text.
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    return payload
