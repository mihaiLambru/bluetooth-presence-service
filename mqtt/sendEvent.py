import enum, json
from typing import TypedDict
from bleak.backends.device import BLEDevice
from mqtt.config import mqttc

class SentEvent(enum.StrEnum): 
	DEVICE_UPDATE = "device_update"

def sendEvent(eventType: str, data: object | str) -> None:
	print(f"Sending event: {eventType} {data}")
	if isinstance(data, dict):
		print("It's a dict object")
		mqttc.publish(eventType, json.dumps(data))
	if isinstance(data, str):
		mqttc.publish(eventType, data)
	else:
		print('Unkown data while sending event')

class DeviceStatusUpdateData(TypedDict):
	address: str
	device: BLEDevice | None
	found: bool

