import enum, json
from typing import TypedDict
from bleak.backends.device import BLEDevice
from mqtt.config import mqttc

class SentEvent(enum.StrEnum): 
	DEVICE_UPDATE = "device_update"

def sendEvent(eventType: str, data: any) -> None: # type: ignore
	print(f"Sending event: {eventType} {data}")
	mqttc.publish(eventType, json.dumps(data))

class DeviceStatusUpdateData(TypedDict):
	address: str
	device: BLEDevice | None
	found: bool

def sendDeviceUpdateEvent(event: DeviceStatusUpdateData):
	deviceName = 'None'
	if event['device']:
		deviceName = event['device'].name

	data: dict = { # type: ignore
		"address": event['address'],
		"deviceName": deviceName,
		"found": event['found']
	}
	sendEvent(SentEvent.DEVICE_UPDATE, data)