
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
  "manufacturer": "Lambru",
  "model": "bt-presence",
  "sw_version": "0.1.0"
}

def publish_discovery_message_for_device_tracker(device_address: str):
	print(f"Publishing discovery message for {device_address}")
	discovery_topic = get_discovery_topic(device_address)
	safe_device_address = device_address.replace(":", "_")
	discovery_payload: DiscoveryPayload = {
		"device": device_payload,
		"state_topic": f"homeassistant/{Components.DeviceTracker}/{safe_device_address}/state",
		"name": f"Device Tracker {safe_device_address}",
		"unique_id": f"device_tracker_{safe_device_address}",
		"payload_home": HomeState.home,
		"payload_not_home": HomeState.not_home,
		"source_type": "bluetooth_le"
	}
	sendEvent(discovery_topic, discovery_payload)

def runDiscovery(devices: list[str]):
	for device in devices:
		publish_discovery_message_for_device_tracker(device)