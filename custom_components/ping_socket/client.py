"""Ping (socket) client code"""
from __future__ import annotations

import socket
import logging
from typing import Any, Final

import voluptuous as vol

from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PAYLOAD,
    CONF_PORT,
    CONF_TIMEOUT,
    CONF_VALUE_TEMPLATE,
)

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import TemplateError
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.template import Template
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_BUFFER_SIZE,
    CONF_VALUE_ON,
    DEFAULT_BUFFER_SIZE,
    DEFAULT_NAME,
    DEFAULT_TIMEOUT,
)
from .model import PingSocketSensorConfig

_LOGGER = logging.getLogger(__name__)

PING_SOCKET_PLATFORM_SCHEMA: Final[dict[vol.Marker, Any]] = {
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_PORT): cv.port,
    vol.Optional(CONF_PAYLOAD): cv.string,
    vol.Optional(CONF_BUFFER_SIZE, default=DEFAULT_BUFFER_SIZE): cv.positive_int,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,
    vol.Optional(CONF_VALUE_ON): cv.string,
    vol.Optional(CONF_VALUE_TEMPLATE): cv.template,
}


class PingSocketEntity(Entity):
    """Base entity class for Ping (Socket) platform"""

    def __init__(self, hass: HomeAssistant, config: ConfigType) -> None:

        value_template: Template | None = config.get(CONF_VALUE_TEMPLATE)
        if value_template is not None:
            value_template.hass = hass

        self._hass = hass
        self._config: PingSocketSensorConfig = {
            CONF_NAME: config.get(CONF_NAME),
            CONF_HOST: config.get(CONF_HOST),
            CONF_PORT: config.get(CONF_PORT),
            CONF_TIMEOUT: config.get(CONF_TIMEOUT),
            CONF_PAYLOAD: config.get(CONF_PAYLOAD),
            CONF_VALUE_TEMPLATE: value_template,
            CONF_VALUE_ON: config.get(CONF_VALUE_ON),
            CONF_BUFFER_SIZE: config.get(CONF_BUFFER_SIZE),
        }

        self._state: str | None = None
        self._connected = False
        self._available = False
        self.async_update()

    async def async_update(self) -> None:
        """Get the latest value for this sensor."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            self._available = True

            sock.settimeout(self._config[CONF_TIMEOUT])

            # Attempt to connect to the target host
            try:
                _LOGGER.debug(
                    "ping socket %s:%s",
                    self._config[CONF_HOST],
                    self._config[CONF_PORT],
                )
                sock.connect((self._config[CONF_HOST], self._config[CONF_PORT]))
            except OSError:
                _LOGGER.debug(
                    "ping socket failed to connect to %s:%s",
                    self._config[CONF_HOST],
                    self._config[CONF_PORT],
                )
                self._connected = False
                return

            # We managed to successfully connect to the target at this point
            self._connected = True

            # Send payload if specified by user
            if self._config[CONF_PAYLOAD] is not None:
                try:
                    sock.send(self._config[CONF_PAYLOAD].encode())
                except OSError:
                    return

            # Read data from the target
            try:
                value = sock.recv(self._config[CONF_BUFFER_SIZE]).decode()
            except OSError:
                pass

            sock.close()

        # If a value template was specified, we should render the value and update state for comparison
        value_template = self._config[CONF_VALUE_TEMPLATE]
        if value_template is not None:
            try:
                self._state = value_template.render(parse_result=False, value=value)
                return
            except TemplateError:
                return

        # Set state to the value read from target
        self._state = value
