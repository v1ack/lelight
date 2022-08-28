"""Platform for light integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    LightEntity,
    ColorMode,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util.color import (
    color_temperature_mired_to_kelvin,
    color_temperature_kelvin_to_mired,
)

from .connector import App
from .connector_bless import BlessBackend
from .const import DOMAIN
from .encoder import Commands

logger = logging.getLogger("lelight")


async def async_setup_entry(hass, config_entry, async_add_entities):
    # Получаем ссылку на родительский класс нашей интеграции из конфигурации модуля.
    light = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([light])


def normalize_value(value: int, max: int, new_max: int) -> int:
    """Normalize value to new range."""
    return int(value * new_max / max)


class LeLight(LightEntity):
    min_mireds = color_temperature_kelvin_to_mired(6400)
    max_mireds = color_temperature_kelvin_to_mired(3000)

    _attr_unique_id = "lelight_light"

    supported_color_modes = {
        ColorMode.ONOFF,
        ColorMode.BRIGHTNESS,
        ColorMode.COLOR_TEMP,
    }

    def __init__(self, host: str) -> None:
        self._host = host
        self._name = "LeLight"
        self._state = False
        self.app = App(host, BlessBackend())

        # brightness from 0 to 1000 (device format)
        self._brightness = 1000

        # temp in kelvin from 3000 to 6400 (device format)
        self._temp = 4700

    @property
    def name(self) -> str:
        return self._name

    @property
    def brightness(self):
        return normalize_value(self._brightness, 1000, 255)

    @property
    def color_temp(self) -> int | None:
        return color_temperature_kelvin_to_mired(self._temp)

    @property
    def color_mode(self) -> ColorMode | None:
        return ColorMode.COLOR_TEMP

    def turn_on(self, **kwargs: Any) -> None:
        if not self._state:
            self.app.send(Commands.turn_on())
        # resp = requests.post(f"{self._host}/lamp?command=turn_on").json()
        # logger.info(f"lamp turn_on: {resp}")
        self._state = True
        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = normalize_value(kwargs[ATTR_BRIGHTNESS], 255, 1000)
            # resp = requests.post(
            #     f"{self._host}/lamp?command=bright&value={self._brightness}"
            # ).json()
            # logger.info(f"lamp bright: {resp}")
            self.app.send(Commands.bright(self._brightness))
        if ATTR_COLOR_TEMP in kwargs:
            self._temp = color_temperature_mired_to_kelvin(kwargs[ATTR_COLOR_TEMP])
            # resp = requests.post(
            #     f"{self._host}/lamp?command=temp&value={self._temp}"
            # ).json()
            # logger.info(f"lamp temp: {resp}")
            self.app.send(Commands.temp(self._temp))

    def turn_off(self, **kwargs: Any) -> None:
        # resp = requests.post(f"{self._host}/lamp?command=turn_off").json()
        # logger.info(f"lamp turn_off: {resp}")
        self.app.send(Commands.turn_off())
        self._state = False

    def update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        pass
        # data = requests.get(f"{self._host}/lamp").json()
        # logger.info(f"lamp update: {data}")
        # self._state = data["is_on"]
        # self._brightness = data["brightness"]
        # self._temp = data["temp"]

    @property
    def is_on(self) -> bool:
        return self._state

    @property
    def device_info(self) -> DeviceInfo | None:
        return {
            "identifiers": {(DOMAIN, self._host)},
            "name": "lelight lamp",
            "sw_version": "none",
            "model": "lelight lamp",
            "manufacturer": "lelight",
        }

    async def async_removed_from_registry(self) -> None:
        await self.app.backend.close()
