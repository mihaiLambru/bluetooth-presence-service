import enum, json
from typing import TypedDict
from bleak.backends.device import BLEDevice

class SentEvent(enum.Enum): 
	DEVICE_UPDATE = "device_update"

async def sendEvent(eventType: SentEvent, event: dict):
  mqttc.publish(eventType, json.dumps(event))

class DeviceStatusUpdateData(TypedDict):
	address: str
	device: BLEDevice | None
	found: bool


async def sendDeviceUpdateEvent(event: DeviceStatusUpdateData):
  mqttc.publish(SentEvent.DEVICE_UPDATE, f"address={event['address']},deviceName={event['device'].name if event['device'] else 'None'},found={event['found']}")