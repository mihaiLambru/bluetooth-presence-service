import enum
from typing import NotRequired
from mqtt.discovery.components import Components
from mqtt.discovery.device_payload import device_payload
from mqtt.discovery.discovery_payload import DiscoveryPayload
from mqtt.sendEvent import DeviceStatusUpdateData, sendEvent
from mqtt.types import HomeState

class SourceType(enum.StrEnum):
	bluetooth_le = "bluetooth_le"

class DeviceTrackerDiscoveryPayload(DiscoveryPayload):
	payload_home: HomeState
	payload_not_home: HomeState
	source_type: SourceType
	unit_of_measurement: NotRequired[str]
	state_topic: str


# Device Tracker
def get_device_tracker_core_topic(device_address: str):
	safeDeviceAddress = device_address.replace(":", "_")
	return f"homeassistant/{Components.DeviceTracker.value}/{safeDeviceAddress}"

def get_device_tracker_config_topic(device_address: str):
	coreTopic = get_device_tracker_core_topic(device_address)
	return f"{coreTopic}/config"


def get_device_tracker_state_update_topic(device_address: str):
	coreTopic = get_device_tracker_core_topic(device_address)
	return f"{coreTopic}/state"


def publish_discovery_message_for_device_tracker(device_address: str):
	print(f"Publishing discovery message for {device_address}")
	discovery_topic = get_device_tracker_config_topic(device_address)
	state_topic = get_device_tracker_state_update_topic(device_address)
	safe_device_address = device_address.replace(":", "_")

	discovery_payload: DeviceTrackerDiscoveryPayload = {
		"device": device_payload,
		"state_topic": state_topic,
		"name": f"Device Tracker {safe_device_address}",
		"unique_id": f"device_tracker_{safe_device_address}",
		"payload_home": HomeState.home,
		"payload_not_home": HomeState.not_home,
		"source_type": SourceType.bluetooth_le
	}

	sendEvent(discovery_topic, discovery_payload)

def sendDeviceHomeEvent(device: DeviceStatusUpdateData):
	deviceTopic = get_device_tracker_config_topic(device["address"])
	sendEvent(deviceTopic, HomeState.home.value)

def sendDeviceNotHomeEvent(deviceAddress: str):
	deviceTopic = get_device_tracker_config_topic(deviceAddress)
	sendEvent(deviceTopic, HomeState.not_home.value)
