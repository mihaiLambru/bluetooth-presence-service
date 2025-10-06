import enum
import logging
from typing import NotRequired
from config import Device
from mqtt.discovery.components import Components
from mqtt.discovery.device_payload import device_payload
from mqtt.discovery.discovery_payload import DiscoveryPayload
from mqtt.send_event import DeviceStatusUpdateData, send_event
from mqtt.types import HomeState

logger = logging.getLogger("components.device_tracker")

class SourceType(enum.StrEnum):
	bluetooth_le = "bluetooth_le"

class DeviceTrackerDiscoveryPayload(DiscoveryPayload):
	payload_home: str
	payload_not_home: str
	source_type: SourceType
	unit_of_measurement: NotRequired[str]
	state_topic: str


# Device Tracker
def get_device_tracker_core_topic(device_address: str):
	if (device_address == ""):
		raise ValueError("Device address cannot be empty")

	safeDeviceAddress = device_address.replace(":", "_")
	return f"homeassistant/{Components.DeviceTracker.value}/{safeDeviceAddress}"

def get_device_tracker_config_topic(device_address: str):
	coreTopic = get_device_tracker_core_topic(device_address)
	return f"{coreTopic}/config"


def get_device_tracker_state_topic(device_address: str):
	coreTopic = get_device_tracker_core_topic(device_address)
	return f"{coreTopic}/state"


def publish_discovery_message_for_device_tracker(device: Device):
	logger.info(f"Publishing discovery message for {device.address}")
	discovery_topic = get_device_tracker_config_topic(device.address)
	state_topic = get_device_tracker_state_topic(device.address)
	safe_device_address = device.address.replace(":", "_")

	discovery_payload: DeviceTrackerDiscoveryPayload = {
		"device": device_payload,
		"state_topic": state_topic,
		"name": f"Device Tracker {device.name}",
		"unique_id": f"device_tracker_{safe_device_address}",
		"payload_home": HomeState.home.value,
		"payload_not_home": HomeState.not_home.value,
		"source_type": SourceType.bluetooth_le
	}

	send_event(discovery_topic, discovery_payload)

def sendDeviceHomeEvent(device: DeviceStatusUpdateData):
	deviceTopic = get_device_tracker_state_topic(device["address"])
	send_event(deviceTopic, HomeState.home.value)

def sendDeviceNotHomeEvent(deviceAddress: str):
	deviceTopic = get_device_tracker_state_topic(deviceAddress)
	send_event(deviceTopic, HomeState.not_home.value)
