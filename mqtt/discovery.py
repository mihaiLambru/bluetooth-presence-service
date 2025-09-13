
import enum
from typing import TypedDict
from mqtt.sendEvent import sendEvent
from mqtt.states import HomeState
from mqtt.topics import get_device_tracker_config_topic, get_device_tracker_state_update_topic, get_discovery_topic # type: ignore

class DevicePayload(TypedDict):
	identifiers: list[str]
	name: str
	manufacturer: str
	model: str
	sw_version: str

class SourceType(enum.StrEnum):
	bluetooth_le = "bluetooth_le"

class DiscoveryPayload(TypedDict):
	state_topic: str
	name: str
	payload_home: HomeState
	payload_not_home: HomeState
	unique_id: str
	device: DevicePayload
	source_type: SourceType

device_payload: DevicePayload = {
  "identifiers": ["bt-scan-service"],
  "name": "Bluetooth Presence Service",
  "manufacturer": "Lambru",
  "model": "bt-presence",
  "sw_version": "0.1.0"
}

def publish_discovery_message_for_device_tracker(device_address: str):
	print(f"Publishing discovery message for {device_address}")
	discovery_topic = get_device_tracker_config_topic(device_address)
	state_topic = get_device_tracker_state_update_topic(device_address)
	safe_device_address = device_address.replace(":", "_")
	discovery_payload: DiscoveryPayload = {
		"device": device_payload,
		"state_topic": state_topic,
		"name": f"Device Tracker {safe_device_address}",
		"unique_id": f"device_tracker_{safe_device_address}",
		"payload_home": HomeState.home,
		"payload_not_home": HomeState.not_home,
		"source_type": SourceType.bluetooth_le
	}
	sendEvent(discovery_topic, discovery_payload)

def runDiscovery(devices: list[str]):
	for device in devices:
		publish_discovery_message_for_device_tracker(device)