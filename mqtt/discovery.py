
from typing import Dict, TypedDict
from mqtt.sendEvent import sendEvent # type: ignore

def get_discovery_topic(device_address: str):
	safeDeviceAddress = device_address.replace(":", "_")
	return f"homeassistant/device_tracker/{safeDeviceAddress}/config"

class DevicePayload(TypedDict):
	identifiers: list[str]
	name: str
	manufacturer: str
	model: str
	sw_version: str

class DiscoveryPayload(TypedDict):
	dev: DevicePayload
	o: Dict[str, str]
	cmps: Dict[str, Dict[str, str]]

device_payload: DevicePayload = {
  "identifiers": ["bt-scan-service"],
  "name": "Bluetooth Presence Service",
  "manufacturer": "Mihai",
  "model": "bt-presence",
  "sw_version": "0.1.0"
}
origin = {
	"name":"origin.name",
	"sw": "2.1",
}
cmps = {
	"bluetooth_presence_device_tracker": {
		"p": "device_tracker",
		"device_class":"temperature",
		"unit_of_measurement":"°C",
		"value_template":"{{ value_json.temperature}}",
		"unique_id":"temp01ae_t"
	},
}

def publish_discovery_message(device_address: str):
	discovery_topic = get_discovery_topic(device_address)
	discovery_payload: DiscoveryPayload = {
		"dev": device_payload,
		"o": origin,
		"cmps": cmps
	}
	sendEvent(discovery_topic, discovery_payload)

def runDiscovery(devices: list[str]):
	for device in devices:
		publish_discovery_message(device)