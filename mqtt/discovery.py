
import enum
from typing import Dict, TypedDict
from mqtt.sendEvent import sendEvent # type: ignore

class Components(enum.StrEnum):
	DeviceTracker = "device_tracker"
	Device = "device"
def get_discovery_topic(device_address: str):
	safeDeviceAddress = device_address.replace(":", "_")
	return f"homeassistant/{Components.Device}/{safeDeviceAddress}/config"

class DevicePayload(TypedDict):
	identifiers: list[str]
	name: str
	manufacturer: str
	model: str
	sw_version: str

class HomeState(enum.StrEnum):
	home = "home"
	not_home = "not_home"

class DiscoveryPayload(TypedDict):
	state_topic: str
	name: str
	payload_home: HomeState
	payload_not_home: HomeState
	unique_id: str
	device: DevicePayload
	# o: Dict[str, str]
	components: Dict[str, Dict[str, str]]
	platform: Components

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
	print(f"Publishing discovery message for {device_address}")
	discovery_topic = get_discovery_topic(device_address)
	safe_device_address = device_address.replace(":", "_")
	discovery_payload: DiscoveryPayload = {
		"device": device_payload,
		# "o": origin,
		"components": cmps,
		"state_topic": f"homeassistant/{Components.Device}/{safe_device_address}/state",
		"name": "Mihai's tracker",
		"unique_id": "mihais_tracker",
		"payload_home": HomeState.home,
		"payload_not_home": HomeState.not_home,
		"platform": Components.DeviceTracker
	}
	sendEvent(discovery_topic, discovery_payload)

def runDiscovery(devices: list[str]):
	for device in devices:
		publish_discovery_message(device)