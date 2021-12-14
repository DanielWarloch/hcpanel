import logging
import aiohttp
import json
import time
import asyncio

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)

THERMOSTAT_PROPERTIES = [
    "Cooling",
    "Heating",
    "Max_temp",
    "Min_temp",
    "Max_humidity",
    "Min_humidity",
    "Temperature_auto",
    "Ventilation_auto",
]

SENSOR_PROPERTIES = ["Humidity", "Pressure", "Temperature"]


class Wrapper:
    API_URL = "http://localhost:3500"

    def __init__(
        self, session: aiohttp.ClientSession, base_url=API_URL, update_interval=30
    ):
        _LOGGER.debug("Init wrapper...")
        self.headers = {"Accept": "application/json", "Accept-Encoding": "gzip"}
        self.base_url = base_url
        self.update_interval = update_interval
        self.session = session
        self.last_update = None
        self.update_lock = asyncio.Lock()

    async def get(self, request_path):
        url = self.base_url + request_path
        _LOGGER.debug("Sending GET request: " + url)
        async with self.session.get(url) as response:
            if response.status != 200:
                _LOGGER.warning("Invalid response from API: %s", response.status)

            data = await response.text()
            _LOGGER.debug(data)
            return data

    async def post(self, request_path, post_data):
        url = self.base_url + request_path
        _LOGGER.debug("Sending POST request: " + url)
        async with self.session.post(url, data=post_data) as response:
            if response.status != 200:
                _LOGGER.warning("Invalid response from API: %s", response.status)

            data = await response.text()
            _LOGGER.debug(data)
            return data

    async def get_device(self):
        device = {"name": "Thermostat"}
        device.update(await self.get_thermostat_properties())
        device.update(await self.get_sensor_properties())
        device.update(await self.get_control_device_property('Heating', 'State_on'))
        device.update(await self.get_control_device_property('Cooling', 'State_on'))
        #print("device:", device)
        return device

    async def set_thermostat_property(self, name, value):
        path = f"/thermostat/setProperty?name={name}&value={value}"
        _LOGGER.debug("Setting property...")
        data = {"name": name, "value": value}
        _LOGGER.debug(data)
        result = await self.post(path, json.dumps(data))
        _LOGGER.debug(result)

        return result

    async def get_thermostat_property(self, name):
        path = f"/thermostat/getProperty?name={name}"
        _LOGGER.debug("Getting property...")
        data = {
            "name": name,
        }
        _LOGGER.debug(data)
        #        result = await self.post(path, json.dumps(data))
        result = await self.get(path)
        _LOGGER.debug(result)

        return result

    async def get_control_device_property(self, device_name, property_name):
        path = f"/getControlDeviceProperty?device={device_name}&property={property_name}"
        _LOGGER.debug("Getting property...")
        
        result = await self.get(path)
        _LOGGER.debug(result)
        print(result)
        return { f'{device_name}_{property_name}': result }

    async def get_thermostat_properties(self):
        properties = {}
        for property in THERMOSTAT_PROPERTIES:
            value = await self.get_thermostat_property(property)
            properties.update({property: value})
        _LOGGER.debug(f"device_properties:{properties}")
        return properties

    async def get_sensor_properties(self):
        path = f"/sensors/getSensorData?name=BME280"
        _LOGGER.debug("Getting sensor properties...")
        data = {"name": "BME280"}
        _LOGGER.debug(data)
        # result = await self.post(path, json.dumps(data))
        result = await self.get(path)
        #print("aaaaaaaaaaaa:", result)
        return self.get_sensor_data_as_dict(result)

    def get_sensor_data_as_dict(self, data):
        keys = ["Temperature", "Humidity", "Pressure"]
        dict = {}
        for key in keys:
            key_idx = data.find(key)
            colon_idx = data.find(":", key_idx)
            comma_idx = data.find(",", key_idx)
            value = float(data[colon_idx + 2 : comma_idx])
            dict.update({key: value})
        return dict
