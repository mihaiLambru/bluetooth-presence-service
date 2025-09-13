import enum, json
from typing import TypedDict
from bleak.backends.device import BLEDevice
from mqtt.config import mqttc

class SentEvent(enum.StrEnum): 
	DEVICE_UPDATE = "device_update"

def sendEvent(eventType: str, data: object | str) -> None:
	print(f"Sending event: {eventType} {data}")
	mqttc.publish(eventType, json.dumps(data))

class DeviceStatusUpdateData(TypedDict):
	address: str
	device: BLEDevice | None
	found: bool

