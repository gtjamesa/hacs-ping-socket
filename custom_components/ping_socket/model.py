"""Models for Ping Socket platform."""
from __future__ import annotations

from typing import TypedDict

from homeassistant.helpers.template import Template


class PingSocketSensorConfig(TypedDict):
    """TypedDict for PingSocketSensor config."""

    name: str
    host: str
    port: str
    timeout: int
    payload: str | None
    value_template: Template | None
    value_on: str | None
    buffer_size: int
