import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client

from .const import DOMAIN
from .wrapper import Wrapper

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["climate"]

async def async_setup(hass, config):
    hass.states.async_set("hcpanel.HC_Panel", "XD")

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.debug("Setting up component's entry.")
    _LOGGER.debug("Entry -> title: " + entry.title + ", data: " + str(entry.data) + ", id: " + entry.entry_id + ", domain: " + entry.domain)
    hass.data.setdefault(DOMAIN, {})
    http_session = aiohttp_client.async_get_clientsession(hass)
    hass.data[DOMAIN][entry.entry_id] = Wrapper(http_session)

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True