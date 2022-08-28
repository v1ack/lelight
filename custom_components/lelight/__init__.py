from __future__ import annotations
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .light import LeLight
import logging

_LOGGER = logging.getLogger(__name__)
# Перечисляем типы устройств, которое поддерживает интеграция
PLATFORMS: list[str] = ["light"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Создаем объект с подключением к сервису

    # host = hass.data[DOMAIN][config_entry.entry_id]
    #
    # sst1 = sst.SST(hass, entry.data["username"], entry.data["password"])
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = LeLight(entry.data["host"])
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
