import logging
import voluptuous as vol
from homeassistant import config_entries, core, exceptions
from homeassistant.helpers import aiohttp_client
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({
    vol.Required("username"): str,
})

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            info = {
                "user_id": user_input,
                "udid": "Room 1"
            }

            return self.async_create_entry(title='HC Panel Integration', data=info)

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA
        )

class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""