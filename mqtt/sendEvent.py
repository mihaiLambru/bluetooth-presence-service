import enum, json
from typing import TypedDict
from bleak.backends.device import BLEDevice
from mqtt.config import mqttc
from mqtt.states import HomeState
from mqtt.topics import get_device_tracker_config_topic

class SentEvent(enum.StrEnum): 
	DEVICE_UPDATE = "device_update"

def sendEvent(eventType: str, data: object | str) -> None:
	print(f"Sending event: {eventType} {data}")
	mqttc.publish(eventType, json.dumps(data))

class DeviceStatusUpdateData(TypedDict):
	address: str
	device: BLEDevice | None
	found: bool

def sendDeviceHomeEvent(device: DeviceStatusUpdateData):
	deviceTopic = get_device_tracker_config_topic(device["address"])
	sendEvent(deviceTopic, HomeState.home.value)

def sendDeviceNotHomeEvent(deviceAddress: str):
	deviceTopic = get_device_tracker_config_topic(deviceAddress)
	sendEvent(deviceTopic, HomeState.not_home.value)