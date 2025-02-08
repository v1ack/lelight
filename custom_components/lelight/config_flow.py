from logging import getLogger
from typing import Any

import voluptuous as vol
from homeassistant import config_entries, exceptions
from homeassistant.core import HomeAssistant

from .const import DOMAIN

logger = getLogger(DOMAIN)

DATA_SCHEMA = vol.Schema({vol.Required("host"): str})


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    if len(data["host"].strip()) != 8:
        raise InvalidHost("Host name must be 8 characters long")

    return {"title": data["host"].strip()}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hello World."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                return self.async_create_entry(title=info["title"], data=user_input)
            except InvalidHost:
                errors["host"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                logger.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""
