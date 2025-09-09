import enum, json
from typing import TypedDict
from bleak.backends.device import BLEDevice
from mqtt.config import mqttc

class SentEvent(enum.Enum): 
	DEVICE_UPDATE = "device_update"

async def sendEvent(eventType: SentEvent, event: dict):
  mqttc.publish(eventType.value, json.dumps(event))

class DeviceStatusUpdateData(TypedDict):
	address: str
	device: BLEDevice | None
	found: bool


async def sendDeviceUpdateEvent(event: DeviceStatusUpdateData):
	deviceName = 'None'
	if event['device']:
		deviceName = event['device'].name

	data = {
		"address": event['address'],
		"deviceName": deviceName,
		"found": event['found']
	}

	mqttc.publish(SentEvent.DEVICE_UPDATE, data)