import enum
import logging
from datetime import datetime, timezone
from typing import NotRequired, TypedDict
from config import Config, Device
from mqtt.discovery.components import Components
from mqtt.discovery.device_payload import DevicePayload, device_payload
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
	json_attributes_topic: str
	json_attributes_template: str

class DeviceTrackerAttributesPayload(TypedDict):
	rssi: int
	last_seen: str

def get_device_tracker_payload(address: str) -> DevicePayload:
  device = Config.get_instance().devices[address]
  identifiers = [device_payload["identifiers"][0], address]
  name = f"Device Tracker {device.name if device.name is not None else address}"

  return {
		"connections": {("mac", address)},
    "identifiers": identifiers,
    "name": name,
  }

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
	attributes_topic = state_topic
	safe_device_address = device.address.replace(":", "_")

	device_name = device.name if device.name is not None else safe_device_address

	discovery_payload: DeviceTrackerDiscoveryPayload = {
		"device": get_device_tracker_payload(device.address),
		"state_topic": state_topic,
    "value_template": "{{ value_json.state }}",
		"json_attributes_topic": attributes_topic,
    "json_attributes_template": "{{ {'rssi': value_json.rssi, 'last_seen': value_json.last_seen} | tojson }}",
		"name": f"Device Tracker {device_name}",
		"unique_id": f"device_tracker_{safe_device_address}",
		"payload_home": HomeState.home.value,
		"payload_not_home": HomeState.not_home.value,
		"source_type": SourceType.bluetooth_le,
		# "payload_available": "online",
		# "payload_not_available": "offline",
		# "availability": 
		# {
		# 	"topic": device_availability_topic,
		# }
		
	}

	send_event(discovery_topic, discovery_payload)

def sendDeviceHomeEvent(device: DeviceStatusUpdateData):
	config = Config.get_instance()
	config_device = config.devices[device["address"]]
	now = datetime.now(timezone.utc)

	previous_state = config_device.state
	previous_rssi = config_device.rssi

	current_rssi = device["rssi"]
	state_changed = previous_state != HomeState.home
	# rssi_changed = previous_rssi is None or abs(current_rssi - previous_rssi) > 5

	if not (state_changed):
		config_device.mark_home(previous_rssi if previous_rssi is not None else -100, now)
		logger.debug("No state change for %s; skipping MQTT publish", config_device.address)
		return

	config_device.mark_home(current_rssi, now)
	deviceTopic = get_device_tracker_state_topic(device["address"])
	send_event(deviceTopic, {
		"state": HomeState.home.value,
		"rssi": config_device.rssi,
		"last_seen": now.isoformat()
	})

def sendDeviceNotHomeEvent(deviceAddress: str):
	config = Config.get_instance()
	config_device = config.devices[deviceAddress]
	previous_state = config_device.state
	config_device.mark_not_home()

	if previous_state == HomeState.not_home:
		logger.debug("State already not_home for %s; skipping MQTT publish", config_device.address)
		return

	deviceTopic = get_device_tracker_state_topic(deviceAddress)
	send_event(deviceTopic, {
		"state": HomeState.not_home.value,
	})
