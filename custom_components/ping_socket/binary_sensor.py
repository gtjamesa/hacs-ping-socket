"""Provides a binary sensor which gets its values from a TCP socket"""
from __future__ import annotations

from typing import Any, Final

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    DEVICE_CLASS_CONNECTIVITY,
    PLATFORM_SCHEMA as PARENT_PLATFORM_SCHEMA,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType

from .client import PING_SOCKET_PLATFORM_SCHEMA, PingSocketEntity
from .const import CONF_VALUE_ON

PLATFORM_SCHEMA: Final = PARENT_PLATFORM_SCHEMA.extend(PING_SOCKET_PLATFORM_SCHEMA)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: dict[str, Any] | None = None,
) -> None:
    """Set up the TCP ping binary sensor."""
    add_entities([PingSocketBinarySensor(hass, config)])


class PingSocketBinarySensor(PingSocketEntity, BinarySensorEntity):
    """A binary sensor which is on when its state == CONF_VALUE_ON."""

    @property
    def name(self) -> str:
        """Return the name of this sensor."""
        return self._config[CONF_NAME]

    @property
    def available(self) -> str:
        """Return if we have done the first ping."""
        return self._available

    @property
    def device_class(self) -> str:
        """Return the class of this sensor."""
        return DEVICE_CLASS_CONNECTIVITY

    @property
    def is_on(self) -> bool:
        """
        Binary sensor which is on when either of the following is true:
        - a `value_on` is specified, and matches the response from the target host
        - no `value_on` specified, and the server is listening to connections on `port`
        """

        value_on = self._config[CONF_VALUE_ON]

        # We need to do a value comparison
        if value_on is not None and self._connected:
            return self._state == value_on

        # Return whether or not the connection to the target was successful
        return self._connected
