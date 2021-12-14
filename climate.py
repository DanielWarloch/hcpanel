from __future__ import annotations

import logging
import json

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_HEAT,
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT_COOL,
    HVAC_MODE_OFF,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_IDLE,
    CURRENT_HVAC_OFF,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_TARGET_TEMPERATURE_RANGE
)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SUPPORT_HVAC = [HVAC_MODE_HEAT, HVAC_MODE_COOL, HVAC_MODE_HEAT_COOL, HVAC_MODE_OFF]


async def async_setup_entry(hass, config_entry, async_add_entities):
    api = hass.data[DOMAIN][config_entry.entry_id]
    device = await api.get_device()
    async_add_entities([Thermostat(device, api, config_entry)], True)


class Thermostat(ClimateEntity):
    def __init__(self, device, api, config_entry):
        _LOGGER.debug("Init Thermostat...")
        self._device = device
        print("thermostat#init " + str(device))
        self._config_entry = config_entry
        self._api = api
        self.update_properties(device)
        self._mode = HVAC_MODE_OFF

    def update_properties(self, device):
        self._name = device["name"]
        if device["Humidity"] is not None:
            self._humidity = float(device["Humidity"])
        else:
            self._humidity = None
        if device["Pressure"] is not None:
            self._pressure = float(device["Pressure"])
        else:
            self._pressure = None
        if device["Temperature"] is not None:
            self._temperature = float(device["Temperature"])
        else:
            self._temperature = None
        if device["Min_temp"] is not None:
            self._min_temperature = float(device["Min_temp"])
        else:
            self._min_temperature = None
        if device["Max_temp"] is not None:
            self._max_temperature = float(device["Max_temp"])
        else:
            self._max_temperature = None
        if device["Min_temp"] is not None and device["Max_temp"] is not None:
            self._target_temperature = (float(device["Min_temp"])+float(device["Max_temp"]))/2
        else:
            self._target_temperature = None
        if device["Min_humidity"] is not None:
            self._min_humidity = float(device["Min_humidity"])
        else:
            self._min_humidity = None
        if device["Max_humidity"] is not None:
            self._max_humidity = float(device["Max_humidity"])
        else:
            self._max_humidity = None
        if device["Temperature_auto"] is not None:
            self._temperature_auto = bool(device["Temperature_auto"])
        else:
            self._temperature_auto = None
        if device["Ventilation_auto"] is not None:
            self._ventilation_auto = bool(device["Ventilation_auto"])
        else:
            self._ventilation_auto = None
        if bool(device["Heating_State_on"]):
            self._state = CURRENT_HVAC_HEAT
        elif bool(device["Cooling_State_on"]):
            self._state = CURRENT_HVAC_COOL
        if not bool(device["Heating_State_on"]) and not bool(device["Cooling_State_on"]):
            self._state = CURRENT_HVAC_IDLE
        if not bool(device["Temperature_auto"]) and not bool(device["Heating_State_on"]) and not bool(device["Cooling_State_on"]):
            self._state = CURRENT_HVAC_OFF
        #print(device)


    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    async def async_update(self):
        _LOGGER.debug("Updating...")
        self.update_properties(await self._api.get_device())

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._temperature

#    @property
#    def target_temperature(self):
#        """Return the temperature we try to reach."""
#        return self._target_temperature


    @property
    def target_temperature_low(self):
        """Return the lower bound target temperature."""
        return self._min_temperature

    @property
    def target_temperature_high(self):
        """Return the upper bound target temperature."""
        return self._max_temperature

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_TARGET_TEMPERATURE_RANGE #SUPPORT_PRESET_MODE #SUPPORT_TARGET_TEMPERATURE  # | SUPPORT_PRESET_MODE

    @property
    def hvac_mode(self):
        """Return hvac operation ie. heat, cool mode.

        Need to be one of HVAC_MODE_*.
        """
        return self._mode

    @property
    def hvac_modes(self):
        """Return the list of available hvac operation modes.

        Need to be a subset of HVAC_MODES.
        """
        return SUPPORT_HVAC

    @property
    def hvac_action(self) -> Optional[str]:
        """Return the current running hvac operation if supported.

        Need to be one of CURRENT_HVAC_*.
        """
        #        return self._state
        return self._mode

    async def async_set_temperature(self, **kwargs):
        """Set new target temperatures."""
        target_temperature_low = kwargs.get("target_temp_low")
        target_temperature_high = kwargs.get("target_temp_high")
        print(f'Kwargs: {kwargs}')
        print(f' low: {target_temperature_low} high: {target_temperature_high}')
        if target_temperature_low and target_temperature_high:
            print('Print 1')
            _LOGGER.debug(
                "%s: Setting target temperature range from %s to %s", self._name, target_temperature_low, target_temperature_high
            )
            self._min_temperature = target_temperature_low
            await self._api.set_thermostat_property("Min_temp", target_temperature_low)
            await self._api.set_thermostat_property("Max_temp", target_temperature_high)

    async def async_set_hvac_mode(self, hvac_mode):
        _LOGGER.debug("%s: Setting hvac mode to %s", self._name, hvac_mode)
        print(hvac_mode)
        self._mode=hvac_mode
        print(self)
        if hvac_mode == HVAC_MODE_HEAT:
            await self._api.set_thermostat_property("Temperature_auto", "false")
            await self._api.set_thermostat_property("Cooling", "false")
            await self._api.set_thermostat_property("Heating", "true")
#            self._state = CURRENT_HVAC_HEAT
        elif hvac_mode == HVAC_MODE_COOL:
            await self._api.set_thermostat_property("Temperature_auto", "false")
            await self._api.set_thermostat_property("Heating", "false")
            await self._api.set_thermostat_property("Cooling", "true")
#            self._state = CURRENT_HVAC_COOL
        elif hvac_mode == HVAC_MODE_HEAT_COOL:
            await self._api.set_thermostat_property("Temperature_auto", "true")
        elif hvac_mode == HVAC_MODE_OFF:
            await self._api.set_thermostat_property("Temperature_auto", "false")
            await self._api.set_thermostat_property("Heating", "false")
            await self._api.set_thermostat_property("Cooling", "false")
#            self._state = CURRENT_HVAC_OFF

HVAC_MODE_HEAT_COOL
