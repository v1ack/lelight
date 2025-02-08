from functools import cached_property
from logging import getLogger
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    LightEntity,
    ColorMode,
)
from homeassistant.helpers.entity import DeviceInfo

from .connector import App
from .connector_bless import BlessBackend
from .const import DOMAIN
from .encoder import Commands

logger = getLogger(DOMAIN)


async def async_setup_entry(hass, config_entry, async_add_entities):
    # Получаем ссылку на родительский класс нашей интеграции из конфигурации модуля.
    light = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([light])


def normalize_value(value: int, max: int, new_max: int) -> int:
    """Normalize value to new range."""
    return int(value * new_max / max)


class LeLight(LightEntity):
    min_color_temp_kelvin = 3000
    max_color_temp_kelvin = 6400

    unique_id = "lelight_light"
    color_mode = ColorMode.COLOR_TEMP
    supported_color_modes = {
        ColorMode.COLOR_TEMP,
    }

    def __init__(self, host: str) -> None:
        self._host = host
        self._state = False
        self.app = App(host, BlessBackend())

        # brightness from 0 to 1000 (device format)
        self._brightness = 1000

        # temp in kelvin from 3000 to 6400 (device format)
        self._temp = 4700

    @cached_property
    def name(self) -> str:
        return f"LeLight {self._host}"

    @property
    def brightness(self):
        return normalize_value(self._brightness, 1000, 255)

    @property
    def color_temp_kelvin(self) -> int | None:
        return self._temp

    async def async_turn_on(self, **kwargs: Any) -> None:
        if not self._state:
            await self.app.send(Commands.turn_on())
        logger.debug(f"lamp turn_on: {kwargs}")
        self._state = True

        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = normalize_value(kwargs[ATTR_BRIGHTNESS], 255, 1000)
            await self.app.send(Commands.bright(self._brightness))

        if ATTR_COLOR_TEMP_KELVIN in kwargs:
            self._temp = kwargs[ATTR_COLOR_TEMP_KELVIN]

            await self.app.send(Commands.temp(self._temp))

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.app.send(Commands.turn_off())
        self._state = False

    def update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """

    @property
    def is_on(self) -> bool:
        return self._state

    @cached_property
    def device_info(self) -> DeviceInfo | None:
        return {
            "identifiers": {(DOMAIN, self._host)},
            "name": f"lelight lamp {self._host}",
            "sw_version": "none",
            "model": "lelight lamp",
            "manufacturer": "lelight",
        }

    async def async_removed_from_registry(self) -> None:
        await self.app.backend.close()
